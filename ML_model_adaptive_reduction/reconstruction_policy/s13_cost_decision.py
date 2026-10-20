"""Bounded-cost decisions with a fixed control and an out-of-range fallback."""
from s00_reconstruction_common import *
import struct
from s10_cases import features

def scores(model,x):
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x]
 total=[0.]*len(model['trees'][0]['value'][0])
 for tree in model['trees']:
  i=0
  while tree['left'][i]>=0:
   i=tree['left'][i] if x[tree['feature'][i]]<=tree['cut'][i] else tree['right'][i]
  for j,v in enumerate(tree['value'][i]):total[j]+=v/len(model['trees'])
 return total

def choose(policy,x,learned=True,group=None):
 actions=policy['actions'];fixed=policy.get('fixed_by_structure',{}).get(group,policy['fixed'])
 if any(v<lo-1e-9 or v>hi+1e-9 for v,lo,hi in zip(x,policy['minimum'],policy['maximum'])):
  return 'previous',dict(reason='outside_measured_feature_range',model_used=False)
 if not learned or not policy['enabled']:
  return fixed,dict(reason='validated_fixed_choice',model_used=False)
 y=scores(policy['model'],x);n=len(actions);k=actions.index(fixed)
 choices=[i for i in range(n) if y[n+i]<=policy['failure_limit']]
 i=min(choices,key=lambda j:y[j]) if choices else k
 if y[i]>=y[k]*(1-policy['margin']):i=k
 return actions[i],dict(reason='cost_prediction',model_used=True,predicted_relative_cost=y[:n],predicted_failure_fraction=y[n:],selected_index=i)
