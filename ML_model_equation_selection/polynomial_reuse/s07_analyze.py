"""Separate arithmetic and process-reuse effects in the complete measurements."""
import random,statistics
from s04_study import *
def ratio(rows,num,den,key):
 groups=sorted({r["input"] for r in rows});values=[median(rows,g,num,key)/median(rows,g,den,key) for g in groups]
 rng=random.Random(913337);boot=sorted(math.exp(sum(math.log(rng.choice(values)) for _ in values)/len(values)) for i in range(6000))
 return dict(ratio=math.exp(sum(map(math.log,values))/len(values)),interval95=[boot[149],boot[5849]],groups=len(values))
def main():
 audit=json.loads((HERE/"model_test/audit.json").read_text());assert audit["all_exact"]
 rows=read_rows("model_test");selected=json.loads((HERE/"deployment.json").read_text())["variant"]
 comparisons={v:{k:ratio(rows,v,"baseline",k) for k in ["complete_seconds","external_seconds","oracle_seconds","substitution_seconds"]} for v in ["transforms","taylor","both"]}
 groups=[]
 for g in sorted({r["input"] for r in rows}):
  requests=json.loads((HERE/g).read_text())["requests"]
  groups.append(dict(input=g,targets=sum(len(c["targets"]) for c in requests),maximum_power=max(sum(b) for c in requests for b in c["targets"]),medians={v:{k:median(rows,g,v,k) for k in ["complete_seconds","external_seconds","oracle_seconds","substitution_seconds"]} for v in ["baseline","transforms","taylor","both"]}))
 sr=[json.loads(p.read_text()) for p in (HERE/"model_test/streams").glob("*.json")];assert len(sr)==36 and all(r["success"] for r in sr)
 sequences=[]
 for i in range(3):
  rr=[r for r in sr if r["sequence"]==i]
  medians={m:statistics.median(r["external_seconds"] for r in rr if r["mode"]==m) for m in ["baseline_cold","baseline_stream","optimized_cold","optimized_stream"]}
  sequences.append(dict(sequence=i,requests=rr[0]["requests"],median_external_seconds=medians))
 comparisons_stream={}
 for name,numerator,denominator in [("combined_vs_previous","optimized_stream","baseline_cold"),("worker_reuse_only","optimized_stream","optimized_cold"),("arithmetic_in_stream","optimized_stream","baseline_stream")]:
  values=[x["median_external_seconds"][numerator]/x["median_external_seconds"][denominator] for x in sequences]
  comparisons_stream[name]=dict(ratio=math.exp(sum(map(math.log,values))/len(values)),sequence_ratios=values,note="Descriptive ratios for three specified, overlapping input sequences; no statistical interval.")
 summary=dict(all_exact=True,selected=selected,model_retrained=False,single_applications=160,stream_applications=192,stream_runs=36,validation_applications=48,comparisons=comparisons,groups=groups,sequences=sequences,stream_comparisons=comparisons_stream,audit=audit)
 base.write(HERE/"model_test/summary.json",summary)
 print(json.dumps({k:summary[k] for k in ["selected","comparisons","stream_comparisons"]},indent=2),flush=True)
if __name__=="__main__":main()
