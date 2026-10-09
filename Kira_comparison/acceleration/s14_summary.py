"""Summarize all planned records, with separate failed and skipped observations."""
import collections,csv,gzip,json,math,pathlib,random,statistics
from s61_evidence_archive import unpack
from s39_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
plan=json.loads((HERE/"plan.json").read_text());frozen=json.loads((HERE/"frozen_policy.json").read_text())
paths=sorted((HERE/"results").glob("*.json.gz"))
assert len(paths)==frozen["expected_trials"],(len(paths),frozen["expected_trials"])
def metric_record(path):
 r=read_record(path)
 r.pop("checks",None)
 r.get("model",{}).pop("probabilities",None)
 for attempt in r.get("attempts",[]):attempt.pop("combination",None)
 return r
records=[metric_record(p) for p in paths]
policies=frozen["policies"];groups=collections.defaultdict(list)
def good(r):return r.get("measured",True) and r["status"]=="completed" and r["success"]
def measurement(r):
 if not good(r):return {}
 a=r["attempts"];model=r.get("model",{})
 core=sum(x["native_seconds"] for x in a)+model.get("load_seconds",0)+model.get("inference_seconds",0) if all("native_seconds" in x for x in a) else None
 import re
 counters={}
 logs=unpack({k:v for k,v in r["evidence"].items() if k in ("attempt0/run.log","attempt1/run.log")})
 for key,pattern in [
  ("generated_equations",r"(\d+) equations:\s*\d+ zero \+"),
  ("selected_equations",r"Number of selected equations to reduce:\s*(\d+)"),
  ("forward_updates",r"redundant:\s*\d+; insertions (\d+)")]:
  counters[key]=sum(int(v) for name,text in logs.items() for v in re.findall(pattern,text))
 counts_complete=all("error" not in x for x in a)
 return dict(total_seconds=r["cold_seconds"],native_with_inference_seconds=core,
  generated_equations=counters["generated_equations"],selected_equations=counters["selected_equations"],
  forward_updates=counters["forward_updates"] if counts_complete else None,
  model_seconds=model.get("load_seconds",0)+model.get("inference_seconds",0),
  peak_rss_bytes=r["peak_rss_bytes"],fallback=r["fallback"])
for r in records:groups[r["case"],r["size"],r["policy"]].append(r)
assert len(groups)==len(plan["test"])*len(plan["target_sizes"])*len(policies)
cases=[]
for case in range(len(plan["test"])):
 for size in plan["target_sizes"]:
  entry=dict(case=case,family=plan["test"][case]["meta"]["family"],group=plan["test"][case]["meta"]["group"],size=size,methods={})
  for policy in policies:
   rows=groups[case,size,policy];assert {x["repetition"] for x in rows}==set(range(plan["repetitions"]))
   measured=[x for x in rows if x.get("measured",True)];success=[x for x in rows if good(x)]
   m=dict(planned=len(rows),executed=len(measured),successes=len(success),skipped=len(rows)-len(measured),
    five_successes=len(success)==plan["repetitions"],fallbacks=sum(x.get("fallback",False) for x in success),
    failures=[dict(trial=x["trial"],status=x["status"]) for x in measured if not good(x)])
   if m["five_successes"]:
    values=[measurement(x) for x in success]
    m["medians"]={key:statistics.median(v[key] for v in values) if all(v[key] is not None for v in values) else None
       for key in values[0] if key!="fallback"}
   entry["methods"][policy]=m
  cases.append(entry)
def comparison(numerator,denominator,metric):
 pairs=[]
 completion=dict(control_only_batches=[dict(case=c["case"],size=c["size"]) for c in cases if c["methods"][denominator]["five_successes"] and not c["methods"][numerator]["five_successes"]],
  learned_only_batches=[dict(case=c["case"],size=c["size"]) for c in cases if c["methods"][numerator]["five_successes"] and not c["methods"][denominator]["five_successes"]])
 for c in cases:
  a=c["methods"][numerator];b=c["methods"][denominator]
  if not (a["five_successes"] and b["five_successes"]):continue
  x=a["medians"][metric];y=b["medians"][metric]
  if x is not None and y is not None and x>0 and y>0:pairs.append(dict(case=c["case"],size=c["size"],group=c["group"],ratio=x/y,log=math.log(x/y)))
 if not pairs:return dict(numerator=numerator,denominator=denominator,metric=metric,batches=0,ratio=None,interval95=None,**completion)
 bygroup=collections.defaultdict(list)
 for x in pairs:bygroup[x["group"]].append(x["log"])
 data=list(bygroup.values());rng=random.Random(20261008);boot=[]
 for _ in range(10000):
  selected=[data[rng.randrange(len(data))] for _ in data]
  boot.append(math.exp(sum(map(sum,selected))/sum(map(len,selected))))
 boot.sort()
 return dict(numerator=numerator,denominator=denominator,metric=metric,batches=len(pairs),kinematic_groups=len(data),
  ratio=math.exp(sum(x["log"] for x in pairs)/len(pairs)),interval95=[boot[249],boot[9749]],pairs=pairs,
  interval_scope="Descriptive bootstrap over the completed kinematic groups; incomplete groups are reported separately.",**completion)
learned=[frozen["selected_seed_policy"],"row_cpp","combined"];controls=["trim","tight","pool_filter"]
comparisons=[comparison(a,b,m) for a in learned for b in controls for m in ["total_seconds","native_with_inference_seconds","generated_equations","selected_equations","forward_updates"]]
totals={}
for policy in policies:
 rows=[r for r in records if r["policy"]==policy]
 measured=[r for r in rows if r.get("measured",True)]
 totals[policy]=dict(planned=len(rows),executed=len(measured),exact_successes=sum(good(x) for x in rows),
  failed_attempts=sum(not good(x) for x in measured),skipped=len(rows)-len(measured),
  batches_with_five_successes=sum(c["methods"][policy]["five_successes"] for c in cases),
  completed_fallbacks=sum(x.get("fallback",False) for x in rows if good(x)),
  observed_successful_time_range=[min((x["cold_seconds"] for x in rows if good(x)),default=None),max((x["cold_seconds"] for x in rows if good(x)),default=None)])
out=dict(planned_records=len(records),executed_trials=sum(r.get("measured",True) for r in records),
 exact_successes=sum(good(r) for r in records),skipped_repetitions=sum(not r.get("measured",True) for r in records),
 family_instances=len(plan["test"]),kinematic_groups=len({x["meta"]["group"] for x in plan["test"]}),
 target_batch_sizes=plan["target_sizes"],policies=policies,selected_seed_policy=frozen["selected_seed_policy"],
 cases=cases,totals=totals,comparisons=comparisons,
 peak_rss_bytes=max(r.get("peak_rss_bytes",0) for r in records),
 peak_scratch_bytes=max(r.get("scratch_peak_bytes",0) for r in records),
 definition="Complete process time includes family input, features and prediction, exact Kira work, target combination, fallback and coefficient checks. Native-with-inference time is a separate subprocess timing subtotal plus seed prediction; it excludes preparation, target combination and verification.")
(HERE/"summary.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
with (HERE/"figure_values.csv").open("w") as f:
 writer=csv.writer(f);writer.writerow(["family","group","size","policy","five_successes","median_seconds","native_with_inference_seconds","generated_equations","forward_updates"])
 for c in cases:
  for policy,m in c["methods"].items():
   v=m.get("medians",{});writer.writerow([c["family"],c["group"],c["size"],policy,m["five_successes"],v.get("total_seconds"),v.get("native_with_inference_seconds"),v.get("generated_equations"),v.get("forward_updates")])
print(json.dumps({k:out[k] for k in ["planned_records","executed_trials","exact_successes","skipped_repetitions","totals"]},indent=2),flush=True)
