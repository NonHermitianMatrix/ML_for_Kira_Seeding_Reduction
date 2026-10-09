"""Summarize frozen supplied-expression confirmation without discarding failures."""
import collections,hashlib,json,math,pathlib,random,statistics
from s39_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
f=read(HERE/"expression_freeze.json");plan=read(HERE/"plan.json");audit=read(HERE/"expression_test_validation.json")
assert audit["passed"] and audit["trials"]==f["expected_trials"]
records=[read_record(p) for p in sorted((HERE/"expression_test").glob("*.json.gz"))]
assert len(records)==f["expected_trials"]
def good(r):return r["status"]=="completed" and r["success"]
groups=collections.defaultdict(list)
for r in records:groups[r["case"],r["size"],r["policy"]].append(r)
cases=[]
for case in f["cases"]:
 for size in f["sizes"]:
  entry=dict(case=case,size=size,family=plan["test"][case]["meta"]["family"],group=plan["test"][case]["meta"]["group"],methods={})
  for policy in f["policies"]:
   rows=groups[case,size,policy];assert {r["repetition"] for r in rows}==set(range(f["repetitions"]))
   completed=[r for r in rows if good(r)]
   entry["methods"][policy]=dict(planned=len(rows),executed=sum(r.get("measured",True) for r in rows),exact=len(completed),
    full_pair=len(completed)==f["repetitions"],fallbacks=sum(r.get("fallback",False) for r in completed),
    median_seconds=statistics.median(r["cold_seconds"] for r in completed) if len(completed)==f["repetitions"] else None,
    final_source_equations=statistics.median(r["attempts"][-1]["source_equations"] for r in completed) if len(completed)==f["repetitions"] else None,
    selected_seeds=statistics.median(r["model"]["selected"] for r in completed) if len(completed)==f["repetitions"] and "selected" in completed[0].get("model",{}) else None)
  cases.append(entry)
def compare(numerator,denominator,size=None):
 pairs=[];lost=[];gained=[]
 for case in cases:
  if size is not None and case["size"]!=size:continue
  a=case["methods"][numerator];b=case["methods"][denominator]
  if a["full_pair"] and b["full_pair"]:
   pairs.append(dict(case=case["case"],size=case["size"],group=case["group"],ratio=a["median_seconds"]/b["median_seconds"]))
  elif b["full_pair"]:lost.append(dict(case=case["case"],size=case["size"]))
  elif a["full_pair"]:gained.append(dict(case=case["case"],size=case["size"]))
 ratio=None;interval=None
 if pairs:
  ratio=math.exp(statistics.mean(math.log(p["ratio"]) for p in pairs))
  groups=collections.defaultdict(list)
  for p in pairs:groups[p["group"]].append(math.log(p["ratio"]))
  values=list(groups.values());rng=random.Random(20261008);boot=[]
  for _ in range(10000):
   sample=[values[rng.randrange(len(values))] for value in values]
   boot.append(math.exp(sum(map(sum,sample))/sum(map(len,sample))))
  boot.sort();interval=[boot[249],boot[9749]]
 return dict(numerator=numerator,denominator=denominator,size=size,ratio=ratio,interval95=interval,
  paired_batches=len(pairs),pairs=pairs,control_only=lost,learned_only=gained)
comparisons=[compare(f["selected_policy"],control,size) for control in ["stored_pool","stored_distance"] for size in [None,1,16]]
comparisons += [compare("stored_distance","stored_pool")]
totals={}
for policy in f["policies"]:
 rows=[r for r in records if r["policy"]==policy]
 totals[policy]=dict(planned=len(rows),executed=sum(r.get("measured",True) for r in rows),exact=sum(good(r) for r in rows),
  failed=sum(not good(r) for r in rows if r.get("measured",True)),skipped=sum(not r.get("measured",True) for r in rows),
  completed_fallbacks=sum(r.get("fallback",False) for r in rows if good(r)))
out=dict(planned=len(records),executed=sum(r.get("measured",True) for r in records),exact=sum(good(r) for r in records),
 selected_policy=f["selected_policy"],totals=totals,cases=cases,comparisons=comparisons,
 peak_rss_bytes=max(r.get("peak_rss_bytes",0) for r in records),
 audit_sha256=hashlib.sha256((HERE/"expression_test_validation.json").read_bytes()).hexdigest(),
 scope=f["scope"],time_definition="Complete process time includes input preparation, prediction, supplied-equation export, exact Kira reduction, admission checks when enabled, failed attempts, fallback and exact coefficient checks. Prior construction of the shared identity pool is excluded from both methods.")
(HERE/"expression_test_summary.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({k:v for k,v in out.items() if k!="cases"},indent=2),flush=True)
