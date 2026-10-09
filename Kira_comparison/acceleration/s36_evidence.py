"""Content-addressed solver text: preserve evidence without repeated copies."""
import gzip,hashlib,os,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def pack(evidence):
 out={}
 for name,text in evidence.items():
  raw=text.encode("utf-8")
  if len(raw)<4096:out[name]=text;continue
  digest=hashlib.sha256(raw).hexdigest()
  dest=HERE/"evidence"/(digest+".txt.gz");dest.parent.mkdir(exist_ok=True)
  if not dest.exists():
   tmp=dest.with_name(dest.name+"."+str(os.getpid())+".tmp")
   try:
    with tmp.open("wb") as f:
     with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=6) as g:g.write(raw)
    os.replace(tmp,dest)
   finally:
    if tmp.exists():tmp.unlink()
  out[name]={"sha256":digest,"bytes":len(raw)}
 return out
def unpack(evidence):
 out={}
 for name,value in evidence.items():
  if isinstance(value,str):out[name]=value;continue
  assert set(value)=={"sha256","bytes"}
  digest=value["sha256"];assert len(digest)==64 and all(x in "0123456789abcdef" for x in digest)
  with gzip.open(HERE/"evidence"/(digest+".txt.gz"),"rb") as f:raw=f.read()
  assert len(raw)==value["bytes"] and hashlib.sha256(raw).hexdigest()==digest,name
  out[name]=raw.decode("utf-8")
 return out
