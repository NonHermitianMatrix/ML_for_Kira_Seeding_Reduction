"""Check the exact identity under coordinate changes without rerunning native timings."""
from s00_loop_common import *
from s01_bubble_tree import reduce
import re

def main():
 p=read(HERE/'protocol.json.gz');count=0;rows=[]
 for c in [p['trees'][0],next(c for c in p['trees'] if len(c['definition']['loop_momenta'])==3 and c['shape']=='chain'),p['trees'][-1]]:
  reference=reduce(c);assert reference is not None
  for transform in ['names','line_signs','physical_order']:
   x=copy.deepcopy(c);d=x['definition'];n=len(d['propagators']);order=list(range(n))
   if transform=='names':
    names=d['loop_momenta']+d['external_momenta'];mapping={a:'z'+str(i+1) for i,a in enumerate(names)}
    for item in d['propagators']:item['momentum']=re.sub(r'\b[a-zA-Z][a-zA-Z0-9]*\b',lambda m:mapping[m.group(0)],item['momentum'])
    d['loop_momenta']=[mapping[a] for a in d['loop_momenta']];d['external_momenta']=[mapping[a] for a in d['external_momenta']]
    d['scalarproduct_rules']=[[[mapping[a] for a in pair],v] for pair,v in d['scalarproduct_rules']]
   elif transform=='line_signs':
    for item in d['propagators']:item['momentum']='-('+item['momentum']+')'
    d['quadratic_momentum_vectors']=[[-v for v in a] for a in d['quadratic_momentum_vectors']]
   else:
    P=d['physical_propagators'];order=list(reversed(range(P)))+list(range(P,n));d['propagators']=[d['propagators'][i] for i in order];x['targets']=[[a[i] for i in order] for a in x['targets']];d['quadratic_momentum_vectors']=[d['quadratic_momentum_vectors'][i] for i in order]
   x['id']='arbitrary_name';x['topology_group']='unused_label';r=reduce(x);assert r is not None
   refmaster=reference['masters'][0];newmaster=[refmaster[i] for i in order]
   for a in c['targets']:
    b=[a[i] for i in order]
    assert reference['coefficients'][label(a)][label(refmaster)]==r['coefficients'][label(b)][label(newmaster)]
    count+=1
   rows.append(dict(case=c['id'],transform=transform,checks=len(c['targets'])))
 result=dict(complete=True,checks=count,rows=rows);write(HERE/'structure_checks.json',result);return result
if __name__=='__main__':print(json.dumps(main()))
