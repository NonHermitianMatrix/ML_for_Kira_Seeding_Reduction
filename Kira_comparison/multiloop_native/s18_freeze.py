"""Select seed settings on validation and freeze all final scientific inputs."""
import datetime,hashlib,json,math,pathlib,statistics
from s04_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=HERE/"freeze.json";assert not out.exists()
 assert json.loads((HERE/"runtime_check.json").read_text())["all_passed"]
 assert len(list((HERE/"rollouts").glob("*_summary.json.gz")))==9
 model=ROOT/"ML_model_reduction/cost_training"
 assert "remaining" in json.loads((model/"trained_model.json").read_text())["kind"]
 val=[]
 for p in (HERE/"validation_final").glob("*.json.gz"):
  if "_monitor." not in p.name:val.append(read_record(p))
 assert len(val)==140 and all(r["success"] for r in val),(len(val),sum(r["success"] for r in val))
 candidates=["seed_safe","seed_full_safe","seed_full_low_safe"];scores=[]
 for policy in candidates:
  cases={}
  for case in sorted({r["case"] for r in val}):
   ratios=[]
   for size in sorted({r["size"] for r in val if r["case"]==case}):
    a=[r for r in val if r["case"]==case and r["size"]==size and r["policy"]==policy]
    b=[r for r in val if r["case"]==case and r["size"]==size and r["policy"]=="native"]
    assert len(a)==len(b)==2 and all(r["success"] for r in a+b),(policy,case,size)
    ratios.append(math.log(statistics.median(r["complete_seconds"] for r in a)/statistics.median(r["complete_seconds"] for r in b)))
   cases[case]=sum(ratios)/len(ratios)
  assert len(cases)==3
  scores.append(dict(policy=policy,geometric_ratio=math.exp(sum(cases.values())/len(cases))))
 seed=min(scores,key=lambda x:x["geometric_ratio"])["policy"]
 closure="closure_full_safe" if "_full_" in seed else "closure_safe"
 combined={"seed_safe":"combined_safe","seed_full_safe":"combined_full_safe","seed_full_low_safe":"combined_full_low_safe"}[seed]
 policies=["stock","native","tight","row_full",closure,seed,combined,"split_native","split_combined_safe"]
 paths=[p for p in list(HERE.glob("s*.py"))+list(HERE.glob("s*.sh")) if int(p.name[1:3])<=24]+[HERE/"families.json",HERE/"resource_plan.json",HERE/"family_audit.json"]
 paths+=list(model.glob("s*.py"))+list(model.glob("s*.h"))+[model/"trained_model.json",model/"trained_weights.txt",model/"training_results.json",model/"build.json",model/"tree_build.json",model/"tree_promotion.json",HERE/"runtime_check.json"]
 paths+=[ROOT/"Kira_comparison/acceleration/s01_fast_seed.py",ROOT/"Kira_comparison/acceleration/seed_export.json",
  ROOT/"Kira_comparison/acceleration/seed_weights.npz",ROOT/".tools/kira-cost-tree/kira",ROOT/".tools/kira-fast-expression/kira"]
 manifest={str(p.relative_to(ROOT)):sha(p) for p in paths}
 record=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=manifest,
  policies=policies,seed_policy=seed,closure_control=closure,combined_policy=combined,validation_seed_scores=scores,
  repeats=3,sizes=[32,128],timeout_seconds=300,reference_timeout_seconds=450,
  order="case-size dependent cyclic order, reversed on alternate repetitions",
  stop_rule="after a failed measured trial, later repetitions for that policy and batch are explicitly skipped",
  reference_rule="stock conservative bounds, same prescribed basis and exact reference for all policies within a batch",
  larger_bound_check="16 fixed targets per reserved case, stock margin 2 with a 300 second cap",
  trained_and_reserved_cases_disjoint=True,test_results_do_not_select_policies=True)
 out.write_text(json.dumps(record,indent=2)+"\n");print(json.dumps({k:record[k] for k in ["policies","validation_seed_scores"]}),flush=True)
if __name__=="__main__":main()
