"""Collect exact local symbolic costs across ordinary and deeper target batches."""
import json,os,pathlib,sys
from s02_run import run
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 task=int(os.environ.get("SGE_TASK_ID",sys.argv[1] if len(sys.argv)>1 else "1"))-1
 manifest=json.loads((HERE/"families.json").read_text())
 base=manifest["runtime_development_base_ids"][task]
 assert read_record(HERE/"pilot_topological_v2/validation_01_double_box_native_c1_m1.json.gz")["success"]
 assert json.loads((ROOT/"ML_model_reduction/runtime_training/feature_tests.json").read_text())["all_passed"]
 results=[]
 for name in [base,base+"_deep"]:
  case=next(c for c in manifest["cases"] if c["id"]==name);size=min(32,len(case["targets"]))
  oldref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  ref=oldref if oldref.exists() else HERE/"references"/f"{name}_n{size}.json.gz"
  if not ref.exists():
   os.environ["KIRA_RUNTIME_BINARY"]=".tools/kira-integrated-runtime/kira"
   r=run(case,size,"native",ref,timeout=240,margin=1,records=False,compact=True)
   assert r["success"],(name,"reference",r["status"])
  assert read_record(ref)["success"]
  dest=HERE/"collection"/f"{name}_n{size}.json.gz"
  if not dest.exists():
   os.environ["KIRA_RUNTIME_BINARY"]=".tools/kira-runtime-modular/kira"
   os.environ["KIRA_RUNTIME_TRAIN_GROUPS"]="500"
   r=run(case,size,"collect",dest,timeout=300,margin=1,reference=ref,records=True,check_masters=True,compact=True)
  else:r=read_record(dest)
  result=dict(case=name,size=size,success=r["success"],status=r["status"],seconds=r["complete_seconds"],groups=len(r.get("choices",[])),metrics=r.get("metrics",[]))
  results.append(result);print(json.dumps(result),flush=True)
  assert r["success"] and not r.get("mismatches"),(name,r["status"])
 path=HERE/"collection"/f"family_{task:02d}_summary.json"
 path.write_text(json.dumps(results,indent=2)+"\n")
if __name__=="__main__":main()
