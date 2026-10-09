"""Deduplicate archived predictions/checks without changing any measured value."""
import argparse,fcntl,gzip,hashlib,json,os,pathlib,time
from s39_records import canonical,read_record
HERE=pathlib.Path(__file__).resolve().parent
def packed(value):
 raw=canonical(value)
 if len(raw)<4096:return value
 digest=hashlib.sha256(raw).hexdigest();dest=HERE/"structured_evidence"/(digest+".json.gz")
 dest.parent.mkdir(exist_ok=True)
 if not dest.exists():
  tmp=dest.with_name(dest.name+"."+str(os.getpid())+".tmp")
  try:
   with tmp.open("wb") as f:
    with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as stream:stream.write(raw)
   os.replace(tmp,dest)
  finally:
   if tmp.exists():tmp.unlink()
 return {"$json":digest,"bytes":len(raw)}
def _compact_completed(min_age=30,stage="results"):
 changed=0;old_bytes=0;new_bytes=0
 for path in sorted((HERE/stage).glob("*.json.gz")):
  if time.time()-path.stat().st_mtime<min_age:continue
  with gzip.open(path,"rt") as stream:r=json.load(stream)
  if "_storage" in r or not r.get("measured",True):continue
  digest=hashlib.sha256(canonical(r)).hexdigest()
  old_size=path.stat().st_size
  if "checks" in r:r["checks"]=packed(r["checks"])
  if "probabilities" in r.get("model",{}):r["model"]["probabilities"]=packed(r["model"]["probabilities"])
  r["_storage"]=dict(format="shared-json-v1",logical_sha256=digest,
     original_gzip_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
  tmp=path.with_name(path.name+"."+str(os.getpid())+".tmp")
  try:
   with tmp.open("wb") as f:
    with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as stream:stream.write(canonical(r))
   assert hashlib.sha256(canonical(read_record(tmp))).hexdigest()==digest
   os.replace(tmp,path)
  finally:
   if tmp.exists():tmp.unlink()
  changed+=1;old_bytes+=old_size;new_bytes+=path.stat().st_size
 out=dict(stage=stage,records_compacted=changed,original_record_bytes=old_bytes,new_record_bytes=new_bytes,
          shared_payload_bytes=sum(x.stat().st_size for x in (HERE/"structured_evidence").glob("*.gz")),
          measured_values_unchanged=True,frozen_runtime_sources_unchanged=True)
 if changed:
  p=HERE/"storage_compaction.json";previous=json.loads(p.read_text()) if p.exists() else []
  previous.append(out);p.write_text(json.dumps(previous,indent=2)+"\n")
 return out
def compact_completed(min_age=30,stage="results"):
 assert stage.isidentifier(),stage
 with (HERE/".structured_compaction.lock").open("w") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  return _compact_completed(min_age,stage)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--min-age",type=int,default=30);ap.add_argument("--stage",default="results");a=ap.parse_args()
 print(json.dumps(compact_completed(a.min_age,a.stage)),flush=True)
