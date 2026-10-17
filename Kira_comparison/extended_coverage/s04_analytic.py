"""Check the unchanged analytic route through twelve loops."""
import copy,sys
import sympy as sp
from s00_protocol import HERE,ROOT,read,write,module
from s02_study import call

def recurrence(L,a,q):
 d=sp.Symbol('d');n=L+1;v=[1]*n;r=sp.Integer(1)
 for j,goal in enumerate(a):
  while v[j]<goal:
   A=sum(v);r*=((A-L*d/2)*(n*d/2-A-1))/((d/2-v[j]-1)*v[j]*q);v[j]+=1
 return sp.cancel(r)
def main():
 gen=module('banana_grid',ROOT/'Kira_comparison/coverage_study/s00_cases.py');rows=[]
 for L in range(1,13):
  for symbolic in [False,True]:
   c=gen.case('propagator_massless',L,symbolic,h=1011);c['id']='analytic_'+c['id'];d=c['definition'];n=L+1
   d['propagators']=d['propagators'][:n];d.pop('quadratic_momentum_vectors',None);d.pop('rank',None)
   a=[1]*n;b=a.copy();b[0]=2;cc=a.copy();cc[-1]=4;e=a.copy();e[0]=e[-1]=2
   c['targets']=[a,b,cc,e];c['size']=4;basis=[a];q=sp.sympify(d['scalarproduct_rules'][0][1]);m=','.join(map(str,a))
   ref=dict(success=True,masters=basis,coefficients={','.join(map(str,t)):{m:str(recurrence(L,t,q))} for t in c['targets']},check='Independent single-power raising recurrence from the gamma expression')
   rp=HERE/'analytic'/(c['id']+'_reference.json.gz');write(rp,ref);write(HERE/'analytic'/(c['id']+'_input.json'),c)
   methods=['direct_exact','previous','selected'];ok=True
   for rep in range(3):
    for method in methods[rep:]+methods[:rep]:
     r=call(c,method,HERE/'analytic'/f'{c["id"]}_{method}_{rep}.json.gz',basis,rp);ok &= r['success']
   rows.append(dict(id=c['id'],loops=L,symbolic=symbolic,success=ok,targets=4))
 write(HERE/'analytic_completion.json',dict(complete=True,cases=rows,all_exact=all(r['success'] for r in rows),repetitions=3))
if __name__=='__main__':main()
