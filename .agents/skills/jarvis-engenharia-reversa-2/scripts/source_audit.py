#!/usr/bin/env python3
"""Bounded static inventory; does not import, evaluate or run source code."""
import argparse,ast,hashlib,json,os,re
from pathlib import Path
SKIP={".git","node_modules",".venv","venv","__pycache__","dist","build"}
EXT={".js",".mjs",".cjs",".jsx",".ts",".tsx",".py",".json",".md"}
SENSITIVE={".env","auth.json","credentials.json","default_voice.json","perfil_voz.json","package-lock.json","pnpm-lock.yaml"}

def inspect(path,root):
    data=path.read_bytes()
    if len(data)>1048576:return {"path":path.relative_to(root).as_posix(),"skipped":"larger_than_1_MiB"}
    try:text=data.decode("utf-8")
    except UnicodeDecodeError:return {"path":path.relative_to(root).as_posix(),"skipped":"not_utf8"}
    evidence=[]
    if path.suffix==".py":
        try:
            tree=ast.parse(text)
            for n in ast.walk(tree):
                if isinstance(n,(ast.Import,ast.ImportFrom)):
                    evidence.append({"line":n.lineno,"kind":"import","symbols":[x.name for x in n.names]})
                elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    evidence.append({"line":n.lineno,"kind":type(n).__name__,"symbol":n.name})
        except SyntaxError as e:evidence.append({"line":e.lineno,"kind":"parse_error"})
    elif path.suffix in {".js",".mjs",".cjs",".jsx",".ts",".tsx"}:
        for i,line in enumerate(text.splitlines(),1):
            for kind,pattern in [("import",r"\bimport\b.*?(?:from\s*)?[\"']([^\"']+)[\"']"),("require",r"\brequire\s*\(\s*[\"']([^\"']+)[\"']"),("export",r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]*)")]:
                for match in re.finditer(pattern,line):evidence.append({"line":i,"kind":kind,"symbol":match.group(1)})
    return {"path":path.relative_to(root).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"evidence":evidence[:500],"evidence_truncated":len(evidence)>500}

def main():
    a=argparse.ArgumentParser();a.add_argument("source",type=Path);a.add_argument("--output",required=True,type=Path);a.add_argument("--max-files",type=int,default=500);o=a.parse_args()
    root=o.source.resolve()
    if not root.is_dir() or not 1<=o.max_files<=5000:a.error("source must be a directory and max-files 1..5000")
    out=o.output.resolve()
    if out.exists():a.error("output already exists; choose a fresh file")
    records=[];omitted=0
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith(".") and not (Path(base)/d).is_symlink())
        for name in sorted(files):
            p=Path(base)/name
            if p.is_symlink() or name.startswith(".") or name in SENSITIVE or p.suffix.lower() not in EXT or p.resolve()==out:continue
            if len(records)>=o.max_files:omitted+=1;continue
            records.append(inspect(p,root))
    result={"engine":"jarvis_static_inventory_2","analysis":"heuristic_static_only","source_executed":False,"files":records,"omitted_by_file_limit":omitted,"limits":["JS/TS regex are not a semantic parser","Does not prove runtime behavior","Does not detect all secrets or vulnerabilities"]}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"output":str(out),"files":len(records),"source_executed":False}));return 0
if __name__=="__main__":raise SystemExit(main())
