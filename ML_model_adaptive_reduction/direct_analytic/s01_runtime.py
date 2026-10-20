"""Direct analytic evaluation followed by guarded learned native choices."""
from s00_direct_common import *

def attach_tadpole_values(r):
 if not r.get('success'):return r
 for block in r.get('blocks',[]):
  result=block['result'];d=block['case']['definition']
  if len(d['loop_momenta'])!=1 or d.get('cut_propagators') or d.get('symbolic_ibp'):continue
  values=result.setdefault('master_values',{});ps=d['propagators']
  for a in result.get('masters',[]):
   if sum(a)==1 and a.count(1)==1 and all(v in [0,1] for v in a):
    prop=ps[a.index(1)]
    try:v=current().vector(prop['momentum'],d['loop_momenta']+d['external_momenta'])
    except (ValueError,TypeError,SyntaxError,KeyError,IndexError):continue
    if abs(v[0])!=1:continue
    mass=prop['mass_squared'];values.setdefault(label(a),dict(formula='0' if mass=='0' else '-Gamma(1-d/2)*(mass_squared-i0)^(d/2-1)',mass_squared=mass))
  result['analytic_evaluation_complete']=all(label(a) in values for a in result.get('masters',[]))
 return r

def run(c,method='integrated'):
 start=time.perf_counter()
 if method=='previous':return current().run(c,'integrated')
 # New exact rules have structural admission tests and bounded work.
 from s05_vacuum import decompose,scaleless
 zero=scaleless(c)
 if zero is not None:return dict(success=True,status='completed',blocks=[dict(case=c,indices=list(range(len(c['definition']['propagators']))),result=zero)],model_used=False,total_seconds=time.perf_counter()-start)
 r=decompose(c)
 if r is not None:r['total_seconds']=time.perf_counter()-start;return r
 d=c['definition']
 # Load only the exact dependency chain for a supported connected tree.
 if not d['external_momenta']:
  path=ROOT/'ML_model_adaptive_reduction/vacuum_learning';sys.path.insert(0,str(path));rule=load('direct_tree',path/'s01_vacuum.py');sys.path.insert(0,str(HERE));r=rule.reduce(c)
  if r is not None:
   t=rule.recognize(c);master=r['masters'][0];num,den=rule.Reducer(master,t).arguments(master);mass=str(t['scale'])[1:];L=len(d['loop_momenta']);P=d['physical_propagators']
   r['master_values']={label(master):dict(sign=(-1)**P,mass_squared=mass,mass_exponent=[-P,L],gamma_numerator=num,gamma_denominator=den,argument_convention='Each pair [a,b] denotes a+b*d/2.',formula='sign*(mass_squared-i0)^(L*d/2-P)*product(Gamma(numerator))/product(Gamma(denominator))')}
   return dict(success=True,status='completed',blocks=[dict(case=c,indices=list(range(len(d['propagators']))),result=r)],model_used=False,total_seconds=time.perf_counter()-start)
 old=current()
 if method in ['dense','wide']:
  h=helper();original=h.rt.native.run
  def native(*args,**kwargs):
   # Dense uses all seeds in the same finite region as the sparse attempt.
   saved=os.environ.pop('KIRA_ML_SEEDS',None)
   try:
    result=original(*args,**kwargs);result['complete_seed_region']=True;return result
   finally:
    if saved is not None:os.environ['KIRA_ML_SEEDS']=saved
  if method=='dense':h.rt.native.run=native
  try:r=old.run(c,'sparse_wide' if method=='wide' else 'sparse_tight')
  finally:h.rt.native.run=original
  for block in r.get('blocks',[]):
   for attempt in block['result'].get('attempts',[]):
    if attempt.get('complete_seed_region'):attempt['seed_policy']=None
  r.update(selected_action=method,total_seconds=time.perf_counter()-start);return r
 if method.startswith('order'):
  order=int(method[5:]);h=helper();original=h.rt.native.run
  def native(*args,**kwargs):kwargs['ordering']=order;return original(*args,**kwargs)
  h.rt.native.run=native
  try:r=old.run(c,'sparse_tight')
  finally:h.rt.native.run=original
  r.update(selected_action=method,selected_order=order,total_seconds=time.perf_counter()-start);return r
 # Apply the new policy only to its native two-loop training domain.
 if len(d['loop_momenta'])==2 and len(d['propagators'])==9 and old.previous().previous().batch.eligible(c) and (HERE/'trained_model/policy.json').exists():
  tick=time.perf_counter();m=read(HERE/'trained_model/policy.json');actions=m['actions'];k=actions.index(m['fixed']);j=k;scores=None;info=dict(reason='fixed')
  if method!='fixed' and m['enabled']:
   x=old.features(c)
   def predict(t):
    while 'feature' in t:t=t['left'] if x[t['feature']]<=t['cut'] else t['right']
    return t['cost']
   scores=[statistics.mean(predict(t)[a] for t in m['trees']) for a in range(len(actions))];j=min(range(len(actions)),key=scores.__getitem__)
   if scores[j]+.002>=scores[k]*(1-m['margin']):j=k
   from s11_failure_guard import gate
   j,info=gate(m,x,j,k)
  prediction=time.perf_counter()-tick;r=run(c,actions[j]);r.update(model_used=scores is not None,selection_scores=scores,failure_gate=info,prediction_seconds=prediction,total_seconds=time.perf_counter()-start);return r
 r=attach_tadpole_values(old.run(c,'all_fixed' if method=='fixed' else 'integrated'));r['total_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r)
