"""Run the fixed, independent native multiloop comparison."""
import fcntl,hashlib,json,pathlib,sys
from s02_run import run
from s04_records import read_record,write_record
from s15_fresh import execute_fresh
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def reference_run(*args,**kwargs):
 plan=json.loads((HERE/"resource_plan.json").read_text())
 with (ROOT/".tools/kira-cost-training/reference.lock").open("a") as guard:
  fcntl.flock(guard,fcntl.LOCK_EX)
  return run(*args,**kwargs,scratch_cap=plan["reference_scratch_bytes"])
def main(index):
 frozen=json.loads((HERE/"freeze.json").read_text())
 for name,want in frozen["sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,name
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="reserved"]
 case=cases[index];policies=frozen["policies"]
 for size in frozen["sizes"]:
  reference=HERE/"reserved_references"/(case["id"]+f"_n{size}.json.gz")
  ref=read_record(reference) if reference.exists() else reference_run(case,size,"stock",reference,timeout=frozen["reference_timeout_seconds"])
  blocked=set()
  for repeat in range(frozen["repeats"]):
   offset=(index+size+repeat)%len(policies);order=policies[offset:]+policies[:offset]
   if repeat%2:order=list(reversed(order))
   for policy in order:
    output=HERE/"model_test"/(case["id"]+f"_n{size}_r{repeat}_{policy}.json.gz")
    if output.exists():r=read_record(output)
    elif not ref["success"] or policy in blocked:
     r=dict(case=case["id"],group=case["group"],topology=case["topology_group"],split="reserved",
      loops=len(case["definition"]["loop_momenta"]),size=size,policy=policy,repeat=repeat,success=False,
      status="skipped",reason="reference_failed" if not ref["success"] else "prior_resource_failure",
      completed_targets=0,incomplete_targets=size,attempts=[])
     write_record(output,r)
    else:r=execute_fresh(case,size,policy,output,reference,timeout=frozen["timeout_seconds"])
    if not r.get("success") and r.get("status")!="skipped":blocked.add(policy)
    print(json.dumps({k:r.get(k) for k in ["case","size","policy","success","status","complete_seconds","completed_targets","fallback_attempts"]}),flush=True)
 # A separate expanded-bound check uses the first and last eight targets.
 reference=HERE/"reserved_references"/(case["id"]+"_n128.json.gz")
 if reference.exists() and read_record(reference)["success"]:
  chosen=case["targets"][:8]+case["targets"][120:128]
  part=dict(case,targets=chosen);output=HERE/"reference_checks"/(case["id"]+"_larger_bounds.json.gz")
  r=read_record(output) if output.exists() else reference_run(part,16,"stock",output,timeout=300,margin=2,reference=reference,check_masters=True)
  print(json.dumps(dict(case=case["id"],stage="expanded_bounds",success=r["success"],status=r["status"])),flush=True)
if __name__=="__main__":main(int(sys.argv[1]))
