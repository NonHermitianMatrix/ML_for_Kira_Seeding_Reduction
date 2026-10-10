"""Fit seed thresholds from complete training workflows, retaining failed attempts."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 task=int(os.environ.get("SGE_TASK_ID","1"))-1
 allcases=json.loads((HERE/"families.json").read_text())["cases"]
 bases=[c["id"] for c in allcases if c["split"]=="training" and not c["id"].endswith("_deep")]
 cases=[c for c in allcases if c["id"] in [bases[task],bases[task]+"_deep"]]
 options=[("small",None),("closure",None)]+[("seed",t) for t in [.003,.01,.03,.1,.3,.5]]
 env=dict(os.environ,KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=".tools/kira-runtime-sparse/kira",KIRA_VECTOR_SEED="1",KIRA_SPARSE_FEATURES="1")
 for case in cases:
  name=case["id"];size=min(32,len(case["targets"]));ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
  options=options[task%len(options):]+options[:task%len(options)]
  for variant,threshold in options:
   label=variant if threshold is None else f"seed_t{threshold:g}"
   path=HERE/"seed_threshold_training"/f"{name}_{label}.json.gz"
   if not path.exists():
    e=env.copy()
    if (HERE/"rejected_workflows"/path.name).exists():e["KIRA_WORKFLOW_ATTEMPT_TAG"]="admission_v2"
    if threshold is not None:e["KIRA_SEED_THRESHOLD"]=str(threshold)
    subprocess.run([sys.executable,str(HERE/"s24_workflow.py"),name,"--size",str(size),"--variant",variant,"--reference",str(ref),"--output",str(path)],env=e,check=True,timeout=540)
   r=read_record(path);assert r["success"] and r["reference_checked"],(name,label,r["status"])
   print(json.dumps(dict(case=name,label=label,seconds=r["complete_seconds"],attempts=r["attempt_count"],operations=r["operations"])),flush=True)
if __name__=="__main__":main()
