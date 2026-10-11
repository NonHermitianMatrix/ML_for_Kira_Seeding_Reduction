"""Check release integrity, existing-data applications and storage bounds."""
import gzip,hashlib
from s00_math import *
def main():
 f=json.loads((HERE/"trained_model/freeze.json").read_text())
 for n,h in f["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 v=json.loads((HERE/"model_test/verification.json").read_text());assert v["all_passed"]
 old=ROOT/"ML_model_equation_selection/early_generation/trained_model/freeze.json"
 preceding=json.loads(old.read_text())
 for n,h in preceding["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 examples=json.loads(gzip.decompress((HERE/"training/examples.json.gz").read_bytes()))
 assert len(examples)==2016
 for e in examples:
  b=tuple(e["indices"]);p=tuple(e["pair"]);assert features(b,p)==e["features"]
  a,c=children(b,p);assert len(teacher(a)[0]|teacher(c)[0]|{b})==e["teacher_cost"]
 apps=[json.loads(p.read_text()) for p in (HERE/"model_test/integration").glob("*_result.json")]
 assert len(apps)==3 and all(r["success"] for r in apps)
 plan=json.loads((HERE/"resource_plan.json").read_text())
 def allocated(p):return sum(q.stat().st_blocks*512 for q in p.rglob("*") if q.is_file())
 retained=allocated(HERE);tools=allocated(ROOT/".tools/kira-higher-loops")
 assert retained<plan["new_retained_cap_bytes"] and tools<plan["new_tools_cap_bytes"]
 assert plan["combined_upper_bytes"]<plan["limit_bytes"]
 out=dict(all_passed=True,frozen_files=len(f["sha256"]),previous_frozen_files=len(preceding["sha256"]),training_examples=len(examples),existing_and_basis_applications=len(apps),extension_allocated_bytes=retained,tools_allocated_bytes=tools,combined_storage_upper_bytes=plan["combined_upper_bytes"])
 write(HERE/"model_test/release_check.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
