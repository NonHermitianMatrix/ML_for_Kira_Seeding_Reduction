"""Learn action failure risks and reject unsupported native predictions."""
from s00_light_common import *

def fit(X,Y,ids,depth,rng):
 n=len(ids);rate=sum(Y[i] for i in ids)/n;node={'risk':rate,'support':n}
 if depth==0 or n<4 or rate in [0,1]:return node
 best=None;columns=list(range(len(X[0])));rng.shuffle(columns)
 for j in columns:
  values=sorted({X[i][j] for i in ids})
  for lo,hi in zip(values,values[1:]):
   cut=(lo+hi)/2;left=[i for i in ids if X[i][j]<=cut];right=[i for i in ids if X[i][j]>cut]
   if min(len(left),len(right))<2:continue
   def impurity(js):
    k=sum(Y[i] for i in js);return 2*k*(len(js)-k)/len(js)
   gain=2*n*rate*(1-rate)-impurity(left)-impurity(right)
   if gain>1e-9 and (best is None or gain>best[0]):best=(gain,j,cut,left,right)
 if best:
  _,j,cut,left,right=best;node=dict(feature=j,cut=cut,left=fit(X,Y,left,depth-1,rng),right=fit(X,Y,right,depth-1,rng))
 return node

def train(rows):
 X=[r['features'] for r in rows];out=[]
 for a in range(3):
  Y=[not r['verified'][a] for r in rows];rng=random.Random(8911+a);trees=[]
  # The first tree sees every observed failure. Bootstrap trees estimate variation.
  for k in range(12):
   ids=list(range(len(rows))) if k==0 else [rng.randrange(len(rows)) for _ in rows]
   trees.append(fit(X,Y,ids,3,rng))
  out.append(dict(trees=trees,observed_failures=sum(Y),training_requests=len(rows)))
 return dict(actions=out,depth=3,trees_per_action=12,objective='Weighted binary Gini impurity for verified versus unverified complete actions.')

def predict(model,x):
 out=[]
 for action in model['actions']:
  rates=[]
  for tree in action['trees']:
   while 'feature' in tree:tree=tree['left'] if x[tree['feature']]<=tree['cut'] else tree['right']
   rates.append(tree['risk'])
  out.append(statistics.mean(rates))
 return out

def gate(model,x,selected,fixed):
 if any(v<a or v>b for v,a,b in zip(x,model['minimum'],model['maximum'])):return fixed,dict(reason='outside_training_range',risks=None,proposed=selected,selected=fixed)
 risks=predict(model['failure_guard'],x)
 if risks[selected]>model['failure_threshold']:return fixed,dict(reason='predicted_failure_risk',risks=risks,proposed=selected,selected=fixed)
 return selected,dict(reason='admitted',risks=risks,proposed=selected,selected=selected)
