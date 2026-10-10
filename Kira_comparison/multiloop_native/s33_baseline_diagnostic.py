"""Post-comparison diagnostic of stock and instrumented smaller-region failures."""
import json,pathlib
from s02_run import run
from s04_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 case=next(c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["id"]=="validation_01_double_box")
 ref=HERE/"references"/"validation_01_double_box_n128.json.gz"
 out=HERE/"baseline_diagnostic";out.mkdir(exist_ok=True)
 results=[]
 for policy in ["stock","native"]:
  p=out/(policy+"_margin0.json.gz")
  r=read_record(p) if p.exists() else run(case,128,policy,p,timeout=120,margin=0,reference=ref,
   weights=ROOT/"ML_model_reduction/cost_training/trained_weights.txt",records=False,check_masters=True)
  results.append(dict(policy=policy,path=str(p.relative_to(HERE)),success=r["success"],status=r["status"],
   complete_seconds=r["complete_seconds"],allocation_failure="std::bad_alloc" in r["log"],
   recursive_termination="terminate called recursively" in r["log"],returncode=r.get("returncode")))
  print(json.dumps(results[-1]),flush=True)
 record=dict(purpose="Determine whether smaller-region allocation failures also occur in the responsive stock executable.",
  post_comparison=True,validation_only=True,models_and_reserved_protocol_unchanged=True,
  performance_comparison=False,results=results)
 (out/"summary.json").write_text(json.dumps(record,indent=2)+"\n")
if __name__=="__main__":main()
