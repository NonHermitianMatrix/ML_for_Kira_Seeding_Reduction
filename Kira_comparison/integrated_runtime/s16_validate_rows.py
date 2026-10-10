"""Test repeated row decisions in fresh native reductions on validation cases."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
from s14_runtime_config import configuration
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 config=configuration();manifest=json.loads((HERE/"families.json").read_text())
 training=json.loads((ROOT/"ML_model_reduction/runtime_training/training_results.json").read_text())
 assert training["training_groups"]>0 and training["validation_groups"]>0
 cases=[c for c in manifest["cases"] if c["split"]=="validation"]
 variants=["native","fill","local_time","output_bytes","time_and_bytes","old_row"]
 out=HERE/"row_validation";out.mkdir(exist_ok=True)
 for repeat in range(3):
  for case_index,case in enumerate(cases):
   name=case["id"];size=min(32,len(case["targets"]))
   ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
   if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
   offset=(repeat+case_index)%len(variants);ordered=variants[offset:]+variants[:offset]
   for variant in ordered:
    path=out/f"{name}_{variant}_r{repeat}.json.gz"
    if not path.exists():
     binary=".tools/kira-integrated-runtime/kira" if variant=="old_row" else ".tools/kira-runtime-modular/kira"
     env=dict(os.environ,KIRA_RUNTIME_SCRATCH=config["scratch_location"],KIRA_RUNTIME_BINARY=binary)
     policy=variant if variant in ["native","fill"] else "learned"
     args=[sys.executable,str(HERE/"s02_run.py"),name,"--size",str(size),"--policy",policy,"--margin","1","--timeout","180","--reference",str(ref),"--check-masters","--output",str(path)]
     if variant=="old_row":args+=["--weights",str(ROOT/"ML_model_reduction/cost_training/trained_weights.txt")]
     elif policy=="learned":args+=["--weights",str(ROOT/"ML_model_reduction/runtime_training/candidates"/variant/"weights.txt")]
     subprocess.run(args,env=env,cwd=ROOT,check=True,timeout=240)
    r=read_record(path);assert not r.get("mismatches"),path
    print(json.dumps(dict(case=name,variant=variant,repeat=repeat,success=r["success"],status=r["status"],seconds=r["complete_seconds"],metrics=r.get("metrics",[]))),flush=True)
if __name__=="__main__":main()
