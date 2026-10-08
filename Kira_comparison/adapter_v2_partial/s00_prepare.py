"""Freeze outcome-independent held-out cases, models, and resource limits."""
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(s):return hashlib.sha256(("kira-cost-v1:"+s).encode()).hexdigest()
def main():
 m=json.loads((ROOT/"ML_model_seed_selection/split_manifest.json").read_text())
 groups={}
 for x in m["families"]:
  if x["split"]!="test":continue
  domain="vacuum" if x["family"].startswith("vacuum_") else x["family"].split("_")[0]
  groups.setdefault((domain,x["loops"]),[]).append(x)
 selected=[]
 for (domain,loops),items in sorted(groups.items()):
  if domain=="box":
   order=sorted(items,key=lambda x:(x["counts"]["candidate_seed_labels"]/x["counts"]["targets"],key(x["family"])))
   chosen=[order[i] for i in sorted(set([0,len(order)//2,len(order)-1]))]
  else:chosen=[min(items,key=lambda x:key(x["family"]))]
  for x in chosen:selected.append(dict(meta=x,domain=domain))
 plan=dict(schema=2,selection="one SHA256-ranked family per domain/loop; three box candidate-pool size strata; nested SHA256-ranked target prefixes",
  family_cases=selected,batch_sizes=[1,4,16],repetitions=3,
  policies=["kira_pool","ml_seeds","ml_reduction","local_reduction"],
  native_policies=["kira_native","kira_native_trim"],
  threshold=0.5,timeout_seconds=180,case_scratch_limit=33554432,
  result_limit=25165824,work_limit=100663296,virtual_memory_bytes=1610612736,
  seed_model_sha256=sha(ROOT/"ML_model_seed_selection/trained_model.pt"),
  reduction_model_sha256=sha(ROOT/"ML_model_reduction/trained_model.pt"),
  split_sha256=sha(ROOT/"ML_model_seed_selection/split_manifest.json"),
  kira_binary_sha256=sha(ROOT/".tools/kira/bin/kira"),
  source_commit="5760f42f8decd7eb5474c780db75b5e5e7b450a0",
  previous_conservative_total_bytes=9727848960,
  comparison_total_upper_bytes=9727848960+3*25165824+100663296+16777216,
  purpose="Measure actual complete symbolic reductions and costs; no retraining, no held-out threshold fitting.")
 assert plan["comparison_total_upper_bytes"]<10000000000
 out=HERE/"plan.json"
 if out.exists():assert json.loads(out.read_text())==plan
 else:out.write_text(json.dumps(plan,indent=2)+"\n")
 print(json.dumps(dict(families=len(selected),upper_bytes=plan["comparison_total_upper_bytes"])))
if __name__=="__main__":main()
