"""Separate measured stages and family outcomes after exact validation."""
from s01_common import *
import statistics,math
def med(v):return statistics.median(v)
def geo(v):return math.exp(statistics.mean(math.log(x) for x in v))
def summarize(folder):
 summary=read(folder/"summary.json");assert read(folder/"validation.json")["passed"]
 groups=collections.defaultdict(list)
 for p in sorted((folder/"results").glob("*.json.gz")):
  with gzip.open(p,"rt") as f:r=json.load(f)
  groups[r["case"],r["size"],r["policy"]].append(r)
 stages=[]
 for (i,n,policy),rr in sorted(groups.items()):
  if not all(r["success"] and r["resource_status"]=="completed" for r in rr):continue
  c=next(x for x in summary["cases"] if (x["case"],x["size"],x["policy"])==(i,n,policy))
  stage=dict(case=i,family=c["family"],domain=c["domain"],loops=c["loops"],size=n,policy=policy)
  for key,fn in {
   "cold_seconds":lambda r:r["cold_seconds"],
   "input_load_seconds":lambda r:r["input_load_seconds"],
   "model_load_seconds":lambda r:r["model"].get("load_seconds",0),
   "prediction_or_symbolic_preprocessing_seconds":lambda r:r["model"].get("inference_seconds",r["model"].get("preprocess_seconds",0)),
   "solver_seconds":lambda r:sum(a["seconds"] for a in r["attempts"] if "error" not in a),
   "failed_attempt_elapsed_seconds":lambda r:sum(a["seconds"] for a in r["attempts"] if "error" in a),
   "verification_seconds":lambda r:r["verification_seconds"],
   "first_attempt_solver_seconds":lambda r:r["attempts"][0]["seconds"],
   "fallback_solver_seconds":lambda r:sum(a["seconds"] for a in r["attempts"][1:]),
   "completed_preprocessor_targets":lambda r:sum(p["status"]=="complete" for p in r["model"].get("paths",[])),
   "incomplete_preprocessor_targets":lambda r:sum(p["status"]!="complete" for p in r["model"].get("paths",[])),
  }.items():stage[key]=med([fn(r) for r in rr])
  stages.append(stage)
 by_domain=[]
 for c in summary["comparisons"]:
  for domain in sorted({x["domain"] for x in c["pairs_detail"]}):
   pp=[x for x in c["pairs_detail"] if x["domain"]==domain]
   by_domain.append(dict(baseline=c["baseline"],policy=c["policy"],domain=domain,pairs=len(pp),
    cold_geomean_ratio=geo([x["cold_ratio"] for x in pp]),
    prepared_geomean_ratio=geo([x["warm_ratio"] for x in pp]),
    cold_faster=sum(x["cold_ratio"]<1 for x in pp),
    prepared_faster=sum(x["warm_ratio"]<1 for x in pp)))
 native={}
 if folder.name=="native_seed":
  lookup={(x["case"],x["policy"]):x for x in summary["cases"]}
  for c in summary["comparisons"]:
   pairs=[(lookup[x["case"],c["policy"]],lookup[x["case"],c["baseline"]]) for x in c["pairs_detail"]]
   native[c["baseline"]]=dict(pairs=len(pairs),
    summed_initial_equation_ratio=sum(a["initial_generation_counts"] for a,b in pairs)/sum(b["initial_generation_counts"] for a,b in pairs),
    summed_selected_equation_ratio=sum(a["selected_equations"] for a,b in pairs)/sum(b["selected_equations"] for a,b in pairs))
 return dict(stage_medians=stages,domain_comparisons=by_domain,native_work=native)
def main():
 result=dict(main=summarize(HERE),native=summarize(HERE/"native_seed"),
  interpretation="Stage medians are reported separately and need not sum to the median total. Failed native attempt elapsed times include adapter preparation and can overlap model inference; they are separated from completed solver calls. The cold and prepared total times count all work once. Row preprocessing includes learned/local choices AND exact symbolic substitutions. Equation counts do not count internal polynomial arithmetic.")
 write(HERE/"cost_breakdown.json",result)
 print(json.dumps(dict(main_complete_stage_groups=len(result["main"]["stage_medians"]),native_complete_stage_groups=len(result["native"]["stage_medians"]),native_work=result["native"]["native_work"]),indent=2))
if __name__=="__main__":main()
