#!/usr/bin/env python3
"""Restore the versioned Jarvis 2 files from a trusted local checkout, preserving conflicts."""
import argparse,hashlib,json,os,shutil,tempfile
from pathlib import Path,PurePosixPath
NAMES={"jarvis-instagram-2","jarvis-diagnostico-2","jarvis-engenharia-reversa-2","jarvis-clone-voz-2","jarvis-studio-editor-2","jarvis-lab-2","jarvis-ltx-mobile-2"}
MANIFEST=Path("jarvis-instagram-2/references/suite-manifest.json")

def safe_path(root,relative):
    p=PurePosixPath(relative)
    if p.is_absolute() or not p.parts or ".." in p.parts or p.parts[0] not in NAMES:raise ValueError("invalid_manifest_path")
    path=root.joinpath(*p.parts)
    for item in [path,*path.parents]:
        if item==root:break
        if item.is_symlink():raise ValueError("symlink_not_allowed")
    if not path.resolve().is_relative_to(root):raise ValueError("path_outside_root")
    return path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    a=argparse.ArgumentParser();a.add_argument("--source",type=Path,required=True);a.add_argument("--target",type=Path,default=Path.home()/".codex/skills/remote-skills");a.add_argument("--apply",action="store_true");o=a.parse_args()
    source=o.source.resolve();target=o.target.resolve()
    if not source.is_dir():raise ValueError("source_unavailable")
    manifest=safe_path(source,MANIFEST.as_posix());data=json.loads(manifest.read_text())
    if set(data.get("skills",[]))!=NAMES:raise ValueError("unexpected_skill_set")
    plan=[];conflicts=[];seen=set()
    for e in data["files"]:
        name=e["path"]
        if name in seen:raise ValueError("duplicate_manifest_path")
        seen.add(name);src=safe_path(source,name);dst=safe_path(target,name)
        if not src.is_file() or digest(src)!=e["sha256"]:raise ValueError("source_integrity_failed:"+name)
        if dst.exists():
            if not dst.is_file() or digest(dst)!=e["sha256"]:conflicts.append(name)
        else:plan.append((src,dst))
    existing_manifest=safe_path(target,MANIFEST.as_posix())
    if existing_manifest.exists() and existing_manifest.read_bytes()!=manifest.read_bytes():conflicts.append(MANIFEST.as_posix())
    if conflicts:
        print(json.dumps({"applied":False,"conflicts":conflicts,"note":"No changes were made; inspect and preserve existing edits."}));return 2
    if o.apply:
        for src,dst in plan:
            dst.parent.mkdir(parents=True,exist_ok=True)
            # Exclusive creation prevents overwriting a concurrent edit.
            with dst.open("xb") as out:out.write(src.read_bytes())
        if not existing_manifest.exists():
            existing_manifest.parent.mkdir(parents=True,exist_ok=True)
            with existing_manifest.open("xb") as out:out.write(manifest.read_bytes())
    print(json.dumps({"applied":o.apply,"missing_files":len(plan),"verified_files":len(data["files"]),"skills":sorted(NAMES),"catalog_registration_verified":False,"note":"Use a trusted pinned source checkout. File restoration does not confirm account catalog registration."}));return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({"applied":False,"error":str(e)}));raise SystemExit(2)
