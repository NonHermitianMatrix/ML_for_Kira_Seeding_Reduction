"""Summarize frozen complete timings, decoding costs and model comparisons."""
from s16_reader_study import *
def compare(rows,left,right,metric):
 groups=sorted({r["input"] for r in rows});rat=[]
 for g in groups:
  a=statistics.median(r[metric] for r in rows if r["input"]==g and r["arm"]==left)
  b=statistics.median(r[metric] for r in rows if r["input"]==g and r["arm"]==right);rat.append(a/b)
 logs=list(map(math.log,rat));rng=random.Random(788123);boot=sorted(math.exp(sum(rng.choice(logs) for _ in logs)/len(logs)) for k in range(4000))
 return dict(ratio=math.exp(sum(logs)/len(logs)),interval95=[boot[99],boot[3899]],batch_ratios=rat)
def main():
 check_freeze();audit=read(HERE/"reader_final_test/audit.json");assert audit["all_exact"]
 rows=[read(p) for p in (HERE/"reader_final_test/results").glob("*.json")];armnames=sorted({r["arm"] for r in rows});metrics=["complete_seconds","external_seconds","roundtrip_seconds","read_seconds"]
 comparisons={a:{k:compare(rows,a,"baseline",k) for k in metrics} for a in armnames if a!="baseline"}
 dep=read(HERE/"reader_final_deployment.json");fixed="native_binary" if dep["best_fixed_policy"]=="extreme" else "native_binary_"+dep["best_fixed_policy"]
 model_vs_fixed={k:compare(rows,"learned",fixed,k) for k in metrics}
 deployed=dep["mode"]+("_"+dep["policy"] if dep["policy"] and dep["policy"]!="extreme" else "")
 assert deployed in armnames
 groups=[]
 for inp in sorted({r["input"] for r in rows}):
  med={a:{k:statistics.median(r[k] for r in rows if r["input"]==inp and r["arm"]==a) for k in metrics} for a in armnames}
  sizes={a:statistics.median(r["coefficient_bytes"] for r in rows if r["input"]==inp and r["arm"]==a) for a in armnames}
  groups.append(dict(input=inp,medians=med,coefficient_bytes=sizes))
 streams=[read(p) for p in (HERE/"reader_final_test/streams").glob("*.json")];assert len(streams)==36
 seqs=[]
 for seq in range(3):
  med={a:{k:statistics.median(r[k] for r in streams if r["sequence"]==seq and r["arm"]==a) for k in ["external_seconds","roundtrip_seconds"]} for a in ["baseline","native","learned","deployed"]}
  seqs.append(dict(sequence=seq,medians=med))
 sr={a:{k:math.exp(sum(math.log(s["medians"][a][k]/s["medians"]["baseline"][k]) for s in seqs)/len(seqs)) for k in ["external_seconds","roundtrip_seconds"]} for a in ["native","learned","deployed"]}
 # Descriptive route-label agreement; fastest measured policy is a noisy reference.
 validation=[read(p) for p in (HERE/"reader_validation/results").glob("*.json")]
 correct=0;regrets=[];n=0
 for inp in sorted({r["input"] for r in validation}):
  candidates=["native_binary"]+["native_binary_"+p for p in POLICIES if p!="extreme"]
  costs={a:statistics.median(r["roundtrip_seconds"] for r in validation if r["input"]==inp and r["arm"]==a) for a in candidates}
  route=next(r["route"] for r in validation if r["input"]==inp and r["arm"]=="learned");arm="native_binary" if route=="extreme" else "native_binary_"+route
  correct+=arm==min(costs,key=costs.get);regrets.append(costs[arm]/min(costs.values()));n+=1
 summary=dict(all_exact=True,audit=audit,deployment=dep,deployed_arm=deployed,comparisons=comparisons,model_vs_best_fixed=model_vs_fixed,groups=groups,sequences=seqs,stream_ratios=sr,
  validation_policy_agreement=dict(batches=n,fastest_candidate_matches=correct,geometric_measured_cost_ratio=math.exp(sum(map(math.log,regrets))/len(regrets)),note="Descriptive validation label comparison, affected by timing noise; no proof of optimality."),
  resource_plan=read(HERE/"resource_plan.json"),training=read(HERE/"training/model_check.json"))
 summary["reader_comparison"]=read(HERE/"reader_final_test/reader_comparison.json")
 write(HERE/"reader_final_test/summary.json",summary)
 print(json.dumps(dict(deployed=deployed,comparisons=comparisons,model_vs_fixed=model_vs_fixed,streams=sr),indent=2),flush=True)
if __name__=="__main__":main()
