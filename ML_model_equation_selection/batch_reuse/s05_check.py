"""Independent arithmetic and domain checks, including equivalent loop expansions."""
from s00_common import *
from s08_reader import parse as fast_reader
from s10_polynomial import parse as previous_reader
def main():
 begin=time.perf_counter();rng=random.Random(55131);count=0
 for r in [2,3,4]:
  for k in range(30):
   b=rng.choice(list(compositions(2+k%13,r)));rho=rng.sample(range(2,80),r)
   z=symbolic_oracle(rho,b)
   for L in [1,2,6,12,16,32]:
    want=old.oracle(L,rho,b)
    got={j:substitute(p,L) for j,p in z.items()}
    assert got==want,(r,b,rho,L)
    for p in z.values():assert substitute(p,L)==canonical(old.poly_substitute(p,L))
    count+=len(want)
   for p in options(r):
    rows=dependency([b],p)
    for a,pair in rows.items():
     assert sum(a)>1 and all(sum(c)==sum(a)-1 for c in children(a,pair))
     assert all(sum(c)==1 or c in rows for c in children(a,pair))
     assert all(a[j]>0 for j in pair)
 reader_checks=0
 for text in ["0","-7","(z^3+2*z+1)/123","(z^2-1)/(z-1)","(z+1)^5/27","z/3+z/7"]:
  assert fast_reader(text,"z")==previous_reader(text,"z");reader_checks+=1
 for text in ["1/0","x+1","1/(z+1)","f(z)","z^33","1.2"]:
  try:fast_reader(text,"z")
  except (AssertionError,ValueError,ZeroDivisionError):pass
  else:raise AssertionError(text)
 valid=make_case("validation",91,3,8,8);validate(valid)
 bad=[]
 for key,value in [("loops",[0]),("mass_ratios",[1,1,2]),("targets",[[0,0,0]]),("mass_scale_squared",2),("family","unknown")]:
  c=dict(valid);c[key]=value
  try:validate(c)
  except AssertionError:bad.append(key)
  else:raise AssertionError(key)
 assert len(bad)==5
 write(HERE/"validation/arithmetic_check.json",dict(all_passed=True,coefficient_checks=count,reader_checks=reader_checks,loop_orders=[1,2,6,12,16,32],invalid_inputs_rejected=bad,seconds=time.perf_counter()-begin))
 print("arithmetic checks",count,flush=True)
if __name__=="__main__":main()
