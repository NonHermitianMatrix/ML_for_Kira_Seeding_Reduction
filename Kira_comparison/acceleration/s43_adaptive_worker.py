"""Ranked seed expansion with an early native master-basis check.

Each rejected set costs only equation generation and modular selection.
The final symbolic reduction and coefficient checks remain exact.
"""
import argparse,json,os,pathlib,re,shutil,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import load_case,write,read,exact_check,sha
import s10_native_worker as native
from s02_worker import kira_run as stock_run
def bounds(seeds):
 sectors={}
 for a in seeds:
  sector=sum(1<<i for i,v in enumerate(a) if v>0)
  if not sector:continue
  r=sum(max(0,v) for v in a);s=sum(max(0,-v) for v in a);d=sum(max(0,v-1) for v in a)
  row=sectors.setdefault(sector,dict(topologies=["F"],sectors=[sector],r=0,s=0,d=0))
  for k,v in [("r",r),("s",s),("d",d)]:row[k]=max(row[k],v)
 return [sectors[k] for k in sorted(sectors)]
def main():
 ap=argparse.ArgumentParser()
 for name in ["partition","case","size","policy","scratch","output"]:
  ap.add_argument(name,type=int if name in ("case","size") else pathlib.Path if name in ("scratch","output") else str)
 a=ap.parse_args();plan=read(HERE/"plan.json");begin=time.perf_counter()
 fam=load_case(plan[a.partition][a.case],a.size)
 record=dict(family=fam["id"],group=fam["meta"]["group"],partition=a.partition,policy=a.policy,size=a.size,
  targets=[t["id"] for t in fam["targets"]],input_load_seconds=time.perf_counter()-begin)
 model={};ranked=[];seedfile=a.scratch/"seeds.txt"
 if a.policy=="adaptive_ml":
  t=time.perf_counter()
  from s01_fast_seed import FastSeed
  predictor=FastSeed();model["load_seconds"]=time.perf_counter()-t;t=time.perf_counter()
  shared=predictor.shared(fam["definition"],fam["masters"],fam["seeds"])
  scores=[0.0]*len(fam["seeds"]);probabilities=[]
  for target in fam["targets"]:
   values=predictor.predict(target,shared)
   probabilities.append(dict(target=target["id"],probabilities=[float(x) for x in values]))
   scores=[max(x,float(y)) for x,y in zip(scores,values)]
  ranked=[s for _,s in sorted(zip(scores,fam["seeds"]),key=lambda z:(-z[0],z[1]))]
  model.update(inference_seconds=time.perf_counter()-t,probabilities=probabilities,candidates=len(ranked),
   aggregation="maximum candidate score over supplied expressions",initial_budget=32)
 elif a.policy=="adaptive_distance":
  t=time.perf_counter();components={tuple(term["indices"]) for target in fam["targets"] for term in target["terms"]}
  ranked=sorted(fam["seeds"],key=lambda s:(min(sum(abs(x-y) for x,y in zip(s,c)) for c in components),sum(max(0,v-1) for v in s),s))
  model=dict(candidates=len(ranked),inference_seconds=time.perf_counter()-t,initial_budget=32)
 elif a.policy=="pool_checked":
  ranked=list(sorted(fam["seeds"]));model=dict(candidates=len(ranked),initial_budget=len(ranked))
 elif a.policy!="trim_checked":raise ValueError(a.policy)
 budget=min(model.get("initial_budget",0),len(ranked));selected=set(ranked[:budget]) if ranked else None
 history=[]
 def adaptive_run(w,p):
  nonlocal selected,budget
  jobs=read(w/"jobs.yaml");j=jobs["jobs"][0]["reduce_sectors"];j["check_masters"]=True
  logs=[];started=time.perf_counter()
  while True:
   if selected is not None:
    j["reduce"]=bounds(selected)
    seedfile.write_text("".join("F["+','.join(map(str,s))+"]\n" for s in sorted(selected)))
   write(w/"jobs.yaml",jobs)
   oldrun=subprocess.run
   def run(argv,**kw):
    argv=list(argv)
    if selected is not None:
     argv[0]=str(ROOT/".tools/kira-acceleration/kira")
     kw["env"]=dict(kw["env"],KIRA_ML_SEEDS=str(seedfile),KIRA_ML_SEED_AUDIT=str(w/"seed_audit.json"))
    return oldrun(argv,**kw)
   t=time.perf_counter();remaining=p["timeout_seconds"]-(t-started)
   if remaining<=11:raise RuntimeError("Seed expansion exhausted initial allowance")
   subprocess.run=run
   try:
    result=stock_run(w,dict(p,timeout_seconds=remaining));error=None
   except RuntimeError as e:
    result=None;error=e
   finally:subprocess.run=oldrun
   log=(w/"run.log").read_text(errors="replace")
   logs.append(log)
   rejected="check_masters: found additional master integrals" in log
   history.append(dict(budget=budget,selected_seeds=[list(s) for s in sorted(selected or [])],
    seconds=time.perf_counter()-t,rejected_master_basis=rejected,
    returncode=result["returncode"] if result else 1,log_sha256=sha(w/"run.log")))
   if result is not None:
    (w/"run.log").write_text("\n".join(logs))
    result["seconds"]=time.perf_counter()-started
    result["log_sha256"]=sha(w/"run.log");result["preflight"]=list(history)
    combined_log="\n".join(logs)
    result["counters"]={k:[int(x) for x in re.findall(pattern,combined_log)] for k,pattern in {
     "generated_equations":r"(\d+) equations:\s*\d+ zero \+",
     "selected_equations":r"Number of selected equations to reduce:\s*(\d+)",
     "forward_insertions":r"redundant:\s*\d+; insertions (\d+)",
     "reduced_equations":r"(\d+) equations were reduced"}.items()}
    return result
   if not rejected or selected is None or budget==len(ranked):
    (w/"run.log").write_text("\n".join(logs));raise error
   budget=min(len(ranked),max(32,2*budget));selected=set(ranked[:budget])
   for name in ["results","tmp","sectormappings","input_kira"]:
    folder=w/name
    if folder.exists():shutil.rmtree(folder)
 native.kira_run=adaptive_run
 attempts=[];rows={};t=time.perf_counter()
 try:
  rows,result=native.native_selected(fam,selected is None,a.scratch/"attempt0",
   dict(plan,timeout_seconds=plan["timeout_seconds"]-10),selected)
  result["bounds"]=read(a.scratch/"attempt0/jobs.yaml")["jobs"][0]["reduce_sectors"]["reduce"]
  attempts.append(result)
  complete=all(x["id"] in rows and all(k in fam["masters"] or c==0 for k,c in rows[x["id"]].items()) for x in fam["targets"])
 except (ValueError,RuntimeError,subprocess.TimeoutExpired) as e:
  attempts.append(dict(error=str(e),seconds=time.perf_counter()-t,preflight=list(history)));complete=False
 record.update(attempts=attempts,model=model,first_attempt_complete=complete,success=False,preflight=list(history))
 write(a.output,record)
 if not complete:
  if a.policy=="trim_checked":raise RuntimeError("Checked native baseline incomplete")
  native.kira_run=stock_run
  remaining=plan["timeout_seconds"]-15-(time.perf_counter()-begin)
  if remaining<=10:raise RuntimeError("No time left for fallback")
  rows,result=native.native_selected(fam,True,a.scratch/"attempt1",dict(plan,timeout_seconds=remaining),None)
  attempts.append(result)
 if selected is not None:model.update(selected=len(selected),selected_seeds=[list(s) for s in sorted(selected)])
 record.update(attempts=attempts,model=model,fallback=len(attempts)>1,reduction_seconds=time.perf_counter()-t,
  seed_audits={p.parent.name:read(p) for p in a.scratch.glob("attempt*/seed_audit.json")})
 t=time.perf_counter();checks=exact_check(rows,fam)
 record.update(verification_seconds=time.perf_counter()-t,checks=checks,success=all(x["status"]=="exact_match" for x in checks),
  script_seconds=time.perf_counter()-begin)
 write(a.output,record)
 print(json.dumps({k:record[k] for k in ["family","policy","fallback","success","script_seconds"]}),flush=True)
if __name__=="__main__":main()
