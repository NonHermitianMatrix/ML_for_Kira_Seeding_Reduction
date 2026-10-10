"""Verify sparse feature decisions and measure the selected policies with shared controls."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 task=int(os.environ.get("SGE_TASK_ID","1"))-1
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
 bases=[c["id"] for c in cases if not c["id"].endswith("_deep")];cases=[c for c in cases if c["id"] in [bases[task],bases[task]+"_deep"]]
 models=json.loads((ROOT/"ML_model_reduction/runtime_training/trajectory_selection.json").read_text())["selected"]
 env=dict(os.environ,KIRA_RUNTIME_BINARY=".tools/kira-runtime-sparse/kira",KIRA_RUNTIME_SCRATCH="node",KIRA_VECTOR_SEED="1")
 for case in cases:
  size=min(32,len(case["targets"]));name=case["id"]
  ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
  for model in models:
   # Full/sparse decisions must preserve deterministic operations and exact exports.
   records=[]
   for sparse in [0,1]:
    path=HERE/"sparse_parity"/f"{name}_{model}_s{sparse}.json.gz"
    if not path.exists():
     e=dict(env,KIRA_SPARSE_FEATURES=str(sparse))
     if sparse:e["KIRA_SPARSE_PARITY"]="1"
     args=[sys.executable,str(HERE/"s02_run.py"),name,"--size",str(size),"--policy","learned","--margin","1","--timeout","180","--reference",str(ref),"--check-masters","--no-records","--weights",str(ROOT/"ML_model_reduction/runtime_training/trajectory_candidates"/model/"weights.txt"),"--output",str(path)]
     subprocess.run(args,env=e,check=True,timeout=240)
    r=read_record(path);assert r["success"] and r["reference_checked"],path;records.append(r)
   assert records[0]["raw_export"]==records[1]["raw_export"]
   for field in ["operations","groups","changed_sources","updates"]:
    assert [m[field] for m in records[0]["metrics"]]==[m[field] for m in records[1]["metrics"]],(name,model,field)
   assert sum(m["feature_parity_checked"] for m in records[1]["metrics"])>0
  variants=["native","fill"]+["row:"+m for m in models]+["small","seed","closure"]+["combined:"+m for m in models if m!="length_only"]
  for repeat in range(3):
   offset=(repeat+task)%len(variants);ordered=variants[offset:]+variants[:offset]
   for variant in ordered:
    path=HERE/"sparse_validation"/f"{name}_{variant.replace(':','-')}_r{repeat}.json.gz"
    if not path.exists():
     e=dict(env,KIRA_SPARSE_FEATURES="1")
     subprocess.run([sys.executable,str(HERE/"s24_workflow.py"),name,"--size",str(size),"--variant",variant,"--reference",str(ref),"--output",str(path)],env=e,check=True,timeout=540)
    r=read_record(path);assert r["success"] and r["reference_checked"],(name,variant,r["status"])
    print(json.dumps({k:r.get(k) for k in ["case","variant","complete_seconds","operations","forward_seconds","success"]}),flush=True)
if __name__=="__main__":main()
