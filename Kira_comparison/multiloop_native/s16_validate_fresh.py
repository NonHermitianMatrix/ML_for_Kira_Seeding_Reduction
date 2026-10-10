"""Compare frozen candidate workflows in fresh validation processes."""
import json,os,pathlib,sys
from s02_run import run
from s04_records import read_record
from s15_fresh import execute_fresh
HERE=pathlib.Path(__file__).resolve().parent
def main(index):
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"];case=cases[index]
 policies=os.getenv("KIRA_VALIDATE_POLICIES","native:tight:row_full:row:seed_safe:combined_safe:split_native:split_combined_safe").split(":")
 if any(x in policies for x in ["row","row_full","combined_safe","combined_full_safe","split_combined_safe"]):
  model=json.loads((HERE.parents[1]/"ML_model_reduction/cost_training/trained_model.json").read_text());assert "remaining" in model["kind"]
 directory=os.getenv("KIRA_VALIDATE_DIRECTORY","validation_fresh")
 if directory=="validation_final":assert json.loads((HERE/"runtime_check.json").read_text())["all_passed"]
 for size in sorted({min(x,len(case["targets"])) for x in [32,128]}):
  reference=HERE/"references"/(case["id"]+f"_n{size}.json.gz")
  ref=read_record(reference) if reference.exists() else run(case,size,"stock",reference,timeout=600)
  if not ref["success"]:print("Reference failed",case["id"],size,flush=True);continue
  for repeat in range(2):
   offset=(index+repeat)%len(policies)
   for policy in policies[offset:]+policies[:offset]:
    output=HERE/directory/(case["id"]+f"_n{size}_r{repeat}_{policy}.json.gz")
    r=execute_fresh(case,size,policy,output,reference,timeout=300)
    print(json.dumps({k:r[k] for k in ["case","size","policy","success","complete_seconds","fallback_attempts"]}),flush=True)
if __name__=="__main__":main(int(sys.argv[1]))
