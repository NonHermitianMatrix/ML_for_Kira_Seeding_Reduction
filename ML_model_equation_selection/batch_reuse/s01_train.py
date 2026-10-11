"""Train a fast predictor of shared equation-substitution cost."""
import gzip
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from s00_common import *
def main():
 start=time.perf_counter();X=[];Y=[];records=[]
 for k in range(420):
  r=3+k%2;B=[5,7,9,11,13,14][(k//2)%6];n=[4,8,16,32,64,96,128][(k//12)%7]
  c=make_case("training",k,r,B,n);rows=[]
  for p in options(r):
   v=cost(dependency(c["targets"],p));x=feature(c["targets"],p)
   X.append(x);Y.append(math.log(v));rows.append(dict(permutation=p,features=x,cost=v))
  records.append(dict(request=c,candidates=rows))
 with gzip.open(HERE/"training/examples.json.gz","wt",compresslevel=9) as f:json.dump(records,f,separators=(",",":"))
 for ntrees in [4,16]:
  model=ExtraTreesRegressor(n_estimators=ntrees,max_depth=12,min_samples_leaf=3,random_state=741,n_jobs=1)
  model.fit(np.array(X),np.array(Y));trees=[]
  for tree in model.estimators_:
   t=tree.tree_;trees.append([[int(t.feature[i]),float(t.threshold[i]),int(t.children_left[i]),int(t.children_right[i]),float(t.value[i][0][0])] for i in range(t.node_count)])
  write(HERE/"trained_model"/("forest%d.json"%ntrees),dict(trees=trees,kind="ExtraTreesRegressor",label="log of sum(3*total_power-2) over shared dependency equations",training_batches=len(records),candidate_rows=len(Y),maximum_depth=12,seed=741,features=32,probabilities=False))
 cases=[]
 for k in range(12):
  r=[2,3,4][k%3];B=[8,12][(k//3)%2];n=[16,64][(k//6)%2]
  cases.append(make_case("validation",k,r,B,n))
 for c in cases:write(HERE/"validation/inputs"/(c["id"]+".json"),c)
 for k in range(12):
  r=[2,3,4][k%3];B=[10,14][(k//3)%2];n=[24,96][(k//6)%2]
  c=make_case("test",k,r,B,n)
  write(HERE/"model_test/inputs"/(c["id"]+".json"),c)
 write(HERE/"training/summary.json",dict(batches=len(records),candidate_rows=len(Y),seconds=time.perf_counter()-start,sha256=sha(Path(__file__))))
 print("training complete",len(Y),time.perf_counter()-start,flush=True)
if __name__=="__main__":main()
