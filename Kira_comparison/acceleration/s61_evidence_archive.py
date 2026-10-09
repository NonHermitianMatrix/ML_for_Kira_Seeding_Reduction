"""Lossless high-dictionary compression of archived solver evidence.

Runtime trial sources remain frozen. Both formats reconstruct the same
SHA-256-addressed UTF-8 bytes, so record hashes and measurements stay fixed.
"""
import argparse,fcntl,gzip,hashlib,json,lzma,os,pathlib,time
HERE=pathlib.Path(__file__).resolve().parent
def unpack(evidence):
 out={}
 for name,value in evidence.items():
  if isinstance(value,str):out[name]=value;continue
  assert set(value)=={"sha256","bytes"}
  digest=value["sha256"];assert len(digest)==64 and all(c in "0123456789abcdef" for c in digest)
  plain=HERE/"evidence"/(digest+".txt.gz");compact=HERE/"evidence"/(digest+".txt.xz")
  # The compressor publishes the verified xz file before removing gzip.
  if compact.exists():
   with lzma.open(compact,"rb") as stream:raw=stream.read()
  else:
   try:
    with gzip.open(plain,"rb") as stream:raw=stream.read()
   except FileNotFoundError:
    with lzma.open(compact,"rb") as stream:raw=stream.read()
  assert len(raw)==value["bytes"] and hashlib.sha256(raw).hexdigest()==digest,name
  out[name]=raw.decode("utf-8")
 return out
def plain_hash(path,opener):
 h=hashlib.sha256();size=0
 with opener(path,"rb") as stream:
  while True:
   part=stream.read(1048576)
   if not part:break
   h.update(part);size+=len(part)
 return h.hexdigest(),size
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--min-age",type=int,default=30);ap.add_argument("--minimum-bytes",type=int,default=100000)
 a=ap.parse_args();changes=[]
 with (HERE/".evidence_compression.lock").open("w") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for path in sorted((HERE/"evidence").glob("*.txt.gz"),key=lambda p:p.stat().st_size,reverse=True):
   stat=path.stat()
   if stat.st_size<a.minimum_bytes or time.time()-stat.st_mtime<a.min_age:continue
   digest=path.name.split(".")[0];dest=path.with_suffix(".xz")
   if dest.exists():
    assert plain_hash(dest,lzma.open)[0]==digest
    assert plain_hash(path,gzip.open)[0]==digest
    changes.append(dict(sha256=digest,old_bytes=stat.st_size,new_bytes=0,duplicate_gzip_removed=True));path.unlink();continue
   temp=dest.with_name(dest.name+"."+str(os.getpid())+".tmp")
   try:
    h=hashlib.sha256();size=0
    with gzip.open(path,"rb") as source,lzma.open(temp,"wb",preset=3) as output:
     while True:
      part=source.read(1048576)
      if not part:break
      h.update(part);size+=len(part);output.write(part)
    assert h.hexdigest()==digest
    assert plain_hash(temp,lzma.open)==(digest,size)
    assert path.stat().st_mtime_ns==stat.st_mtime_ns
    if temp.stat().st_size>=stat.st_size:continue
    newsize=temp.stat().st_size
    os.replace(temp,dest);path.unlink()
    entry=dict(sha256=digest,bytes=size,old_bytes=stat.st_size,new_bytes=newsize,verified_round_trip=True)
    changes.append(entry);print(json.dumps(entry),flush=True)
   finally:
    if temp.exists():temp.unlink()
  history=HERE/"evidence_compression.json"
  old=json.loads(history.read_text()) if history.exists() else []
  old.append(dict(epoch=time.time(),changes=changes,measured_values_unchanged=True,frozen_runtime_sources_unchanged=True))
  history.write_text(json.dumps(old,indent=2)+"\n")
 print(json.dumps(dict(files=len(changes),bytes_saved=sum(r["old_bytes"]-r["new_bytes"] for r in changes))),flush=True)
if __name__=="__main__":main()
