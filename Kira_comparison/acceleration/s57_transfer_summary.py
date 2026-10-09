"""Paired timing summary for the fixed two-loop transfer experiment."""
import collections,json,math,pathlib,random,statistics
from s39_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
plan=json.loads((HERE/"transfer_plan.json").read_text())
audit=json.loads((HERE/"transfer_test_validation.json").read_text())
assert audit["passed"] and audit["trials"]==60
records=[read_record(p) for p in sorted((HERE/"transfer_test").glob("*.json.gz"))]
assert len(records)==60
groups=collections.defaultdict(list)
for r in records:groups[r["size"],r["policy"]].append(r)
def good(r):return r.get("measured",True) and r["success"] and r["status"]=="completed"
def ci(learned,control):
 rng=random.Random(20261009)
 pairs=[(x["cold_seconds"],y["cold_seconds"]) for x,y in zip(learned,control)]
 values=[]
 for _ in range(10000):
  selected=rng.choices(pairs,k=len(pairs))
  values.append(statistics.median(x for x,y in selected)/statistics.median(y for x,y in selected))
 values.sort();return [values[249],values[9749]]
cases=[]
for size in plan["target_sizes"]:
 methods={}
 for method in plan["policies"]:
  rows=sorted(groups[size,method],key=lambda x:x["repetition"])
  assert {r["repetition"] for r in rows}==set(range(5))
  successes=[r for r in rows if good(r)]
  methods[method]=dict(planned=5,executed=sum(r.get("measured",True) for r in rows),successes=len(successes),
   all_repeats_exact=len(successes)==5,median_seconds=statistics.median(r["cold_seconds"] for r in rows) if len(successes)==5 else None,
   observed_seconds=[r["cold_seconds"] for r in rows if r.get("measured",True)],
   statuses=[r["status"] for r in rows],fallbacks=sum(r.get("fallback",False) for r in successes))
 comparisons=[]
 for learned,control in [("ml_lower","trim"),("ml_lower","pool_filter"),("row_cpp","trim"),("row_cpp","row_cpp_native"),("combined","trim")]:
  valid=methods[learned]["all_repeats_exact"] and methods[control]["all_repeats_exact"]
  x=sorted(groups[size,learned],key=lambda r:r["repetition"]);y=sorted(groups[size,control],key=lambda r:r["repetition"])
  comparisons.append(dict(learned=learned,control=control,complete_pair=valid,
   ratio=methods[learned]["median_seconds"]/methods[control]["median_seconds"] if valid else None,
   descriptive_interval=ci(x,y) if valid else None))
 cases.append(dict(size=size,methods=methods,comparisons=comparisons))
result=dict(planned=60,executed=sum(r.get("measured",True) for r in records),exact_successes=sum(good(r) for r in records),
 family=plan["transfer"][0]["meta"]["family"],loops=2,target_offset=plan["target_offset"],cases=cases,
 scope=plan["scope"],interval="Descriptive paired-repeat bootstrap, 10000 resamples, fixed seed; one family cannot establish a general-family confidence interval.")
(HERE/"transfer_summary.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
