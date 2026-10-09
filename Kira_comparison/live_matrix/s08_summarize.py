"""Summarize complete paired trials and preserve incomplete-case counts."""
import collections,gzip,json,math,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent
def median(v):return statistics.median(v)
def main():
 plan=json.load(open(HERE/"plan.json"));audit=json.load(open(HERE/"validation.json"));assert audit["passed"]
 grouped=collections.defaultdict(list)
 for path in sorted((HERE/"results").glob("*.json.gz")):
  r=json.load(gzip.open(path,"rt"))
  forward=r.get("native",{}).get("forward",[])
  summaries=[]
  for key,value in r.get("evidence",{}).items():
   if key.endswith(".policy.jsonl.gz"):
    summaries +=[x for line in value.splitlines() if (x:=json.loads(line))["event"]=="summary"]
  stats=dict(cold_seconds=r["cold_seconds"],peak_rss_bytes=r["peak_rss_bytes"],
     native_seconds=r.get("native",{}).get("native_seconds",0),
     forward_seconds=sum(x["forward_seconds"] for x in forward),
     steps=sum(x["steps"] for x in forward),
     operations=sum(x["coefficient_operations"] for x in forward),
     peak_row_nonzeros=max([x["peak_row_nonzeros"] for x in forward] or [0]),
     model_load_seconds=sum(x["load_seconds"] for x in summaries),
     feature_seconds=sum(x["feature_seconds"] for x in summaries),
     inference_seconds=sum(x["inference_seconds"] for x in summaries),
     sampling_seconds=sum(x["sampling_seconds"] for x in summaries))
  stats["forward_loaded_seconds"]=stats["forward_seconds"]-stats["model_load_seconds"]
  stats["complete_loaded_seconds"]=stats["cold_seconds"]-stats["model_load_seconds"]
  stats["status"]=r["status"];stats["success"]=r["success"]
  grouped[(r["case"],r["policy"])].append(stats)
 cases=[]
 for (case,policy),rows in grouped.items():
  successes=[r for r in rows if r["success"] and r["status"]=="completed"]
  record=dict(case=case,family=plan["family_cases"][case]["meta"]["family"],
       policy=policy,repeats=len(rows),complete=len(successes))
  if len(successes)==3:
   record.update({k:median([r[k] for r in successes]) for k in rows[0] if k not in ["status","success"]})
   record["peak_rss_bytes"]=max(r["peak_rss_bytes"] for r in successes)
  cases.append(record)
 comparisons=[]
 ix={(r["case"],r["policy"]):r for r in cases}
 for baseline in ["stock","native","deterministic"]:
  for policy in ["native","deterministic","learned"]:
   if baseline==policy:continue
   pairs=[(ix[(c,policy)],ix[(c,baseline)]) for c in range(len(plan["family_cases"]))
      if ix[(c,policy)]["complete"]==3 and ix[(c,baseline)]["complete"]==3]
   entry=dict(baseline=baseline,policy=policy,pairs=len(pairs),metrics={})
   for k in ["cold_seconds","native_seconds","forward_seconds","forward_loaded_seconds",
             "complete_loaded_seconds","operations","steps","peak_rss_bytes"]:
    matched=[(a[k],b[k],a["case"]) for a,b in pairs if a[k]>0 and b[k]>0
      and (not k.startswith("forward_") or (a["steps"]>0 and b["steps"]>0))]
    entry["metrics"][k]=dict(pairs=len(matched),
       geometric_mean_ratio=math.exp(sum(math.log(a/b) for a,b,c in matched)/len(matched)) if matched else None,
       faster=sum(a<b for a,b,c in matched),sum_policy=sum(a for a,b,c in matched),
       sum_baseline=sum(b for a,b,c in matched),
       case_ratios=[dict(case=c,ratio=a/b) for a,b,c in matched])
   comparisons.append(entry)
 result=dict(trials=sum(len(v) for v in grouped.values()),cases=cases,comparisons=comparisons,
       validation=audit,notes="Ratios use case medians; no ratios for unfinished trials or zero operation counts.")
 (HERE/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(dict(trials=result["trials"],incomplete=audit["incomplete"])),flush=True)
if __name__=="__main__":main()

