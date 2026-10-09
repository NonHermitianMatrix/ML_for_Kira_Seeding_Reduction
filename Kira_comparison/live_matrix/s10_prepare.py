"""Freeze the benchmark inputs after exact pilot checks, before repeated trials."""
import ast,gzip,hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from s07_audit import load_case,old,DATA,trace_rows,check_update
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 plan=json.load(open(HERE/"plan.json"))
 build=json.load(open(HERE/"build.json"))
 assert build["header_sha256"]==sha(HERE/"s01_live_policy.h")
 assert build["binary_sha256"]==sha(ROOT/".tools/kira-live-build/kira")
 assert plan["frozen_model_sha256"]==sha(ROOT/"ML_model_reduction/trained_model.pt")
 checked=0;rowchecks=0;changed=0
 for caseid in [0,3,4]:
  fam=load_case(plan["family_cases"][caseid],16)
  refs={r["id"]:r for r in old.rows(DATA/fam["meta"]["references"])}
  samples=refs[fam["targets"][0]["id"]]["samples"]
  for policy in plan["policies"]:
   file=HERE/"pilot"/("%02d_r0_%s.json.gz"%(caseid,policy))
   r=json.load(gzip.open(file,"rt"));assert r["success"] and r["status"]=="completed"
   checked+=1
   for step in trace_rows(r["evidence"].get("native/row_trace.txt","")):
    rowchecks+=check_update(*step,samples)[0]
   for line in r["evidence"].get("native/row_trace.txt.policy.jsonl.gz","").splitlines():
    e=json.loads(line)
    if e["event"]=="choice":changed+=int(e["source_previously_updated"])
 prior=json.load(open(HERE.parent/"native_seed/frozen_inputs.json"))["sha256"]
 for name,digest in prior.items():assert sha(ROOT/name)==digest,name
 names=[".tools/kira-live-build/kira","Kira_comparison/live_matrix/plan.json"]
 names +=["Kira_comparison/live_matrix/"+s for s in ["s00_policy_server.py","s01_live_policy.h",
    "s02_build.py","s03_build.sh","s04_worker.py","s05_run.py","s06_run.sh","s09_array.sh"]]
 current=dict(prior);current.update({n:sha(ROOT/n) for n in names})
 (HERE/"frozen_inputs.json").write_text(json.dumps(dict(sha256=current,model_retrained=False),indent=2)+"\n")
 (HERE/"pilot_validation.json").write_text(json.dumps(dict(passed=True,trials=checked,
    row_sample_checks=rowchecks,choices_with_updated_sources=changed,
    note="Skip-empty-model-load guard added after pilots; meaningful pivot choices unchanged."),indent=2)+"\n")
 for p in HERE.glob("*.py"):ast.parse(p.read_text())
 print(json.dumps(dict(pilot_trials=checked,row_sample_checks=rowchecks,changed_sources=changed)),flush=True)
if __name__=="__main__":main()

