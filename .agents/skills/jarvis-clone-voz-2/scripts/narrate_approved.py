#!/usr/bin/env python3
"""Synthesize using a private approved voice profile and cached model only."""
import argparse,hashlib,importlib.metadata,json,re,sys
from pathlib import Path
from preflight import inspect_profile
SOURCE_COMMIT="cce58a5b59303c9bd63d12f23afe6a49a4a80c59"
MODEL_REVISION="32279effe8c19989596f05d353d1447f51d9e915"

def chunks(text,limit=200):
    words=re.sub(r"\s+"," ",text).strip()
    if not words:raise ValueError("empty_text")
    result=[]
    for sentence in re.split(r"(?<=[.!?])\s+",words):
        part=""
        for word in sentence.split():
            if len(word)>limit:raise ValueError("word_too_long")
            if part and len(part)+len(word)+1>limit:result.append(part);part=""
            part=(part+" "+word).strip()
        if part:result.append(part)
    return result

def main():
    a=argparse.ArgumentParser();a.add_argument("--voice-profile",required=True,type=Path);a.add_argument("--text-file",required=True,type=Path);a.add_argument("--output",required=True,type=Path);o=a.parse_args()
    check=inspect_profile(o.voice_profile)
    if not check["valid"]:raise ValueError(check["reason"])
    if o.output.exists() or o.output.with_suffix(".json").exists():raise ValueError("output_already_exists")
    profile=json.loads(o.voice_profile.read_text());root=o.voice_profile.resolve().parent
    text=o.text_file.read_text(encoding="utf-8");parts=chunks(text)
    if len(text)>5000:raise ValueError("text_too_long")
    settings=profile.get("generation_settings",{})
    for key,wanted in {"source_commit":SOURCE_COMMIT,"model_revision":MODEL_REVISION,"seed":42,"cfg_value":2.0,"inference_timesteps":10,"sample_rate":48000}.items():
        if settings.get(key)!=wanted:raise ValueError("unsupported_approved_settings:"+key)
    package=importlib.metadata.distribution("voxcpm")
    direct=json.loads(package.read_text("direct_url.json") or "{}")
    installed=direct.get("vcs_info",{}).get("commit_id")
    if installed!=SOURCE_COMMIT:raise ValueError("voxcpm_source_revision_not_verified")
    import numpy as np
    import soundfile as sf
    import torch
    from huggingface_hub import snapshot_download
    from voxcpm import VoxCPM
    snapshot=snapshot_download("openbmb/VoxCPM2",revision=MODEL_REVISION,local_files_only=True)
    torch.set_num_threads(4);previous=torch.get_default_dtype()
    try:
        torch.set_default_dtype(torch.bfloat16)
        model=VoxCPM.from_pretrained(snapshot,load_denoiser=False,optimize=False,device="cpu",local_files_only=True)
    finally:torch.set_default_dtype(previous)
    rate=int(model.tts_model.sample_rate)
    if rate!=48000:raise ValueError("unexpected_sample_rate")
    audio=[]
    for i,part in enumerate(parts):
        with torch.inference_mode():
            wav=np.asarray(model.generate(text=part,reference_wav_path=str(root/profile["reference_audio"]),prompt_wav_path=str(root/profile["reference_audio"]),prompt_text=(root/profile["reference_transcript"]).read_text(encoding="utf-8").strip(),seed=42,cfg_value=2.0,inference_timesteps=10,max_len=256,retry_badcase=False),dtype=np.float32).reshape(-1)
        if wav.size<rate*.25 or not np.isfinite(wav).all() or np.max(np.abs(wav))<1e-4:raise ValueError("invalid_audio")
        if len(wav)/rate>max(25,len(part)*.25):raise ValueError("suspected_truncated_or_runaway_generation")
        if i:audio.append(np.zeros(round(.14*rate),dtype=np.float32))
        audio.append(wav)
    wav=np.concatenate(audio);peak=float(np.max(np.abs(wav)))
    if peak>.98:wav*=.98/peak
    o.output.parent.mkdir(parents=True,exist_ok=True)
    sf.write(o.output,wav,rate,subtype="PCM_16")
    report={"engine":"VoxCPM2","source_commit_requested":SOURCE_COMMIT,"model_revision":MODEL_REVISION,"reference_sha256":check["reference_sha256"],"audio_sha256":hashlib.sha256(o.output.read_bytes()).hexdigest(),"script_sha256":hashlib.sha256(text.encode()).hexdigest(),"seed":42,"cfg_value":2.0,"inference_timesteps":10,"sample_rate":rate,"segments":len(parts),"duration_seconds":len(wav)/rate,"peak_before_normalization":peak,"requires_review":"Listen and verify transcript; reference approval is not output approval."}
    o.output.with_suffix(".json").write_text(json.dumps(report,indent=2),encoding="utf-8");print(json.dumps(report))
    return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except (ValueError,OSError,ImportError) as e:print("Voice generation failed: "+str(e),file=sys.stderr);raise SystemExit(2)
