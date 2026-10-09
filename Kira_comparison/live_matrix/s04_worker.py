"""Run native equation generation and choose live forward operations inside Kira."""
import argparse,json,os,pathlib,re,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=HERE.parent
sys.path.insert(0,str(PARENT))
from s01_common import read,write,sha,load_case,sample_point,exact_check
import s10_native_worker as native
from s02_worker import kira_run as original_run
def main():
 ap=argparse.ArgumentParser();ap.add_argument("case",type=int);ap.add_argument("policy")
 ap.add_argument("scratch",type=pathlib.Path);ap.add_argument("output",type=pathlib.Path);args=ap.parse_args()
 plan=read(HERE/"plan.json");case=plan["family_cases"][args.case]
 t=time.perf_counter();size=min(16,case["meta"]["counts"]["targets"]);fam=load_case(case,size)
 loaded=time.perf_counter()-t
 point,prime=sample_point(fam["definition"])
 context=dict(family={k:fam["definition"][k] for k in ("loop_momenta","external_momenta","propagators","invariants","scalarproduct_rules")},
              master_columns=[",".join(map(str,a)) for a in fam["masters"]],point=point,prime=prime)
 contextpath=args.scratch/"context.json";write(contextpath,context)
 def run(w,p):
  if args.policy=="stock":return original_run(w,p)
  env=dict(os.environ,FERMATPATH=str(ROOT/".tools/Ferl7/fer64"),
      KIRA_LIVE_POLICY=args.policy,KIRA_LIVE_METRICS=str(w/"forward.jsonl"),
      KIRA_LIVE_TRACE=str(w/"row_trace.txt"),KIRA_LIVE_CONTEXT=str(contextpath),
      KIRA_LIVE_PYTHON=str(ROOT/".tools/seed-model/venv/bin/python"),
      KIRA_LIVE_SERVER=str(HERE/"s00_policy_server.py"))
  t=time.perf_counter()
  with (w/"run.log").open("w") as log:
   cp=subprocess.run([str(ROOT/".tools/kira-live-build/kira"),"--parallel=1","jobs.yaml"],
       cwd=w,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=p["timeout_seconds"]-10)
  elapsed=time.perf_counter()-t;logtext=(w/"run.log").read_text(errors="replace")
  if cp.returncode:raise RuntimeError("Kira exit %d: %s"%(cp.returncode,logtext[-3000:]))
  metrics=[json.loads(x) for x in (w/"forward.jsonl").read_text().splitlines()]
  return dict(seconds=elapsed,returncode=cp.returncode,forward=metrics,
      counters={k:[int(v) for v in re.findall(pattern,logtext)] for k,pattern in {
       "selected_equations":r"Number of selected equations to reduce:\s*(\d+)",
       "forward_insertions":r"redundant:\s*\d+; insertions (\d+)",
       "generated_equations":r"(\d+) equations:\s*\d+ zero \+"}.items()},
      log_sha256=sha(w/"run.log"))
 native.kira_run=run
 t=time.perf_counter()
 rows,result=native.native_selected(fam,True,args.scratch/"native",plan,None)
 reduction_seconds=time.perf_counter()-t
 t=time.perf_counter();checks=exact_check(rows,fam);verification=time.perf_counter()-t
 write(args.output,dict(family=fam["id"],domain=fam["domain"],loops=fam["meta"]["loops"],
      targets=[t["id"] for t in fam["targets"]],size=size,policy=args.policy,
      input_load_seconds=loaded,reduction_seconds=reduction_seconds,verification_seconds=verification,
      native=result,checks=checks,success=all(c["status"]=="exact_match" for c in checks)))
if __name__=="__main__":main()

