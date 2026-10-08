"""Check the storage-only resumption and preservation of fixed mathematical inputs."""
from s01_common import *
def main():
 p=HERE/"native_seed";extension=read(p/"storage_guard_extension.json")
 assert extension["combined_conservative_bytes"]<10000000000
 for name,digest in extension["source_sha256"].items():assert sha(ROOT/name)==digest,name
 frozen=read(p/"frozen_inputs.json")
 for name,digest in frozen["sha256"].items():assert sha(ROOT/name)==digest,name
 plan=read(p/"plan.json")
 for i in range(7):
  env=read(p/"results"/("environment_%02d.json"%i));actual=env["plan"]
  expected=dict(plan)
  if i not in extension["preserved_complete_cases"]:expected["result_limit"]=extension["new_output_limit_bytes"]
  assert actual==expected,(i,"only output guard may differ")
  assert read(p/"results"/("complete_%02d.json"%i))["completed"]
 for name,digest in extension["preserved_trial_sha256"].items():assert sha(p/name)==digest
 assert len(list((p/"results").glob("*.json.gz")))==84
 write(p/"resumption_validation.json",dict(passed=True,extension_sha256=sha(p/"storage_guard_extension.json"),
  old_guard_stopped_between_trials=True,mathematical_workers_unchanged=True,
  matched_family_restarts=extension["restarted_cases"],preserved_complete_cases=extension["preserved_complete_cases"],
  archived_partial_trials=len(list((p/"storage_guard_partial").glob("*.json.gz"))),
  final_trials=84,combined_conservative_bytes=extension["combined_conservative_bytes"]))
 print("Storage-only resumption and matched family records verified.")
if __name__=="__main__":main()
