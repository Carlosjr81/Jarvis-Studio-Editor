#!/usr/bin/env python3
"""Isolated Frascolino PET voice generation; no personal voice profile is read."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import ipaddress

SOURCE_COMMIT = "cce58a5b59303c9bd63d12f23afe6a49a4a80c59"
MODEL_REVISION = "32279effe8c19989596f05d353d1447f51d9e915"
PROFILE_ID = "frascolino_pet_globalpack"
TEST_TEXT = "Olá! Eu sou o Frascolino, o mascote da Globalpack. Juntos, transformamos qualidade em confiança."
MAX_BYTES = 64 * 1024 * 1024

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise ValueError("A referência exige URL HTTPS sem credenciais no endereço.")
    # Reject local/private targets before any request, including redirect targets.
    addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):
        raise ValueError("A origem da referência precisa ser pública e acessível por HTTPS.")
    return url

class SecureRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def download_reference(target):
    try:
        url = validate_url(os.environ.get("FRASCOLINO_REFERENCE_URL", "").strip())
        opener = urllib.request.build_opener(SecureRedirect())
        total = 0
        with opener.open(url, timeout=60) as response, target.open("xb") as out:
            while True:
                block = response.read(65536)
                if not block:
                    break
                total += len(block)
                if total > MAX_BYTES:
                    raise ValueError("reference_too_large")
                out.write(block)
        if not total:
            raise ValueError("empty_reference")
    except Exception:
        target.unlink(missing_ok=True)
        raise ValueError("Não foi possível baixar a referência. Confira o secret exclusivo do Frascolino; URLs temporários podem expirar.") from None

def audio_metrics(path, rate, minimum, maximum):
    import numpy as np
    import soundfile as sf
    data, actual_rate = sf.read(path, dtype="float32", always_2d=True)
    if actual_rate != rate or data.shape[1] != 1 or not data.size:
        raise ValueError("Formato de áudio inesperado.")
    values = data[:, 0]
    duration = values.size / rate
    if not np.isfinite(values).all() or not minimum <= duration <= maximum:
        raise ValueError("Áudio não finito ou duração inválida.")
    rms = float(np.sqrt(np.mean(values.astype(np.float64) ** 2)))
    if rms < 0.0001:
        raise ValueError("Áudio silencioso.")
    return {"sample_rate": rate, "duration_seconds": duration,
            "rms": rms, "peak": float(np.max(np.abs(values)))}

def prepare_reference(source, target):
    # Keep the complete original. A fixed, documented 12-second excerpt conditions the model.
    result = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-n",
         "-protocol_whitelist", "file,pipe", "-i", str(source), "-t", "12", "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "pcm_s16le", str(target)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=90, check=False)
    if result.returncode:
        raise ValueError("Não foi possível extrair o áudio do arquivo de referência.")
    return audio_metrics(target, 16000, 3, 12.1)

def load_model():
    direct = json.loads(importlib.metadata.distribution("voxcpm").read_text("direct_url.json") or "{}")
    if direct.get("vcs_info", {}).get("commit_id") != SOURCE_COMMIT:
        raise ValueError("A revisão instalada do VoxCPM não corresponde à revisão fixada.")
    import torch
    from huggingface_hub import snapshot_download
    from voxcpm import VoxCPM
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    snapshot = snapshot_download("openbmb/VoxCPM2", revision=MODEL_REVISION)
    previous = torch.get_default_dtype()
    try:
        torch.set_default_dtype(torch.bfloat16)
        model = VoxCPM.from_pretrained(snapshot, load_denoiser=False,
                                       optimize=False, device="cpu", local_files_only=True)
    finally:
        torch.set_default_dtype(previous)
    if int(model.tts_model.sample_rate) != 48000:
        raise ValueError("Taxa de amostragem do modelo inesperada.")
    return model

def check_password(password):
    if len(password) < 20:
        raise ValueError("Configure FRASCOLINO_ARCHIVE_PASSWORD com pelo menos 20 caracteres.")

def archive_profile(folder, archive, password):
    import pyzipper
    check_password(password)
    if archive.exists():
        raise ValueError("O pacote de saída já existe.")
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    if not files or any(p.is_symlink() for p in folder.rglob("*")):
        raise ValueError("Conteúdo do pacote inválido.")
    with pyzipper.AESZipFile(archive, "x", compression=pyzipper.ZIP_DEFLATED,
                             encryption=pyzipper.WZ_AES) as bundle:
        bundle.setpassword(password.encode("utf-8"))
        bundle.setencryption(pyzipper.WZ_AES, nbits=256)
        for path in files:
            bundle.write(path, str(Path(PROFILE_ID) / path.relative_to(folder)))
    # Verify authenticated decryption and exact contents before allowing upload.
    with pyzipper.AESZipFile(archive) as bundle:
        bundle.setpassword(password.encode("utf-8"))
        expected = {str(Path(PROFILE_ID) / p.relative_to(folder)): p for p in files}
        if set(bundle.namelist()) != set(expected):
            raise ValueError("O conteúdo do pacote não corresponde ao perfil.")
        for name, path in expected.items():
            if bundle.read(name) != path.read_bytes():
                raise ValueError("Falha na verificação do pacote criptografado.")

def generate(archive):
    import numpy as np
    import soundfile as sf
    import torch
    password = os.environ.get("FRASCOLINO_ARCHIVE_PASSWORD", "")
    check_password(password)
    if archive.exists():
        raise ValueError("A saída já existe; nenhum arquivo será substituído.")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="frascolino-private-") as tmp:
        root = Path(tmp)
        source = root / "Referencia_Voz_Frascolino_Translucido_PET_Globalpack.mp4"
        reference = root / "referencia.wav"
        download_reference(source)
        metrics = prepare_reference(source, reference)
        source_hash, reference_hash = sha256(source), sha256(reference)
        model = load_model()
        with torch.inference_mode():
            wav = np.asarray(model.generate(
                text=TEST_TEXT, reference_wav_path=str(reference),
                seed=42, cfg_value=2.0, inference_timesteps=10,
                max_len=256, retry_badcase=False), dtype=np.float32).reshape(-1)
        rate = 48000
        if not wav.size or not np.isfinite(wav).all() or not 1 <= wav.size / rate < 35:
            raise ValueError("A geração falhou ou pode ter atingido o limite. Nenhuma amostra será entregue.")
        peak = float(np.max(np.abs(wav)))
        if peak > .98:
            wav *= .98 / peak
        sample = root / "Frascolino_Amostra_Teste.wav"
        sf.write(sample, wav, rate, subtype="PCM_16")
        sample_metrics = audio_metrics(sample, rate, 1, 35)
        (root / "texto_teste.txt").write_text(TEST_TEXT + "\n", encoding="utf-8")
        profile = {
            "schema_version": 1, "profile_id": PROFILE_ID,
            "display_name": "Frascolino translúcido PET — Globalpack",
            "is_default": False, "scope": "Globalpack/Frascolino/PET",
            "reference_authorization": "authorized_by_user",
            "sample_approval": "pending_listening_review",
            "source_file": source.name, "source_sha256": source_hash,
            "reference_audio": reference.name, "reference_sha256": reference_hash,
            "reference_excerpt": {"start_seconds": 0, "maximum_seconds": 12, "metrics": metrics},
            "reference_transcript": None, "cloning_mode": "reference_only",
            "sample_file": sample.name, "sample_sha256": sha256(sample),
            "sample_metrics": sample_metrics, "test_text": TEST_TEXT,
            "engine": "VoxCPM2", "source_commit": SOURCE_COMMIT,
            "model_revision": MODEL_REVISION, "device": "cpu", "dtype": "bfloat16",
            "generation_settings": {"seed": 42, "cfg_value": 2.0,
                "inference_timesteps": 10, "max_len": 256, "retry_badcase": False},
            "inference": "local_on_github_hosted_runner_no_voice_api",
            "personal_profile_accessed": False,
            "limitations": "A semelhança e o conteúdo da fala exigem escuta. Este perfil não substitui a voz pessoal padrão."
        }
        (root / "profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (root / "LEIA-ME.txt").write_text(
            "Perfil exclusivo Frascolino PET Globalpack. Não substituir default_voice.json pessoal.\n"
            "O MP4 original está preservado. A referência usada é o início de até 12 segundos, sem alteração de tom/velocidade.\n"
            "Amostra sintetizada: requer comparação auditiva e conferência do texto antes do uso.\n"
            "Abra este ZIP AES-256 com 7-Zip e a senha exclusiva cadastrada em FRASCOLINO_ARCHIVE_PASSWORD.\n",
            encoding="utf-8")
        if sha256(source) != source_hash or sha256(reference) != reference_hash:
            raise ValueError("A referência foi alterada durante a geração.")
        archive_profile(root, archive, password)
    print("Perfil exclusivo e amostra técnica criados em pacote criptografado; revisão auditiva pendente.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["preflight", "generate"])
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "preflight":
            load_model()
            print("VoxCPM2 carregado em CPU; nenhuma referência ou voz pessoal foi acessada.")
        else:
            if args.archive is None:
                raise ValueError("--archive é obrigatório.")
            generate(args.archive)
        return 0
    except Exception as exc:
        # HTTP exceptions are handled before this boundary; never print private URLs.
        print("Falha no perfil Frascolino: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
