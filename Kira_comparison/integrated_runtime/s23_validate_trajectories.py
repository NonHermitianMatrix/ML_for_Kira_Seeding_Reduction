"""Measure learned trajectory policies and seed integration on development validation."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
from s14_runtime_config import configuration
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 task=int(os.environ.get("SGE_TASK_ID","1"))-1
 if task==0:subprocess.run([sys.executable,str(HERE/"s29_ephemeral_pilot.py")],check=True,cwd=ROOT,timeout=1260)
 if task==2:subprocess.run([sys.executable,str(HERE/"s35_profile_preparation.py")],check=True,cwd=ROOT,timeout=500)
 bases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation" and not c["id"].endswith("_deep")]
 base=bases[task]
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["id"] in [base["id"],base["id"]+"_deep"]]
 folder=ROOT/"ML_model_reduction/runtime_training"
 selected=json.loads((folder/"trajectory_selection.json").read_text())["selected"]
 variants=["native","fill"]+["row:"+v for v in selected]+["small","seed","closure","combined:"+selected[0]]
 env=dict(os.environ,KIRA_RUNTIME_SCRATCH=configuration()["scratch_location"],KIRA_RUNTIME_BINARY=".tools/kira-runtime-fast/kira",KIRA_VECTOR_SEED="1")
 for rep in range(3):
  for ci,case in enumerate(cases):
   name=case["id"];size=min(32,len(case["targets"]))
   ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
   if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
   offset=(rep+ci+task)%len(variants);ordered=variants[offset:]+variants[:offset]
   for variant in ordered:
    path=HERE/"trajectory_validation"/f"{name}_{variant.replace(':','-')}_r{rep}.json.gz"
    if not path.exists():
     args=[sys.executable,str(HERE/"s24_workflow.py"),name,"--size",str(size),"--variant",variant,"--reference",str(ref),"--output",str(path)]
     subprocess.run(args,cwd=ROOT,env=env,check=True,timeout=540)
    r=read_record(path);assert r["success"] and r["reference_checked"],(name,variant,r["status"])
    print(json.dumps({k:r.get(k) for k in ["case","variant","complete_seconds","operations","forward_seconds","attempt_count","success"]}),flush=True)
if __name__=="__main__":main()
