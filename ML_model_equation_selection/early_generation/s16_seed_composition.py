"""Measure the existing seed model with early filtering before release selection."""
import json,os,sys
from s04_workflows import HERE,ROOT,setup,cases,reference,workflow,read,guard
from s06_validate import aggregate,rows,compare,method
def main():
 setup()
 sys.path.insert(0,str(ROOT/"Kira_comparison/integrated_runtime"))
 from s108_reduce import select
 initial=json.loads((HERE/"validation/summary.json").read_text())
 prior=json.loads((HERE/"validation/composition_summary.json").read_text())
 for i,(c,n) in enumerate(cases("validation")):
  choice=initial["by_topology"][c["topology_group"]]["label"]
  if choice=="early_off":continue
  ref=reference(c,n);policy=method(choice);policy.pop("label")
  variant,threshold=select(c,n,"both");name=variant.split(":")[1]
  weights=ROOT/"ML_model_reduction/runtime_training/trajectory_candidates"/name/"weights.txt"
  os.environ["KIRA_SEED_THRESHOLD"]=str(threshold)
  methods=[dict(label="native"),dict(label="early",**policy),dict(label="early_seed",base="seed_closed",**policy),dict(label="early_both",base="combined_closed",weights=weights,**policy)]
  for rep in range(3):
   ordered=methods[rep%4:]+methods[:rep%4]
   if (i+rep)%2:ordered=list(reversed(ordered))
   for m in ordered:
    out=HERE/"validation/seed_composition"/f'{c["id"]}_n{n}_{m["label"]}_r{rep}.json.gz'
    if out.exists():continue
    r=workflow(c,n,ref=ref,out=out,**m)
    print(json.dumps(dict(case=c["id"],size=n,rep=rep,label=r["label"],seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
 bs=aggregate(rows(HERE/"validation/seed_composition"));routes={}
 for top in initial["by_topology"]:
  sub=[b for b in bs if b["topology"]==top]
  if not sub:routes[top]=dict(label="previous",row=False,seed=False);continue
  checks={l:compare(sub,l,"native") for l in ["early","early_seed","early_both"]}
  increments={l:compare(sub,l,"early") for l in ["early_seed","early_both"]}
  # Require at least one percent incremental saving before adding another policy.
  eligible=[(checks["early"]["complete_seconds"],"early")]
  for label in ["early_seed","early_both"]:
   v=checks[label]
   if v["fallback_workflows"]==0 and v["complete_seconds"]<.99 and increments[label]["complete_seconds"]<.99:
    eligible.append((v["complete_seconds"],label))
  chosen=min(eligible)[1]
  if checks[chosen]["fallback_workflows"] or checks[chosen]["complete_seconds"]>=.99 or checks[chosen]["equation_preparation_seconds"]>=.95:chosen="previous"
  row_only=prior["by_topology"][top].get("comparisons",{}).get("row_increment")
  if chosen=="early" and row_only and row_only["fallback_workflows"]==0 and row_only["complete_seconds"]<.99:chosen="early_row"
  routes[top]=dict(label=initial["by_topology"][top]["label"] if chosen!="previous" else "previous",row=chosen in ["early_both","early_row"],seed=chosen in ["early_seed","early_both"],selected_combination=chosen,comparisons=checks,incremental_comparisons=increments)
 result=dict(by_topology=routes,batches=bs,workflows=len(rows(HERE/"validation/seed_composition")),rule="Use a learned early filter only with complete-time saving above one percent and preparation saving above five percent. Add existing seed/row policies only with at least one percent incremental validation saving and no fallback. Choose the lowest eligible complete cost.")
 (HERE/"validation/final_selection.json").write_text(json.dumps(result,indent=2)+"\n");guard();print(json.dumps(routes,indent=2),flush=True)
if __name__=="__main__":main()
