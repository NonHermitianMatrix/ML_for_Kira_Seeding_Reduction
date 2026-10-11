"""Verify the public deployed interface and its exact expanded output."""
import subprocess
from s00_contract import *
def main():
 c=base.make_case("test",7601,3,7,8);c["loops"]=[1,12,16,24,32]
 inp=HERE/"model_test/integration/default_input.json";out=HERE/"model_test/integration/default_cli.json"
 base.write(inp,dict(requests=[c]));begin=time.perf_counter()
 subprocess.run([sys.executable,str(HERE/"s01_application.py"),"--input",str(inp),"--output",str(out)],check=True,timeout=120)
 x=json.loads(out.read_text());x["external_seconds"]=time.perf_counter()-begin;base.write(out,x)
 assert x["success"] and x["fallbacks"]==0 and x["method"]==json.loads((HERE/"deployment.json").read_text())["mode"]
 raw=gzip.decompress((HERE/"objects"/(x["payload_sha256"]+".json.gz")).read_bytes());assert hashlib.sha256(raw).hexdigest()==x["payload_sha256"];d=json.loads(raw)
 checks=0
 for L in c["loops"]:
  for b,row in zip(c["targets"],base.decode(d["coefficients"][c["id"]][str(L)])):
   want=base.old.oracle(L,c["mass_ratios"],b)
   assert all(base.canonical(row.get(j,()))==base.canonical(want.get(j,())) for j in set(row)|set(want))
   checks+=len(want)
 p=HERE/"model_test/integration/summary.json";d=json.loads(p.read_text())
 d.update(applications=5,public_deployed_interface_passed=True,deployed_coefficient_checks=checks);base.write(p,d)
if __name__=="__main__":main()
