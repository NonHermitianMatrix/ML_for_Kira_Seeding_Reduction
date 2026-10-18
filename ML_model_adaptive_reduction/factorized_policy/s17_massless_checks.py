"""Check the massless numerator formula with gamma ratios and native Kira."""
from s00_common import *
from s01_families import gen
from s04_checks import reference
import s16_massless_tensor as tensor
EXT=HERE/'extension'

def cases():
 out=[]
 for L in range(2,14):
  c=canonical(gen.case('propagator_massless',L,False,1801+6*L));P=c['definition']['physical_propagators'];N=len(c['definition']['propagators']);ts=[]
  for j in [0,P-1]:
   a=[int(i<P) for i in range(N)];a[j]+=1;ts.append(a.copy());a[P]=-1;ts.append(a)
  # Include an auxiliary with an external momentum when one is available.
  ext=next((j for j in range(P,N) if 'p1' in c['definition']['propagators'][j]['momentum']),None)
  if ext is not None:
   a=[int(i<P) for i in range(N)];a[0]+=1;a[ext]=-1;ts.append(a)
  c.update(targets=ts,size=len(ts),scope='analytic_massless',split='reserved',shape='scalar_and_quadratic_numerator');out.append(c)
 return out

def main(native=True):
 rows=[];folder=EXT/('massless_formula_checks' if native else 'massless_formula_audit')
 for c in cases():
  f=folder/(c['id']+'.json.gz')
  if f.exists():rows.append(READ(f));continue
  a=tensor.reduce(c);b=tensor.reduce(c,reference=True);assert a is not None and b is not None
  ok,n=equal(a['coefficients'],b['coefficients']);assert ok,(c['id'],a,b)
  ref=None;native_ok=None;checks=0
  if native and len(c['definition']['loop_momenta'])<=4:
   ref=reference(c,force_native=True)
   if ref['success']:native_ok,checks=equal(a['coefficients'],ref['blocks'][0]['result']['coefficients']);assert native_ok,(c['id'],a,ref)
  r=dict(case=c,formula=a,gamma=b,gamma_checks=n,native=ref,native_equal=native_ok,native_checks=checks);write(f,r);rows.append(r);print(json.dumps(dict(case=c['id'],gamma=ok,native=native_ok)),flush=True)
 saved=[]
 if not native:
  for c in READ(HERE/'protocol.json')['cases']:
   if c.get('topology_group','').startswith('propagator_massless_L') and len(c['definition']['loop_momenta']) in [2,4]:
    f=HERE/'references'/(c['id']+'.json.gz')
    if not f.exists():continue
    ref=READ(f)
    if not ref['success']:continue
    a=tensor.reduce(c);assert a is not None;ok,n=equal(a['coefficients'],ref['blocks'][0]['result']['coefficients']);assert ok,(c['id'],a,ref);saved.append(dict(case=c['id'],checks=n))
 write(folder/'summary.json',dict(complete=True,requests=len(rows),gamma_checks=sum(r['gamma_checks'] for r in rows),native_checks=sum(r['native_checks'] for r in rows),native_verified=sum(r['native_equal'] is True for r in rows),native_unavailable=sum(r['native'] is not None and not r['native']['success'] for r in rows),saved_native=saved))

if __name__=='__main__':main(native='--algebra-only' not in sys.argv)
