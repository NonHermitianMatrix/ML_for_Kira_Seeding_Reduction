"""Summarize matched repetitions, resource outcomes and distinct cost measures."""
from s01_common import *
import math,statistics
HERE=HERE/"native_seed"
def median(v):return statistics.median(v) if v else None
def mean(v):return statistics.mean(v) if v else None
def geo(v):return math.exp(mean([math.log(x) for x in v])) if v else None
def counter(r,key):
 return sum(a["counters"].get(key,[0])[-1] if a["counters"].get(key) else 0 for a in r.get("attempts",[]))
def main():
 assert read(HERE/"validation.json")["passed"]
 plan=read(HERE/"plan.json");records=[]
 for p in sorted((HERE/"results").glob("*.json.gz")):
  with gzip.open(p,"rt") as f:r=json.load(f)
  r.pop("evidence",None);records.append(r)
 groups=collections.defaultdict(list)
 for r in records:groups[(r["case"],r["size"],r["policy"])].append(r)
 cases=[]
 for (i,n,policy),rr in sorted(groups.items()):
  c=plan["family_cases"][i];ok=all(r["success"] and r["resource_status"]=="completed" for r in rr)
  result=dict(case=i,family=c["meta"]["family"],domain=c["domain"],loops=c["meta"]["loops"],size=n,policy=policy,
   repeats=len(rr),complete_repeats=sum(r["success"] and r["resource_status"]=="completed" for r in rr),all_complete=ok,
   cold_seconds=median([r["cold_seconds"] for r in rr]),peak_rss_bytes=max(r["process_tree_peak_rss_bytes"] for r in rr),
   statuses=dict(collections.Counter(r["resource_status"] for r in rr)))
  if ok:
   result.update(warm_seconds=median([r["warm_with_verification_seconds"] for r in rr]),
    verification_seconds=median([r["verification_seconds"] for r in rr]),
    load_seconds=median([r["model"].get("load_seconds",0) for r in rr]),
    model_seconds=median([r["model"].get("inference_seconds",r["model"].get("preprocess_seconds",0)) for r in rr]),
    kira_seconds=median([sum(a["seconds"] for a in r["attempts"]) for r in rr]),
    selected_equations=median([counter(r,"selected_equations") for r in rr]),
    triangular_insertions=median([sum(sum(a["counters"].get("forward_insertions",[])) for a in r["attempts"]) for r in rr]),
    first_selected_equations=median([r["attempts"][0]["counters"]["selected_equations"][-1] if r["attempts"][0]["counters"]["selected_equations"] else 0 for r in rr]),
    fallback_repeats=sum(r["fallback"] for r in rr),
    first_attempt_complete_repeats=sum(r["first_attempt_complete"] for r in rr),
    coefficient_field_operations=median([r["model"].get("coefficient_field_operations",0) for r in rr]),
    feature_trial_field_operations=median([r["model"].get("feature_trial_field_operations",0) for r in rr]))
   if "native" not in policy:
    result["source_equations"]=median([sum(a["source_equations"] for a in r["attempts"]) for r in rr])
    result["first_source_equations"]=median([r["attempts"][0]["source_equations"] for r in rr])
    result["source_terms"]=median([sum(a["source_terms"] for a in r["attempts"]) for r in rr])
   if policy=="ml_native_seeds":
    result["selected_seeds"]=median([r["model"]["selected"] for r in rr])
    result["candidate_seeds"]=rr[0]["model"]["candidates"]
  cases.append(result)
 lookup={(c["case"],c["size"],c["policy"]):c for c in cases}
 comparisons=[]
 for base in ["kira_native","kira_native_trim"]:
  for policy in ["ml_native_seeds"]:
   if policy==base:continue
   paired=[]
   for c in cases:
    if c["policy"]!=policy:continue
    b=lookup.get((c["case"],c["size"],base))
    if b is None or not c["all_complete"] or not b["all_complete"]:continue
    pair=dict(case=c["case"],size=c["size"],domain=c["domain"],loops=c["loops"],
      cold_ratio=c["cold_seconds"]/b["cold_seconds"],warm_ratio=c["warm_seconds"]/b["warm_seconds"],
      rss_ratio=c["peak_rss_bytes"]/b["peak_rss_bytes"],selected_equation_ratio=c["selected_equations"]/max(1,b["selected_equations"]))
    paired.append(pair)
   outcomes=dict(eligible_cases=0,both_complete=0,baseline_incomplete_policy_complete=0,
     policy_incomplete_baseline_complete=0,both_incomplete=0,timeout_elapsed_over_policy_time=[])
   for c in cases:
    if c["policy"]!=policy:continue
    b=lookup.get((c["case"],c["size"],base))
    if b is None:continue
    outcomes["eligible_cases"]+=1
    tag=("both_complete" if c["all_complete"] and b["all_complete"] else
      "baseline_incomplete_policy_complete" if c["all_complete"] else
      "policy_incomplete_baseline_complete" if b["all_complete"] else "both_incomplete")
    outcomes[tag]+=1
    if c["all_complete"] and b["statuses"].get("timeout",0)==b["repeats"]:
     outcomes["timeout_elapsed_over_policy_time"].append(dict(case=c["case"],size=c["size"],
       limit_over_learned_time=b["cold_seconds"]/c["cold_seconds"]))
   if paired:
    comparisons.append(dict(baseline=base,policy=policy,pairs=len(paired),
     cold_geomean_ratio=geo([x["cold_ratio"] for x in paired]),warm_geomean_ratio=geo([x["warm_ratio"] for x in paired]),
     cold_faster=sum(x["cold_ratio"]<1 for x in paired),warm_faster=sum(x["warm_ratio"]<1 for x in paired),
     rss_geomean_ratio=geo([x["rss_ratio"] for x in paired]),
     equation_geomean_ratio=geo([x["selected_equation_ratio"] for x in paired if x["selected_equation_ratio"]>0]),
     pairs_detail=paired,outcomes=outcomes))
 totals={p:dict(trials=sum(r["policy"]==p for r in records),
  complete=sum(r["policy"]==p and r["success"] and r["resource_status"]=="completed" for r in records),
  fallback_trials=sum(r["policy"]==p and r.get("fallback",False) for r in records)) for p in sorted({r["policy"] for r in records})}
 write(HERE/"summary.json",dict(trials=len(records),family_cases=len(plan["family_cases"]),batch_cases=len({(r["case"],r["size"]) for r in records}),
  unique_targets=sum(min(16,c["meta"]["counts"]["targets"]) for c in plan["family_cases"]),
  totals=totals,cases=cases,comparisons=comparisons,validation_sha256=sha(HERE/"validation.json"),
  scope="fixed stored IBP pools at loops 1--12; native Kira only for independent bases; field-operation counts exclude polynomial internals"))
 print(json.dumps(dict(trials=len(records),totals=totals,comparisons=[{k:v for k,v in c.items() if k!="pairs_detail"} for c in comparisons]),indent=2))
if __name__=="__main__":main()
