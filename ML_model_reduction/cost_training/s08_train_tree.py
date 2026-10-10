"""Fit a small nonlinear cost model from the same exact continuations."""
import hashlib,json,math,pathlib,sys
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"Kira_comparison/multiloop_native"))
from s04_records import read_record
def data():
 out=[];hashes={}
 for p in sorted((ROOT/"Kira_comparison/multiloop_native/rollouts").glob("*_summary.json.gz")):
  r=read_record(p);hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
  for g in r["groups"]:
   if not all(t["valid"] and t["remaining_operations"]>0 for t in g["trials"]):continue
   f=np.array([c["features"] for c in g["candidates"]]);cost=np.array([t["remaining_operations"] for t in g["trials"]],float)
   out.append(dict(case=r["case"],split=r["split"],id=r["case"]+":"+str(g["group"]),x=f-f[0],cost=cost))
 return out,hashes
def fit(x,y,wt,depth,minleaf):
 nodes=[]
 def build(ids,level):
  w=wt[ids];v=float(w@y[ids]/w.sum());index=len(nodes);nodes.append(dict(feature=-1,cut=0.,left=-1,right=-1,value=v))
  if level==depth or len(ids)<2*minleaf:return index
  base=float(np.sum(w*(y[ids]-v)**2));best=None
  for j in range(x.shape[1]):
   order=ids[np.argsort(x[ids,j],kind="stable")];z=x[order,j];w=wt[order];yy=y[order]
   sw=np.cumsum(w);sy=np.cumsum(w*yy);s2=np.cumsum(w*yy*yy)
   for k in range(minleaf,len(ids)-minleaf+1):
    if z[k-1]==z[k]:continue
    loss=s2[k-1]-sy[k-1]**2/sw[k-1]+s2[-1]-s2[k-1]-(sy[-1]-sy[k-1])**2/(sw[-1]-sw[k-1])
    if best is None or loss<best[0]:best=(float(loss),j,float((z[k-1]+z[k])/2),order[:k],order[k:])
  if best is None or best[0]>=base-1e-16:return index
  _,j,cut,left,right=best;l=build(left,level+1);r=build(right,level+1)
  nodes[index]=dict(feature=j,cut=cut,left=l,right=r,value=v);return index
 build(np.arange(len(y)),0);return nodes
def predict(nodes,x):
 i=0
 while nodes[i]["feature"]>=0:
  n=nodes[i];i=n["left"] if x[n["feature"]]<=n["cut"] else n["right"]
 return nodes[i]["value"]
def evaluate(groups,nodes,gain):
 choices=[];families={}
 for g in groups:
  s=np.array([0.]+[predict(nodes,x) for x in g["x"][1:]]);q=int(s.argmin())
  if s[q]>-gain:q=0
  ratio=float(g["cost"][q]/g["cost"][0]);families.setdefault(g["case"],[]).append(math.log(ratio))
  choices.append(dict(group=g["id"],selected=q,ratio=ratio,regret=float(g["cost"][q]/g["cost"].min())))
 return dict(groups=len(groups),changed=sum(c["selected"]!=0 for c in choices),
  geometric_ratio=math.exp(sum(sum(v)/len(v) for v in families.values())/len(families)),choices=choices)
def main():
 groups,hashes=data();tr=[g for g in groups if g["split"]=="training"];va=[g for g in groups if g["split"]=="validation"]
 assert len(tr)==24 and len(va)>=5
 count={f:sum(g["case"]==f for g in tr) for f in {g["case"] for g in tr}}
 candidates=[]
 for target in ["log_relative_cost","normalized_cost_change"]:
  x=[];y=[];wt=[]
  for g in tr:
   c=g["cost"];label=np.log(c/c[0]) if target=="log_relative_cost" else (c-c[0])/max(1,float(c.max()-c.min()))
   for q in range(1,len(c)):
    x.append(g["x"][q]);y.append(label[q]);wt.append(1/(count[g["case"]]*(len(c)-1)))
  x=np.array(x);y=np.array(y);wt=np.array(wt)
  for depth in [2,3,4,5]:
   for minleaf in [1,2,3]:
    nodes=fit(x,y,wt,depth,minleaf)
    for gain in [0,1e-5,1e-4,.01]:
     candidates.append(dict(target=target,depth=depth,minleaf=minleaf,gain=gain,nodes=nodes,validation=evaluate(va,nodes,gain)))
 best=min(candidates,key=lambda c:(c["validation"]["geometric_ratio"],len(c["nodes"]),c["validation"]["changed"],c["depth"],c["gain"]))
 model=dict(kind="regression tree of measured remaining forward cost",features=18,
  feature_transform="candidate features minus native-source features; native score fixed to zero",
  target=best["target"],nodes=best["nodes"],minimum_predicted_gain=best["gain"],depth=best["depth"],minimum_leaf_examples=best["minleaf"],
  input_sha256=hashes,confidence="uncalibrated softmax of negative scores")
 (HERE/"tree_candidate_model.json").write_text(json.dumps(model,indent=2)+"\n")
 lines=[f'18 0 {best["gain"]:.17g}'," ".join(["0"]*18)," ".join(["1"]*18)," ".join(["0"]*18),str(len(best["nodes"]))]
 for n in best["nodes"]:lines.append(f'{n["feature"]} {n["cut"]:.17g} {n["left"]} {n["right"]} {n["value"]:.17g}')
 (HERE/"tree_candidate_weights.txt").write_text("\n".join(lines)+"\n")
 result=dict(training=evaluate(tr,best["nodes"],best["gain"]),validation=best["validation"],
  training_candidates=sum(len(g["cost"]) for g in tr),validation_candidates=sum(len(g["cost"]) for g in va),
  candidates=[{k:v for k,v in c.items() if k not in ("nodes","validation")}|
              dict(nodes=len(c["nodes"]),validation={k:v for k,v in c["validation"].items() if k!="choices"}) for c in candidates])
 (HERE/"tree_candidate_results.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(dict(nodes=len(best["nodes"]),depth=best["depth"],target=best["target"],
  training={k:v for k,v in result["training"].items() if k!="choices"},
  validation={k:v for k,v in result["validation"].items() if k!="choices"})),flush=True)
if __name__=="__main__":main()
