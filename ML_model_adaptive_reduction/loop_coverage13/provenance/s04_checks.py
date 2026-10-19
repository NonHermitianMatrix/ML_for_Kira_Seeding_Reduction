"""Independent Gamma evaluation and native IBP checks of the new exact identity."""
from s00_loop_common import *
from s01_bubble_tree import reduce,recognize
from s03_cases import tree_case
import sympy as sp

def gamma_reference(c):
 # Reconstruct the rooted integral from the declared physical momenta.
 # Evaluate complete Gamma expressions independently of finite-shift factor cancellation.
 d=sp.Symbol('d');s=sp.Symbol('s');t=recognize(c);assert t
 def full(a):
  powers={k:sp.Integer(a[t['one'][k]]) for k in t['order']};result=sp.Integer(1)
  for k in reversed(t['order'][1:]):
   u=powers[k];v=a[t['edge'][k]]
   result*=sp.gamma(u+v-d/2)*sp.gamma(d/2-u)*sp.gamma(d/2-v)/(sp.gamma(u)*sp.gamma(v)*sp.gamma(d-u-v))
   powers[t['parent'][k]]+=u+v-d/2
  a0=powers[t['order'][0]];b=a[t['middle']];c0=a[t['last']]
  result*=sp.gamma(a0+b+c0-d/2)*sp.gamma(d/2-a0-b)*sp.gamma(d/2-b-c0)/(sp.gamma(a0)*sp.gamma(c0)*sp.gamma(d-a0-b-c0))
  return result
 P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))];base=full(master);rows={}
 for a in c['targets']:
  ratio=full(a)/base;ratio=sp.combsimp(ratio);ratio=sp.cancel(sp.expand_func(ratio))*sp.sympify(t['scale'])**(sum(master)-sum(a))
  assert not ratio.has(sp.gamma),str(ratio)
  rows[label(a)]={label(master):str(ratio)}
 return dict(success=True,status='completed',masters=[master],coefficients=rows)

def native(c):
 old=prior();h=old.legacy().h
 with h.rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  return h.rt.compact(h.rt.native.run(c,c['size'],'native',HERE/'unused',timeout=45,margin=0,archive=False,records=False,basis=None,check_masters=False,scratch_cap=32*1024**2,bounds=h.inputs.bounds(c,'expanded'),ordering=2,threads=1))

def check_native(c,r):
 f=reduce(c);P=c['definition']['physical_propagators'];a=[int(i<P) for i in range(len(c['definition']['propagators']))];basis=label(a)
 if not r['success'] or basis not in r.get('coefficients',{}):return False,0
 n=0
 for target,row in f['coefficients'].items():
  scalar=sp.sympify(row[basis]);ref=r['coefficients'].get(target)
  if ref is None:return False,n
  for m in set(ref)|set(r['coefficients'][basis]):
   if sp.cancel(sp.sympify(ref.get(m,'0'))-scalar*sp.sympify(r['coefficients'][basis].get(m,'0')))!=0:return False,n
   n+=1
 return True,n

def main():
 rows=[]
 for L,shape,symbolic in [(1,'star',False),(2,'star',False),(2,'chain',True),(3,'star',False),(3,'chain',False),(3,'branched',False)]:
  c=tree_case(L,shape,3101,symbolic);start=time.perf_counter();f=reduce(c);g=gamma_reference(c)
  h=prior().legacy().h;ok,n=h.equal(f['coefficients'],g['coefficients']);assert ok
  r=native(c);verified,count=check_native(c,r)
  row=dict(case=c,finite_shift_gamma_equal=ok,gamma_checks=n,native=r,native_verified=verified,native_checks=count,seconds=time.perf_counter()-start)
  write(HERE/'development'/(c['id']+'.json.gz'),row);rows.append({k:v for k,v in row.items() if k not in ['case','native']}|dict(case=c['id'],native_status=r.get('status')));print(json.dumps(rows[-1]),flush=True)
 guards=[];c=tree_case(3,'chain')
 for name in ['mass','off_shell','auxiliary_numerator','cut','symbolic_index','zero_end','cycle']:
  x=copy.deepcopy(c)
  if name=='mass':x['definition']['propagators'][0]['mass_squared']='m2'
  elif name=='off_shell':x['definition']['scalarproduct_rules'][0][1]='1'
  elif name=='auxiliary_numerator':x['targets'][0][-1]=-1
  elif name=='cut':x['definition']['cut_propagators']=[1]
  elif name=='symbolic_index':x['definition']['symbolic_ibp']=True
  elif name=='zero_end':x['targets'][0][0]=0
  elif name=='cycle':x['definition']['propagators'][4]['momentum']='k2-k3'
  ok=reduce(x) is None;assert ok,name;guards.append(dict(name=name,rejected=ok))
 write(HERE/'development_checks.json',dict(complete=True,rows=rows,guards=guards,all_gamma_exact=True,native_passes=sum(r['native_verified'] for r in rows)))
if __name__=='__main__':main()
