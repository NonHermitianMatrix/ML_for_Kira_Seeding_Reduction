"""Fit compact row-cost trees with grouped validation and exact native cost labels."""
import collections,hashlib,json,math,pathlib,sys
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"Kira_comparison/integrated_runtime"))
from s03_records import read_record
EXPERIMENT=ROOT/"Kira_comparison/integrated_runtime"
def fit(x,y,weight,depth,minleaf):
 nodes=[]
 def build(ids,level):
  w=weight[ids];yy=y[ids];value=float(w@yy/w.sum());slot=len(nodes)
  nodes.append(dict(feature=-1,cut=0.,left=-1,right=-1,value=value))
  if level>=depth or len(ids)<2*minleaf:return slot
  base=float(np.sum(w*(yy-value)**2));best=None
  for col in range(x.shape[1]):
   order=ids[np.argsort(x[ids,col],kind="stable")];z=x[order,col];w=weight[order];yy=y[order]
   sw=np.cumsum(w);sy=np.cumsum(w*yy);s2=np.cumsum(w*yy*yy)
   k=np.arange(minleaf,len(ids)-minleaf+1);a=k-1
   valid=z[a]!=z[k];k=k[valid];a=a[valid]
   if not len(k):continue
   loss=s2[a]-sy[a]**2/sw[a]+s2[-1]-s2[a]-(sy[-1]-sy[a])**2/(sw[-1]-sw[a])
   j=int(np.argmin(loss));v=float(loss[j])
   if best is None or v<best[0]:best=(v,col,float((z[k[j]-1]+z[k[j]])/2),order[:k[j]],order[k[j]:])
  if best is None or best[0]>=base-1e-14:return slot
  _,col,cut,left,right=best
  a=build(left,level+1);b=build(right,level+1)
  nodes[slot]=dict(feature=col,cut=cut,left=a,right=b,value=value);return slot
 build(np.arange(len(y)),0);return nodes
def predict(nodes,x):
 i=0
 while nodes[i]["feature"]>=0:
  n=nodes[i];i=n["left"] if x[n["feature"]]<=n["cut"] else n["right"]
 return nodes[i]["value"]
def evaluate(groups,nodes=None,gain=0,fill=False):
 families=collections.defaultdict(lambda:dict(native_seconds=0.,chosen_seconds=0.,native_bytes=0.,chosen_bytes=0.,groups=0,changed=0))
 for g in groups:
  scores=g["absolute"][:,18] if fill else np.array([0.]+[predict(nodes,x) for x in g["x"][1:]])
  q=int(scores.argmin())
  if not fill and scores[q]>-gain:q=0
  f=families[g["family"]];f["groups"]+=1;f["changed"]+=q!=0
  f["native_seconds"]+=g["seconds"][0];f["chosen_seconds"]+=g["seconds"][q]
  f["native_bytes"]+=g["bytes"][0];f["chosen_bytes"]+=g["bytes"][q]
 for f in families.values():
  f["time_ratio"]=f["chosen_seconds"]/f["native_seconds"]
  f["bytes_ratio"]=(f["chosen_bytes"]+1)/(f["native_bytes"]+1)
 return dict(groups=len(groups),changed=sum(f["changed"] for f in families.values()),
  time_ratio=math.exp(sum(math.log(f["time_ratio"]) for f in families.values())/len(families)),
  bytes_ratio=math.exp(sum(math.log(f["bytes_ratio"]) for f in families.values())/len(families)),families=dict(families))
def main():
 manifest=json.loads((EXPERIMENT/"families.json").read_text());groups=[];hashes={};excluded=0
 for case in manifest["cases"]:
  path=EXPERIMENT/"collection"/f'{case["id"]}_n{min(32,len(case["targets"]))}.json.gz'
  assert path.exists(),path
  r=read_record(path);assert r["success"] and r["reference_checked"]
  hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
  for item in r.get("choices",[]):
   candidates=item["candidates"]
   f=np.asarray([c["features"] for c in candidates],float)
   if not item["measured"] or f.shape[1]!=24 or not np.all(f[:,23]==1):excluded+=1;continue
   seconds=np.asarray([c["seconds"] for c in candidates],float);size=np.asarray([c["after_bytes"] for c in candidates],float)
   assert np.isfinite(f).all() and np.all(seconds>0) and np.all(size>=0)
   groups.append(dict(case=case["id"],family=case["id"].removesuffix("_deep"),split=case["split"],x=f-f[0],absolute=f,seconds=seconds,bytes=size))
 train=[g for g in groups if g["split"]=="training"];valid=[g for g in groups if g["split"]=="validation"]
 assert train and valid
 totals=collections.defaultdict(float)
 for g in train:totals[g["family"]]+=max(g["seconds"][0],1e-5)
 results=[];selected=[]
 for objective in ["local_time","output_bytes","time_and_bytes"]:
  x=[];y=[];weights=[]
  for g in train:
   time_label=np.log((g["seconds"]+1e-5)/(g["seconds"][0]+1e-5))
   byte_label=np.log((g["bytes"]+1)/(g["bytes"][0]+1))
   label=time_label if objective=="local_time" else byte_label if objective=="output_bytes" else (time_label+byte_label)/2
   for q in range(1,len(label)):
    x.append(g["x"][q]);y.append(label[q]);weights.append(max(g["seconds"][0],1e-5)/totals[g["family"]]/(len(label)-1))
  x=np.asarray(x);y=np.asarray(y);weights=np.asarray(weights)
  candidates=[]
  for depth in [2,3,4]:
   for minleaf in [8,16]:
    nodes=fit(x,y,weights,depth,minleaf)
    for gain in [0.,.01,.03,.1]:
     result=evaluate(valid,nodes,gain)
     candidates.append(dict(objective=objective,depth=depth,minleaf=minleaf,gain=gain,nodes=nodes,validation=result))
  key="bytes_ratio" if objective=="output_bytes" else "time_ratio"
  best=min(candidates,key=lambda c:(c["validation"][key],len(c["nodes"]),c["validation"]["changed"]))
  model=dict(features=24,kind="relative candidate-cost regression tree",objective=objective,
   feature_transform="candidate minus native source; native score fixed to zero",nodes=best["nodes"],minimum_predicted_gain=best["gain"],
   depth=best["depth"],minimum_leaf_examples=best["minleaf"],input_sha256=hashes,
   training_families=sorted(totals),confidence="uncalibrated softmax of negative cost scores")
  folder=HERE/"candidates"/objective;folder.mkdir(parents=True,exist_ok=True)
  (folder/"model.json").write_text(json.dumps(model,indent=2)+"\n")
  lines=[f'24 0 {best["gain"]:.17g}'," ".join(["0"]*24)," ".join(["1"]*24)," ".join(["0"]*24),str(len(best["nodes"]))]
  lines.extend(f'{n["feature"]} {n["cut"]:.17g} {n["left"]} {n["right"]} {n["value"]:.17g}' for n in best["nodes"])
  (folder/"weights.txt").write_text("\n".join(lines)+"\n")
  result=dict(objective=objective,training=evaluate(train,best["nodes"],best["gain"]),validation=best["validation"],nodes=len(best["nodes"]),depth=best["depth"],gain=best["gain"])
  selected.append(result)
  results.extend({k:v for k,v in c.items() if k!="nodes"}|dict(nodes=len(c["nodes"])) for c in candidates)
 report=dict(training_groups=len(train),validation_groups=len(valid),excluded_modular_samples=excluded,
  labels="measured immediate exact insertion times and resulting coefficient text sizes; full repeated-policy timings are still required",
  selected=selected,fill_control=dict(training=evaluate(train,fill=True),validation=evaluate(valid,fill=True)),candidates=results)
 (HERE/"training_results.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({k:v for k,v in report.items() if k not in ["candidates"]}),flush=True)
if __name__=="__main__":main()
