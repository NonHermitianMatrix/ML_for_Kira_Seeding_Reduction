"""Independently audit reserved coefficients, binary readers and fixed policies."""
from s05_study import *
def main():
 check_freeze()
 cold=list((HERE/"model_test/results").glob("*.json"));stream=list((HERE/"model_test/stream_results").glob("*.json"))
 expected=read(HERE/"model_test/complete.json")["applications"];assert len(cold)==expected and len(stream)==144
 unique={};payloads={};policies={}
 inputs={sha(p):p for p in (HERE/"model_test/inputs").glob("*.json")}
 for p in cold+stream:
  r=read(p);assert r["success"] and r["fallbacks"]==0,p
  identity=(r["coefficient_format"],r["coefficients_sha256"])
  if identity not in payloads:
   coeff=load_coeff(r);payloads[identity]=hashlib.sha256(json.dumps(coeff,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  h=payloads[identity];inp=inputs[r["request_sha256"]]
  if inp in unique:assert unique[inp][0]==h,p
  else:unique[inp]=(h,r)
  if "canonical_coefficients_sha256" in r:assert r["canonical_coefficients_sha256"]==h
  if r.get("mode")=="learned":policies[r["route"]]=policies.get(r["route"],0)+1
  eh=r["evidence_sha256"];raw=gzip.decompress((HERE/"objects"/(eh+".json.gz")).read_bytes());assert hashlib.sha256(raw).hexdigest()==eh
 positions=0;symbolic_checks=0
 for inp,(h,r) in unique.items():
  requests=read(inp)["requests"];coeff=load_coeff(r)
  for c in requests:
   rows=base.decode(coeff["symbolic_coefficients"][c["id"]])
   for b,row in zip(c["targets"],rows):
    assert row=={j:p for j,p in base.symbolic_oracle(c["mass_ratios"],b).items() if p};symbolic_checks+=len(row)
   for L in c["loops"]:
    rows=base.decode(coeff["coefficients"][c["id"]][str(L)])
    assert len(rows)==len(c["targets"])
    for b,row in zip(c["targets"],rows):
     assert row=={j:p for j,p in base.old.oracle(L,c["mass_ratios"],b).items() if p};positions+=len(row)
 assert len(unique)==12
 assert read(HERE/"model_test/integration/summary.json")["all_passed"]
 assert read(HERE/"development/kernel_check.json")["all_passed"]
 guard()
 write(HERE/"model_test/audit.json",dict(all_exact=True,applications=len(cold)+len(stream),cold_applications=len(cold),stream_applications=len(stream),distinct_input_batches=12,symbolic_coefficient_positions=symbolic_checks,expanded_coefficient_positions=positions,all_output_formats_identical=True,independent_old_oracle_passed=True,integration_passed=True,learned_routes=policies))
 print("audit passed",len(cold)+len(stream),positions,flush=True)
if __name__=="__main__":main()
