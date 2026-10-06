"""Prepare bounded immutable features using training families only."""
import collections,hashlib,json,os,time
import numpy as np
from s01_data import HERE,DATA,read,config,encode,encode_shared,family_records,public_family,storage_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+".part")
 t.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(t,p)
def main():
 cfg=config();manifest=read(HERE/"split_manifest.json");start=time.time()
 train=[m for m in manifest["families"] if m["split"]=="train"]
 held=[m for m in manifest["families"] if m["split"]=="test"]
 assert not {m["group"] for m in train}&{m["group"] for m in held}
 signature=dict(encoder=sha(HERE/"s01_data.py"),preparer=sha(HERE/"s12_prepare_features.py"),config=sha(HERE/"config.json"))
 result=[]
 for i,meta in enumerate(train):
  out=HERE/"data/training"/(meta["family"]+".npz");audit=out.with_suffix(".json")
  hashes={meta[k]:sha(DATA/meta[k]) for k in ("definition","masters","inputs","references","seeds")}
  if out.exists() and audit.exists():
   saved=read(audit)
   if saved["sources"]==hashes and saved["signature"]==signature and saved["sha256"]==sha(out):
    result.append(saved);continue
  xs=[];ys=[];offsets=[0];ids=[];shared=None
  for target,family,seeds,y in family_records(meta,cfg):
   if shared is None:shared=encode_shared(family,seeds,cfg)
   x=encode(target,family,seeds,cfg,shared)
   xs.append(x["terms"].numpy());ys.append(y.numpy().astype(np.uint8));offsets.append(offsets[-1]+len(target["terms"]));ids.append(target["id"])
  assert len(ids)==meta["counts"]["targets"] and len(set(ids))==len(ids)
  arrays=dict(terms=np.concatenate(xs),offsets=np.asarray(offsets,np.int64),labels=np.stack(ys),target_ids=np.asarray(ids),
      family=shared["family"].numpy(),masters=shared["masters"].numpy(),seeds=shared["seeds"].numpy())
  assert sum(x.nbytes for x in arrays.values())<268435456
  out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name(out.name+".part")
  with tmp.open("wb") as f:np.savez_compressed(f,**arrays)
  assert tmp.stat().st_size<67108864;os.replace(tmp,out)
  saved=dict(family=meta["family"],loops=meta["loops"],targets=len(ids),candidates=len(seeds),file=str(out.relative_to(HERE)),
    sha256=sha(out),bytes=out.stat().st_size,sources=hashes,signature=signature)
  write(audit,saved);result.append(saved)
  if i%50==0:
   write(HERE/"runs/feature_status.json",dict(completed=i+1,total=len(train),elapsed_seconds=time.time()-start))
   print("Seed features",i+1,len(train),flush=True)
 assert sum(m["targets"] for m in result)==sum(m["counts"]["targets"] for m in train)
 write(HERE/"data/manifest.json",dict(status="complete",split_sha256=sha(HERE/"split_manifest.json"),families=result,
   training_families=len(train),training_targets=sum(m["targets"] for m in result),held_out_data_read=False,
   held_out_families=len(held),held_out_targets=sum(m["counts"]["targets"] for m in held),
   bytes=sum(m["bytes"] for m in result),elapsed_seconds=time.time()-start))
 print("Seed features complete",len(result),flush=True)
if __name__=="__main__":main()
