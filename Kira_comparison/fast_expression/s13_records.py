"""Lossless shared arrays keep repeated timing evidence within the storage cap."""
import gzip,hashlib,json,os,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def shared(value):
 raw=json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
 if len(raw)<2048:return value
 digest=hashlib.sha256(raw).hexdigest();p=HERE/"shared"/(digest+".json.gz");p.parent.mkdir(exist_ok=True)
 if not p.exists():
  tmp=p.with_name(p.name+"."+str(os.getpid())+".tmp")
  with tmp.open("wb") as f:
   with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=9) as z:z.write(raw)
  os.replace(tmp,p)
 return {"_shared":1,"sha256":digest,"bytes":len(raw)}
def compact(r):
 for k in ["checks"]:
  if k in r:r[k]=shared(r[k])
 for k in ["probabilities","selected_seeds"]:
  if k in r.get("model",{}):r["model"][k]=shared(r["model"][k])
 for a in r.get("attempts",[]):
  for k in ["manifest","source_ids"]:
   if k in a:a[k]=shared(a[k])
 return r
def restore(v):
 if isinstance(v,dict):
  if set(v)=={"_shared","sha256","bytes"} and v["_shared"]==1:
   h=v["sha256"];assert len(h)==64 and all(c in "0123456789abcdef" for c in h)
   raw=gzip.decompress((HERE/"shared"/(h+".json.gz")).read_bytes())
   assert len(raw)==v["bytes"] and hashlib.sha256(raw).hexdigest()==h
   return json.loads(raw)
  return {k:restore(x) for k,x in v.items()}
 if isinstance(v,list):return [restore(x) for x in v]
 return v
def read_record(p):
 with gzip.open(p,"rt") as f:return restore(json.load(f))
