"""Exact Kira execution with an optional learned seed-bound decision and no other ML."""
import contextlib,gzip,json,math,os,resource,sys,time
from pathlib import Path
from s00_inputs import HERE,ROOT,ACTIONS,bounds,features,sha,truncation,signature
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction'))
import s23_parametric_runner as native
BINARY=ROOT/'.tools/kira-parametric/kira'
def cpu():return sum(resource.getrusage(k).ru_utime+resource.getrusage(k).ru_stime for k in [resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN])
def read(p):
 raw=Path(p).read_bytes();return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=gzip.compress(json.dumps(d,separators=(',',':')).encode(),mtime=0)
 assert len(raw)<2*1024**2
 used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file());assert used+len(raw)<24*1024**2
 q=p.with_suffix('.writing');q.write_bytes(raw);q.replace(p)
def compact(d):return {k:v for k,v in d.items() if k not in ['log','input','raw_export','choices','predictions','equation_records']}|dict(log_tail=d.get('log','')[-1800:])
@contextlib.contextmanager
def environment():
 saved={k:v for k,v in os.environ.items() if k.startswith('KIRA_')}
 for k in saved:os.environ.pop(k,None)
 os.environ.update(KIRA_RUNTIME_SCRATCH='node',KIRA_RUNTIME_BINARY=str(BINARY),KIRA_EPHEMERAL_DB='1',KIRA_RESTRICT_SECTOR_INIT='1',KIRA_PROJECT_ZERO_CRITERION='1',KIRA_PROJECT_PARAMETRIC='1',KIRA_REUSE_SELECTED_EQUATIONS='1',KIRA_INDEX_SECTOR_FILES='1',KIRA_EQ_MODE='off',KIRA_EQ_COLLECT='0',KIRA_PARALLEL_EVAL='1',KIRA_FAST_EVAL='1',KIRA_SPARSE_FEATURES='1',KIRA_ROW_PAIR_FASTPATH='1')
 try:yield
 finally:
  for k in list(os.environ):
   if k.startswith('KIRA_'):os.environ.pop(k,None)
  os.environ.update(saved)
def attempt(c,basis=None,action='native',custom=None,timeout=90):
 with environment():
  r=native.run(c,c['size'],'native',HERE/'unused',timeout=timeout,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=custom or bounds(c,action),ordering=1,threads=1,truncate=truncation(c,action))
 assert r.get('equation_mode','off')=='off' and not r.get('weights_sha256') and not r.get('model')
 r['learned_algebra_disabled']=True;return r

def verify(r,reference):
 start=time.perf_counter();want=read(reference)['coefficients'];got=r.get('coefficients',{});bad=[];checks=0
 if set(got)!=set(want):bad.append('targets')
 for t,row in got.items():
  for m in set(row)|set(want.get(t,{})):
   a,b=row.get(m,'0'),want.get(t,{}).get(m,'0');checks+=1
   if a!=b:
    import sympy as sp
    if sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))!=0:bad.append([t,m])
 r.update(reference_checked=not bad,mismatches=bad,coefficient_checks=checks,verification_seconds=time.perf_counter()-start)
 r['success']=r['success'] and not bad

def predict(model,x):
 if model['kind']=='mlp':
  v=[(a-b)/s for a,b,s in zip(x,model['mean'],model['scale'])]
  for k,(w,b) in enumerate(zip(model['weights'],model['bias'])):
   v=[b[j]+sum(v[i]*w[i][j] for i in range(len(v))) for j in range(len(b))]
   if k<len(model['weights'])-1:v=[max(0.,a) if model['activation']=='relu' else math.tanh(a) for a in v]
  return v
 # Match scikit-learn's float32 input conversion at split thresholds.
 import struct
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x]
 scores=[0.]*len(ACTIONS)
 for t in model['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  for j,v in enumerate(t['value'][i]):scores[j]+=v/len(model['trees'])
 return scores

def choose(c,freeze):
 x=features(c)
 if 'domain' in freeze:
  matches=[g for g,v in freeze['domain'].items() if signature(c) in v['signatures']]
  if len(matches)!=1:return 'native',None
  g=matches[0];v=freeze['domain'][g]
  checked=freeze.get('bounded_features',range(len(x)))
  if any(x[i]<v['minimum'][i]-1e-9 or x[i]>v['maximum'][i]+1e-9 for i in checked):return 'native',None
 else:g=c['topology_group']
 scores=predict(freeze['model'],x);base=freeze['fixed_by_graph'].get(g,freeze['fixed_global']);i=min(range(len(ACTIONS)),key=scores.__getitem__)
 return (ACTIONS[i] if scores[i]<scores[ACTIONS.index(base)]-freeze['gate'] else base),scores

def run(c,basis,method='native',reference=None,freeze_path=None,first=None,timeout=90):
 start=time.perf_counter();cpu0=cpu();decision=0.;loaded=0.;scores=None
 d=c['definition'];n=len(d['propagators']);tops=d['top_level_sectors']
 if not(0<n<=31) or d.get('cut_propagators') or d.get('symbolic_ibp'):raise ValueError('Unsupported family definition')
 if not isinstance(basis,list) or c['size']!=len(c['targets']) or c['size']==0:raise ValueError('Invalid target or basis list')
 if not tops or any(type(s) is not int or not 0<s<2**n for s in tops):raise ValueError('Invalid top sector')
 for a in c['targets']+basis:
  if len(a)!=n or any(type(v) is not int for v in a):raise ValueError('Invalid integral index vector')
  sector=sum(1<<i for i,v in enumerate(a) if v>0)
  if not any(sector&top==sector for top in tops):raise ValueError('Integral lies outside declared top sectors')
 if method=='learned':
  tick=time.perf_counter();f=read(freeze_path or HERE/'trained_model/freeze.json');loaded=time.perf_counter()-tick
  tick=time.perf_counter();first,scores=choose(c,f);decision=time.perf_counter()-tick
 elif method=='fixed':
  # The fixed configuration contains action names only, with no model weights.
  cfg=read(freeze_path or HERE/'trained_model/fixed.json');first=cfg['fixed_by_graph'].get(c['topology_group'],cfg['fixed_global'])
 elif first is None:first='native'
 assert first in ACTIONS
 attempts=[];seen=set()
 for action in dict.fromkeys([first,'native','expanded']):
  b=bounds(c,action)
  key=(tuple(b),truncation(c,action))
  if key in seen:continue
  seen.add(key);r=attempt(c,basis,action,timeout=timeout);r['action']=action;attempts.append(compact(r))
  if r['success']:break
 result=dict(case=c['id'],method=method,first_action=first,attempts=attempts,success=r['success'],coefficients=r.get('coefficients',{}),fallbacks=len(attempts)-1,decision_seconds=decision,model_loading_seconds=loaded,scores=scores,reference_coefficients_supplied=False,no_other_ml=True)
 if reference:verify(result,reference)
 result.update(complete_seconds=time.perf_counter()-start,cpu_seconds=cpu()-cpu0)
 return result

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis',required=True);p.add_argument('--output',required=True);p.add_argument('--method',choices=['native','fixed','learned'],default='learned');args=p.parse_args()
 start=time.perf_counter();c=read(args.case);basis=read(args.basis);r=run(c,basis,args.method);save(args.output,r)
 print(json.dumps(dict(success=r['success'],seconds=time.perf_counter()-start,action=r['first_action'])))
if __name__=='__main__':main()
