"""Fit a small cost ranker to exact counterfactual Kira updates."""
import argparse,gzip,hashlib,json,math,pathlib,sys
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"Kira_comparison/multiloop_native"))
from s04_records import read_record
def load(paths):
 groups=[];hashes={}
 for p in paths:
  r=read_record(p)
  if not r.get("success") or not r.get("reference_checked"):continue
  hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
  for i,g in enumerate(r.get("choices",[])):
   if not g.get("measured"):continue
   c=g["candidates"]
   if len(c)<2 or any(x["seconds"]<=0 for x in c):continue
   groups.append(dict(family=r["case"],id=p.name+":"+str(i),
    x=np.array([x["features"] for x in c],float),
    y=np.log(np.array([x["seconds"] for x in c],float)),
    seconds=np.array([x["seconds"] for x in c],float)))
 return groups,hashes
def metrics(groups,mean,scale,w,gain):
 ratios=[];chosen=[];families={}
 for g in groups:
  scores=(g["x"]-mean)/scale@w
  q=int(scores.argmin())
  if scores[q]>scores[0]-gain:q=0
  ratio=float(g["seconds"][q]/g["seconds"][0])
  optimum=float(g["seconds"].min())
  confidence=float(np.exp(-(scores-scores.min()))[q]/np.exp(-(scores-scores.min())).sum())
  families.setdefault(g["family"],[]).append(math.log(ratio))
  ratios.append(ratio);chosen.append(dict(group=g["id"],selected=q,confidence=confidence,relative_to_native=ratio,
    local_regret=float(g["seconds"][q]/optimum),minimum_measured_candidate=int(g["seconds"].argmin())))
 return dict(groups=len(groups),changed=sum(x["selected"]!=0 for x in chosen),
  geometric_ratio=math.exp(sum(sum(v)/len(v) for v in families.values())/len(families)),
  mean_local_regret=float(np.mean([x["local_regret"] for x in chosen])),choices=chosen)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data",type=pathlib.Path,required=True);a=ap.parse_args()
 paths=sorted(a.data.resolve().glob("*.json.gz"));train=[];validation=[]
 for p in paths:
  r=read_record(p)
  if r["split"]=="training":train.append(p)
  elif r["split"]=="validation":validation.append(p)
  else:raise ValueError("Reserved data cannot enter fitting")
 tr,th=load(train);va,vh=load(validation)
 assert len(tr)>=20 and len(va)>=10,(len(tr),len(va))
 x=np.concatenate([g["x"] for g in tr]);mean=x.mean(0);scale=x.std(0);scale[scale<1e-8]=1
 families={g["family"] for g in tr};counts={f:sum(g["family"]==f for g in tr) for f in families}
 A=np.zeros((18,18));b=np.zeros(18)
 for g in tr:
  z=(g["x"]-mean)/scale;z-=z.mean(0);y=g["y"]-g["y"].mean()
  weight=1/(counts[g["family"]]*len(z))
  A+=weight*z.T@z;b+=weight*z.T@y
 candidates=[]
 for ridge in [1e-4,1e-3,1e-2,.1,1.0]:
  w=np.linalg.solve(A+ridge*np.eye(18),b)
  for gain in [0,.05,.15,.3]:
   m=metrics(va,mean,scale,w,gain)
   candidates.append(dict(ridge=ridge,gain=gain,weights=w,validation=m))
 best=min(candidates,key=lambda c:(c["validation"]["geometric_ratio"],c["validation"]["changed"],c["ridge"],c["gain"]))
 w=best["weights"];gain=best["gain"]
 model=dict(kind="linear ranking of log measured symbolic-update time",features=18,mean=mean.tolist(),scale=scale.tolist(),
  weights=w.tolist(),bias=0.0,minimum_predicted_log_gain=gain,ridge=best["ridge"],
  target="mean exact insertion time over two rotated repeats; cloning excluded",
  input_sha256=dict(training=th,validation=vh),original_model_unchanged=True,confidence="uncalibrated softmax of negative predicted log costs")
 (HERE/"trained_model.json").write_text(json.dumps(model,indent=2)+"\n")
 lines=[f"18 0 {gain:.17g}"]+[" ".join(format(x,".17g") for x in v) for v in [mean,scale,w]]
 (HERE/"trained_weights.txt").write_text("\n".join(lines)+"\n")
 evaluation=dict(training=metrics(tr,mean,scale,w,gain),validation=best["validation"],
  candidate_models=[dict(ridge=c["ridge"],gain=c["gain"],validation={k:v for k,v in c["validation"].items() if k!="choices"}) for c in candidates],
  training_families=sorted(families),validation_families=sorted({g["family"] for g in va}),
  training_candidates=sum(len(g["x"]) for g in tr),validation_candidates=sum(len(g["x"]) for g in va))
 (HERE/"training_results.json").write_text(json.dumps(evaluation,indent=2)+"\n")
 print(json.dumps({k:{x:y for x,y in evaluation[k].items() if x!="choices"} for k in ["training","validation"]}),flush=True)
if __name__=="__main__":main()
