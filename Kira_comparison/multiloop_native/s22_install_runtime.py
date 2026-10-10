"""Install bounded per-workflow seed caches after the earlier validation jobs end."""
import pathlib
HERE=pathlib.Path(__file__).resolve().parent
def main():
 p=HERE/"s07_seed.py";t=p.read_text();assert "_NATIVE_CACHE" not in t
 t=t.replace('from s01_fast_seed import FastSeed','from s21_seed_loader import NativeSeed as FastSeed\n_NATIVE_CACHE=None\n_SHARED_CACHE={}')
 t=t.replace('def candidates(definition,r,s,d):','@functools.lru_cache(maxsize=2)\ndef _candidates(n,physical,r,s,d):')
 t=t.replace(' n=len(definition["propagators"]);physical=definition["physical_propagators"];out=[]',' out=[]')
 anchor='def choose(definition,masters,targets,spec,closure=False,use_model=True,threshold=.01):'
 t=t.replace(anchor,'def candidates(definition,r,s,d):\n return _candidates(len(definition["propagators"]),definition["physical_propagators"],r,s,d)\n'+anchor)
 t=t.replace(' begin=time.perf_counter();seeds=', ' global _NATIVE_CACHE\n begin=time.perf_counter();seeds=')
 t=t.replace(' t=time.perf_counter();load=0.', ' t=time.perf_counter();load=0.;model_hit=False;shared_hit=False')
 old='''  model=FastSeed();load=time.perf_counter()-t;t=time.perf_counter()
  shared=model.shared(definition,masters,seeds)'''
 new='''  model_hit=_NATIVE_CACHE is not None
  if _NATIVE_CACHE is None:_NATIVE_CACHE=FastSeed()
  model=_NATIVE_CACHE;load=time.perf_counter()-t;t=time.perf_counter()
  key=(json.dumps(definition,sort_keys=True),tuple(map(tuple,masters)),spec["r"],spec["s"],spec["d"])
  shared_hit=key in _SHARED_CACHE
  if shared_hit:shared=_SHARED_CACHE[key]
  else:
   shared=model.shared(definition,masters,seeds)
   if len(_SHARED_CACHE)>=2:_SHARED_CACHE.pop(next(iter(_SHARED_CACHE)))
   _SHARED_CACHE[key]=shared'''
 assert old in t;t=t.replace(old,new)
 t=t.replace('timing=dict(enumeration_seconds=', 'timing=dict(model_cache_hit=model_hit,shared_cache_hit=shared_hit,enumeration_seconds=')
 p.write_text(t);compile(t,str(p),"exec")
 p=HERE/"s02_run.py";t=p.read_text()
 t=t.replace('else ".tools/kira-cost-training/kira"','else ".tools/kira-cost-tree/kira"')
 assert '".tools/kira-cost-tree/kira"' in t
 p.write_text(t);compile(t,str(p),"exec")
 (HERE/"s04_records.py").write_text("\"\"\"Losslessly share scientific evidence with atomic writes and a storage bound.\"\"\"\nimport fcntl,gzip,hashlib,json,os,pathlib,subprocess,tempfile\nHERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]\nFIELDS=(\"input\",\"targets\",\"raw_export\",\"coefficients\",\"masters\",\"choices\",\"predictions\",\"seed_audit\")\ndef payload(value):return json.dumps(value,separators=(\",\",\":\"),sort_keys=True).encode()\ndef retained():\n names=[str(HERE),str(ROOT/\"ML_model_reduction/cost_training\")]\n return sum(int(x.split()[0]) for x in subprocess.check_output([\"du\",\"-s\",\"-B1\",*names],text=True).splitlines())\ndef put(path,data):\n path.parent.mkdir(exist_ok=True,parents=True)\n lock=ROOT/\".tools/kira-cost-training/records.lock\"\n with lock.open(\"a\") as guard:\n  fcntl.flock(guard,fcntl.LOCK_EX)\n  cap=json.loads((HERE/\"resource_plan.json\").read_text())[\"new_retained_cap_bytes\"]\n  if retained()+len(data)+8192>cap:raise RuntimeError(\"Retained experiment storage cap\")\n  fd,name=tempfile.mkstemp(prefix=f\".atomic_{os.getpid()}_\",suffix=\".tmp\",dir=path.parent)\n  try:\n   with os.fdopen(fd,\"wb\") as raw:\n    with gzip.GzipFile(filename=\"\",mode=\"wb\",compresslevel=6,fileobj=raw,mtime=0) as f:f.write(data)\n   try:os.link(name,path)\n   except FileExistsError:\n    with gzip.open(path,\"rb\") as f:assert f.read()==data,\"Conflicting result publication\"\n  finally:os.unlink(name)\ndef write_record(path,record):\n path=pathlib.Path(path);assert not path.exists(),path\n record=dict(record)\n for key in FIELDS:\n  if key not in record:continue\n  data=payload(record[key]);digest=hashlib.sha256(data).hexdigest();p=HERE/\"shared\"/(digest+\".json.gz\")\n  if not p.exists():put(p,data)\n  else:\n   with gzip.open(p,\"rb\") as f:assert hashlib.sha256(f.read()).hexdigest()==digest\n  record[key]={\"shared_sha256\":digest}\n put(path,payload(record))\ndef read_record(path):\n with gzip.open(path,\"rt\") as f:r=json.load(f)\n for key in FIELDS:\n  v=r.get(key)\n  if isinstance(v,dict) and set(v)=={\"shared_sha256\"}:\n   digest=v[\"shared_sha256\"];assert len(digest)==64 and all(c in \"0123456789abcdef\" for c in digest)\n   with gzip.open(HERE/\"shared\"/(digest+\".json.gz\"),\"rb\") as f:data=f.read()\n   assert hashlib.sha256(data).hexdigest()==digest\n   r[key]=json.loads(data)\n return r\n")
 print("Installed read-once loader and two-entry per-process caches",flush=True)
if __name__=="__main__":main()
