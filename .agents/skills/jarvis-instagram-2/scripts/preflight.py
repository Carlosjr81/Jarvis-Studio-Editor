#!/usr/bin/env python3
"""Inspect local execution resources; never downloads, synthesizes or spends credits."""
import argparse, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path

def inspect_profile(path):
    p=Path(path).resolve()
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("is_default") is not True or d.get("approval",{}).get("status")!="approved_by_user":
            return {"valid":False,"reason":"profile_not_approved_default"}
        paths={}
        for key in ("reference_audio","reference_transcript"):
            f=(p.parent/d[key]).resolve()
            if not f.is_relative_to(p.parent) or not f.is_file():
                return {"valid":False,"reason":"missing_or_external_reference"}
            paths[key]=f
        digest=hashlib.sha256(paths["reference_audio"].read_bytes()).hexdigest()
        if digest!=d.get("reference_sha256"):
            return {"valid":False,"reason":"reference_hash_mismatch"}
        if not paths["reference_transcript"].read_text(encoding="utf-8").strip():
            return {"valid":False,"reason":"empty_transcript"}
        return {"valid":True,"reference_sha256":digest,"approved_date":d["approval"].get("date")}
    except (OSError,ValueError,KeyError,TypeError) as e:
        return {"valid":False,"reason":type(e).__name__}

def available(name):
    try: return importlib.util.find_spec(name) is not None
    except (ImportError,ValueError,ModuleNotFoundError): return False

def main():
    a=argparse.ArgumentParser();a.add_argument("--voice-profile");o=a.parse_args()
    modules={n:available(n) for n in ("torch","torchaudio","numpy","soundfile","transformers","voxcpm","PIL")}
    caches=[Path.home()/".cache/huggingface/hub",Path("/workspace")]
    revision="32279effe8c19989596f05d353d1447f51d9e915"
    cached=False
    h=caches[0]/"models--openbmb--VoxCPM2/snapshots"/revision
    if h.is_dir(): cached=any(p.suffix in (".safetensors",".bin",".pt") and p.is_file() for p in h.rglob("*"))
    font_names=""
    if shutil.which("fc-list"):
        font_names=subprocess.run(["fc-list",":","family"],capture_output=True,text=True,timeout=20).stdout.lower()
    result={"brand_fonts":{n:n.lower() in font_names for n in ("Teko","Gilroy")},"local_tools":{n:bool(shutil.which(n)) for n in ("ffmpeg","ffprobe","fc-match","node")},"python_modules":modules,"voxcpm2_snapshot_cached":cached,"note":"Presence checks do not prove synthesis, provider authentication or catalog registration."}
    if o.voice_profile:result["voice_profile"]=inspect_profile(o.voice_profile)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not o.voice_profile or result["voice_profile"]["valid"] else 2
if __name__=="__main__":raise SystemExit(main())
