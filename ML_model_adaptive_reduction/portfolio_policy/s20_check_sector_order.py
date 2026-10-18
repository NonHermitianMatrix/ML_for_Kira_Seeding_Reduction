"""Compare retained sector order and minimum-line counts with exhaustive controls."""
from s00_common import *
import itertools,math,random

def ordered(n,p,perm,restricted,ordering):
 top=(1<<p)-1
 def permute(s):return sum(1<<perm[k] for k in range(n) if s&(1<<k))
 out=[]
 for original in range(top+1 if restricted else 1<<n):
  s=permute(original);lines=s.bit_count() if hasattr(s,'bit_count') else bin(s).count('1');copy=s;lineweight=0
  for k in range(n):
   if not copy&1:lineweight+=1
   copy>>=1;lineweight<<=1
  outside=bool(s&~permute(top));lineweight+=(1<<n) if outside else 0
  key=(0,s) if ordering==1 else (lines,s+((1<<n) if outside else 0)) if ordering==2 else (lines,lineweight)
  out.append((key,original))
 return [s for key,s in sorted(out)]
def main():
 rng=random.Random(1193);comparisons=0;minimum_checks=0
 for n in range(1,9):
  for p in range(1,n+1):
   random_perm=list(range(n));rng.shuffle(random_perm)
   for perm in [list(range(n)),list(reversed(range(n))),random_perm]:
    for order in [1,2,3]:
     full=[s for s in ordered(n,p,perm,False,order) if s<(1<<p)]
     reduced=ordered(n,p,perm,True,order)
     assert full==reduced;comparisons+=1
  subsets=[set(),set(range(1<<n))]+[{s for s in range(1<<n) if rng.random()<rng.random()} for k in range(20)]
  for trivial in subsets:
   expected=min([bin(s).count('1') for s in range(1<<n) if s not in trivial],default=n)
   counts=[sum(bin(s).count('1')==k for s in trivial) for k in range(n+1)]
   actual=next((k for k in range(n+1) if counts[k]<math.comb(n,k)),n)
   assert actual==expected;minimum_checks+=1
 write(HERE/'integration/ordering_validation.json',dict(passed=True,sector_comparisons=comparisons,minimum_line_checks=minimum_checks,coordinate_counts=list(range(1,9)),seed=1193,control='Exhaustive native sector order filtered to retained sectors; exhaustive minimum nontrivial line count.'))
 print('ORDER_CHECKS',comparisons,minimum_checks)
if __name__=='__main__':main()
