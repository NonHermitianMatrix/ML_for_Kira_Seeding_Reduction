"""Validate fitted thresholds and row policies against the smaller native control."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def main():
 task=int(os.environ.get("SGE_TASK_ID","1"))-1
 manifest=json.loads((HERE/"families.json").read_text());allcases=manifest["cases"]
 bases=[c["id"] for c in allcases if c["split"]=="validation" and not c["id"].endswith("_deep")]
 cases=[c for c in allcases if c["id"] in [bases[task],bases[task]+"_deep"]]
 folder=ROOT/"ML_model_seed_selection/runtime_inference"
 thresholds=json.loads((folder/"threshold_policy.json").read_text())
 assert json.loads((folder/"compiled_threshold_parity.json").read_text())["all_passed"]
 assert json.loads((folder/"cold_benchmark.json").read_text())["all_selection_checks_passed"]
 variants=["small","fill_small","row_small:f1_2","row_small:mixed","closure","seed_numpy","seed_compiled","combined_numpy:f1_2","combined_numpy:mixed","combined_compiled:f1_2","combined_compiled:mixed"]
 env=dict(os.environ,KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=".tools/kira-runtime-final/kira",KIRA_VECTOR_SEED="1",KIRA_SPARSE_FEATURES="1")
 for case in cases:
  name=case["id"];size=min(32,len(case["targets"]));threshold=thresholds["policies"][key(case)]["threshold"]
  ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
  parity=HERE/"control_parity"/f"{name}_fill.json.gz"
  if not parity.exists():
   e=dict(env,KIRA_SPARSE_PARITY="1")
   subprocess.run([sys.executable,str(HERE/"s02_run.py"),name,"--size",str(size),"--policy","fill","--margin","1","--timeout","180","--reference",str(ref),"--check-masters","--no-records","--output",str(parity)],env=e,check=True,timeout=240)
  r=read_record(parity);old=read_record(HERE/"sparse_validation"/f"{name}_fill_r0.json.gz");previous=read_record(ROOT/old["attempts"][0])
  assert r["success"] and r["raw_export"]==previous["raw_export"]
  for field in ["operations","groups","changed_sources","updates"]:
   assert [m[field] for m in r["metrics"]]==[m[field] for m in previous["metrics"]],(name,field)
  assert sum(m["feature_parity_checked"] for m in r["metrics"])>0
  for repeat in range(3):
   offset=(repeat+task)%len(variants);ordered=variants[offset:]+variants[:offset]
   for variant in ordered:
    path=HERE/"integrated_validation"/f"{name}_{variant.replace(':','-')}_r{repeat}.json.gz"
    actual=variant.replace("seed_numpy","seed").replace("seed_compiled","seed").replace("combined_numpy","combined").replace("combined_compiled","combined")
    if not path.exists():
     e=dict(env,KIRA_SEED_THRESHOLD=str(threshold),KIRA_CPP_SEED="1" if "compiled" in variant else "0")
     subprocess.run([sys.executable,str(HERE/"s24_workflow.py"),name,"--size",str(size),"--variant",actual,"--reference",str(ref),"--output",str(path)],env=e,check=True,timeout=540)
    r=read_record(path);assert r["success"] and r["reference_checked"],(name,variant,r["status"])
    print(json.dumps(dict(case=name,variant=variant,threshold=threshold,seconds=r["complete_seconds"],forward=r["forward_seconds"],operations=r["operations"],attempts=r["attempt_count"])),flush=True)
   # The compiled and NumPy modes must choose identical seeds.
   for stem in ["seed","combined"]:
    models=[""] if stem=="seed" else ["-f1_2","-mixed"]
    for suffix in models:
     a=read_record(HERE/"integrated_validation"/f"{name}_{stem}_numpy{suffix}_r{repeat}.json.gz")
     b=read_record(HERE/"integrated_validation"/f"{name}_{stem}_compiled{suffix}_r{repeat}.json.gz")
     aa=read_record(ROOT/a["attempts"][0]);bb=read_record(ROOT/b["attempts"][0])
     assert aa["predictions"]["selection_bits_base64"]==bb["predictions"]["selection_bits_base64"],(name,stem,suffix)
if __name__=="__main__":main()
