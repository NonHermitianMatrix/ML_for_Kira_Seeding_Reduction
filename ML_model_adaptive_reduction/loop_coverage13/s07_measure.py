"""Bounded fresh-process comparisons and independent connected-integral checks."""
from s00_loop_common import *
import subprocess,signal,statistics

def measured(c,method,rep,phase):
 path=HERE/phase/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
 if path.exists():return read(path)
 request=HERE/'requests'/(c['id']+'_'+method+'.json');output=request.with_suffix('.pending.gz');write(request,c)
 start=time.perf_counter();p=subprocess.Popen([sys.executable,str(HERE/'s02_runtime.py'),'--case',str(request),'--output',str(output),'--method',method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=p.communicate(timeout=20);r=read(output) if output.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-700:]
 except subprocess.TimeoutExpired:
  h=prior().legacy().h;helper=h.inputs.module('coverage_process_limits',h.BLOCK/'s11_extension_test.py')
  for pid in helper.descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
 r.update(case=c['id'],method=method,rep=rep,application_seconds=time.perf_counter()-start)
 for b in r.get('blocks',[]):
  for a in b['result'].get('attempts',[]):a.pop('log_tail',None)
 write(path,r);return r

def gamma_checks(c,r):
 import mpmath as mp
 import sympy as sp
 from s01_bubble_tree import recognize,label
 mp.mp.dps=80;t=recognize(c);P=c['definition']['physical_propagators'];a0=[int(i<P) for i in range(len(c['definition']['propagators']))]
 def full(a,d):
  powers={k:mp.mpf(a[t['one'][k]]) for k in t['order']};v=mp.mpf(1)
  for k in reversed(t['order'][1:]):
   u=powers[k];b=a[t['edge'][k]]
   v*=mp.gamma(u+b-d/2)*mp.gamma(d/2-u)*mp.gamma(d/2-b)/(mp.gamma(u)*mp.gamma(b)*mp.gamma(d-u-b))
   powers[t['parent'][k]]+=u+b-d/2
  u=powers[t['order'][0]];b=a[t['middle']];w=a[t['last']]
  return v*mp.gamma(u+b+w-d/2)*mp.gamma(d/2-u-b)*mp.gamma(d/2-b-w)/(mp.gamma(u)*mp.gamma(w)*mp.gamma(d-u-b-w))
 if not r['success']:return dict(passed=False,checks=0)
 rows=r['blocks'][0]['result']['coefficients'];n=0;worst=mp.mpf(0)
 for a in c['targets']:
  expr=sp.sympify(rows[label(a)][label(a0)]);fn=sp.lambdify([sp.Symbol('d'),sp.Symbol('s')],expr,'mpmath',cse=False)
  for num,den in [(137,101),(151,103),(163,107)]:
   d=mp.mpf(num)/den;scale=mp.mpf(-7) if t['scale']=='s' else mp.mpf(t['scale'])
   ref=full(a,d)/full(a0,d)*scale**(sum(a0)-sum(a));value=fn(d,scale)
   error=abs(value-ref)/max(abs(ref),mp.mpf('1e-100'));worst=max(worst,error);assert error<mp.mpf('1e-60'),(c['id'],a,str(error));n+=1
 return dict(passed=True,checks=n,maximum_relative_error=str(worst),precision_digits=80,tolerance='1e-60')

def main(worker):
 protocol=read(HERE/'protocol.json.gz');assert protocol['complete']
 assert all(sha(HERE/k)==v for k,v in protocol['source_sha256'].items())
 assert sha(PRIOR/'trained_model/policy.json')==protocol['prior_model_sha256']
 h=prior().legacy().h
 for group in ['trees','batches','grid']:
  for i,c in enumerate(protocol[group]):
   if i%2!=worker:continue
   dest=HERE/'outcomes'/(group+'_'+c['id']+'.json.gz')
   if dest.exists():continue
   first={};results={m:[] for m in (['integrated','previous','all_fixed'] if group=='batches' else ['integrated','previous'])};checks={}
   repetitions=1 if group=='grid' else 3
   for rep in range(repetitions):
    order=list(results);shift=(i+rep)%len(order);order=order[shift:]+order[:shift]
    for method in order:
     if rep and not first[method]['success']:continue
     r=measured(c,method,rep,group);results[method].append(r['application_seconds'])
     if not rep:first[method]=r
   if group=='trees':
    checks=gamma_checks(c,first['integrated']);paired=False;count=0
    if first['previous']['success'] and len(first['previous'].get('blocks',[]))==1:
     checker=h.inputs.module('loop_native_checker',HERE/'s04_checks.py');check_native=checker.check_native
     paired,count=check_native(c,first['previous']['blocks'][0]['result'])
   else:paired,count=h.compare(first['integrated'],first['previous']) if all(r['success'] for r in first.values()) else (False,0)
   fixed_ok,fixed_n=h.compare(first['integrated'],first['all_fixed']) if group=='batches' and all(r['success'] for r in first.values()) else (False,0)
   row=dict(case=c['id'],group=group,scope=c.get('scope'),shape=c.get('shape'),loops=len(c['definition']['loop_momenta']),kinematics=c.get('kinematics','rational'),targets=c['size'],indices=len(c['definition']['propagators']),checks=checks,paired_verified=paired,coefficient_checks=count,fixed_verified=fixed_ok,fixed_checks=fixed_n,methods={m:dict(success=r['success'],status=r.get('status','not_recorded'),times=results[m],median_seconds=statistics.median(results[m]),block_statuses=[b['result'].get('status','not_recorded') for b in r.get('blocks',[])],routes=[b['result'].get('route') for b in r.get('blocks',[])]) for m,r in first.items()})
   write(dest,row);print(json.dumps(dict(group=group,case=c['id'],paired=paired,success={m:r['success'] for m,r in first.items()},gamma=checks.get('passed'))),flush=True)
 write(HERE/f'worker_{worker}_complete.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
