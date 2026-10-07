"""Losslessly compress completed new families before the final independent checks."""
import concurrent.futures,hashlib,json,lzma,os,time
from pathlib import Path
from s01_generate import HERE,DATA,write,sha
LEVEL=6|lzma.PRESET_EXTREME
def one_family(path):
 manifest=path/"manifest.json";pending=path/".compression_pending.json"
 if pending.exists():
  journal=json.loads(pending.read_text());p=DATA/journal["path"];tmp=p.with_name(p.name+".part")
  if sha(p)!=journal["new"]["sha256"]:
   assert tmp.exists() and sha(tmp)==journal["new"]["sha256"];os.replace(tmp,p)
  saved=json.loads(manifest.read_text());saved["files"][journal["path"]]=journal["new"]
  write(manifest,saved);pending.unlink()
 saved=json.loads(manifest.read_text());source=sha(Path(__file__))
 if saved.get("compression",{}).get("source_sha256")==source:return saved["compression"]
 before=after=0
 for name,info in list(saved["files"].items()):
  if not name.endswith(".jsonl.xz"):continue
  p=DATA/name;assert sha(p)==info["sha256"]
  if info.get("compression_attempted")==LEVEL or info.get("compression_preset")==LEVEL:
   before+=info["original_compressed_bytes"];after+=info["bytes"];continue
  raw=lzma.decompress(p.read_bytes());digest=hashlib.sha256(raw).hexdigest()
  compressed=lzma.compress(raw,preset=LEVEL)
  assert hashlib.sha256(lzma.decompress(compressed)).hexdigest()==digest
  if len(compressed)>=info["bytes"]:
   updated=dict(info,compression_preset=3,compression_attempted=LEVEL,kept_original=True,original_compressed_bytes=info["bytes"],uncompressed_sha256=digest)
   saved["files"][name]=updated;write(manifest,saved);before+=info["bytes"];after+=info["bytes"];continue
  tmp=p.with_name(p.name+".part");tmp.write_bytes(compressed)
  updated=dict(info,sha256=sha(tmp),bytes=tmp.stat().st_size,
   original_compressed_bytes=info["bytes"],original_compressed_sha256=info["sha256"],uncompressed_sha256=digest,compression_preset=LEVEL)
  write(pending,dict(path=name,new=updated));os.replace(tmp,p)
  saved["files"][name]=updated;write(manifest,saved);pending.unlink()
  before+=info["bytes"];after+=updated["bytes"]
 result=dict(codec="XZ",preset="6 extreme; original retained when smaller",source_sha256=source,uncompressed_bytes_unchanged=True,before_bytes=before,after_bytes=after,saved_bytes=before-after)
 saved["compression"]=result;write(manifest,saved)
 return result
def main():
 assert os.environ.get("JOB_ID") and int(os.environ["NSLOTS"])>=4
 task=int(os.environ["SGE_TASK_ID"]);assert task in (1,2,3)
 loops=set(range(4*task-3,4*task+1))
 paths=sorted(p.parent for p in (DATA/"master_to_target/families").glob("vacuum_L*/manifest.json") if int(p.parent.name.split("_L")[1].split("_")[0]) in loops and 351<=int(p.parent.name.split("profile")[1])<=1350)
 assert len(paths)==4000
 started=time.time();before=after=count=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
  for r in pool.map(one_family,paths,chunksize=1):
   count+=1;before+=r["before_bytes"];after+=r["after_bytes"]
   if count%50==0:
    write(HERE/("compression_group_%d.json"%task),dict(status="compressing",families=count,total=4000,before_bytes=before,after_bytes=after,saved_bytes=before-after,elapsed_seconds=time.time()-started))
 result=dict(status="complete",families=count,total=4000,before_bytes=before,after_bytes=after,saved_bytes=before-after,elapsed_seconds=time.time()-started,source_sha256=sha(Path(__file__)))
 write(HERE/("compression_group_%d.json"%task),result);print(json.dumps(result),flush=True)
if __name__=="__main__":main()
