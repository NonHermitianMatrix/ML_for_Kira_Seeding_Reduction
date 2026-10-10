"""Bound new evidence separately and reuse unchanged immutable field blobs."""
import fcntl,gzip,hashlib,json,os,pathlib,subprocess,tempfile
from s03_records import FIELDS,payload,read_record as previous_read
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/parallel_inference"
def retained():
 return int(subprocess.check_output(["du","-s","-B1",str(EXP)],text=True).split()[0])
def put(path,data):
 path=pathlib.Path(path);assert EXP in path.resolve().parents
 path.parent.mkdir(parents=True,exist_ok=True)
 with (ROOT/".tools/kira-parallel-inference/records.lock").open("a") as guard:
  fcntl.flock(guard,fcntl.LOCK_EX)
  cap=json.loads((EXP/"resource_plan.json").read_text())["new_retained_cap_bytes"]
  if retained()+len(data)+8192>cap:raise RuntimeError("New evidence storage cap")
  fd,name=tempfile.mkstemp(prefix=".atomic_",suffix=".tmp",dir=path.parent)
  try:
   with os.fdopen(fd,"wb") as raw:
    with gzip.GzipFile(filename="",mode="wb",compresslevel=6,fileobj=raw,mtime=0) as f:f.write(data)
   try:os.link(name,path)
   except FileExistsError:
    with gzip.open(path,"rb") as f:assert f.read()==data
  finally:os.unlink(name)
def field_path(digest):
 assert len(digest)==64 and all(c in "0123456789abcdef" for c in digest)
 old=HERE/"shared"/(digest+".json.gz")
 return old if old.exists() else EXP/"shared"/(digest+".json.gz")
def write_record(path,record):
 path=pathlib.Path(path);assert not path.exists()
 record=dict(record)
 for key in FIELDS:
  if key not in record:continue
  data=payload(record[key]);digest=hashlib.sha256(data).hexdigest();p=field_path(digest)
  if not p.exists():put(p,data)
  else:
   with gzip.open(p,"rb") as f:assert hashlib.sha256(f.read()).hexdigest()==digest
  record[key]={"shared_sha256":digest}
 put(path,payload(record))
def read_record(path):
 path=pathlib.Path(path)
 if EXP not in path.resolve().parents:return previous_read(path)
 with gzip.open(path,"rt") as f:r=json.load(f)
 for key in FIELDS:
  v=r.get(key)
  if isinstance(v,dict) and set(v)=={"shared_sha256"}:
   digest=v["shared_sha256"]
   with gzip.open(field_path(digest),"rb") as f:data=f.read()
   assert hashlib.sha256(data).hexdigest()==digest;r[key]=json.loads(data)
 return r
