"""Freeze all scientific inputs and executables after development checks."""
import hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];ACC=HERE.parent/"acceleration"
sys.path[:0]=[str(ACC),str(HERE.parent)]
from s01_common import old
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 plan=json.loads((HERE/"plan.json").read_text());audit=json.loads((HERE/"development_validation.json").read_text())
 assert audit["passed"] and audit["trials"]==12 and audit["exact_completions"]>=4 and audit["binary_pair_checks"]>=2
 from s13_records import read_record
 records=[read_record(p) for p in (HERE/"development").glob("*.json.gz")]
 for r in records:
  if r["policy"].startswith("stock_") and r["success"]:
   match=next(x for x in records if x["case"]==r["case"] and x["size"]==r["size"] and x["policy"]=="exit_"+r["policy"].split("_",1)[1])
   assert match["success"],"Modified development mode lost a stock completion"
 assert not (HERE/"test").exists()
 files=list(HERE.glob("s*"))+[HERE/"plan.json",HERE/"build.json",HERE/"reap_validation.json",
 ROOT/".tools/kira/bin/kira",ROOT/".tools/kira-fast-expression/kira",ROOT/".tools/Ferl7/fer64",
 ROOT/"ML_model_seed_selection/trained_model.pt",ROOT/"ML_model_reduction/trained_model.pt",
 ROOT/"ML_model_seed_selection/split_manifest.json"]
 files += [ACC/x for x in ["s78_expression_controls_worker.py","s69_expression_preflight.py","s01_fast_seed.py","seed_weights.npz","seed_export.json","s36_evidence.py"]]
 files += [HERE.parent/x for x in ["s01_common.py","s02_worker.py","s03_run.py"]]
 files += [ROOT/"ML_model_seed_selection/kira_sufficiency_test"/x for x in ["s02_common.py","s03_kira_adapter.py","s08_verify.py","s22_coefficient_reader.py"]]
 for c in plan["test"]+plan["development"]:
  files += [ROOT/"integrals"/c["meta"][k] for k in ["definition","masters","inputs","references","seeds"]]
  files.append(old.family_file(c["meta"]["family"],"identities.jsonl.gz"))
 hashes={str(p.relative_to(ROOT)):sha(p) for p in files if p.is_file()}
 out=dict(schema=1,sha256=hashes,expected_trials=480,cases=list(range(12)),sizes=plan["target_sizes"],
  repetitions=5,policies=plan["policies"],scope=plan["scope"],primary=plan["primary"],
  development_audit_sha256=sha(HERE/"development_validation.json"),timestamp_utc=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())
 (HERE/"freeze.json").write_text(json.dumps(out,indent=2)+"\n")
 print("Frozen 480 trials on new held-out kinematic groups",flush=True)
if __name__=="__main__":main()
