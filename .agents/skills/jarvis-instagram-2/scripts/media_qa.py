#!/usr/bin/env python3
"""Probe an actual export. Does not certify speech quality or music separation."""
import argparse,json,shutil,subprocess
from pathlib import Path

def main():
    a=argparse.ArgumentParser();a.add_argument("media");o=a.parse_args()
    p=Path(o.media)
    if not p.is_file() or not shutil.which("ffprobe"):
        print(json.dumps({"valid":False,"reason":"missing_media_or_ffprobe"}));return 2
    t=subprocess.run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(p)],capture_output=True,text=True,timeout=30)
    if t.returncode:
        print(json.dumps({"valid":False,"reason":"ffprobe_failed"}));return 2
    try:
        d=json.loads(t.stdout);duration=float(d.get("format",{}).get("duration",0))
        videos=[{k:s.get(k) for k in ("codec_name","width","height","r_frame_rate")} for s in d["streams"] if s.get("codec_type")=="video"]
        audios=[{k:s.get(k) for k in ("codec_name","sample_rate","channels")} for s in d["streams"] if s.get("codec_type")=="audio"]
        ok=duration>0 and bool(videos)
        print(json.dumps({"valid":ok,"duration_seconds":duration,"video":videos,"audio":audios,"requires_human_review":["voice_and_music_mix","lip_sync","anatomy","caption_legibility","logo_and_cover"],"note":"A single audio stream may contain multiple mixed songs; listen to the export."},ensure_ascii=False,indent=2))
        return 0 if ok else 2
    except (ValueError,KeyError,TypeError):
        print(json.dumps({"valid":False,"reason":"invalid_probe_result"}));return 2
if __name__=="__main__":raise SystemExit(main())
