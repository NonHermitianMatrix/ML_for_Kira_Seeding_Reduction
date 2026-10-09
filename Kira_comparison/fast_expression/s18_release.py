"""Check frozen inputs, all trial records, resource bounds and release readiness."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s03_run import allocated
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 plan=json.loads((HERE/"plan.json").read_text());freeze=json.loads((HERE/"freeze.json").read_text())
 for name,h in freeze["sha256"].items():assert sha(ROOT/name)==h,name
 counts={};hashes={}
 for stage,n in [("development",12),("test",480)]:
  audit=json.loads((HERE/(stage+"_validation.json")).read_text())
  assert audit["passed"] and audit["trials"]==n
  files=list((HERE/stage).glob("*.json.gz"));assert len(files)==n
  assert set(audit["result_sha256"])=={p.name for p in files}
  for p in files:assert sha(p)==audit["result_sha256"][p.name]
  counts[stage]=dict(trials=n,exact=audit["exact_completions"],paired_checks=audit["binary_pair_checks"])
  hashes[stage]=sha(HERE/(stage+"_validation.json"))
 for p in HERE.glob("*.py"):compile(p.read_text(),str(p),"exec")
 for p in HERE.glob("*.sh"):subprocess.run(["bash","-n",str(p)],check=True)
 assert allocated(HERE)<plan["retained_limit_bytes"]
 assert allocated(ROOT/".tools/kira-fast-expression")<plan["new_tools_reserve_bytes"]
 run=json.loads((HERE/"execution.json").read_text())
 qstat=shutil.which("qstat") or os.environ.get("SGE_ROOT","/u/systems/UGE8.6.4")+"/bin/"+os.environ.get("SGE_ARCH","lx-amd64")+"/qstat"
 text=subprocess.check_output([qstat,"-u",os.environ.get("USER","rushil")],text=True)
 jobs={line.split()[0] for line in text.splitlines() if line.split() and line.split()[0].isdigit()}
 assert not {run["test_job"].split(".")[0],run["audit_job"].split(".")[0]}&jobs
 report=(ROOT/"report/report.tex").read_text()
 abstract=report.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 result=dict(passed=True,declared_records=492,all_declared_jobs_finished=True,audits=counts,audit_sha256=hashes,
  retained_allocated_bytes=allocated(HERE),tools_allocated_bytes=allocated(ROOT/".tools/kira-fast-expression"),
  frozen_inputs_preserved=True,original_models_preserved=True,abstract_preserved=True,
  working_publication_upper_bytes=json.loads((HERE/"scheduler_amendment_02.json").read_text())["combined_working_publication_upper_bytes"],
  timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 (HERE/"release_validation.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
