"""Independent Gamma values, protected-master native checks, and rejection checks."""
from s00_vac_common import *
from s01_vacuum import reduce,recognize
from s04_cases import vacuum_case
import mpmath as mp,sympy as sp

def gamma_check(c,r):
 t=recognize(c);assert t is not None
 P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
 def value(a,d):
  shift={k:mp.mpf(0) for k in t['order']};ans=mp.mpf(1)
  for k in reversed(t['order'][1:]):
   u=a[t['one'][k]]+shift[k];v=a[t['edge'][k]]
   ans*=mp.gamma(u+v-d/2)*mp.gamma(d/2-u)*mp.gamma(d/2-v)/(mp.gamma(u)*mp.gamma(v)*mp.gamma(d-u-v))
   shift[t['parent'][k]]+=u+v-d/2
  root=t['order'][0];sig=shift[root];power=a[t['one'][root]]
  return ans*mp.gamma(d/2-sig)*mp.gamma(sig+power-d/2)/(mp.gamma(d/2)*mp.gamma(power))
 count=0;largest=mp.mpf(0);dd,mm=sp.symbols('d m2')
 with mp.workdps(80):
  for a in c['targets']:
   coef=next(iter(r['coefficients'][tree.label(a)].values()));f=sp.lambdify((dd,mm),sp.sympify(coef),modules='mpmath')
   for num,den in [(137,101),(151,103),(163,107)]:
    d=mp.mpf(num)/den;m2=mp.mpf(11)/7 if t['scale']=='-m2' else -mp.mpf(t['scale'])
    delta=sum(a)-P;ref=value(a,d)/value(master,d)*(-m2)**(-delta);got=f(d,m2)
    err=abs(got-ref)/max(mp.mpf(1),abs(ref));largest=max(largest,err);assert err<mp.mpf('1e-60'),(c['id'],a,str(err));count+=1
 return dict(passed=True,checks=count,precision_digits=80,scaled_tolerance='1e-60',maximum_scaled_error=str(largest))

def native_check(c):
 h=batch.legacy().h;P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
 with h.rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  r=h.rt.compact(h.rt.native.run(c,c['size'],'native',HERE/'unused',timeout=35,margin=0,archive=False,records=False,basis=[master],check_masters=True,scratch_cap=32*1024**2,bounds=h.inputs.bounds(c,'expanded'),ordering=2,threads=1))
 n=0
 if r.get('success'):
  expected=reduce(c)
  ok,n=h.equal(r['coefficients'],expected['coefficients']);assert ok,(c['id'],r)
 return dict(case=c['id'],success=r.get('success'),status=r.get('status'),checks=n,result=r)

def main():
 rows=[]
 for L in [1,2,3,6,13]:
  for shape in ['star','chain','branched']:
   c=vacuum_case(L,shape,6001);rows.append(dict(case=c['id'],gamma=gamma_check(c,reduce(c))))
   if L>2:
    t=recognize(c);internal=set(t['parent'].values())-{None,t['order'][0]};cc=copy.deepcopy(c);cc['targets']=[]
    for k in internal:
     for power in [0,-1]:
      a=c['targets'][0].copy();a[t['one'][k]]=power;cc['targets'].append(a)
    if cc['targets']:rows.append(dict(case=c['id']+'_internal',gamma=gamma_check(cc,reduce(cc))))
 ns=[]
 for L,shape in [(1,'star'),(2,'star'),(3,'chain')]:
  c=vacuum_case(L,shape,6007,symbolic=False);c['targets']=c['targets'][:3];c['size']=len(c['targets']);ns.append(native_check(c))
 base=vacuum_case(3,'chain',6001);rejects=[]
 for name in ['second_mass','cut','symbolic_index','aux_numerator','zero_root','zero_leaf','zero_edge','zero_mass','cycle','external']:
  c=copy.deepcopy(base)
  if name=='second_mass':c['definition']['propagators'][1]['mass_squared']='1'
  elif name=='cut':c['definition']['cut_propagators']=[1]
  elif name=='symbolic_index':c['definition']['symbolic_ibp']=[1]
  elif name=='aux_numerator':c['targets'][0][-1]=-1
  elif name=='zero_root':c['targets'][0][0]=0
  elif name=='zero_leaf':c['targets'][0][3]=0
  elif name=='zero_edge':c['targets'][0][2]=0
  elif name=='zero_mass':c['definition']['propagators'][0]['mass_squared']='0'
  elif name=='cycle':c['definition']['propagators'][4]['momentum']='k2-k1'
  else:c['definition']['external_momenta']=['p']
  assert reduce(c) is None,name;rejects.append(name)
 # Check names, loop signs, physical order, and independent products before reserved tests.
 transforms=[]
 for L,shape in [(3,'chain'),(6,'branched'),(13,'star')]:
  c=vacuum_case(L,shape,6009);cc=copy.deepcopy(c);names=cc['definition']['loop_momenta'];mapping={n:'q'+str(i+1) for i,n in enumerate(names)}
  import re
  cc['definition']['loop_momenta']=[mapping[n] for n in names]
  for prop in cc['definition']['propagators']:
   prop['momentum']='-('+re.sub(r'\bk\d+\b',lambda m:mapping[m.group()],prop['momentum'])+')'
  assert reduce(cc)['coefficients']==reduce(c)['coefficients'];transforms.append(dict(loops=L,kind='rename_and_global_sign',passed=True))
  P=c['definition']['physical_propagators'];order=list(reversed(range(P)))+list(range(P,len(c['targets'][0])));cc=copy.deepcopy(c)
  cc['definition']['propagators']=[c['definition']['propagators'][i] for i in order];cc['targets']=[[a[i] for i in order] for a in c['targets']]
  new=reduce(cc);old=reduce(c)
  for a,b in zip(c['targets'],cc['targets']):assert next(iter(old['coefficients'][tree.label(a)].values()))==next(iter(new['coefficients'][tree.label(b)].values()))
  transforms.append(dict(loops=L,kind='physical_order',passed=True))
 products=[];h=batch.legacy().h;families=h.inputs.module('vac_product_families',h.BLOCK/'s01_families.py')
 run=load('vacuum_checked_application',HERE/'s03_runtime.py').run
 for parts in [[2,2],[3,3,2],[3,3,3,2,2]]:
  blocks=[vacuum_case(L,'chain',6009+i,symbolic=False) for i,L in enumerate(parts)]
  c=families.compose(blocks,'vacuum_product_L'+str(sum(parts)),'development');reference=dict(success=True,blocks=[])
  for part in batch.support.split_blocks(c):reference['blocks'].append(dict(case=part['case'],indices=part['indices'],result=reduce(part['case'])))
  ans=run(c);ok,n=h.compare(ans,reference);assert ok,(c['id'],ans)
  products.append(dict(case=c['id'],loops=sum(parts),coefficient_checks=n,success=True,result=ans))
 write(HERE/'development.json',dict(complete=True,gamma=rows,native=ns,rejections=rejects,transformations=transforms,products=products))
 print(json.dumps(dict(gamma_checks=sum(x['gamma']['checks'] for x in rows),native_checks=sum(x['checks'] for x in ns),native_statuses=[x['status'] for x in ns],rejections=len(rejects))),flush=True)
if __name__=='__main__':main()
