"""Compare shared and graph-specific classifiers before complete-cost validation."""
import time
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from s00_probe import HERE,rt,inputs,save
from s02_train import FEATURES,export

def main():
 dest=HERE/'trained_model';previous=rt.read(dest/'candidates.json')
 if previous.get('graph_specific_fits'):return
 start=time.perf_counter();training=[rt.read(p) for p in sorted((HERE/'training').glob('*.json.gz')) if not p.name.endswith('_failed.json.gz')];validation=[rt.read(p) for p in sorted((HERE/'validation').glob('*.json.gz')) if not p.name.endswith('_failed.json.gz')];fit_records=[];shortlist={}
 for graph in inputs.GRAPHS:
  tr=[r for r in training if r['graph']==graph];va=[r for r in validation if r['graph']==graph]
  if not tr or not va:continue
  x=[];y=[];w=[]
  for r in tr:
   for row in r['samples']:y.append(row[0]);w.append(row[1]/r['source_rows']);x.append(row[2:])
  x=np.array(x,dtype=np.float32);y=np.array(y);w=np.array(w);a=np.concatenate([np.array(r['samples']) for r in va]);vx=a[:,2:].astype(np.float32);ys=a[:,0];ws=a[:,1]
  if not np.sum(ws*ys):continue
  options=list(previous['candidates'].get(graph,[]));models={}
  for depth in [6,10,14,18]:
   for leaf in [4,16]:
    tick=time.perf_counter();name=f'{graph}_d{depth}_l{leaf}';model=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,max_leaf_nodes=4096,random_state=611);model.fit(x,y,sample_weight=w);models[name]=model
    ps=model.predict_proba(vx)[:,1];cuts=np.unique(np.r_[1e-12,np.quantile(ps[ys==1],[0,.001,.005,.01,.02]),.01,.05,.1,.25,.5])
    results=[]
    for cut in cuts:
     keep=ps>=cut;recall=float(np.sum(ws*ys*keep)/np.sum(ws*ys));fraction=float(np.sum(ws*keep)/np.sum(ws))
     if recall<.98:continue
     opt=dict(name=name,threshold=float(cut),recall=recall,retained_fraction=fraction);options.append(opt);results.append(opt)
    fit_records.append(dict(name=name,graph=graph,depth=depth,min_leaf=leaf,max_leaf_nodes=4096,nodes=int(model.tree_.node_count),training_rows=len(y),training_positives=int(y.sum()),training_cases=[r['case'] for r in tr],validation_candidates=results,seconds=time.perf_counter()-tick))
  chosen=[]
  for floor in [.9999,.995,.98]:
   opts=[o for o in options if o['recall']>=floor]
   if not opts:continue
   best=min(opts,key=lambda o:(o['retained_fraction'],o['name']))
   if (best['name'],best['threshold']) not in [(o['name'],o['threshold']) for o in chosen]:chosen.append(best)
  shortlist[graph]=chosen
  for name in {o['name'] for o in chosen if o['name'] in models}:
   nodes=export(models[name],dest/(name+'.txt'));metadata=next(r for r in fit_records if r['name']==name)
   save(dest/(name+'.json.gz'),metadata|dict(nodes=nodes,features=FEATURES,label='Native selected integral-support membership; proxy, not unique necessity.'))
  print('GRAPH_FIT',graph,chosen,flush=True)
 inputs.write(dest/'shared_candidates.json',previous)
 previous.update(candidates=shortlist,graph_specific_fits=len(fit_records),training_seconds=previous['training_seconds']+time.perf_counter()-start)
 inputs.write(dest/'graph_fits.json',dict(fits=fit_records,seconds=time.perf_counter()-start,stored_weights='Only shortlisted graph-specific trees are stored. Other deterministic fits are reproduced from the saved data and code.'))
 inputs.write(dest/'candidates.json',previous)
if __name__=='__main__':main()
