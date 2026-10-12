"""Summarize complete times without selecting a new policy from the test."""
import json,math,pathlib,statistics
from s02_study import HERE,ROOT,load
def main():
 cases=json.loads((HERE/"cases.json").read_text())["cases"];result=[];allruns=[]
 for c in cases:
  rows=[load(p) for p in sorted((HERE/"model_test").glob(c["id"]+"_*.json.gz"))]
  assert len(rows)==10 and all(r["success"] for r in rows)
  times={k:statistics.median([r["complete_seconds"] for r in rows if r["method"]==k]) for k in ["native","learned"]}
  result.append(dict(case=c["id"],symbolic=bool(c["definition"]["invariants"]),targets=c["size"],
   loops=len(c["definition"]["loop_momenta"]),native_seconds=times["native"],learned_seconds=times["learned"],
   learned_to_native=times["learned"]/times["native"],
   fallback_workflows={k:sum(r["fallback_count"]>0 for r in rows if r["method"]==k) for k in times},
   mean_skipped_calls=statistics.mean(sum(a.get("equation_metrics",{}).get("construction_skipped_calls",0) for a in r["attempts"]) for r in rows if r["method"]=="learned")))
  allruns+=rows
 attempts=[a for r in allruns for a in r["attempts"]]
 summary=dict(cases=result,workflows=len(allruns),targets=sum(c["size"] for c in cases),
  geometric_mean_learned_to_native=math.exp(statistics.mean(math.log(x["learned_to_native"]) for x in result)),
  total_case_median_native=sum(x["native_seconds"] for x in result),
  total_case_median_learned=sum(x["learned_seconds"] for x in result),
  fallback_workflows=sum(r["fallback_count"]>0 for r in allruns),
  rejected_attempts=sum(not a["success"] for a in attempts),
  peak_rss_bytes=max(a["peak_rss_bytes"] for a in attempts),peak_scratch_bytes=max(a["peak_scratch_bytes"] for a in attempts),
  deployment="Frozen default remains unchanged; these transfer tests do not activate an unsupported learned route.",
  verification=json.loads((HERE/"verification.json").read_text()),
  certificates=json.loads((HERE/"optimal_paths/verification.json").read_text()))
 if (HERE/"application/verification.json").exists():summary["application_checks"]=json.loads((HERE/"application/verification.json").read_text())
 (HERE/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 import os;os.environ["MPLCONFIGDIR"]=str(ROOT/".tools/cache/kira-cost-plots")
 import matplotlib;matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 labels=[x["case"].replace("nonplanar_box","NP box").replace("one_mass_box","1-mass box").replace("_"," ") for x in result]
 fig,ax=plt.subplots(figsize=(7.1,4.4),constrained_layout=True);ys=list(range(len(result)))
 ax.plot([x["native_seconds"] for x in result],ys,"o",label="Native")
 ax.plot([x["learned_seconds"] for x in result],ys,"s",label="Frozen filter + fallback")
 ax.set_yticks(ys);ax.set_yticklabels(labels);ax.invert_yaxis();ax.set_xscale("log");ax.set_xlabel("Median complete time (s), five repetitions")
 ax.set_xticks([.7,1,2,4,6]);ax.set_xticklabels(["0.7","1","2","4","6"]);ax.minorticks_off();ax.grid(axis="x",alpha=.25);ax.legend(fontsize=9)
 fig.savefig(ROOT/"report/figures/generalization_times.pdf");plt.close(fig)
 print(json.dumps({k:v for k,v in summary.items() if k not in ["cases","verification","certificates"]}),flush=True)
if __name__=="__main__":main()
