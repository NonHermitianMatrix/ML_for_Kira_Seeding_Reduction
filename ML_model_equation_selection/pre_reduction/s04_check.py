"""Independent arithmetic, application, fallback and final-output checks."""
import argparse,random
from s00_contract import *
from s01_application import apply,validate_group
def kernel():
 rng=random.Random(8812);checks=0
 for k in range(1000):
  a=[F(rng.randrange(-500,501),rng.randrange(1,100)) for _ in range(rng.randrange(0,15))]
  b=[F(rng.randrange(-500,501),rng.randrange(1,100)) for _ in range(rng.randrange(0,15))]
  delta=rng.choice([j for j in range(-20,21) if j])
  actual=fractions(subtract(from_fraction(a),from_fraction(b),delta))
  want=base.canonical([(a[i] if i<len(a) else F(0))-(b[i] if i<len(b) else F(0)) for i in range(max(len(a),len(b)))])
  want=base.canonical([x/delta for x in want]);assert actual==want;checks+=1
  power=rng.randrange(1,14);rho=rng.randrange(1,100)
  actual=fractions(euler(from_fraction(a),power,rho));want=[F(0)]*(len(a)+1)
  for i,v in enumerate(a):want[i]+=v/rho;want[i+1]-=v/F(2*power*rho)
  assert actual==base.canonical(want);checks+=1
 for r in [2,3,4]:
  c=base.make_case("validation",6001+r,r,14,100);rows,_=selected(c,"extreme",None);out=recurrence(c,rows)
  for b,row in zip(c["targets"],out):
   oracle=base.symbolic_oracle(c["mass_ratios"],b)
   assert all(base.canonical(row.get(j,()))==base.canonical(oracle.get(j,())) for j in set(row)|set(oracle));checks+=len(oracle)
 base.write(HERE/"validation/kernel_check.json",dict(all_passed=True,checks=checks))
def integration():
 c=base.make_case("test",7601,3,7,8);c["loops"]=[1,12,16,24,32]
 # This application extends loop substitution only; it does not select the policy.
 for mode,fail in [("direct_model",False),("direct_model",True),("direct_extreme",False),("direct_analytic",False)]:
  result=apply([c],mode,inject_failure=fail)
  assert result["success"] and result["fallbacks"]==int(fail)
  save(HERE/"model_test/integration"/(mode+("_failure" if fail else "")+".json"),result)
 c["mass_ratios"]=[3,3,7]
 try:validate_group([c])
 except AssertionError:pass
 else:raise AssertionError("Repeated masses accepted")
 base.write(HERE/"model_test/integration/summary.json",dict(all_passed=True,applications=4,injected_failure_recovered=True,invalid_mass_rejected=True,loops=[1,12,16,24,32]))
def audit():
 from s02_study import check_freeze
 check_freeze();cache=set();checks=0;rawchecks=0;workflows=0
 from s10_polynomial import parse as independent_reader
 for p in sorted((HERE/"model_test/results").glob("*.json")):
  record=json.loads(p.read_text());assert record["success"] and record["fallbacks"]==0,p
  data=gzip.decompress((HERE/"objects"/(record["payload_sha256"]+".json.gz")).read_bytes())
  assert hashlib.sha256(data).hexdigest()==record["payload_sha256"];obj=json.loads(data)
  requests=json.loads((HERE/record["input"]).read_text())["requests"];workflows+=1
  # Check every saved raw expression with the earlier general rational reader.
  # Cache repeated exact expressions while counting all compared occurrences.
  raw=pack.driver.previous.parse(obj["raw_export"])
  for row in raw.values():
   for expression_text in row.values():
    p1=base.canonical(independent_reader(expression_text,"z"))
    from s08_reader import parse as new_reader
    assert p1==base.canonical(new_reader(expression_text,"z"));rawchecks+=1
  # All method outputs must agree with the direct, loop-dependent old oracle.
  key=(record["input"],hashlib.sha256(json.dumps(obj["coefficients"],sort_keys=True).encode()).hexdigest())
  if key in cache:continue
  cache.add(key)
  for c in requests:
   symbolic=base.decode(obj["symbolic_coefficients"][c["id"]])
   for L in c["loops"]:
    expanded=base.decode(obj["coefficients"][c["id"]][str(L)])
    assert len(expanded)==len(c["targets"])
    for b,s,row in zip(c["targets"],symbolic,expanded):
     want=base.old.oracle(L,c["mass_ratios"],b)
     assert all(base.canonical(row.get(j,()))==base.canonical(want.get(j,())) for j in set(row)|set(want))
     assert all(base.canonical(row.get(j,()))==base.canonical(base.old.poly_substitute(s.get(j,()),L)) for j in set(row)|set(s))
     checks+=len(set(row)|set(want))
 assert workflows==200 and len(cache)==8,(workflows,len(cache))
 guard()
 base.write(HERE/"model_test/audit.json",dict(all_exact=True,workflows=workflows,distinct_batch_coefficient_objects=len(cache),expanded_coefficient_positions=checks,raw_kira_coefficients_compared=rawchecks))
 print("exact output audit passed",checks,rawchecks,flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["kernel","integration","audit"]);a=ap.parse_args()
 {"kernel":kernel,"integration":integration,"audit":audit}[a.stage]()
if __name__=="__main__":main()
