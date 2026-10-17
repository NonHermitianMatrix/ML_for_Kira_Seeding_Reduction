"""Derive whole-seed decisions from trained equation scores without changing exact algebra."""
from functools import lru_cache
import time,gzip,json
import numpy as np
from s00_probe import HERE,BOUNDS,rt,inputs,save
from s02_train import FEATURES

def compile_union(source,constants,nops,threshold):
 nodes=[dict(feature=-1,threshold=0.,left=-1,right=-1,probability=0.),dict(feature=-1,threshold=0.,left=-1,right=-1,probability=1.)];unique={}
 def make(f,cut,left,right):
  if left==right:return left
  key=(f,cut,left,right)
  if key not in unique:
   if len(nodes)>50000:raise ValueError('Intermediate decision size limit')
   unique[key]=len(nodes);nodes.append(dict(feature=f,threshold=cut,left=left,right=right,probability=0.))
  return unique[key]
 @lru_cache(None)
 def restrict(i,op,otherwise):
  node=source[i];f=node['feature']
  if f<0:return 1 if node['probability']>=threshold else otherwise
  if f==14 or f in constants:
   value=op if f==14 else constants[f]
   return restrict(node['left'] if value<=node['threshold'] else node['right'],op,otherwise)
  return make(f,node['threshold'],restrict(node['left'],op,otherwise),restrict(node['right'],op,otherwise))
 @lru_cache(None)
 def either(a,b):
  if a==1 or b==1:return 1
  if a==0:return b
  if b==0 or a==b:return a
  x,y=nodes[a],nodes[b]
  if (x['feature'],x['threshold'])==(y['feature'],y['threshold']):
   return make(x['feature'],x['threshold'],either(x['left'],y['left']),either(x['right'],y['right']))
  return make(x['feature'],x['threshold'],either(x['left'],b),either(x['right'],b))
 roots=list(dict.fromkeys(restrict(0,op,0) for op in range(nops)))
 root=0
 for r in reversed(roots):root=either(r,root)
 # The file format permits shared descendants. Put the root first and retain reachable nodes only.
 order=[];seen=set();todo=[root]
 while todo:
  i=todo.pop()
  if i in seen:continue
  seen.add(i);order.append(i)
  if nodes[i]['feature']>=0:todo.extend([nodes[i]['right'],nodes[i]['left']])
 mapping={old:new for new,old in enumerate(order)}
 return [dict(nodes[i],left=mapping[nodes[i]['left']] if nodes[i]['feature']>=0 else -1,right=mapping[nodes[i]['right']] if nodes[i]['feature']>=0 else -1) for i in order]

def score(nodes,x):
 i=0
 while nodes[i]['feature']>=0:
  n=nodes[i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
 return nodes[i]['probability']

def main():
 dest=HERE/'trained_model';candidates=rt.read(dest/'candidates.json')
 if candidates.get('seed_variants_complete'):return
 start=time.perf_counter();cases={c['id']:c for c in rt.read(BOUNDS/'protocol.json')['splits']['validation']};data=[rt.read(p) for p in sorted((HERE/'validation').glob('*.json.gz')) if not p.name.endswith('_failed.json.gz')];record=[]
 inputs.write(dest/'equation_candidates.json',candidates)
 for graph,options in list(candidates['candidates'].items()):
  group=[r for r in data if r['graph']==graph]
  if not group:continue
  definition=cases[group[0]['case']]['definition'];l=len(definition['loop_momenta']);e=len(definition['external_momenta']);nops=l*(l+e)+e*(e-1)//2;constants={0:l,1:e,2:len(definition['propagators'])}
  # Score whole seeds by the maximum over operators, then select thresholds from validation labels.
  alternatives=[]
  for name in sorted({o['name'] for o in options}):
   source=rt.read(dest/(name+'.json.gz'));cache={};scores=[];labels=[];weights=[]
   for r in group:
    for row in r['samples']:
     x=dict(zip(FEATURES,row[2:]));key=tuple(x[f] for f in FEATURES if f!=14)
     if key not in cache:cache[key]=max(score(source['nodes'],x|{14:op}) for op in range(nops))
     scores.append(cache[key]);labels.append(row[0]);weights.append(row[1])
   ps=np.array(scores);ys=np.array(labels);ws=np.array(weights)
   cuts=np.unique(np.r_[1e-12,np.quantile(ps[ys==1],[0,.001,.005,.01,.02]),.01,.05,.1,.25,.5,.75,.9,1.])
   for cut in cuts:
    keep=ps>=cut;recall=float(np.sum(ws*ys*keep)/np.sum(ws*ys));fraction=float(np.sum(ws*keep)/np.sum(ws))
    if recall>=.98 and fraction<.9999:alternatives.append(dict(name=name,threshold=float(cut),recall=recall,retained_fraction=fraction))
  seed_options=[]
  for floor in [.9999,.995,.98]:
   eligible=[o for o in alternatives if o['recall']>=floor]
   if not eligible:continue
   best=min(eligible,key=lambda o:(o['retained_fraction'],o['name']))
   if (best['name'],best['threshold']) not in [(o['name'],o['threshold']) for o in seed_options]:seed_options.append(best)
  additions=[]
  for index,option in enumerate(seed_options):
   model=rt.read(dest/(option['name']+'.json.gz'))
   try:nodes=compile_union(model['nodes'],constants,nops,option['threshold'])
   except ValueError as exc:record.append(dict(graph=graph,source=option,skipped=str(exc)));continue
   if len(nodes)>8191:record.append(dict(graph=graph,source=option,skipped='Compiled decision exceeds 8191 nodes',nodes=len(nodes)));continue
   kept=total=positive=positive_kept=0.;checked=0
   for r in group:
    for i,row in enumerate(r['samples']):
     x=dict(zip(FEATURES,row[2:]));take=score(nodes,x)>=.5;weight=row[1];total+=weight;kept+=weight*take;positive+=weight*row[0];positive_kept+=weight*row[0]*take
     if i<100:
      expected=any(score(model['nodes'],x|{14:op})>=option['threshold'] for op in range(nops))
      assert take==expected;checked+=1
   fraction=kept/total;recall=positive_kept/positive
   if fraction>=.9999:record.append(dict(graph=graph,source=option,skipped='Retains all sampled candidates',retained_fraction=fraction));continue
   name=f'{graph}_seed_union_{index}';weightfile=dest/(name+'.txt')
   text=str(len(nodes))+'\n'+''.join(f'{z["feature"]} {z["threshold"]:.17g} {z["left"]} {z["right"]} {z["probability"]:.17g}\n' for z in nodes)
   metadata=dict(name=name,kind='seed_union',nodes=nodes,features=[f for f in FEATURES if f!=14],depth=model['depth'],min_leaf=model['min_leaf'],origin_model=option['name'],origin_threshold=option['threshold'],operator_count=nops,definition='Retain all operators of a seed if any trained operator score meets the original threshold.',equivalence_checks=checked)
   used=sum(q.stat().st_blocks*512 for root in [HERE,BOUNDS] for q in root.rglob('*') if q.is_file())
   if used+len(text.encode())+len(gzip.compress(json.dumps(metadata).encode()))>24*1024**2:
    record.append(dict(graph=graph,source=option,skipped='Model storage allowance; keep space for exact tests'));continue
   weightfile.write_text(text);save(dest/(name+'.json.gz'),metadata)
   item=dict(name=name,threshold=.5,recall=recall,retained_fraction=fraction,kind='seed_union');additions.append(item);record.append(dict(graph=graph,source=option,derived=item,nodes=len(nodes),equivalence_checks=checked))
  candidates['candidates'][graph]=options+additions
 candidates['seed_variants_complete']=True;candidates['training_seconds']+=time.perf_counter()-start
 inputs.write(dest/'seed_variants.json',dict(records=record,seconds=time.perf_counter()-start));inputs.write(dest/'candidates.json',candidates)
 print('SEED_VARIANTS',sum('derived' in r for r in record),flush=True)
if __name__=='__main__':main()
