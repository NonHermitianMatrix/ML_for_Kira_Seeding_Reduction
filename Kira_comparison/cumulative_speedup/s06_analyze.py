"""Report direct cumulative ratios and absolute times on the same cases."""
from s00_cumulative import *
METRICS=["complete_seconds","external_seconds","read_seconds","roundtrip_seconds"]
def compare(groups,left,right,metric):
 ratios=[g["medians"][left][metric]/g["medians"][right][metric] for g in groups]
 logs=list(map(math.log,ratios));rng=random.Random(611875)
 boot=sorted(math.exp(sum(rng.choice(logs) for _ in logs)/len(logs)) for k in range(10000))
 ratio=math.exp(sum(logs)/len(logs));lo,hi=boot[249],boot[9749]
 return dict(time_ratio=ratio,ratio_interval95=[lo,hi],speedup=1/ratio,speedup_interval95=[1/hi,1/lo],time_saved_percent=100*(1-ratio),batch_ratios=ratios)
def main():
 check_freeze();audit=read(HERE/"test/audit.json");assert audit["all_exact"]
 rows=[read(p) for p in (HERE/"test/results").glob("*.json")]
 groups=[]
 for inp in sorted((HERE/"test/inputs").glob("*.json")):
  req=read(inp)["requests"]
  med={a:{m:statistics.median(r[m] for r in rows if r["input"]==inp.name and r["arm"]==a) for m in METRICS} for a in ARMS}
  groups.append(dict(input=inp.name,max_power=max(sum(b) for c in req for b in c["targets"]),targets=sum(len(c["targets"]) for c in req),medians=med))
 comparisons={right:{m:compare(groups,"final",right,m) for m in METRICS} for right in ["original_kira","chain_baseline"]}
 totals={a:{m:sum(g["medians"][a][m] for g in groups) for m in METRICS} for a in ARMS}
 summary=dict(all_exact=True,audit=audit,groups=groups,comparisons=comparisons,sum_of_batch_medians=totals,primary_metric="roundtrip_seconds",definition="Geometric mean of within-batch median time ratios; descriptive 95% interval resamples eight batches 10000 times.",source_commit=read(HERE/"freeze.json")["source_commit"],resource_plan=read(HERE/"resource_plan.json"))
 write(HERE/"test/summary.json",summary)
 print(json.dumps(dict(comparisons=comparisons,totals=totals),indent=2),flush=True)
if __name__=="__main__":main()
