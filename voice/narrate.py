#!/usr/bin/env python3
"""Synthesize Carlos Jr's authorized voice; never fall back to a generic voice."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave

SOURCE_COMMIT = "cce58a5b59303c9bd63d12f23afe6a49a4a80c59"
MAX_REFERENCE_BYTES = 20 * 1024 * 1024

def chunks(text, limit=200):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise ValueError("O roteiro está vazio.")
    result, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        for word in sentence.split():
            if len(word) > limit:
                raise ValueError("Palavra maior que o limite de geração.")
            if current and len(current) + len(word) + 1 > limit:
                result.append(current)
                current = ""
            current = (current + " " + word).strip()
        # Keep sentence boundaries for predictable short CPU generations.
        if current:
            result.append(current)
            current = ""
    return result

def inspect_wav(path, min_seconds=0.25, max_seconds=180):
    try:
        with wave.open(str(path), "rb") as f:
            channels, width, rate, frames = f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()
            if channels != 1 or width != 2 or rate <= 0:
                raise ValueError("O WAV precisa ser mono PCM16.")
            if not min_seconds <= frames / rate <= max_seconds:
                raise ValueError("Duração do WAV fora do limite.")
            raw = f.readframes(frames)
    except (wave.Error, EOFError) as exc:
        raise ValueError("Arquivo WAV inválido.") from exc
    if len(raw) != frames * 2:
        raise ValueError("WAV truncado.")
    samples = [v[0] for v in struct.iter_unpack("<h", raw)]
    rms = math.sqrt(sum(v * v for v in samples) / len(samples)) / 32768
    peak = max(abs(v) for v in samples) / 32768
    if rms < 0.0001:
        raise ValueError("Áudio vazio ou silencioso.")
    return {"sample_rate": rate, "duration_seconds": frames / rate, "rms": rms, "peak": peak}

def download_reference(env_name, target):
    url = os.environ.get(env_name, "").strip()
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "resource2.heygen.ai" or parsed.username or parsed.password:
        raise ValueError("Referência ausente ou origem não autorizada. Configure o secret de referência.")
    class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            p = urllib.parse.urlsplit(newurl)
            if p.scheme != "https" or p.hostname != "resource2.heygen.ai":
                raise ValueError("Redirecionamento da referência não autorizado.")
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    try:
        opener = urllib.request.build_opener(RestrictedRedirect())
        with opener.open(url, timeout=60) as response, open(target, "wb") as dest:
            total = 0
            while True:
                block = response.read(65536)
                if not block:
                    break
                total += len(block)
                if total > MAX_REFERENCE_BYTES:
                    raise ValueError("Referência excede 20 MB.")
                dest.write(block)
        if total == 0:
            raise ValueError("Referência vazia.")
    except Exception:
        # Never include the private URL in logs.
        Path(target).unlink(missing_ok=True)
        raise ValueError("Falha ao baixar a referência privada; confira o secret e a disponibilidade do áudio.") from None

def prepare_reference(source, target):
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError("Arquivo de referência ausente ou vazio.")
    if not shutil.which("ffmpeg"):
        raise ValueError("FFmpeg não está instalado.")
    result = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(source), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(target)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=90, check=False)
    if result.returncode:
        raise ValueError("Não foi possível decodificar a referência de voz.")
    info = inspect_wav(target, min_seconds=3, max_seconds=30)
    if info["sample_rate"] != 16000:
        raise ValueError("A referência precisa ter 16 kHz.")
    return info

def generate(args):
    text = args.text_file.read_text(encoding="utf-8")
    parts = chunks(text)
    if len(text) > 5000:
        raise ValueError("Limite de 5000 caracteres por execução.")
    if args.output.exists():
        raise ValueError("A saída já existe. Escolha outro caminho para evitar áudio antigo.")
    if args.reference is None and not args.reference_url_env:
        raise ValueError("Sua referência é obrigatória; voz genérica não é permitida.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="jarvis-voice-") as private_dir:
        private_dir = Path(private_dir)
        source = args.reference
        if source is None:
            source = private_dir / "reference-source"
            download_reference(args.reference_url_env, source)
        reference = private_dir / "reference.wav"
        ref_info = prepare_reference(source, reference)
        if args.check_reference_only:
            print(json.dumps({"reference_valid": True, **ref_info}))
            return
        import numpy as np
        import soundfile as sf
        import torch
        from huggingface_hub import snapshot_download
        from voxcpm import VoxCPM
        torch.set_num_threads(min(4, os.cpu_count() or 1))
        model_path = snapshot_download("openbmb/VoxCPM2", revision=args.model_revision)
        print("Modelo disponível. Carregando VoxCPM2.", flush=True)
        model = VoxCPM.from_pretrained(
            model_path, load_denoiser=False, optimize=False,
            device=args.device, local_files_only=True)
        rate = int(model.tts_model.sample_rate)
        audio, timing, cursor = [], [], 0
        for index, part in enumerate(parts):
            print(f"Gerando trecho {index + 1}/{len(parts)}.", flush=True)
            wav = np.asarray(model.generate(
                text=part, reference_wav_path=str(reference), seed=42 + index,
                cfg_value=2.0, inference_timesteps=10, max_len=1024,
                retry_badcase=True, retry_badcase_max_times=1), dtype=np.float32).reshape(-1)
            if not wav.size or not np.isfinite(wav).all():
                raise ValueError("O motor devolveu áudio vazio ou não finito.")
            duration = wav.size / rate
            if not 0.25 <= duration <= 45:
                raise ValueError("Duração inesperada; a geração atingiu o limite ou falhou.")
            if np.sqrt(np.mean(wav.astype(np.float64) ** 2)) < 0.0001:
                raise ValueError("O motor devolveu silêncio.")
            timing.append({"text": part, "start": cursor / rate, "end": (cursor + wav.size) / rate})
            audio.append(wav)
            cursor += wav.size
            if index < len(parts) - 1:
                pause = np.zeros(round(rate * 0.14), dtype=np.float32)
                audio.append(pause)
                cursor += pause.size
        joined = np.concatenate(audio)
        peak = float(np.max(np.abs(joined)))
        if peak > 0.98:
            joined *= 0.98 / peak
        # Final paths only appear after validation; partial/error outputs stay private.
        candidate = private_dir / "candidate.wav"
        sf.write(candidate, joined, rate, subtype="PCM_16")
        metrics = inspect_wav(candidate)
        manifest = {
            "status": "synthesized_needs_listening_review",
            "voice": "Carlos Jr - referencia autorizada",
            "engine": "VoxCPM2", "source_commit": SOURCE_COMMIT,
            "model_snapshot": Path(model_path).name, "device": args.device,
            "script_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "audio_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "metrics": metrics, "segments": timing,
            "limitations": "Métricas técnicas não validam semelhança vocal nem fidelidade da transcrição."
        }
        shutil.copyfile(candidate, args.output)
        args.output.with_suffix(".json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"output": str(args.output), **metrics}, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reference", type=Path)
    group.add_argument("--reference-url-env")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], default="cpu")
    parser.add_argument("--model-revision", default="main")
    parser.add_argument("--check-reference-only", action="store_true")
    args = parser.parse_args()
    try:
        generate(args)
    except Exception as exc:
        # Private transport errors are sanitized by download_reference.
        print(f"Falha na narração: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
