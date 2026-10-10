"""Fit a small target-dependent CART probability model using training groups only."""
import hashlib,json,pathlib,time
import numpy as np
from s02_records import read
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FEATURES=["loops","external_momenta","index_count","log_target_count","seed_lines","seed_dots","seed_numerator_rank","dots_above_target_max","rank_above_target_max","seed_sector_requested","dots_above_sector_target_max","rank_above_sector_target_max","minimum_seed_target_l1","seed_is_target","operator_index","raw_term_count","log_coefficient_characters","raw_target_term_count","maximum_term_lines","maximum_term_dots","maximum_term_rank","minimum_term_dots","target_max_dots","target_max_rank"]
def train(name,depth,minchild):
 maxdepth=depth;start=time.perf_counter();blocks=[];ys=[];ws=[];counts=[];families={}
 for p in sorted(list((HERE.parent/"training").glob("*.json.gz"))+list((HERE/"training").glob("*.json.gz"))):
  if "_failed" in p.name:continue
  r=read(p);assert r["split"]=="training" and r["success"] and r["reference_checked"]
  lines=[l.split("\t") for l in r["equation_records"].splitlines()]
  assert lines and all(len(l)==28 for l in lines),(p,len(lines[0]))
  x=np.array([[float(v) for v in l[2:26]] for l in lines],dtype=np.float64);y=np.array([int(l[1]) for l in lines],dtype=np.float64)
  assert 0<y.sum()<len(y),(p,y.sum(),len(y))
  families[r["group"]]=families.get(r["group"],0)+1
  blocks.append(x);ys.append(y);ws.append((r["group"],len(y)));counts.append(dict(file=str(p.relative_to(ROOT)),case=r["case"],size=r["size"],rows=len(y),positives=int(y.sum()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 x=np.vstack(blocks);y=np.concatenate(ys);w=np.concatenate([np.full(n,1/(n*families[g])) for g,n in ws]);nodes=[]
 def impurity(a,b):return a*b/(a+b) if a+b>0 else 0
 def build(ids,depth):
  idx=len(nodes);pos=float(np.dot(w[ids],y[ids]));tot=float(w[ids].sum())
  # Small smoothing keeps empirical probabilities finite without asserting calibration.
  p=(float(y[ids].sum())+.5)/(len(ids)+1)
  nodes.append(dict(feature=-1,threshold=0,left=-1,right=-1,probability=p,rows=len(ids),positive=int(y[ids].sum())))
  if depth==maxdepth or len(ids)<2*minchild or pos<1e-12 or tot-pos<1e-12:return idx
  best=None;gain=0;parent=impurity(pos,tot-pos)
  for j in range(x.shape[1]):
   if 15<=j<=21:continue  # Expression spelling can vary between equivalent native runs.
   vals=x[ids,j];cuts=np.unique(np.quantile(vals,np.linspace(.02,.98,25)))
   for cut in cuts:
    mask=vals<=cut;nl=int(mask.sum())
    if nl<minchild or len(ids)-nl<minchild:continue
    cut=.5*(float(vals[mask].max())+float(vals[~mask].min()))
    left=ids[mask];lp=float(np.dot(w[left],y[left]));lt=float(w[left].sum())
    score=parent-impurity(lp,lt-lp)-impurity(pos-lp,tot-lt-pos+lp)
    if score>gain+1e-12:gain=score;best=(j,float(cut),mask)
  if best:
   j,cut,mask=best;left=build(ids[mask],depth+1);right=build(ids[~mask],depth+1);nodes[idx].update(feature=j,threshold=cut,left=left,right=right)
  return idx
 build(np.arange(len(y)),0)
 def predict(a):
  out=[]
  for row in a:
   i=0
   while nodes[i]["feature"]>=0:
    z=nodes[i];i=z["left"] if row[z["feature"]]<=z["threshold"] else z["right"]
   out.append(nodes[i]["probability"])
  return np.array(out)
 p=predict(x);loss=float(-np.average(y*np.log(p)+(1-y)*np.log1p(-p),weights=w))
 model=dict(excluded_features=list(range(15,22)),decision_feature_count=17,trainer_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),type="CART",features=FEATURES,nodes=nodes,maximum_depth=maxdepth,minimum_child_rows=minchild,training_groups=len(families),training_rows=len(y),training_positives=int(y.sum()),weighted_training_cross_entropy=loss,training_seconds=time.perf_counter()-start,training_files=counts,label="Integral-support membership in final native regenerated equation set; conservative proxy, not a unique or optimal necessity label.",probability="Smoothed empirical leaf frequency; no calibration claim.")
 dest=HERE/"trained_model"/name;dest.mkdir(exist_ok=True)
 (dest/"model.json").write_text(json.dumps(model,indent=2)+"\n")
 (dest/"weights.txt").write_text(str(len(nodes))+"\n"+"".join(f'{z["feature"]} {z["threshold"]:.17g} {z["left"]} {z["right"]} {z["probability"]:.17g}\n' for z in nodes))
 (HERE/"training"/(name+"_summary.json")).write_text(json.dumps({k:v for k,v in model.items() if k not in ("nodes","features")},indent=2)+"\n")
 print(json.dumps({k:model[k] for k in ["training_groups","training_rows","training_positives","weighted_training_cross_entropy","training_seconds"]}),flush=True)
if __name__=="__main__":
 train("early_d8",8,24)
 train("early_d12",12,8)
