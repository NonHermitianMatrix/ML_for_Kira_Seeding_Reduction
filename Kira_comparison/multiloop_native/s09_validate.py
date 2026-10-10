"""Measure closed-loop validation costs before reserving final test results."""
import os,argparse,hashlib,json,pathlib
from s02_run import run
from s04_records import read_record
from s08_workflow import execute
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("case",type=int);a=ap.parse_args()
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
 case=cases[a.case];weights=ROOT/"ML_model_reduction/cost_training/trained_weights.txt";assert weights.exists()
 policies=os.getenv("KIRA_VALIDATE_POLICIES","native,tight,row,seed,combined,split_native,split_combined").replace(":",",").split(",")
 sizes=sorted({min(x,len(case["targets"])) for x in [32,128]})
 for size in sizes:
  reference=HERE/"references"/(case["id"]+f"_n{size}.json.gz")
  ref=read_record(reference) if reference.exists() else run(case,size,"stock",reference,timeout=600)
  if not ref["success"]:
   print(json.dumps(dict(case=case["id"],size=size,stage="reference",status=ref["status"])),flush=True);continue
  for repeat in range(2):
   offset=(a.case+repeat)%len(policies);order=policies[offset:]+policies[:offset]
   for policy in order:
    out=HERE/os.getenv("KIRA_VALIDATE_DIRECTORY","validation_v1")/(case["id"]+f"_n{size}_r{repeat}_{policy}.json.gz")
    r=read_record(out) if out.exists() else execute(case,size,policy,out,reference,timeout=360,weights=weights)
    print(json.dumps({k:r[k] for k in ["case","size","policy","success","complete_seconds","fallback_attempts","completed_targets"]}),flush=True)
if __name__=="__main__":main()
