"""Create distinct mass profiles and exponent batches before fitting or timing."""
import random
from s00_math import *
def cases(split):
 result=[]
 for r in [2,3,4]:
  for scale,B in enumerate([6,10] if split=="validation" else [8,12]):
   seed=(9000 if split=="validation" else 19000)+r*100+scale
   rng=random.Random(seed);rho=sorted(rng.sample(range(2,50 if split=="validation" else 100),r))
   pool=[b for n in range(max(2,B-2),B+1) for b in compositions(n,r) if sum(x>0 for x in b)>=2]
   rng.shuffle(pool);targets=pool[:min(8 if scale==0 else 32,len(pool))]
   loops=[2,6,12] if split=="validation" else list(range(1,13))
   result.append(dict(id=split+"_r%d_b%d"%(r,B),split=split,family="coupled_vacuum_unit_massless",mass_scale_squared=1,mass_ratios=rho,targets=[list(b) for b in targets],loops=loops))
 return result
def main():
 for split in ["validation","test"]:
  for c in cases(split):write(HERE/split.replace("test","model_test")/"inputs"/(c["id"]+".json"),c)
 write(HERE/"design.json",dict(primary_loop_orders=list(range(1,13)),additional_symbolic_checks=[13,16,24,32],maximum_training_power=9,validation_powers=[6,10],test_powers=[8,12],repetitions=3,baseline="Complete dense Euler and partial-fraction system; supplied identities, not native Kira IBP generation.",restrictions="Unit massless powers, common total momentum, two to four distinct positive massive denominators, normalized squared-mass scale."))
if __name__=="__main__":main()
