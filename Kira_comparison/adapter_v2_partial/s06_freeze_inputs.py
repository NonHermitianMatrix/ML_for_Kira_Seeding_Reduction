"""Record and enforce the exact inputs and executable sources before repeated tests."""
from s01_common import *
def main():
 p=read(HERE/"plan.json")
 assert sha(ROOT/"ML_model_seed_selection/trained_model.pt")==p["seed_model_sha256"]
 assert sha(ROOT/"ML_model_reduction/trained_model.pt")==p["reduction_model_sha256"]
 assert sha(ROOT/"ML_model_seed_selection/split_manifest.json")==p["split_sha256"]
 files=set()
 for item in p["family_cases"]:
  m=item["meta"]
  for k in ("definition","masters","inputs","references","seeds"):files.add(DATA/m[k])
  files.add(old.family_file(m["family"],"identities.jsonl.gz"))
 for d in [HERE,ROOT/"ML_model_reduction",ROOT/"ML_model_seed_selection"]:
  files.update(d.glob("s0[0-6]_*.py"))
 files.update([HERE/"plan.json",ROOT/".tools/kira/bin/kira",ROOT/".tools/Ferl7/fer64"])
 files.update(SUFF/n for n in ["s02_common.py","s03_kira_adapter.py","s08_verify.py","s22_coefficient_reader.py"])
 hashes={str(f.relative_to(ROOT)):sha(f) for f in sorted(files)}
 dest=HERE/"frozen_inputs.json"
 if dest.exists():assert hashes==read(dest)["sha256"]
 else:write(dest,dict(sha256=hashes,model_weights_unchanged=True,threshold=p["threshold"],outcome_independent_selection=True))
 print(json.dumps(dict(verified_files=len(hashes))))
if __name__=="__main__":main()
