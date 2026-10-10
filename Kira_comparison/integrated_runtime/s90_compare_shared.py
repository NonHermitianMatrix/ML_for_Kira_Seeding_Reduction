"""Compare old and shared inference with fixed weights and exact native reductions."""
import argparse,json,os,pathlib,subprocess,sys
from s03_records import read_record
from s81_reduce import select
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=HERE/"fast_evaluation"
def parity(a,b):
 assert a["success"] and b["success"] and a["reference_checked"] and b["reference_checked"]
 for f in ["operations","equations","attempt_count"]:assert a[f]==b[f],f
 for x,y in zip(a["attempts"],b["attempts"]):
  x=read_record(ROOT/x);y=read_record(ROOT/y)
  assert x.get("raw_export")==y.get("raw_export") and x["status"]==y["status"]
  if "predictions" in x:
   for f in ["candidate_sha256","selection_bits_base64","probabilities_float32_base64"]:
    assert x["predictions"][f]==y["predictions"][f],f
  for f in ["groups","changed_sources","updates","operations","choice_digest"]:
   assert [m[f] for m in x.get("metrics",[])]==[m[f] for m in y.get("metrics",[])],f
def main():
 ap=argparse.ArgumentParser();ap.add_argument("phase",choices=["validation","confirmation"]);a=ap.parse_args()
 task=int(os.environ["SGE_TASK_ID"])-1
 if a.phase=="validation":
  cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
  groups=list(dict.fromkeys(c["group"] for c in cases));cases=[c for c in cases if c["group"]==groups[task]]
  batches=[dict(case=c["id"],size=min(32,len(c["targets"]))) for c in cases]
  repetitions=3
 else:
  from s93_freeze_shared import verify
  verify();frozen=json.loads((EXP/"freeze.json").read_text())
  data=json.loads((HERE/"reserved_families.json").read_text());groups=list(dict.fromkeys(c["group"] for c in data["cases"]))
  cases=[c for c in data["cases"] if c["group"]==groups[task]]
  ids={c["id"] for c in cases};batches=[b for b in data["batches"] if b["case"] in ids]
  repetitions=frozen["repetitions"]
 by_id={c["id"]:c for c in cases}
 for batch in batches:
  case=by_id[batch["case"]];size=batch["size"];name=case["id"]
  reference=HERE/"reserved_references"/f"{name}_n{size}.json.gz" if a.phase=="confirmation" else ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not reference.exists():reference=HERE/"references"/f"{name}_n{size}.json.gz"
  assert reference.exists()
  methods=["native","seed","row","both","auto"]
  for rep in range(repetitions):
   order=methods[rep%5:]+methods[:rep%5]
   if (task+rep)%2:order=list(reversed(order))
   for method in order:
    variant,threshold=select(case,size,method);pair={}
    for fast in ([0,1] if (rep+task+methods.index(method))%2==0 else [1,0]):
     out=EXP/("shared_"+a.phase)/f"{name}_n{size}_{method}_f{fast}_r{rep}.json.gz"
     if not out.exists():
      env=dict(os.environ,KIRA_RUNTIME_SCRATCH="node",KIRA_CPP_SEED="1",KIRA_VECTOR_SEED="0",
        KIRA_SPARSE_FEATURES="1",KIRA_ROW_PAIR_FASTPATH="1",KIRA_FAST_EVAL=str(fast),KIRA_SEED_THRESHOLD=str(threshold),
        KIRA_RUNTIME_BINARY=".tools/kira-shared-inference/kira" if fast else ".tools/kira-runtime-pair/kira")
      worker=HERE/("s87_workflow_shared.py" if fast else "s80_workflow_application.py")
      subprocess.run([sys.executable,str(worker),name,"--size",str(size),"--variant",variant,"--reference",str(reference),"--output",str(out)],env=env,check=True,timeout=540,stdout=subprocess.DEVNULL)
     result=read_record(out);pair[fast]=result
     print(json.dumps(dict(phase=a.phase,case=name,size=size,method=method,fast=fast,repeat=rep,success=result["success"],seconds=result["complete_seconds"],forward=result["forward_seconds"],decision=result["decision_seconds"])),flush=True)
    parity(pair[0],pair[1])
if __name__=="__main__":main()
