"""Matched complete-time ratios and exactness summaries."""
import random,statistics
from s00_contract import *
from s02_study import med,check_freeze
def compare(rows,num,den,key):
 groups=sorted({r["input"] for r in rows})
 values=[med(rows,num,g,key)/med(rows,den,g,key) for g in groups]
 rng=random.Random(34719)
 samples=sorted(math.exp(sum(math.log(rng.choice(values)) for _ in values)/len(values)) for k in range(6000))
 return dict(ratio=math.exp(sum(map(math.log,values))/len(values)),interval95=[samples[149],samples[5849]],groups=len(groups))
def main():
 check_freeze();audit=json.loads((HERE/"model_test/audit.json").read_text());assert audit["all_exact"] and audit["workflows"]==200
 rows=[json.loads(p.read_text()) for p in (HERE/"model_test/results").glob("*.json")]
 selected=json.loads((HERE/"deployment.json").read_text())["mode"];methods=["baseline","model","direct_model","direct_extreme","direct_analytic"]
 comparisons={}
 for m in methods[1:]:
  comparisons[m+"_vs_baseline"]={k:compare(rows,m,"baseline",k) for k in ["complete_seconds","external_seconds"]}
 for c in ["direct_extreme","direct_analytic"]:
  comparisons["direct_model_vs_"+c]={k:compare(rows,"direct_model",c,k) for k in ["complete_seconds","external_seconds"]}
 groups=[]
 for g in sorted({r["input"] for r in rows}):
  requests=json.loads((HERE/g).read_text())["requests"]
  d=dict(input=g,profiles=len(requests),targets=sum(len(c["targets"]) for c in requests),max_power=max(sum(b) for c in requests for b in c["targets"]),medians={m:{key:med(rows,m,g,key) for key in ["complete_seconds","external_seconds"]} for m in methods})
  d["stages"]={}
  for m in methods:
   rr=[r for r in rows if r["method"]==m and r["input"]==g]
   d["stages"][m]={k:statistics.median(r.get(k,0) for r in rr) for k in ["model_load_seconds","selection_seconds","contraction_seconds","oracle_seconds","verification_seconds","substitution_seconds","parse_seconds"]}
   d["stages"][m]["kira_seconds"]=statistics.median(r.get("algebra",{}).get("seconds",0) for r in rr)
  groups.append(d)
 summary=dict(all_exact=True,applications=len(rows),validation_applications=90,pilot_applications=8,selected=selected,comparisons=comparisons,groups=groups,scope="coupled scalar vacuum with unit massless powers, 2-4 distinct positive mass ratios, supplied exact Euler and mass identities",model_retrained=False,selection_frozen_before_test=True,coefficient_audit=audit,fallbacks=sum(r["fallbacks"] for r in rows),maximum_sampled_kira_rss_bytes=max(r.get("algebra",{}).get("peak_tree_rss_bytes",0) for r in rows))
 base.write(HERE/"model_test/summary.json",summary);print(json.dumps({k:summary[k] for k in ["applications","selected","comparisons"]},indent=2),flush=True)
if __name__=="__main__":main()
