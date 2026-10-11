"""Audit every saved packed result against the independent original loop oracle."""
import statistics
from s00_common import *
from s10_analyze import object_read,interval
def main():
 stage=HERE/"model_test";records=[json.loads(p.read_text()) for p in (stage/"pack_results").glob("*.json") if "_part" not in p.name]
 assert len(records)==80 and all(x["success"] and x["fallbacks"]==0 for x in records)
 policy=json.loads((HERE/"trained_model/deployment.json").read_text());control=policy["control"]
 groups=sorted(set(x["input"] for x in records));checked=set();checks=0
 for x in records:
  if not x["packed"]:continue
  cp=x["coefficients_sha256"]
  if cp in checked:continue
  checked.add(cp);data=object_read(cp)
  requests=json.loads((HERE/x["input"]).read_text())["requests"]
  for c in requests:
   for L,rows in data["coefficients"][c["id"]].items():
    for b,row in zip(c["targets"],decode(rows)):
     assert row==old.oracle(int(L),c["mass_ratios"],b);checks+=len(row)
 med={}
 for mode in ["model",control]:
  for packed in [True,False]:
   key=mode+("_packed" if packed else "_separate")
   med[key]={g:{f:statistics.median(x["algebra"]["seconds"] if f=="kira_seconds" else x[f] for x in records if x["input"]==g and x["mode"]==mode and x["packed"]==packed) for f in ["complete_seconds","external_seconds","kira_seconds"]} for g in groups}
 comparisons={}
 for a,b in [("model_packed","model_separate"),("model_packed",control+"_packed"),(control+"_packed",control+"_separate")]:
  comparisons[a+"_vs_"+b]={f:interval([med[a][g][f]/med[b][g][f] for g in groups]) for f in ["complete_seconds","external_seconds","kira_seconds"]}
 result=dict(all_exact=True,workflows=len(records),kira_calls=sum(1 if x["packed"] else 3 for x in records),unique_coefficient_objects=len(checked),independent_loop_coefficient_checks=checks,groups=len(groups),families_per_group=3,comparisons=comparisons,case_medians=med,peak_kira_tree_rss_bytes=max(x["algebra"]["peak_tree_rss_bytes"] for x in records),peak_kira_scratch_bytes=max(x["algebra"]["peak_scratch_bytes"] for x in records))
 write(stage/"pack_summary.json",result);print(json.dumps({k:result[k] for k in ["all_exact","workflows","comparisons","independent_loop_coefficient_checks"]},indent=2))
if __name__=="__main__":main()
