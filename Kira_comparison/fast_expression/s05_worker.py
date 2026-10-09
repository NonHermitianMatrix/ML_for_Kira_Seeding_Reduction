"""Run unchanged seed selection and exact checks with a chosen Kira binary."""
import pathlib,sys,os,subprocess,time,re
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];ACC=HERE.parent/"acceleration"
sys.path[:0]=[str(ACC),str(HERE.parent)]
import s02_worker as backend
from s01_common import sha
policy=sys.argv[4]
assert policy in ("stock_pool","stock_ml","exit_pool","exit_ml")
binary=ROOT/(".tools/kira-fast-expression/kira" if policy.startswith("exit_") else ".tools/kira/bin/kira")
def kira_run(w,plan):
 env=dict(os.environ,FERMATPATH=str(ROOT/".tools/Ferl7/fer64"))
 begin=time.perf_counter()
 with (w/"run.log").open("w") as log:
  p=subprocess.run([str(binary),"--parallel=1","jobs.yaml"],cwd=w,env=env,stdout=log,
   stderr=subprocess.STDOUT,timeout=plan["timeout_seconds"]-10)
 elapsed=time.perf_counter()-begin;log=(w/"run.log").read_text(errors="replace")
 counts={k:[int(v) for v in re.findall(pat,log)] for k,pat in {
  "selected_equations":r"Number of selected equations to reduce:\s*(\d+)","selected_terms":r"Number of terms:\s*(\d+)",
  "reduced_equations":r"(\d+) equations were reduced","forward_insertions":r"redundant:\s*\d+; insertions (\d+)",
  "generated_equations":r"(\d+) equations:\s*\d+ zero \+","independent_equations":r"equations:\s*\d+ zero \+\s*(\d+) independent"}.items()}
 result=dict(seconds=elapsed,returncode=p.returncode,counters=counts,log_sha256=sha(w/"run.log"))
 if p.returncode:raise RuntimeError("Kira exit "+str(p.returncode)+": "+log[-1500:])
 return result
backend.kira_run=kira_run
import s78_expression_controls_worker as original
original.HERE=HERE
sys.argv[4]="stored_ml_lower_checked" if policy.endswith("_ml") else "stored_pool"
if __name__=="__main__":original.main()
