"""Losslessly share scientific evidence with atomic writes and a storage bound."""
import fcntl,gzip,hashlib,json,os,pathlib,subprocess,tempfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FIELDS=("input","targets","raw_export","coefficients","masters","choices","predictions","seed_audit")
def payload(value):return json.dumps(value,separators=(",",":"),sort_keys=True).encode()
def retained():
 names=[str(HERE),str(ROOT/"ML_model_reduction/runtime_training"),str(ROOT/"ML_model_seed_selection/runtime_inference")]
 return sum(int(x.split()[0]) for x in subprocess.check_output(["du","-s","-B1",*names],text=True).splitlines())
def put(path,data):
 path.parent.mkdir(exist_ok=True,parents=True)
 lock=ROOT/".tools/kira-integrated-runtime/records.lock"
 with lock.open("a") as guard:
  fcntl.flock(guard,fcntl.LOCK_EX)
  cap=json.loads((HERE/"resource_plan.json").read_text())["new_retained_cap_bytes"]
  if retained()+len(data)+8192>cap:raise RuntimeError("Retained experiment storage cap")
  fd,name=tempfile.mkstemp(prefix=f".atomic_{os.getpid()}_",suffix=".tmp",dir=path.parent)
  try:
   with os.fdopen(fd,"wb") as raw:
    with gzip.GzipFile(filename="",mode="wb",compresslevel=6,fileobj=raw,mtime=0) as f:f.write(data)
   try:os.link(name,path)
   except FileExistsError:
    with gzip.open(path,"rb") as f:assert f.read()==data,"Conflicting result publication"
  finally:os.unlink(name)
def write_record(path,record):
 path=pathlib.Path(path);assert not path.exists(),path
 record=dict(record)
 for key in FIELDS:
  if key not in record:continue
  data=payload(record[key]);digest=hashlib.sha256(data).hexdigest();p=HERE/"shared"/(digest+".json.gz")
  if not p.exists():put(p,data)
  else:
   with gzip.open(p,"rb") as f:assert hashlib.sha256(f.read()).hexdigest()==digest
  record[key]={"shared_sha256":digest}
 put(path,payload(record))
def read_record(path):
 path=pathlib.Path(path)
 previous=ROOT/"Kira_comparison/multiloop_native"
 if previous in path.resolve().parents:
  import importlib.util
  spec=importlib.util.spec_from_file_location("previous_native_records",previous/"s04_records.py")
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  return module.read_record(path)
 with gzip.open(path,"rt") as f:r=json.load(f)
 for key in FIELDS:
  v=r.get(key)
  if isinstance(v,dict) and set(v)=={"shared_sha256"}:
   digest=v["shared_sha256"];assert len(digest)==64 and all(c in "0123456789abcdef" for c in digest)
   with gzip.open(HERE/"shared"/(digest+".json.gz"),"rb") as f:data=f.read()
   assert hashlib.sha256(data).hexdigest()==digest
   r[key]=json.loads(data)
 return r
