"""Test preselected common-scale sequences with independent Kira references."""
import copy
import sympy as sp
from s00_protocol import HERE,ROOT,read,write
from s02_study import call

def main():
 protocol=read(HERE/'protocol.json');rows=[]
 for ident in protocol['scale_cases']:
  base=next(c for c in protocol['cases'] if c['id']==ident);sequence=[];ok=True
  for j,scale in enumerate(protocol['scale_factors']):
   c=copy.deepcopy(base);c['id']+='_'+str(j);factor=sp.Rational(scale)
   for r in c['definition']['scalarproduct_rules']:r[1]=str(sp.cancel(sp.sympify(r[1],rational=True)*factor))
   for p in c['definition']['propagators']:p['mass_squared']=str(sp.cancel(sp.sympify(p['mass_squared'],rational=True)*factor))
   rp=HERE/'scale'/(c['id']+'_reference.json.gz');r=call(c,'reference',rp)
   if not r['success']:ok=False;break
   cp=HERE/'scale'/(c['id']+'_check.json.gz');check=call(c,'check',cp,r['masters'],rp)
   if not check['success']:ok=False;break
   sequence.append(dict(case=c,basis=r['masters'],reference=str(rp)))
  if not ok:rows.append(dict(id=ident,status='reference_failed'));continue
  methods=['previous','selected','selected_reuse'];failed=set()
  for rep in range(3):
   for method in methods[rep:]+methods[:rep]:
    if method in failed:continue
    r=call(base,method,HERE/'scale'/f'{ident}_{method}_{rep}.json.gz',sequence=sequence)
    if not r['success']:failed.add(method)
  rows.append(dict(id=ident,status='verified' if not failed else 'method_failed',failed_methods=sorted(failed)))
 write(HERE/'scale_completion.json',dict(complete=True,cases=rows))
if __name__=='__main__':main()
