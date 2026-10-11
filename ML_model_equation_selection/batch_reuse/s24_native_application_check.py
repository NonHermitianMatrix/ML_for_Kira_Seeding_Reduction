"""Check the final public deployment and compiled backend at extended loop orders."""
import subprocess
from s00_common import *
from s10_analyze import object_read
def main():
 folder=HERE/"model_test/integration"
 inp=folder/"pack_input.json";requests=json.loads(inp.read_text())["requests"];checks=0;hashes=[]
 for backend in ["deployed","native"]:
  out=folder/("final_"+backend+".json")
  if not out.exists():
   subprocess.run([sys.executable,str(HERE/"s17_application.py"),"--input",str(inp),"--output",str(out),"--backend",backend],check=True)
  x=json.loads(out.read_text());assert x["success"] and x["fallbacks"]==0;hashes.append(x["source_sha256"])
  data=object_read(x["coefficients_sha256"])
  for c in requests:
   for L,encoded in data["coefficients"][c["id"]].items():
    for b,row in zip(c["targets"],decode(encoded)):
     assert row==old.oracle(int(L),c["mass_ratios"],b);checks+=len(row)
 assert len(set(hashes))==1
 f=folder/"summary.json";summary=json.loads(f.read_text())
 baseline=summary.get("base_independent_coefficient_checks",summary["independent_coefficient_checks"])
 summary.update(base_independent_coefficient_checks=baseline,independent_coefficient_checks=baseline+checks,normal_applications=7,final_deployment_checked=True,compiled_extended_loops_checked=True)
 write(f,summary);print("final public application checks",checks,flush=True)
if __name__=="__main__":main()
