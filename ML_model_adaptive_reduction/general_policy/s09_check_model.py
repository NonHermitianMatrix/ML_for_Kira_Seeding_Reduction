"""Check permutation invariance, split separation, and fitted inference."""
from s00_common import *
from s02_application import predict
import copy

def main():
 model=READ(HERE/'refit/trained_model/freeze.json');protocol=READ(HERE/'refit/protocol.json');tests=0
 for c in protocol['reserved']:
  x=features(c);other=copy.deepcopy(c);d=other['definition'];P=d['physical_propagators'];N=len(d['propagators']);order=list(range(P-1,-1,-1))+list(range(N-1,P-1,-1))
  d['propagators']=[d['propagators'][j] for j in order];d['loop_momenta'].reverse()
  rename={name:'renamed_loop_'+str(i) for i,name in enumerate(d['loop_momenta'])}
  expression=r'\b(?:'+'|'.join(re.escape(k) for k in rename)+r')\b'
  for entry in d['propagators']:entry['momentum']=re.sub(expression,lambda m:rename[m.group(0)],entry['momentum'])
  d['loop_momenta']=[rename[k] for k in d['loop_momenta']]
  other['targets']=[[a[j] for j in order] for a in other['targets']];other['targets'].reverse()
  d['top_level_sectors']=[sum(1<<i for i,j in enumerate(order) if s&(1<<j)) for s in d['top_level_sectors']]
  other['id']='unseen_name';other['topology_group']='unseen_family';xx=features(other)
  assert max(abs(a-b) for a,b in zip(x,xx))<1e-10
  assert max(abs(a-b) for a,b in zip(predict(model['model'],x),predict(model['model'],xx)))<1e-8
  tests+=1
 assert all(r['loops']<=3 for r in model['training'])
 assert not set(model['validation'])&{c['id'] for c in protocol['reserved']}
 assert not {r['case'] for r in model['training']}&{c['id'] for c in protocol['reserved']}
 write(HERE/'invariance_check.json',dict(complete=True,cases=tests,features=len(FEATURE_NAMES),propagator_loop_and_target_permutations=True,family_names_not_inputs=True,test_identifiers_disjoint=True,highest_training_loop=3))
 print('INVARIANCE',tests,flush=True)
if __name__=='__main__':main()
