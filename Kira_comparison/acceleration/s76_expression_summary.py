"""Summarize whole-expression development and choose a validation interface."""
import collections,hashlib,json,math,pathlib,statistics
from s39_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
expected={"expression_pilot":2,"expression_thresholds":6,"expression_preflight":18,"expression_small":18,"expression_validation":36}
def read(p):return json.loads(p.read_text())
stages={};all_exact=0;all_checks=0
for stage,count in expected.items():
 files=sorted((HERE/stage).glob("*.json.gz"));assert len(files)==count,(stage,len(files),count)
 audit=read(HERE/(stage+"_validation.json"));assert audit["passed"] and audit["trials"]==count
 groups=collections.defaultdict(list)
 for path in files:
  r=read_record(path);groups[(r["partition"],r["case"],r["size"],r["policy"])].append(r)
 cases=[]
 for (partition,case,size,policy),rows in sorted(groups.items()):
  good=[r for r in rows if r["status"]=="completed" and r["success"]]
  cases.append(dict(partition=partition,case=case,size=size,policy=policy,trials=len(rows),exact=len(good),
    median_seconds=statistics.median(r["cold_seconds"] for r in good) if len(good)==len(rows) else None,
    fallbacks=sum(r.get("fallback",False) for r in good),
    selected_seeds=statistics.median(r["model"]["selected"] for r in good) if good and "selected" in good[0].get("model",{}) else None))
 stages[stage]=dict(records=count,exact=audit["exact_completions"],independent_checks=audit["independent_master_sample_checks"],cases=cases,
   audit_sha256=hashlib.sha256((HERE/(stage+"_validation.json")).read_bytes()).hexdigest())
 all_exact+=audit["exact_completions"];all_checks+=audit["independent_master_sample_checks"]
v=stages["expression_validation"]["cases"];comparisons=[]
for policy in ["stored_ml_lower","stored_ml_lower_checked"]:
 pairs=[];lost=[];gained=[]
 for control in [r for r in v if r["policy"]=="stored_pool"]:
  r=next(x for x in v if x["policy"]==policy and (x["case"],x["size"])==(control["case"],control["size"]))
  a=r["median_seconds"];b=control["median_seconds"]
  if a is not None and b is not None:pairs.append(dict(case=r["case"],size=r["size"],ratio=a/b))
  elif a is None and b is not None:lost.append(dict(case=r["case"],size=r["size"]))
  elif a is not None and b is None:gained.append(dict(case=r["case"],size=r["size"]))
 ratio=math.exp(statistics.mean(math.log(x["ratio"]) for x in pairs)) if pairs else None
 comparisons.append(dict(policy=policy,ratio=ratio,pairs=pairs,control_only=lost,learned_only=gained,
  eligible=bool(pairs) and not lost and ratio<1))
eligible=[x for x in comparisons if x["eligible"]]
selection=min(eligible,key=lambda x:x["ratio"])["policy"] if eligible else None
out=dict(planned=sum(expected.values()),exact=all_exact,independent_checks=all_checks,stages=stages,
 validation_comparisons=comparisons,selected_policy=selection,
 scope="Development and adapter validation use original-training groups only. Stored identities are supplied to exact Kira; their offline generation cost is outside these comparisons.")
(HERE/"expression_summary.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({k:v for k,v in out.items() if k!="stages"},indent=2),flush=True)
