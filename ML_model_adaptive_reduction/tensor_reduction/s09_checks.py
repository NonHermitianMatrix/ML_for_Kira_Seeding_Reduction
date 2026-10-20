"""Check coordinate changes, domain rejection, and exact IBP residuals."""
from s00_tensor_common import *
from s01_tensor import reduce,eligible,vector
from s03_cases import case
from fractions import Fraction as Q
import sympy as sp

def main():
 h=previous().batch.legacy().h;transforms=[];rejections=[];residual_checks=0
 for P,e in [(2,1),(2,2),(3,1),(4,1)]:
  c=case(P,e,7021+P+e,rank=2,dots=1,count=2,seed=43);r=reduce(c);assert r
  cc=copy.deepcopy(c);cc['definition']['loop_momenta']=['qloop']
  for p in cc['definition']['propagators']:p['momentum']=p['momentum'].replace('k1','qloop')
  assert h.equal(r['coefficients'],reduce(cc)['coefficients'])[0]
  cc=copy.deepcopy(c)
  for p in cc['definition']['propagators']:p['momentum']=p['momentum'].replace('k1','-k1')
  assert h.equal(r['coefficients'],reduce(cc)['coefficients'])[0]
  order=list(reversed(range(P)))+list(range(P,P+e));cc=copy.deepcopy(c);cc['definition']['propagators']=[c['definition']['propagators'][j] for j in order];cc['targets']=[[a[j] for j in order] for a in c['targets']]
  rr=reduce(cc);assert rr
  perm={label([a[j] for j in order]):{label([tuple(map(int,m.split(',')))[j] for j in order]):v for m,v in r['coefficients'][label(a)].items()} for a in c['targets']}
  assert h.equal(rr['coefficients'],perm)[0];transforms.append(dict(physical=P,coordinates=P+e,checks=['loop_name','loop_sign','physical_permutation']))
 # All signed IBP rows at two seeds. This also checks the numerator terms in
 # the power-first recurrence against the separately implemented derivative.
 for P,e in [(2,1),(3,1)]:
  c=case(P,e,7039+P,rank=2,dots=1,count=1);a=c['targets'][0];d=c['definition'];names=d['loop_momenta']+d['external_momenta'];n=len(a);rules={tuple(sorted(pair)):sp.Rational(v) for pair,v in d['scalarproduct_rules']};q=[[-v for v in vector(p['momentum'],names)[1:]] for p in d['propagators']];m=[sp.Rational(p['mass_squared']) for p in d['propagators']]
  def dot(x,y):return sum(x[i]*y[j]*rules[tuple(sorted([names[i+1],names[j+1]]))] for i in range(n-1) for j in range(n-1))
  Y=[[m[i]+m[j]-dot([x-y for x,y in zip(q[i],q[j])],[x-y for x,y in zip(q[i],q[j])]) for j in range(n)] for i in range(n)];D=sp.Symbol('d');terms=[]
  for i in range(n):
   row=[(tuple(a),D-sum(a))]
   for j,v in enumerate(a):
    if not v:continue
    b=a.copy();b[j]+=1;b[i]-=1;row.append((tuple(b),-v))
    b=a.copy();b[j]+=1;row.append((tuple(b),-v*Y[i][j]))
   terms.append(row)
  cc=copy.deepcopy(c);cc['targets']=[list(a) for a in dict.fromkeys(a for row in terms for a,v in row if v)];rr=reduce(cc,'tensor_largest');assert rr
  for row in terms:
   coefficients={}
   for a,v in row:
    if not v:continue
    for key,x in rr['coefficients'][label(a)].items():coefficients[key]=coefficients.get(key,0)+v*sp.sympify(x)
   for v in coefficients.values():assert sp.cancel(v)==0;residual_checks+=1
 base=case(3,1,7043,rank=1,dots=1)
 for name in ['cut','symbolic_indices','symbolic_mass','singular_gram','rank_limit','missing_invariant']:
  c=copy.deepcopy(base)
  if name=='cut':c['definition']['cut_propagators']=[1]
  elif name=='symbolic_indices':c['definition']['symbolic_ibp']=[1]
  elif name=='symbolic_mass':c['definition']['propagators'][0]['mass_squared']='m2'
  elif name=='singular_gram':
   for rule in c['definition']['scalarproduct_rules']:rule[1]='0'
  elif name=='rank_limit':c['targets'][0][-1]=-7
  else:c['definition']['scalarproduct_rules']=[]
  assert reduce(c) is None,name;rejections.append(name)
 # Rational masses and a nonzero shift of the reference denominator.
 c=case(2,1,7051,rank=2,dots=1);cc=copy.deepcopy(c)
 for i,p in enumerate(cc['definition']['propagators']):
  if i<2:p['mass_squared']=str(Q(p['mass_squared'])/3)
  p['momentum']=p['momentum']+'+p2'
 outputs=[reduce(cc,a) for a in ACTIONS];assert all(outputs)
 assert all(h.equal(outputs[0]['coefficients'],r['coefficients'])[0] for r in outputs[1:])
 write(HERE/'development_checks.json',dict(complete=True,transformations=transforms,ibp_residual_coefficients=residual_checks,rejections=rejections,rational_mass_and_shift=True,native_pilot_sha256=sha(HERE/'pilot.json')))
 print(json.dumps(dict(checks_complete=True,ibp_residual_coefficients=residual_checks)),flush=True)
if __name__=='__main__':main()
