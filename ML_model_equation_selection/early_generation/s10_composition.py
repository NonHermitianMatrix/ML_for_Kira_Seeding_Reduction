"""Validate early equation filtering together with the existing trained row policy."""
import json,sys
from s04_workflows import HERE,ROOT,setup,cases,reference,workflow,read,guard
from s06_validate import aggregate,rows,compare,method
def main():
 setup();config=json.loads((HERE/"validation/summary.json").read_text());old=json.loads((ROOT/"Kira_comparison/integrated_runtime/deployment.json").read_text())
 for i,(c,n) in enumerate(cases("validation")):
  choice=config["by_topology"][c["topology_group"]]["label"]
  if choice=="early_off":continue
  ref=reference(c,n);policy=method(choice);policy.pop("label")
  rowname=old["row_by_topology"].get(c["topology_group"],dict(model=old["unknown_row_model"]))["model"]
  weights=ROOT/"ML_model_reduction/runtime_training/trajectory_candidates"/rowname/"weights.txt"
  assert weights.is_file(),weights
  methods=[dict(label="native"),dict(label="early",**policy),dict(label="early_row",base="learned",weights=weights,**policy)]
  for rep in range(3):
   ordered=methods[rep%3:]+methods[:rep%3]
   if (i+rep)%2:ordered=list(reversed(ordered))
   for m in ordered:
    out=HERE/"validation/composition"/f'{c["id"]}_n{n}_{m["label"]}_r{rep}.json.gz'
    if out.exists():continue
    r=workflow(c,n,ref=ref,out=out,**m)
    print(json.dumps(dict(case=c["id"],size=n,rep=rep,label=r["label"],seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
 bs=aggregate(rows(HERE/"validation/composition"));routes={}
 for top in config["by_topology"]:
  sub=[b for b in bs if b["topology"]==top]
  if not sub:routes[top]=dict(label="previous",row=False,reason="Early filter did not meet the initial validation conditions.");continue
  early=compare(sub,"early","native");joint=compare(sub,"early_row","native");rowratio=compare(sub,"early_row","early")
  options=[(early,"early"),(joint,"early_row")]
  eligible=[(v,l) for v,l in options if v["fallback_workflows"]==0 and v["complete_seconds"]<.99 and v["equation_preparation_seconds"]<.95]
  eligible.sort(key=lambda z:z[0]["complete_seconds"])
  selected=eligible[0][1] if eligible else "previous"
  routes[top]=dict(label=config["by_topology"][top]["label"] if selected!="previous" else "previous",row=selected=="early_row",comparisons=dict(early=early,early_row=joint,row_increment=rowratio))
 result=dict(by_topology=routes,batches=bs,workflows=len(rows(HERE/"validation/composition")),selection="Choose the least complete-time eligible configuration after repeated validation, including the existing row model; reserve all fresh test profiles.")
 (HERE/"validation/composition_summary.json").write_text(json.dumps(result,indent=2)+"\n");guard();print(json.dumps(routes,indent=2),flush=True)
if __name__=="__main__":main()
