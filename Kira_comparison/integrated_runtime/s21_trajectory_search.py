"""Measure complete native trajectories for a bounded learned cost-policy search."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
from s14_runtime_config import configuration
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 task=int(os.environ.get("SGE_TASK_ID","1"))-1
 cases=json.loads((HERE/"families.json").read_text())["cases"]
 bases=[c["id"] for c in cases if c["split"]=="training" and not c["id"].endswith("_deep")]
 base=bases[task]
 folder=ROOT/"ML_model_reduction/runtime_training"
 candidates=json.loads((folder/"trajectory_candidates.json").read_text())["candidates"]
 variants=["native"]+[p["id"] for p in candidates]
 env=dict(os.environ,KIRA_RUNTIME_SCRATCH=configuration()["scratch_location"],KIRA_RUNTIME_BINARY=".tools/kira-runtime-fast/kira")
 for name in [base,base+"_deep"]:
  case=next(c for c in cases if c["id"]==name);size=min(32,len(case["targets"]))
  ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
  assert read_record(ref)["success"]
  shift=task%len(variants);ordered=variants[shift:]+variants[:shift]
  for variant in ordered:
   path=HERE/"trajectory_training"/f"{name}_{variant}.json.gz"
   if not path.exists():
    args=[sys.executable,str(HERE/"s02_run.py"),name,"--size",str(size),"--policy","native" if variant=="native" else "learned","--margin","1","--timeout","180","--reference",str(ref),"--check-masters","--no-records","--output",str(path)]
    if variant!="native":args+=["--weights",str(folder/"trajectory_candidates"/variant/"weights.txt")]
    subprocess.run(args,cwd=ROOT,env=env,check=True,timeout=240)
   r=read_record(path)
   assert r["success"] and r["reference_checked"],(name,variant,r["status"])
   print(json.dumps(dict(case=name,variant=variant,seconds=r["complete_seconds"],metrics=r["metrics"])),flush=True)
if __name__=="__main__":main()
