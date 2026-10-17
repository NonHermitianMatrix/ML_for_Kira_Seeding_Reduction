"""Check the exact seed-decision transformation on exhaustive finite feature grids."""
import itertools,random
from s00_probe import HERE,inputs
from s13_seed_filter import compile_union,score

def main():
 rng=random.Random(42);checked=0;largest=0
 for trial in range(100):
  nodes=[]
  def build(depth):
   i=len(nodes);nodes.append(dict(feature=-1,threshold=0.,left=-1,right=-1,probability=rng.choice([0.,.2,.5,1.])))
   if depth and rng.random()<.9:
    left=build(depth-1);right=build(depth-1);nodes[i].update(feature=rng.choice([0,4,5,14]),threshold=rng.choice([.5,1.5,2.5]),left=left,right=right)
   return i
  build(5)
  for threshold in [.2,.5,1.]:
   derived=compile_union(nodes,{0:2,1:3,2:9},4,threshold);largest=max(largest,len(derived))
   for a,b in itertools.product(range(4),repeat=2):
    x={0:2,1:3,2:9,4:a,5:b,14:0};want=any(score(nodes,x|{14:op})>=threshold for op in range(4));assert (score(derived,x)>=.5)==want;checked+=1
 inputs.write(HERE/'trained_model/seed_decision_check.json',dict(passed=True,checks=checked,largest_compiled=largest,scope='Decision transformation only; these artificial trees are not Feynman-integral performance tests.'))
 print('SEED_DECISION_CHECK',checked,flush=True)
if __name__=='__main__':main()
