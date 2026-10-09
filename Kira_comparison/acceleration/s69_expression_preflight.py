"""Check the master basis early for fast whole-expression seed selection."""
import argparse,json,pathlib,sys,time,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import load_case,read,write,exact_check
from s02_worker import supplied
import s02_worker as supplied_module
original_kira_run=supplied_module.kira_run
def early_checked_run(work, plan):
 lines=(work/"jobs.yaml").read_text().splitlines()
 positions=[i for i,line in enumerate(lines) if line.lstrip().startswith("preferred_masters:")]
 assert len(positions)==1
 i=positions[0];indent=lines[i][:len(lines[i])-len(lines[i].lstrip())]
 lines.insert(i+1,indent+"check_masters: true")
 (work/"jobs.yaml").write_text("\n".join(lines)+"\n")
 return original_kira_run(work,plan)
supplied_module.kira_run=early_checked_run
def main():
 ap=argparse.ArgumentParser()
 for name in ["partition","case","size","policy","scratch","output"]:
  ap.add_argument(name,type=int if name in ("case","size") else pathlib.Path if name in ("scratch","output") else str)
 a=ap.parse_args();plan=read(HERE/"plan.json");begin=time.perf_counter();fam=load_case(plan[a.partition][a.case],a.size)
 r=dict(family=fam["id"],partition=a.partition,case=a.case,size=a.size,policy=a.policy,
  targets=[t["id"] for t in fam["targets"]],input_load_seconds=time.perf_counter()-begin)
 model={};selected=None
 if a.policy.startswith("stored_ml"):
  threshold={"stored_ml":0.5,"stored_ml_low":0.1,"stored_ml_lower":0.01}[a.policy]
  t=time.perf_counter()
  from s01_fast_seed import FastSeed
  predictor=FastSeed();model["load_seconds"]=time.perf_counter()-t;t=time.perf_counter()
  shared=predictor.shared(fam["definition"],fam["masters"],fam["seeds"]);selected=set();probs=[]
  for target in fam["targets"]:
   values=predictor.predict(target,shared)
   probs.append(dict(target=target["id"],probabilities=[float(v) for v in values]))
   selected.update(seed for seed,p in zip(fam["seeds"],values) if p>=threshold)
  model.update(threshold=threshold,inference_seconds=time.perf_counter()-t,selected=len(selected),candidates=len(fam["seeds"]),
   selected_seeds=[list(s) for s in sorted(selected)],probabilities=probs)
 elif a.policy!="stored_pool":raise ValueError(a.policy)
 attempts=[];rows={};t=time.perf_counter()
 try:
  rows,attempt=supplied(fam,fam["targets"],selected,a.scratch/"attempt0",dict(plan,timeout_seconds=plan["timeout_seconds"]-10))
  attempts.append(attempt)
  complete=all(x["id"] in rows and all(k in fam["masters"] or c==0 for k,c in rows[x["id"]].items()) for x in fam["targets"])
 except (RuntimeError,ValueError,subprocess.TimeoutExpired) as error:
  attempts.append(dict(error=str(error),seconds=time.perf_counter()-t));complete=False
 r.update(attempts=attempts,model=model,first_attempt_complete=complete,success=False);write(a.output,r)
 if not complete:
  if a.policy=="stored_pool":raise RuntimeError("Full supplied pool incomplete")
  remaining=plan["timeout_seconds"]-15-(time.perf_counter()-begin)
  if remaining<=10:raise RuntimeError("No allowance left for fallback")
  rows,attempt=supplied(fam,fam["targets"],None,a.scratch/"attempt1",dict(plan,timeout_seconds=remaining))
  attempts.append(attempt)
 r.update(attempts=attempts,model=model,fallback=len(attempts)>1,reduction_seconds=time.perf_counter()-t)
 t=time.perf_counter();checks=exact_check(rows,fam)
 r.update(verification_seconds=time.perf_counter()-t,checks=checks,success=all(x["status"]=="exact_match" for x in checks),script_seconds=time.perf_counter()-begin)
 write(a.output,r);print(json.dumps({k:r[k] for k in ["family","policy","fallback","success","script_seconds"]}),flush=True)
if __name__=="__main__":main()
