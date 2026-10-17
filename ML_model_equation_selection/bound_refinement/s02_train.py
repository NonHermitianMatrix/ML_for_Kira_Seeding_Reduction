"""Collect exact support labels and fit fast equation classifiers on tuned seed regions."""
import hashlib,json,math,sys,time
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from s00_probe import HERE,ROOT,BOUNDS,rt,inputs,attempt,save
FEATURES=list(range(15))+[22,23]
def collect(c,split,cfg):
 p=HERE/split/(c['id']+'.json.gz')
 if p.exists():return rt.read(p)
 eligible=BOUNDS/split/(c['id']+'_native.json.gz')
 if not eligible.exists() or not rt.read(eligible)['success']:return None
 ref=BOUNDS/'references'/(c['id']+'.json.gz')
 if not ref.exists() or not rt.read(ref)['success']:return None
 rr=rt.read(ref)
 if all(row=={t:'1'} for t,row in rr['coefficients'].items()):return None
 start=time.perf_counter();r=attempt(c,rr['masters'],cfg['fixed_by_graph'][c['topology_group']],collect=True)
 rt.verify(r,ref)
 if not r['success'] or not r.get('equation_records'):
  save(p.with_name(c['id']+'_failed.json.gz'),rt.compact(r));return None
 rows=[line.split('\t') for line in r['equation_records'].splitlines()];assert all(len(row)==28 for row in rows)
 # Keep a stratified sample. Inverse sampling weights retain the native class frequencies.
 labels=np.array([int(row[1]) for row in rows]);rng=np.random.default_rng(int(hashlib.sha256(c['id'].encode()).hexdigest()[:8],16));samples=[];keys=[]
 for y in [0,1]:
  ids=np.flatnonzero(labels==y);take=min(2000,len(ids));chosen=rng.choice(ids,take,replace=False) if take else []
  for i in sorted(chosen):
   samples.append([y,len(ids)/take]+[float(rows[i][j+2]) for j in FEATURES]);keys.append(rows[i][0])
 out=dict(case=c['id'],graph=c['topology_group'],split=split,source_rows=len(rows),source_positives=int(labels.sum()),samples=samples,candidate_keys=keys,features=FEATURES,seed_action=cfg['fixed_by_graph'][c['topology_group']],run=rt.compact(r),seconds=time.perf_counter()-start)
 save(p,out);print(json.dumps(dict(stage='collect',case=c['id'],rows=len(rows),retained=len(samples),seconds=out['seconds'])),flush=True);return out

def export(model,path):
 t=model.tree_;n=t.node_count;nodes=[]
 for i in range(n):
  leaf=t.children_left[i]<0;p=float(t.value[i,0,1]/t.value[i,0].sum())
  nodes.append(dict(feature=-1 if leaf else FEATURES[int(t.feature[i])],threshold=float(t.threshold[i]) if not leaf else 0,left=int(t.children_left[i]),right=int(t.children_right[i]),probability=p))
 path.write_text(str(n)+'\n'+''.join(f'{z["feature"]} {z["threshold"]:.17g} {z["left"]} {z["right"]} {z["probability"]:.17g}\n' for z in nodes));return nodes

def main():
 protocol=rt.read(BOUNDS/'protocol.json');cfg=rt.read(BOUNDS/'trained_model/fixed.json');data={}
 for split in ['training','validation']:
  data[split]=[r for c in protocol['splits'][split] if (r:=collect(c,split,cfg)) is not None]
 assert data['training'] and data['validation']
 x=[];y=[];w=[]
 for r in data['training']:
  for row in r['samples']:y.append(row[0]);w.append(row[1]/r['source_rows']);x.append(row[2:])
 x=np.array(x,dtype=np.float32);y=np.array(y);w=np.array(w);candidates=[];dest=HERE/'trained_model';dest.mkdir(exist_ok=True)
 start=time.perf_counter()
 for depth in [6,10,14,18]:
  for leaf in [4,16]:
   name=f'tree_d{depth}_l{leaf}';model=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,max_leaf_nodes=4096,random_state=611)
   model.fit(x,y,sample_weight=w);nodes=export(model,dest/(name+'.txt'));scores={}
   for r in data['validation']:
    a=np.array(r['samples']);scores[r['case']]=model.predict_proba(a[:,2:].astype(np.float32))[:,1].tolist()
   save(dest/(name+'.json.gz'),dict(name=name,nodes=nodes,depth=depth,min_leaf=leaf,max_leaf_nodes=4096,training_rows=len(y),training_positives=int(y.sum()),features=FEATURES,training_files=[r['case'] for r in data['training']],label='Native selected integral-support membership; proxy, not unique necessity.'))
   candidates.append(dict(name=name,scores=scores))
 # Rank candidate filters by retained equation fraction at specified validation recall levels.
 shortlist={}
 for graph in inputs.GRAPHS:
  group=[r for r in data['validation'] if r['graph']==graph]
  if not group:continue
  options=[]
  for candidate in candidates:
   ps=np.concatenate([candidate['scores'][r['case']] for r in group]);a=np.concatenate([np.array(r['samples']) for r in group]);ys=a[:,0];ws=a[:,1]
   cuts=np.unique(np.r_[1e-12,np.quantile(ps[ys==1], [0,.001,.005,.01,.02]),.01,.05,.1,.25,.5])
   for cut in cuts:
    keep=ps>=cut;recall=float(np.sum(ws*ys*keep)/np.sum(ws*ys));fraction=float(np.sum(ws*keep)/np.sum(ws))
    if recall<.98:continue
    options.append(dict(name=candidate['name'],threshold=float(cut),recall=recall,retained_fraction=fraction))
  chosen=[]
  for floor in [.9999,.995,.98]:
   opts=[o for o in options if o['recall']>=floor]
   if not opts:continue
   best=min(opts,key=lambda o:(o['retained_fraction'],o['name']))
   if (best['name'],best['threshold']) not in [(o['name'],o['threshold']) for o in chosen]:chosen.append(best)
  shortlist[graph]=chosen
 inputs.write(dest/'candidates.json',dict(training_seconds=time.perf_counter()-start,training_cases=len(data['training']),validation_cases=len(data['validation']),training_rows=len(y),training_positives=int(y.sum()),candidates=shortlist,source_protocol_sha256=inputs.sha(BOUNDS/'protocol.json'),seed_config_sha256=inputs.sha(BOUNDS/'trained_model/fixed.json')))
 print(json.dumps(dict(stage='trained',shortlist=shortlist)),flush=True)
if __name__=='__main__':main()
