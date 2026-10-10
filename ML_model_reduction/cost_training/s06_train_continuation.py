"""Train on measured remaining forward-elimination operations in exact Kira continuations."""
import json,pathlib,sys,hashlib,math
import numpy as np
from s03_train import metrics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"Kira_comparison/multiloop_native"))
from s04_records import read_record
def main():
 groups=[];hashes={};rejected=[]
 for p in sorted((ROOT/"Kira_comparison/multiloop_native/rollouts").glob("*_summary.json.gz")):
  r=read_record(p);assert r["split"] in ("training","validation")
  hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
  for g in r["groups"]:
   trials=g["trials"]
   if not all(t["valid"] and t["remaining_operations"]>0 for t in trials):
    rejected.append(dict(case=r["case"],group=g["group"]));continue
   c=np.array([t["remaining_operations"] for t in trials],float)
   groups.append(dict(family=r["case"],split=r["split"],id=r["case"]+":"+str(g["group"]),
      x=np.array([x["features"] for x in g["candidates"]],float),y=np.log(c),seconds=c))
 tr=[g for g in groups if g["split"]=="training"];va=[g for g in groups if g["split"]=="validation"]
 assert len(tr)>=10 and len(va)>=5,(len(tr),len(va))
 x=np.concatenate([g["x"] for g in tr]);mean=x.mean(0);scale=x.std(0);scale[scale<1e-8]=1
 families={g["family"] for g in tr};counts={f:sum(g["family"]==f for g in tr) for f in families}
 A=np.zeros((18,18));b=np.zeros(18)
 for g in tr:
  z=(g["x"]-mean)/scale;z-=z.mean(0);y=g["y"]-g["y"].mean()
  wt=1/(counts[g["family"]]*len(z));A+=wt*z.T@z;b+=wt*z.T@y
 candidates=[]
 for ridge in [1e-4,1e-3,1e-2,.1,1]:
  w=np.linalg.solve(A+ridge*np.eye(18),b)
  for gain in [0,.01,.05,.15]:
   candidates.append(dict(ridge=ridge,gain=gain,w=w,validation=metrics(va,mean,scale,w,gain)))
 best=min(candidates,key=lambda c:(c["validation"]["geometric_ratio"],c["validation"]["changed"],c["ridge"],c["gain"]))
 w=best["w"];gain=best["gain"]
 model=dict(kind="linear ranker of log measured remaining forward coefficient operations",features=18,
  mean=mean.tolist(),scale=scale.tolist(),weights=w.tolist(),bias=0,minimum_predicted_log_gain=gain,ridge=best["ridge"],
  target="sum of 1+2*source_nonzeros for every committed forward insertion from the checkpoint through native continuation",
  action_scope="choose one source among rows with the same leading integral; native pivot schedule retained",
  input_sha256=hashes,confidence="uncalibrated softmax of negative predicted log costs",
  previous_model="immediate_cost_v1",original_model_unchanged=True)
 (HERE/"trained_model.json").write_text(json.dumps(model,indent=2)+"\n")
 (HERE/"trained_weights.txt").write_text("\n".join([f"18 0 {gain:.17g}"]+[" ".join(format(v,".17g") for v in a) for a in [mean,scale,w]])+"\n")
 result=dict(training=metrics(tr,mean,scale,w,gain),validation=best["validation"],rejected=rejected,
  training_candidates=sum(len(g["x"]) for g in tr),validation_candidates=sum(len(g["x"]) for g in va),
  candidate_models=[dict(ridge=c["ridge"],gain=c["gain"],validation={k:v for k,v in c["validation"].items() if k!="choices"}) for c in candidates],
  metric_units="coefficient-operation count; ratios use measured continuation costs")
 (HERE/"training_results.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:{x:y for x,y in result[k].items() if x!="choices"} for k in ["training","validation"]}),flush=True)
if __name__=="__main__":main()
