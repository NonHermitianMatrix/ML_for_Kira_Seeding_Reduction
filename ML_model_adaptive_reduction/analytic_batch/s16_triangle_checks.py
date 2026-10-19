"""Check the analytic recognizer against native references and equivalent routings."""
from s00_batch_common import *
from s01_triangle import reduce
import itertools

def main():
 h=legacy().h;comparisons=0;cases=0;guards=0
 for symbolic in [False,True]:
  d=read(HERE/'development'/('triangle_'+str(symbolic)+'.json.gz'));c=d['case'];expected=d['reference']['blocks'][0]['result']['coefficients']
  ok,n=h.equal(reduce(c)['coefficients'],expected);assert ok;comparisons+=n;cases+=1
  for order in itertools.permutations(range(3)):
   q=copy.deepcopy(c);q['definition']['propagators']=[q['definition']['propagators'][j] for j in order];q['targets']=[[a[j] for j in order] for a in c['targets']]
   def permute(key):
    a=list(map(int,key.split(',')));return label([a[j] for j in order])
   ref={permute(t):{permute(m):v for m,v in row.items()} for t,row in expected.items()}
   ok,n=h.equal(reduce(q)['coefficients'],ref);assert ok;comparisons+=n;cases+=1
  for replacement in ['k1+p1','-k1']:
   q=copy.deepcopy(c)
   for prop in q['definition']['propagators']:prop['momentum']=prop['momentum'].replace('k1',replacement)
   ok,n=h.equal(reduce(q)['coefficients'],expected);assert ok;comparisons+=n;cases+=1
  for kind in ['mass','virtuality','cut','power','index_type']:
   q=copy.deepcopy(c)
   if kind=='mass':q['definition']['propagators'][0]['mass_squared']='1'
   elif kind=='virtuality':q['definition']['scalarproduct_rules'][0][1]='1'
   elif kind=='cut':q['definition']['cut_propagators']=[1]
   elif kind=='power':q['targets'][0][0]=17
   else:q['targets'][0][0]=1.0
   assert reduce(q) is None,kind;guards+=1
 r=dict(complete=True,native_reference_routing_cases=cases,coefficient_checks=comparisons,unsupported_guard_cases=guards,source_sha256=sha(HERE/'s01_triangle.py'))
 write(HERE/'triangle_structure_checks.json',r);return r
if __name__=='__main__':print(json.dumps(main()),flush=True)
