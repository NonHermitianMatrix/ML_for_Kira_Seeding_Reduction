"""Apply a frozen cost model before exact Kira equation generation."""
import argparse,json,math,struct,time
from s00_policy import *

def feature(c):
 ts=c['targets'];x=inputs.features(c)
 for sign in [-1,1]:
  x.extend([max([max(0,sign*(t[i] if sign<0 else t[i]-1)) for t in ts] or [0]) if i<len(ts[0]) else 0 for i in range(20)])
 x.append(max(sum(v<0 for v in t) for t in ts));return x

def predict(m,x):
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x];out=None
 for t in m['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  if out is None:out=[0.]*len(t['value'][i])
  for j,v in enumerate(t['value'][i]):out[j]+=v/len(m['trees'])
 return out

def choose(c,freeze,method):
 x=feature(c)
 physical=c['definition']['physical_propagators']
 top_targets=all(t[:physical]==[1]*physical and all(v<=0 for v in t[physical:]) for t in c['targets'])
 if not top_targets or inputs.signature(c)!=freeze['signature'] or len(c['targets'])>freeze['maximum_targets'] or x[6]>freeze['maximum_dots'] or not 2<=x[7]<=freeze['maximum_rank']:
  return None,dict(reason='outside_validated_domain',prediction_used=False)
 fixed=freeze['fixed_index'];j=fixed;scores=None
 if method=='learned' and freeze['enabled']:
  scores=predict(freeze['model'],x);candidate=min(range(len(scores)),key=scores.__getitem__)
  if scores[candidate]<scores[fixed]-freeze['margin']:j=candidate
 return freeze['candidates'][j],dict(index=j,scores=scores,prediction_used=scores is not None,reason='frozen_policy')

def reduce(c,basis,method='learned',reference=None):
 start=time.perf_counter();info=dict(prediction_used=False);theta=None
 sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/batch_policy'))
 from s16_deployment import normalize,validate
 c=normalize(c)
 validate(c,basis)
 if method=='previous':
  from s16_deployment import reduce as old_reduce
  r=old_reduce(c,basis,'learned',reference);r.update(method=method,complete_seconds=time.perf_counter()-start);return r
 # The baseline does not read model parameters or calculate model features.
 if method!='native':
  if method not in ['learned','fixed']:raise ValueError(method)
  matches=[]
  for p in sorted((HERE/'trained_model').glob('cost_*.json')):
   f=rt.read(p)
   if inputs.signature(c)==f['signature']:matches.append(f)
  if len(matches)==1:theta,info=choose(c,matches[0],method)
 decision=time.perf_counter()-start
 r=run(c,basis,theta,reference,timeout=90)
 r.update(method=method,selection=info,decision_seconds=decision,complete_seconds=time.perf_counter()-start)
 return r

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis',required=True);p.add_argument('--output',required=True);p.add_argument('--method',choices=['native','fixed','learned','previous'],default='learned');a=p.parse_args()
 c=rt.read(a.case);basis=rt.read(a.basis)
 # Match the public index and master-domain validation used by the current app.
 n=len(c['definition']['propagators'])
 if not 0<n<=31 or c['size']!=len(c['targets']) or not c['targets']:raise ValueError('Invalid target dimensions')
 for t in c['targets']+basis:
  if len(t)!=n or any(type(v) is not int for v in t):raise ValueError('Invalid integral index')
 r=reduce(c,basis,a.method);save(a.output,r);print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],selection=r.get('selection'))))
if __name__=='__main__':main()
