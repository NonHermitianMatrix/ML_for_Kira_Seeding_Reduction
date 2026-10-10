"""Run a complete fixed fallback policy; all production costs are retained."""
import argparse,json,pathlib,time,os
from s106_run_parallel import run
from s105_parallel_records import read_record,write_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def workflow(case,size,variant,reference,output,basis=None):
 begin=time.perf_counter();folder=ROOT/"ML_model_reduction/runtime_training/trajectory_candidates"
 weights=None
 if ":" in variant:kind,model=variant.split(":",1);weights=folder/model/"weights.txt"
 else:kind=variant
 if kind in ("native","fill","row"):
  steps=[("native" if kind=="native" else "fill" if kind=="fill" else "learned",1)]
 elif kind in ("row_small","fill_small"):
  mode="learned" if kind=="row_small" else "fill"
  steps=[(mode,0),(mode,1)]
 elif kind in ("small","seed","closure","combined"):
  start={"small":"native","seed":"seed_closed","closure":"closure","combined":"combined_closed"}[kind]
  steps=[(start,0)]
  if kind in ("seed","closure","combined"):steps.append(("learned" if kind=="combined" else "native",0))
  steps.append(("learned" if kind=="combined" else "native",1))
 else:raise ValueError(variant)
 attempts=[];records=[]
 for i,(policy,margin) in enumerate(steps):
  path=ROOT/"Kira_comparison/parallel_inference/attempts"/((("" if output.parent.name=="trajectory_validation" else output.parent.name+"_")+output.name.removesuffix(".json.gz"))+f"_a{i}.json.gz")
  if os.environ.get("KIRA_WORKFLOW_ATTEMPT_TAG"):path=path.with_name(path.name.replace(".json.gz","_"+os.environ["KIRA_WORKFLOW_ATTEMPT_TAG"]+".json.gz"))
  assert not path.exists(),"Only complete workflow restarts are supported; preserve partial evidence separately"
  r=run(case,size,policy,path,timeout=160,margin=margin,reference=reference,weights=weights,records=False,check_masters=True,archive=False,basis=basis)
  records.append(r);attempts.append(str(path.relative_to(ROOT)))
  if r["success"] or r.get("mismatches"):break
 successful=records[-1]["success"];result=dict(case=case["id"],group=case["group"],topology=case["topology_group"],split=case["split"],size=size,variant=variant,success=successful,reference_checked=successful and records[-1]["reference_checked"],status=records[-1]["status"],attempts=attempts,attempt_count=len(attempts),complete_seconds=time.perf_counter()-begin,
  operations=sum(sum(m.get("operations",0) for m in r.get("metrics",[])) for r in records),forward_seconds=sum(sum(m.get("forward_seconds",0) for m in r.get("metrics",[])) for r in records),decision_seconds=sum(sum(m.get("decision_seconds",0) for m in r.get("metrics",[])) for r in records),equations=sum((r.get("counters",{}).get("generated_equations") or [0])[0] for r in records))
 result["verification_mode"]="reference_coefficients" if reference else "native_exact_basis"
 result["basis_admitted"]=bool(successful and records[-1].get("basis_admitted"))
 result["seed_threshold"]=float(os.environ.get("KIRA_SEED_THRESHOLD",".01"))
 result["compiled_seed"]=os.environ.get("KIRA_CPP_SEED")=="1"
 # Include per-attempt algebra and exact checks, but exclude compression/retention from production time.
 result["complete_seconds"]=time.perf_counter()-begin
 result["workflow_overhead_seconds"]=max(0,result["complete_seconds"]-sum(r["complete_seconds"] for r in records))
 for relative,r in zip(attempts,records):write_record(ROOT/relative,r)
 write_record(output,result);return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("case");ap.add_argument("--size",type=int,required=True);ap.add_argument("--variant",required=True);ap.add_argument("--reference",type=pathlib.Path,required=True);ap.add_argument("--output",type=pathlib.Path,required=True)
 a=ap.parse_args();cases=json.loads((HERE/"families.json").read_text())["cases"]+json.loads((HERE/"reserved_families.json").read_text())["cases"];case=next(c for c in cases if c["id"]==a.case)
 r=workflow(case,a.size,a.variant,a.reference,a.output);print(json.dumps(r),flush=True)
if __name__=="__main__":main()
