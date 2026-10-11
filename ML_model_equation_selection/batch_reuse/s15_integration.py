"""Check production entry points, extended loop values and exact fallback."""
import subprocess
from s00_common import *
import importlib.util
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 driver=module("new_driver","s02_reduce.py");pack=module("pack_driver","s11_pack.py")
 policy=json.loads((HERE/"trained_model/deployment.json").read_text());cases=[]
 for k,r in enumerate([2,3,4]):
  c=make_case("test",810+k,r,6,4);c["loops"]=[1,12,16,24,32];cases.append(c)
 results=[]
 for c in cases:
  x=driver.apply(c,policy["mode"],policy["model"]);assert x["success"] and x["fallbacks"]==0
  driver.save(HERE/"model_test/integration"/(c["id"]+".json"),x);results.append(dict(case=c["id"],success=True))
 # Force a bad exact check in the new path, then require the preserved full-system fallback.
 original=driver.symbolic_oracle
 driver.symbolic_oracle=lambda rho,b:{0:(F(123456789),)}
 x=driver.apply(cases[0],"model",policy["model"]);driver.symbolic_oracle=original
 assert x["success"] and x["fallbacks"]==1
 write(HERE/"model_test/integration/fallback.json",x)
 p=HERE/"model_test/integration/pack_input.json";out=HERE/"model_test/integration/public_pack.json"
 write(p,dict(requests=cases))
 subprocess.run([sys.executable,str(HERE/"s11_pack.py"),"--input",str(p),"--output",str(out)],check=True)
 y=json.loads(out.read_text());assert y["success"] and y["fallbacks"]==0
 a=HERE/"model_test/integration/single_input.json";out2=HERE/"model_test/integration/public_single.json";write(a,cases[0])
 subprocess.run([sys.executable,str(HERE/"s09_application.py"),"--input",str(a),"--output",str(out2)],check=True)
 y=json.loads(out2.read_text());assert y["success"] and y["fallbacks"]==0
 checks=0
 from s10_analyze import object_read
 for file in (HERE/"model_test/integration").glob("*.json"):
  z=json.loads(file.read_text())
  if not z.get("coefficients_sha256"):continue
  data=object_read(z["coefficients_sha256"])
  source=cases if z.get("packed") else [next(c for c in cases if c["id"]==z["case"])]
  for c in source:
   rows=data["coefficients"][c["id"]] if z.get("packed") else data["coefficients"]
   for L,coeff in rows.items():
    for b,row in zip(c["targets"],decode(coeff)):assert row==old.oracle(int(L),c["mass_ratios"],b);checks+=len(row)
 write(HERE/"model_test/integration/summary.json",dict(all_passed=True,normal_applications=5,forced_fallbacks=1,loop_orders=[1,12,16,24,32],independent_coefficient_checks=checks))
 print("integration checks",checks,flush=True)
if __name__=="__main__":main()
