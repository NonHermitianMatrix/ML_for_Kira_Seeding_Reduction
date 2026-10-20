"""Apply exact tensor identities before the preceding exact and native ML rules."""
from s00_tensor_common import *
from s17_fast_tensor import eligible,reduce

def fast_choice(c,method):
 if method in ACTIONS:return method,False
 p=HERE/'trained_model/fast_policy.json'
 if not p.exists():return ACTIONS[0],False
 model=read(p)
 if method=='all_fixed' or not model['enabled']:return model['fixed'],False
 x=features(c)
 if any(v<a or v>b for v,a,b in zip(x,model['minimum'],model['maximum'])):return model['fixed'],False
 cost=[statistics.mean(predict(t,x)[j] for t in model['trees']) for j in range(len(ACTIONS))];j=min(range(len(ACTIONS)),key=cost.__getitem__);k=ACTIONS.index(model['fixed'])
 if cost[j]+.001>=cost[k]*(1-model['margin']):j=k
 return ACTIONS[j],True

def tensor_parts(c):
 import re
 d=c['definition'];lm=d['loop_momenta'];em=d['external_momenta'];N=len(d['propagators']);P=d['physical_propagators']
 if len(lm)<2 or d.get('cut_propagators') or d.get('symbolic_ibp'):return None
 if not 1<=len(em)<=4 or any(len(a)!=N for a in c['targets']):return None
 inc=[{k for k in lm if re.search(r'\b'+re.escape(k)+r'\b',p['momentum'])} for p in d['propagators']]
 if any(len(inc[j])!=1 and any(a[j]!=0 for a in c['targets']) for j in range(N)):return None
 parts=[]
 for i,k in enumerate(lm):
  indices=[j for j in range(N) if inc[j]=={k}]
  if len(indices)!=len(em)+1:return None
  sd=copy.deepcopy(d);sd['loop_momenta']=['k1'];sd['propagators']=[dict(d['propagators'][j],momentum=re.sub(r'\b'+re.escape(k)+r'\b','k1',d['propagators'][j]['momentum'])) for j in indices];sd['physical_propagators']=sum(j<P for j in indices);sd['top_level_sectors']=[(1<<sd['physical_propagators'])-1];sd['rank']=len(indices);sd.pop('quadratic_momentum_vectors',None)
  ts=[list(a) for a in dict.fromkeys(tuple(t[j] for j in indices) for t in c['targets'])];cc=dict(c,id=c['id']+'_block'+str(i),definition=sd,targets=ts,size=len(ts))
  if not eligible(cc):return None
  parts.append(dict(indices=indices,case=cc))
 return parts

def run(c,method='integrated'):
 start=time.perf_counter();used=False
 if method!='previous' and eligible(c):
  tick=time.perf_counter();action,used=fast_choice(c,method);prediction=time.perf_counter()-tick
  r=reduce(c,action,deadline=time.perf_counter()+12)
  if r is not None:
   r.update(model_used=used,prediction_seconds=prediction)
   return dict(success=True,status='completed',application='tensor_reduction_factored',blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=r)],model_used=used,total_seconds=time.perf_counter()-start)
 parts=tensor_parts(c) if method!='previous' else None
 old=None if parts else previous()
 if parts or method!='previous' and len(c['definition']['loop_momenta'])>1:
  parts=parts or old.batch.support.split_blocks(c)
  if len(parts)>1:
   records=[];memo={}
   for part in parts:
    cc=part['case'];key=json.dumps([cc['definition'],cc['targets']],sort_keys=True)
    if key not in memo:memo[key]=run(cc,method)
    result=memo[key]
    if not result.get('success'):return dict(success=False,status='incomplete_block_reduction',blocks=records,failed_component=result,total_seconds=time.perf_counter()-start)
    assert len(result['blocks'])==1
    records.append(dict(indices=part['indices'],case=cc,result=result['blocks'][0]['result']))
   return dict(success=True,status='completed',application='tensor_reduction_factored',blocks=records,model_used=any(b['result'].get('model_used',False) or b['result'].get('batch_model_used',False) for b in records),total_seconds=time.perf_counter()-start,representation='Product of exact independent component reductions.')
 # Keep the preceding deployed ML policy for inputs outside the new identity.
 r=(old or previous()).run(c,'all_fixed' if method=='all_fixed' else 'integrated');r['total_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:
  assert Path(a.case).stat().st_size<2*1024**2
  r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 from s27_output_budget import output
 output(a.output,r)
