"""Audit stored exact results against the older loop-dependent formula."""
from s04_study import *
def main():
 check_freeze()
 paths=list((HERE/"model_test/results").glob("*.json"))+list((HERE/"model_test/stream_results").glob("*.json"))
 assert len(paths)==352,len(paths)
 unique={};hashes=set();positions=0
 for p in paths:
  r=json.loads(p.read_text());assert r["success"] and r["fallbacks"]==0,p
  for key in ["coefficients_sha256","evidence_sha256"]:
   h=r[key]
   if h not in hashes:
    raw=gzip.decompress((HERE/"objects"/(h+".json.gz")).read_bytes());assert hashlib.sha256(raw).hexdigest()==h
    hashes.add(h)
  # The request hash identifies its canonical, frozen input.
  inputs={base.sha(x):x for x in (HERE/"model_test/inputs").glob("*.json")}
  inp=inputs[r["request_sha256"]]
  if inp in unique:assert unique[inp]==r["coefficients_sha256"]
  else:unique[inp]=r["coefficients_sha256"]
 assert len(unique)==8
 for inp,h in unique.items():
  source=json.loads(inp.read_text())["requests"];data=json.loads(gzip.decompress((HERE/"objects"/(h+".json.gz")).read_bytes()))
  for c in source:
   symbolic=base.decode(data["symbolic_coefficients"][c["id"]])
   for b,row in zip(c["targets"],symbolic):
    want=base.symbolic_oracle(c["mass_ratios"],b)
    assert all(base.canonical(row.get(j,()))==base.canonical(want.get(j,())) for j in set(row)|set(want))
   for L in c["loops"]:
    rows=base.decode(data["coefficients"][c["id"]][str(L)])
    assert len(rows)==len(c["targets"])
    for b,row in zip(c["targets"],rows):
     want=base.old.oracle(L,c["mass_ratios"],b)
     assert all(base.canonical(row.get(j,()))==base.canonical(want.get(j,())) for j in set(row)|set(want))
     positions+=len(set(row)|set(want))
 integration=json.loads((HERE/"model_test/integration/summary.json").read_text());assert integration["all_passed"]
 guard()
 base.write(HERE/"model_test/audit.json",dict(all_exact=True,applications=len(paths),single_applications=160,stream_applications=192,distinct_input_groups=8,expanded_coefficient_positions=positions,independent_symbolic_oracle_passed=True,old_loop_dependent_oracle_passed=True,all_method_coefficients_identical=True,persistent_interface_passed=True))
 print("audit passed",len(paths),positions,flush=True)
if __name__=="__main__":main()
