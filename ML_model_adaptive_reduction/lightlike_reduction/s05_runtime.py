"""Apply every supported exact rule before learned native seed selection."""
from s00_light_common import *
from s01_lightlike import reduce as lightlike,eligible
from s12_complete_tensor import reduce as tensor
ACTIONS=['sparse_wide','sparse_tight','sparse_medium']

def features(c):
 ts=c['targets'];r=[sum(max(-a,0) for a in t) for t in ts];u=[-t[-2] for t in ts];v=[-t[-1] for t in ts]
 d=c['definition'];import re
 incidence=[[bool(re.search(r'\b'+re.escape(k)+r'\b',p['momentum'])) for k in d['loop_momenta']] for p in d['propagators'][:d['physical_propagators']]]
 return [len(ts),min(r),max(r),statistics.mean(r),len(set(r)),min(u),max(u),statistics.mean(u),min(v),max(v),statistics.mean(v),sum(x==0 for x in u),sum(x==0 for x in v),sum(x*y for x,y in zip(u,v)),sum((x-y)**2 for x,y in zip(u,v)),sum(sum(row)>1 for row in incidence),max(sum(row[i] for row in incidence) for i in range(len(d['loop_momenta'])))]+[sum(x==i for x in r) for i in range(1,5)]

def choice(c,method):
 if method in ACTIONS:return method,None,None
 path=HERE/'trained_model/policy.json'
 if not path.exists():return None,None,None
 m=read(path);k=ACTIONS.index(m['fixed'])
 if method=='all_fixed':return m['fixed'],None,None
 if not m['enabled']:return m['fixed'],None,dict(reason='model_disabled',selected=k)
 x=features(c)
 def predict(t):
  while 'feature' in t:t=t['left'] if x[t['feature']]<=t['cut'] else t['right']
  return t['cost']
 scores=[statistics.mean(predict(t)[j] for t in m['trees']) for j in range(3)];j=min(range(3),key=scores.__getitem__)
 if scores[j]+.002>=scores[k]*(1-m['margin']):j=k
 from s21_failure_guard import gate
 j,info=gate(m,x,j,k)
 return ACTIONS[j],scores,info

def independent_parts(c):
 import re
 d=c['definition'];lm=d['loop_momenta'];N=len(d['propagators']);P=d['physical_propagators']
 if len(lm)<2 or d.get('cut_propagators') or d.get('symbolic_ibp'):return None
 inc=[{k for k in lm if re.search(r'\b'+re.escape(k)+r'\b',p['momentum'])} for p in d['propagators']]
 if any(len(inc[j])!=1 and any(a[j]!=0 for a in c['targets']) for j in range(N)):return None
 out=[]
 for i,k in enumerate(lm):
  ids=[j for j in range(N) if inc[j]=={k}]
  if not ids or len(ids)>5:return None
  sd=copy.deepcopy(d);sd['loop_momenta']=['k1'];sd['propagators']=[dict(d['propagators'][j],momentum=re.sub(r'\b'+re.escape(k)+r'\b','k1',d['propagators'][j]['momentum'])) for j in ids];sd['physical_propagators']=sum(j<P for j in ids);sd['top_level_sectors']=[(1<<sd['physical_propagators'])-1];sd['rank']=len(ids);sd.pop('quadratic_momentum_vectors',None)
  ts=[list(a) for a in dict.fromkeys(tuple(t[j] for j in ids) for t in c['targets'])];cc=dict(c,id=c['id']+'_block'+str(i),definition=sd,targets=ts,size=len(ts));out.append(dict(indices=ids,case=cc))
 return out

def run(c,method='integrated'):
 start=time.perf_counter()
 if method=='previous':return previous().run(c,'integrated')
 if len(c['definition']['loop_momenta'])==1:
  r=lightlike(c,deadline=time.perf_counter()+8)
  if r is None and c['definition'].get('invariants'):
   from s09_symbolic import reduce as symbolic
   r=symbolic(c)
  if r is None:r=tensor(c,'tensor_smallest',deadline=time.perf_counter()+12)
  if r is not None:return dict(success=True,status='completed',application='exact_and_learned_decomposition',blocks=[dict(case=c,indices=list(range(len(c['definition']['propagators']))),result=r)],model_used=False,total_seconds=time.perf_counter()-start)
  # Apply the exact identity to each admitted target in a mixed request.
  accepted={};remaining=[]
  for t in c['targets']:
   cc=dict(c,targets=[t],size=1);rr=lightlike(cc,deadline=time.perf_counter()+2) if eligible(cc) else None
   if rr is None:remaining.append(t)
   else:accepted.update(rr['coefficients'])
  if accepted and not remaining:
   rr=dict(success=True,status='completed',coefficients=accepted,masters=[list(map(int,m.split(','))) for m in sorted({m for row in accepted.values() for m in row})],model_used=False,attempts=[])
   return dict(success=True,status='completed',blocks=[dict(case=c,indices=list(range(len(c['definition']['propagators']))),result=rr)],model_used=False,total_seconds=time.perf_counter()-start)
  if accepted and remaining:
   cc=dict(c,targets=remaining,size=len(remaining));rr=previous().run(cc,'all_fixed' if method=='all_fixed' else 'integrated')
   if rr.get('success') and len(rr['blocks'])==1:
    block=rr['blocks'][0];block['case']=c;block['result']['coefficients'].update(accepted);block['result']['masters']=[list(map(int,m.split(','))) for m in sorted({m for row in block['result']['coefficients'].values() for m in row})];block['result']['exact_pre_reduced_targets']=len(accepted);rr['total_seconds']=time.perf_counter()-start;return rr
   return dict(success=False,status='remaining_targets_incomplete',exact_coefficients=accepted,remaining=rr,total_seconds=time.perf_counter()-start)
 parts=independent_parts(c)
 old=None if parts else previous()
 if parts:
  blocks=[];memo={}
  for p in parts:
   cc=p['case'];key=json.dumps([cc['definition'],cc['targets']],sort_keys=True)
   if key not in memo:memo[key]=run(cc,method)
   rr=memo[key]
   if not rr.get('success'):return dict(success=False,status='incomplete_component',blocks=blocks,failed_component=rr,total_seconds=time.perf_counter()-start)
   blocks.append(dict(indices=p['indices'],case=cc,result=rr['blocks'][0]['result']))
  return dict(success=True,status='completed',blocks=blocks,model_used=any(b['result'].get('model_used',False) for b in blocks),representation='Product of exact component reductions.',total_seconds=time.perf_counter()-start)
 # Restrict learned native actions to the domain for which they were measured.
 if len(c['definition']['loop_momenta'])==2 and len(c['definition']['propagators'])==9:
  vac=old.previous()
  if vac.batch.eligible(c):
   tick=time.perf_counter();action,scores,admission=choice(c,method);prediction=time.perf_counter()-tick
   if action is not None:
    native=load('lightlike_native_runtime',vac.HERE/'s02_native.py');r=native.run(c,action)
    r.update(model_used=scores is not None,selected_native_action=action,selection_scores=scores,failure_gate=admission,prediction_seconds=prediction,total_seconds=time.perf_counter()-start);return r
 r=old.run(c,'all_fixed' if method=='all_fixed' else 'integrated');r['total_seconds']=time.perf_counter()-start;return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:
  assert Path(a.case).stat().st_size<1024**2;r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r)
