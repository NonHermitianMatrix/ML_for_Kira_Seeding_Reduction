"""Collect native labels and compare frozen filters with exact fallback."""
import argparse,hashlib,json,os,pathlib,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from s03_run import run
from s02_records import read,packed
RUNTIME=ROOT/"Kira_comparison/integrated_runtime"
def setup():
 os.environ.update(KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=os.environ.get("KIRA_EQ_RUNTIME_BINARY",".tools/kira-equation-selection/kira-lazy"),KIRA_PARALLEL_EVAL="1",KIRA_FAST_EVAL="1",KIRA_CPP_SEED="1",KIRA_SPARSE_FEATURES="1",KIRA_ROW_PAIR_FASTPATH="1")
def cases(phase):
 manifest=json.loads((HERE/"families.json").read_text())
 return [(c,b["size"]) for b in manifest["batches"] for c in manifest["cases"] if c["id"]==b["case"] and c["split"]==phase]
def reference(c,n):
 name=f'{c["id"]}_n{n}.json.gz'
 for d in [HERE/"references",RUNTIME/"references",ROOT/"Kira_comparison/multiloop_native/references",RUNTIME/"reserved_references"]:
  p=d/name
  if p.exists():return p
 p=HERE/"references"/name;old=os.environ.get("KIRA_EQ_MODE","off");os.environ["KIRA_EQ_MODE"]="off"
 r=run(c,n,"native",p,timeout=200,margin=1,records=False)
 os.environ["KIRA_EQ_MODE"]=old
 assert r["success"],(c["id"],r["status"]);return p
def workflow(c,n,mode,threshold,out,ref,base="native",basis=None):
 start=time.perf_counter();results=[]
 requested_mode=mode;requested_threshold=threshold
 if mode=="auto":
  config=json.loads((HERE/"trained_model/deployment.json").read_text())
  route=config.get("by_topology",{}).get(c["topology_group"],dict(mode="off",threshold=0))
  mode=route["mode"];threshold=route["threshold"]
 os.environ.update(KIRA_EQ_MODE=mode,KIRA_EQ_THRESHOLD=str(threshold),KIRA_EQ_WEIGHTS=str(HERE/"trained_model/weights.txt"),KIRA_EQ_COLLECT="0")
 policy="native";weights=None
 if base!="native":
  sys.path.insert(0,str(RUNTIME));from s108_reduce import select
  variant,seed_threshold=select(c,n,base);os.environ["KIRA_SEED_THRESHOLD"]=str(seed_threshold)
  policy={"seed":"seed_closed","both":"combined_closed","row":"learned"}[base]
  if ":" in variant:weights=ROOT/"ML_model_reduction/runtime_training/trajectory_candidates"/variant.split(":")[1]/"weights.txt"
 steps=[(mode,policy,0)]
 if mode!="off":steps.append(("off",policy,0))
 if policy in ("seed_closed","combined_closed"):steps.append(("off","learned" if base=="both" else "native",0))
 steps.append(("off","learned" if base in ("row","both") else "native",1))
 for eqmode,pol,margin in steps:
  os.environ["KIRA_EQ_MODE"]=eqmode
  r=run(c,n,pol,out,timeout=160,margin=margin,reference=ref,weights=weights,records=False,check_masters=True,archive=False,basis=basis)
  results.append(r)
  if r["success"] or r.get("mismatches"):break
 result=dict(case=c["id"],group=c["group"],topology=c["topology_group"],split=c["split"],size=n,mode=requested_mode,threshold=requested_threshold,applied_mode=mode,applied_threshold=threshold,base=base,success=results[-1]["success"],reference_checked=results[-1]["reference_checked"],status=results[-1]["status"],attempt_count=len(results),complete_seconds=time.perf_counter()-start,attempts=results,forward_seconds=sum(m.get("forward_seconds",0) for r in results for m in r.get("metrics",[])),back_substitution_seconds=sum(m.get("seconds",0) for r in results for m in r.get("stage_metrics",[]) if m.get("stage")=="back_substitution"),filter_seconds=sum(r.get("equation_metrics",{}).get("filter_seconds",0) for r in results),generated_equations=sum((r.get("counters",{}).get("generated_equations") or [0])[0] for r in results),selected_equations=sum((r.get("counters",{}).get("selected_equations") or [0])[-1] for r in results))
 packed(out,result);return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("action",choices=["collect","validate","test","pilot"]);a=ap.parse_args();setup()
 if a.action in ("collect","pilot"):
  selected=cases("training")
  if a.action=="pilot":selected=selected[:1]
  for c,n in selected:
   ref=reference(c,n);out=HERE/"training"/f'{c["id"]}_n{n}.json.gz'
   if out.exists():continue
   os.environ.update(KIRA_EQ_MODE="collect",KIRA_EQ_COLLECT="1")
   r=run(c,n,"native",out,timeout=180,margin=0,reference=ref,records=False,check_masters=True,archive=False)
   if not r["success"]:
    packed(out.with_name(out.name.replace(".json.gz","_failed.json.gz")),r)
    r=run(c,n,"native",out,timeout=180,margin=1,reference=ref,records=False,check_masters=True,archive=False)
   packed(out,r);assert r["success"],r["status"]
   print(json.dumps(dict(case=c["id"],size=n,status=r["status"],metrics=r.get("equation_metrics"),record_bytes=len(r.get("equation_records","")))),flush=True)
 else:
  frozen=json.loads((HERE/"trained_model/freeze.json").read_text()) if a.action=="test" else None
  if frozen:
   for name,digest in frozen["sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
  phase="testing" if frozen else "validation";reps=5 if frozen else 3
  config=json.loads((HERE/"trained_model/deployment.json").read_text()) if frozen else None
  for index,(c,n) in enumerate(cases(phase)):
   ref=reference(c,n)
   methods=[("off",0),("learned",config["threshold"]),("distance",config["distance_threshold"]),("auto",0)] if frozen else [("off",0)]+[("learned",t) for t in [.0001,.001,.005,.01,.03,.1]]+[("distance",d) for d in [2,3,4]]
   if not frozen and os.environ.get("KIRA_EQ_VALIDATION_GRID"):methods=json.loads(pathlib.Path(os.environ["KIRA_EQ_VALIDATION_GRID"]).read_text())
   for rep in range(reps):
    order=methods[rep%len(methods):]+methods[:rep%len(methods)]
    if (index+rep)%2:order=list(reversed(order))
    for mode,threshold in order:
     out=HERE/("model_test" if frozen else "validation")/f'{c["id"]}_n{n}_{mode}_t{threshold:g}_r{rep}.json.gz'
     if out.exists():continue
     r=workflow(c,n,mode,threshold,out,ref)
     print(json.dumps({k:r[k] for k in ["case","size","mode","threshold","success","attempt_count","complete_seconds","filter_seconds","generated_equations","selected_equations"]}),flush=True)
if __name__=="__main__":main()
