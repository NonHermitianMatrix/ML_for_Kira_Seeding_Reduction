"""Measure CPU thread scaling on existing training examples without updating weights."""
import hashlib,json,os,resource,statistics,sys,time
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MODEL=ROOT/"ML_model_seed_selection"
sys.path.insert(0,str(MODEL))
from s01_data import config,read
from s02_model import SeedSelector
from s13_batch import collate,forward
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert os.environ.get("JOB_ID") and int(os.environ["NSLOTS"])>=4
 cfg=config();torch.set_num_interop_threads(1);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 warm=MODEL/"runs/before_expansion_250/runs/all_loops_latest.pt";digest=sha(warm)
 saved=torch.load(warm,map_location="cpu",weights_only=False)
 model=SeedSelector(cfg);model.load_state_dict(saved["model"]);original={k:v.clone() for k,v in model.state_dict().items()}
 metas=read(MODEL/"data/manifest.json")["families"]
 allowed={m["family"] for m in read(MODEL/"split_manifest.json")["families"] if m["split"]=="train"}
 ordered=sorted(metas,key=lambda m:m["candidates"])
 chosen={m["family"]:m for m in [ordered[i] for i in [0,len(ordered)//2,len(ordered)*9//10,-1]]}
 for r in (2,3,4):
  meta=next(m for m in metas if m["family"].startswith("vacuum_L12_profile") and m["candidates"]=={2:20,3:55,4:125}[r])
  chosen[meta["family"]]=meta
 results=[]
 for item in chosen.values():
  assert item["family"] in allowed
  path=MODEL/item["file"];assert sha(path)==item["sha256"]
  with np.load(path,allow_pickle=False) as z:a={k:z[k] for k in z.files}
  lengths=np.diff(a["offsets"]);indices=np.argsort(lengths).tolist()
  ids=list(dict.fromkeys(indices[:16]+indices[-16:]));x,mask,shared,y=collate(a,ids)
  records=[];reference=None;reference_grad=None
  for threads in [1,2,4,4,2,1]:
   torch.set_num_threads(threads)
   model.zero_grad(set_to_none=True);logits=forward(model,x,mask,shared)
   loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,y);loss.backward()
   gradient=torch.cat([p.grad.flatten() for p in model.parameters()])
   if reference is None:reference=logits.detach().clone();reference_grad=gradient.clone()
   assert torch.allclose(logits,reference,atol=3e-5,rtol=3e-5)
   assert torch.allclose(gradient,reference_grad,atol=3e-5,rtol=3e-4)
   start=time.perf_counter()
   for _ in range(12):
    model.zero_grad(set_to_none=True);loss=torch.nn.functional.binary_cross_entropy_with_logits(forward(model,x,mask,shared),y);loss.backward()
   records.append(dict(threads=threads,seconds_per_batch=(time.perf_counter()-start)/12))
  results.append(dict(family=item["family"],candidates=item["candidates"],batch=len(ids),max_terms=int(lengths[ids].max()),
   seconds_per_batch={str(t):statistics.median(r["seconds_per_batch"] for r in records if r["threads"]==t) for t in (1,2,4)}))
 assert sha(warm)==digest and all(torch.equal(model.state_dict()[k],v) for k,v in original.items())
 out=dict(status="passed",optimizer_updates=0,held_out_examples_read=False,warm_checkpoint_sha256=digest,
  numerical_score_and_gradient_agreement=True,measurements=results,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
  sources={p:sha(MODEL/p) for p in ["s02_model.py","s13_batch.py"]})
 (HERE/"cpu_thread_pilot.json").write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps(out),flush=True)
if __name__=="__main__":main()
