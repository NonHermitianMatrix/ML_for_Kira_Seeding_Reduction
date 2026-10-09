"""Report all completions and group-resampled paired complete-time ratios."""
import argparse,collections,gzip,hashlib,json,math,pathlib,random,statistics
HERE=pathlib.Path(__file__).resolve().parent
from s13_records import read_record
def read(p):return json.loads(p.read_text())
def good(r):return r["status"]=="completed" and r["success"]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--stage",required=True);a=ap.parse_args()
 plan=read(HERE/"plan.json");audit=read(HERE/(a.stage+"_validation.json"));assert audit["passed"]
 records=[]
 for p in sorted((HERE/a.stage).glob("*.json.gz")):
  records.append(read_record(p))
 assert len(records)==audit["trials"]
 groups=collections.defaultdict(list)
 for r in records:groups[r["case"],r["size"],r["policy"]].append(r)
 cases=[]
 for case,size in sorted({(r["case"],r["size"]) for r in records}):
  meta=plan[a.stage][case]["meta"];entry=dict(case=case,size=size,family=meta["family"],group=meta["group"],methods={})
  for policy in plan["policies"]:
   rows=groups[case,size,policy];complete=[r for r in rows if good(r)];reps=plan["repetitions"] if a.stage=="test" else 1
   assert {r["repetition"] for r in rows}==set(range(reps))
   entry["methods"][policy]=dict(planned=len(rows),executed=sum(r.get("measured",True) for r in rows),exact=len(complete),
    full_pair=len(complete)==reps,fallbacks=sum(r.get("fallback",False) for r in complete),
    median_seconds=statistics.median(r["cold_seconds"] for r in complete) if len(complete)==reps else None,
    median_kira_seconds=statistics.median(sum(x.get("seconds",0) for x in r["attempts"]) for r in complete) if len(complete)==reps else None,
    median_equations=statistics.median(r["attempts"][-1]["source_equations"] for r in complete) if len(complete)==reps else None)
  cases.append(entry)
 def compare(num,den,size):
  pairs=[];lost=[];gained=[]
  for c in cases:
   if size is not None and c["size"]!=size:continue
   x,y=c["methods"][num],c["methods"][den]
   if x["full_pair"] and y["full_pair"]:pairs.append(dict(case=c["case"],size=c["size"],group=c["group"],ratio=x["median_seconds"]/y["median_seconds"],numerator_seconds=x["median_seconds"],denominator_seconds=y["median_seconds"]))
   elif y["full_pair"]:lost.append(dict(case=c["case"],size=c["size"]))
   elif x["full_pair"]:gained.append(dict(case=c["case"],size=c["size"]))
  ratio=interval=None;gm_num=gm_den=None
  if pairs:
   ratio=math.exp(statistics.mean(math.log(p["ratio"]) for p in pairs))
   gm_num=math.exp(statistics.mean(math.log(p["numerator_seconds"]) for p in pairs))
   gm_den=math.exp(statistics.mean(math.log(p["denominator_seconds"]) for p in pairs))
   g=collections.defaultdict(list)
   for p in pairs:g[p["group"]].append(math.log(p["ratio"]))
   values=list(g.values());rng=random.Random(20261009);boot=[]
   for _ in range(10000):
    sample=[values[rng.randrange(len(values))] for _ in values]
    boot.append(math.exp(sum(map(sum,sample))/sum(map(len,sample))))
   boot.sort();interval=[boot[249],boot[9749]]
  return dict(numerator=num,denominator=den,size=size,ratio=ratio,interval95=interval,paired_batches=len(pairs),
   numerator_geometric_mean_seconds=gm_num,denominator_geometric_mean_seconds=gm_den,pairs=pairs,control_only=lost,modified_only=gained)
 contrasts=[("exit_ml","stock_ml"),("exit_ml","exit_pool"),("exit_ml","stock_pool"),("exit_pool","stock_pool"),("stock_ml","stock_pool")]
 comparisons=[compare(x,y,s) for x,y in contrasts for s in [None,1,16]]
 totals={}
 for policy in plan["policies"]:
  rows=[r for r in records if r["policy"]==policy]
  totals[policy]=dict(planned=len(rows),executed=sum(r.get("measured",True) for r in rows),exact=sum(good(r) for r in rows),
   failed=sum(not good(r) for r in rows if r.get("measured",True)),skipped=sum(not r.get("measured",True) for r in rows),
   completed_fallbacks=sum(r.get("fallback",False) for r in rows if good(r)))
 out=dict(planned=len(records),executed=sum(r.get("measured",True) for r in records),exact=sum(good(r) for r in records),
  totals=totals,cases=cases,comparisons=comparisons,peak_rss_bytes=max(r.get("peak_rss_bytes",0) for r in records),
  peak_scratch_bytes=max(r.get("scratch_peak_bytes",0) for r in records),scope=plan["scope"],
  audit_sha256=hashlib.sha256((HERE/(a.stage+"_validation.json")).read_bytes()).hexdigest())
 (HERE/(a.stage+"_summary.json")).write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({k:v for k,v in out.items() if k not in ["cases","comparisons"]}),flush=True)
 print(json.dumps([{k:v for k,v in c.items() if k!="pairs"} for c in comparisons]),flush=True)
if __name__=="__main__":main()
