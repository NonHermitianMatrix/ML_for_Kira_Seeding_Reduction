"""Paths, bounded storage and reproducible file operations."""
import gzip, hashlib, json, os, pathlib, shutil, time
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
INTEGRALS=ROOT/"integrals"
SPLIT=ROOT/"ML_model_seed_selection/split_manifest.json"
def read(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
def config():
    return read(HERE/"config.json")
def rows(p):
    with gzip.open(str(p),"rt",encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)
def sha(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def write_json(p,value):
    p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+".part")
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    os.replace(str(tmp),str(p))
def atomic_torch(p,value):
    import torch
    p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+".part");torch.save(value,tmp)
    if tmp.stat().st_size>8388608: raise RuntimeError("Checkpoint exceeds 8 MiB limit")
    os.replace(str(tmp),str(p))
def folder_size(path):
    total=0
    for directory,dirs,files in os.walk(str(path),followlinks=False):
        dirs[:]=[d for d in dirs if not pathlib.Path(directory,d).is_symlink()]
        for name in files:
            p=pathlib.Path(directory,name)
            if not p.is_symlink(): total+=p.stat().st_size
    return total
def storage_guard(full=False):
    free=shutil.disk_usage(str(ROOT)).free
    if free<2000000000: raise RuntimeError("Less than 2 GB free on project filesystem")
    if full:
        total=folder_size(ROOT)
        # Includes a 150 MB allowance for the report-only local checkout.
        if total+150000000>8500000000: raise RuntimeError("Project approaches 10 GB combined ceiling")
        return total
    if folder_size(HERE)>1500000000: raise RuntimeError("Reduction-model folder exceeds 1.5 GB budget")
    return None
def status(stage,**kwargs):
    write_json(HERE/"runs/status.json",dict(stage=stage,utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),**kwargs))
