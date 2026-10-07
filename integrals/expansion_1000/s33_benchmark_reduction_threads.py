"""Measure reduction-training CPU threads using saved training states only."""
import json,os,random,resource,statistics,sys,time
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MODEL=ROOT/"ML_model_reduction"
sys.path.insert(0,str(MODEL))
from s00_common import read,sha,folder_size,config
from s03_model import ReductionSelector
from s10_train_all_loops import collate
def main():
 assert os.environ.get("JOB_ID") and int(os.environ["NSLOTS"])>=4
 cfg=config();torch.set_num_interop_threads(1);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 data=read(MODEL/"data/manifest.json");metas=data["families"]
 allowed={m["family"] for m in read(ROOT/"ML_model_seed_selection/split_manifest.json")["families"] if m["split"]=="train"}
 old=[m for m in metas if m["family"].startswith("box")][:8]
 new=[m for m in metas if m["family"].startswith("vacuum_L12_profile")][:8]
 warm=MODEL/"runs/before_expansion_250/runs/all_loops_latest.pt";digest=sha(warm)
 saved=torch.load(warm,map_location="cpu",weights_only=False);model=ReductionSelector(data["feature_dim"],cfg);model.load_state_dict(saved["model"])
 original={k:v.clone() for k,v in model.state_dict().items()};measurements=[]
 for name,selected in [("box",old),("vacuum",new),("mixed",old[:4]+new[:4])]:
  shards=[]
  for m in selected:
   assert m["family"] in allowed and sha(MODEL/m["file"])==m["sha256"]
   with np.load(MODEL/m["file"],allow_pickle=False) as z:shards.append({k:z[k] for k in ("features","offsets","labels")})
  ids=[(f,i) for f,z in enumerate(shards) for i in range(len(z["labels"])) if z["offsets"][i+1]-z["offsets"][i]>1]
  random.Random(20261006).shuffle(ids);ids=ids[:256]
  maximum=max(int(shards[f]["offsets"][i+1]-shards[f]["offsets"][i]) for f,i in ids)
  assert len(ids)*maximum<=cfg["max_padded_actions"]
  x,mask,y=collate(shards,ids,maximum);ref=refgrad=None;timings=[]
  for threads in [1,2,4,4,2,1]:
   torch.set_num_threads(threads);model.zero_grad(set_to_none=True)
   scores=model(x,mask);loss=torch.nn.functional.cross_entropy(scores,y);loss.backward()
   grad=torch.cat([(p.grad if p.grad is not None else torch.zeros_like(p)).flatten() for p in model.parameters()])
   if ref is None:ref=scores.detach().clone();refgrad=grad.clone()
   assert torch.allclose(scores,ref,atol=3e-5,rtol=3e-5)
   assert torch.allclose(grad,refgrad,atol=3e-5,rtol=3e-4)
   start=time.perf_counter()
   for _ in range(20):
    model.zero_grad(set_to_none=True);loss=torch.nn.functional.cross_entropy(model(x,mask),y);loss.backward()
   timings.append(dict(threads=threads,seconds_per_batch=(time.perf_counter()-start)/20))
  measurements.append(dict(group=name,families=[m["family"] for m in selected],batch=len(ids),max_actions=maximum,
   seconds_per_batch={str(t):statistics.median(r["seconds_per_batch"] for r in timings if r["threads"]==t) for t in (1,2,4)}))
 assert sha(warm)==digest and all(torch.equal(model.state_dict()[k],v) for k,v in original.items())
 start=time.perf_counter();size=folder_size(MODEL);scan=time.perf_counter()-start
 result=dict(status="passed",optimizer_updates=0,held_out_examples_read=False,warm_checkpoint_sha256=digest,
  numerical_score_and_gradient_agreement=True,measurements=measurements,
  timing_scope="Forward and backward network calculations; batch preparation and optimizer updates excluded.",
  model_folder_bytes=size,model_folder_scan_seconds=scan,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
  sources={p:sha(MODEL/p) for p in ["s03_model.py","s10_train_all_loops.py"]},benchmark_source_sha256=sha(Path(__file__)))
 (HERE/"reduction_cpu_thread_pilot.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
