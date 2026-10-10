"""Summarize every frozen trial, preserving failures and grouped paired timing."""
import collections,json,math,pathlib,random,statistics
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def gm(xs):return math.exp(statistics.mean(math.log(x) for x in xs))
def compare(data,a,b,field):
 pairs=[dict(case=r["case"],size=r["size"],group=r["group"],topology=r["topology"],a=r["methods"][a][field],b=r["methods"][b][field]) for r in data if r["methods"][a]["complete_repeats"] and r["methods"][b]["complete_repeats"] and r["methods"][a][field]>0 and r["methods"][b][field]>0]
 groups=collections.defaultdict(list)
 for p in pairs:groups[p["group"]].append(math.log(p["a"]/p["b"]))
 values=[statistics.mean(v) for v in groups.values()]
 if not values:return dict(paired_batches=0)
 rng=random.Random(61010);draws=sorted(math.exp(statistics.mean(rng.choices(values,k=len(values)))) for _ in range(10000))
 return dict(ratio=math.exp(statistics.mean(values)),descriptive_interval=[draws[249],draws[9749]],physical_profiles=len(values),paired_batches=len(pairs),median_time_geomeans=dict(numerator=gm(p["a"] for p in pairs),denominator=gm(p["b"] for p in pairs)))
def main():
 frozen=json.loads((HERE/"pair_freeze.json").read_text());manifest=json.loads((HERE/"reserved_families.json").read_text());cases={c["id"]:c for c in manifest["cases"]}
 data=[];outcomes=collections.Counter();attempt_outcomes=collections.Counter();attempts=0;peaks=dict(tree_rss_bytes=0,scratch_bytes=0)
 for b in manifest["batches"]:
  case=cases[b["case"]];entry=dict(case=case["id"],size=b["size"],group=case["group"],topology=case["topology_group"],methods={})
  for v in frozen["variants"]:
   rr=[]
   for rep in range(frozen["repetitions"]):
    path=HERE/"pair_reserved_test"/f'{case["id"]}_n{b["size"]}_{v}_r{rep}.json.gz';assert path.exists(),path
    r=read_record(path);rr.append(r);outcomes[r["status"]]+=1;attempts+=r["attempt_count"]
    for name in r["attempts"]:
     a=read_record(ROOT/name);attempt_outcomes[a["status"]]+=1
     assert not a.get("mismatches"),name
     peaks["tree_rss_bytes"]=max(peaks["tree_rss_bytes"],a.get("peak_rss_bytes",0))
     peaks["scratch_bytes"]=max(peaks["scratch_bytes"],a.get("peak_scratch_bytes",0))
   entry["methods"][v]=dict(complete_repeats=all(r["success"] and r["reference_checked"] for r in rr),successes=sum(r["success"] for r in rr),fallback_repeats=sum(r["attempt_count"]>1 for r in rr),attempts=sum(r["attempt_count"] for r in rr),
    **{f:statistics.median(r[f] for r in rr) for f in ["complete_seconds","operations","forward_seconds","decision_seconds","equations"]})
  data.append(entry)
 comparisons={}
 for a,b in [("seed","small"),("row","small"),("combined","small"),("combined","seed"),("row","fill_small")]:
  key=a+"_over_"+b;comparisons[key]={}
  for field in ["complete_seconds","operations","forward_seconds","equations"]:
   comparisons[key][field]=dict(all=compare(data,a,b,field),by_topology={t:compare([r for r in data if r["topology"]==t],a,b,field) for t in sorted({r["topology"] for r in data})})
 result=dict(planned=frozen["planned"],observed=sum(outcomes.values()),outcomes=dict(outcomes),attempts=attempts,attempt_outcomes=dict(attempt_outcomes),peaks=peaks,batches=data,comparisons=comparisons,
  inference="Ratios below one indicate lower measured cost. Intervals resample eight physical profiles and are descriptive; topology intervals use only two profiles. No test data selected models.")
 assert result["observed"]==result["planned"]
 (HERE/"pair_reserved_summary.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:v["complete_seconds"] for k,v in comparisons.items()},indent=2),flush=True)
if __name__=="__main__":main()
