"""Summarize every reserved outcome and form paired descriptive comparisons."""
import csv,hashlib,json,math,pathlib,statistics
import numpy as np
from s04_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
def median(a):return statistics.median(a)
def comparison(records,left,right,size=None,metric="complete_seconds"):
 groups={}
 for r in records:
  if size is not None and r["size"]!=size:continue
  groups.setdefault((r["case"],r["size"],r["policy"]),[]).append(r)
 pairs=[]
 keys=sorted({(r["case"],r["size"]) for r in records if size is None or r["size"]==size})
 for case,n in keys:
  a=groups.get((case,n,left),[]);b=groups.get((case,n,right),[])
  if len(a)!=3 or len(b)!=3 or not all(r["success"] for r in a+b):continue
  if not all(metric in r and r[metric]>0 for r in a+b):continue
  x=median([r[metric] for r in a]);y=median([r[metric] for r in b])
  pairs.append(dict(case=case,size=n,left=x,right=y,ratio=x/y))
 if not pairs:return dict(left=left,right=right,size=size,metric=metric,paired_batches=0,pairs=[])
 families={}
 for p in pairs:families.setdefault(p["case"],[]).append(p)
 logratios=np.array([np.mean([math.log(p["ratio"]) for p in ps]) for ps in families.values()])
 logs_a=[np.mean([math.log(p["left"]) for p in ps]) for ps in families.values()]
 logs_b=[np.mean([math.log(p["right"]) for p in ps]) for ps in families.values()]
 rng=np.random.default_rng(20261009)
 ci=np.exp(np.percentile(logratios[rng.integers(0,len(logratios),size=(5000,len(logratios)))].mean(1),[2.5,97.5])).tolist() if len(logratios)>1 else None
 return dict(left=left,right=right,size=size,metric=metric,paired_batches=len(pairs),paired_cases=len(families),
  ratio=float(np.exp(logratios.mean())),interval95=ci,geometric_left=float(np.exp(np.mean(logs_a))),
  geometric_right=float(np.exp(np.mean(logs_b))),pairs=pairs)
def main():
 frozen=json.loads((HERE/"freeze.json").read_text());records=[];hashes={};attempt_count=0;failed_attempts=[];reference_checks=[]
 for path in sorted((HERE/"model_test").glob("*.json.gz")):
  if "_monitor." in path.name:continue
  r=read_record(path);hashes[str(path.relative_to(HERE))]=hashlib.sha256(path.read_bytes()).hexdigest()
  attempts=[read_record(HERE/a) for a in r.get("attempts",[])];attempt_count+=len(attempts)
  r["operations"]=sum(m["operations"] for a in attempts for m in a.get("metrics",[]))
  r["forward_seconds"]=sum(m["forward_seconds"] for a in attempts for m in a.get("metrics",[]))
  r["changed_sources"]=sum(m["changed_sources"] for a in attempts for m in a.get("metrics",[]))
  r["initial_equations"]=sum((a.get("counters",{}).get("generated_equations") or [0])[0] for a in attempts)
  r["initial_success"]=r["success"] and bool(attempts) and all(a["success"] for a in attempts if a["attempt"]==0)
  r["reference_checked"]=bool(attempts) and all(a["reference_checked"] for a in attempts if a["success"])
  r["peak_solver_rss_bytes"]=max([a.get("peak_rss_bytes",0) for a in attempts]+[0])
  r["peak_scratch_bytes"]=max([a.get("peak_scratch_bytes",0) for a in attempts]+[0])
  monitor=path.with_name(path.name.replace(".json.gz","_monitor.json.gz"))
  r["peak_tree_rss_bytes"]=read_record(monitor)["peak_tree_rss_bytes"] if monitor.exists() else 0
  r["attempt_count"]=len(attempts)
  for a in attempts:
   if not a["success"]:failed_attempts.append(dict(case=r["case"],size=r["size"],policy=r["policy"],
    attempt=a["attempt"],chunk=a["chunk"],status=a["status"],master_admission_rejected=a.get("master_admission_rejected",False),
    error=a.get("error"),coefficient_mismatches=a.get("mismatches",[]),
    allocation_failure="std::bad_alloc" in a.get("log",""),recursive_termination="terminate called recursively" in a.get("log","")))
  records.append(r)
 expected=6*len(frozen["sizes"])*len(frozen["policies"])*frozen["repeats"]
 assert len(records)==expected,(len(records),expected)
 assert all(r["reference_checked"] for r in records if r["success"])
 assert not any(a["coefficient_mismatches"] for a in failed_attempts),"Exact result mismatch needs investigation"
 counts={}
 for policy in frozen["policies"]:
  rows=[r for r in records if r["policy"]==policy]
  counts[policy]=dict(planned=len(rows),measured=sum(r.get("status")!="skipped" for r in rows),
   completed=sum(r["success"] for r in rows),skipped=sum(r.get("status")=="skipped" for r in rows),
   failed=sum(not r["success"] and r.get("status")!="skipped" for r in rows),
   initially_complete=sum(r["initial_success"] for r in rows),
   rescued_by_fallback=sum(r["success"] and not r["initial_success"] for r in rows),
   fallback_attempts=sum(r.get("fallback_attempts",0) for r in rows),
   completed_targets=sum(r.get("completed_targets",0) for r in rows))
 comps=[]
 for policy in frozen["policies"]:
  for control in ["stock","native","tight"]:
   if policy!=control:
    for size in [None,32,128]:comps.append(comparison(records,policy,control,size))
 for size in [None,32,128]:
  comps.append(comparison(records,frozen["seed_policy"],frozen["closure_control"],size))
  comps.append(comparison(records,"row_full","native",size,"operations"))
  comps.append(comparison(records,"row_full","native",size,"forward_seconds"))
  for metric in ["initial_equations","operations"]:
   for control in ["native","tight"]:comps.append(comparison(records,frozen["seed_policy"],control,size,metric))
 topology_comparisons=[]
 for topology in sorted({r["topology"] for r in records}):
  subset=[r for r in records if r["topology"]==topology]
  for policy in [frozen["seed_policy"],"row_full",frozen["combined_policy"],"split_native","split_combined_safe"]:
   for control in ["stock","native","tight",frozen["closure_control"]]:
    if policy==control:continue
    for size in [None,32,128]:
     c=comparison(subset,policy,control,size);c["topology"]=topology;topology_comparisons.append(c)
 counts_by_size={}
 for size in frozen["sizes"]:
  counts_by_size[str(size)]={}
  for policy in frozen["policies"]:
   rows=[r for r in records if r["size"]==size and r["policy"]==policy]
   counts_by_size[str(size)][policy]=dict(planned=len(rows),completed=sum(r["success"] for r in rows),
    initially_complete=sum(r["initial_success"] for r in rows),
    rescued_by_fallback=sum(r["success"] and not r["initial_success"] for r in rows),
    failed=sum(not r["success"] and r.get("status")!="skipped" for r in rows),
    skipped=sum(r.get("status")=="skipped" for r in rows))
 refs=[]
 for p in sorted((HERE/"reserved_references").glob("*.json.gz")):
  r=read_record(p);entry={k:r.get(k) for k in ["case","size","success","status","complete_seconds","peak_rss_bytes","peak_scratch_bytes"]}
  entry.update(master_count=len(r.get("masters",[])),zero_targets=sum(not row for row in r.get("coefficients",{}).values()),identity_master_targets=len(r.get("identity_master_targets",[])))
  refs.append(entry)
 for p in sorted((HERE/"reference_checks").glob("*.json.gz")):
  r=read_record(p);reference_checks.append({k:r.get(k) for k in ["case","success","status","complete_seconds","mismatches"]})
 summary=dict(planned=len(records),measured=sum(r.get("status")!="skipped" for r in records),completed=sum(r["success"] for r in records),
  native_attempts=attempt_count,counts=counts,counts_by_size=counts_by_size,comparisons=comps,topology_comparisons=topology_comparisons,failed_attempts=failed_attempts,
  reference_calculations=refs,expanded_bound_checks=reference_checks,trial_sha256=hashes,
  peak_tree_rss_bytes=max(r["peak_tree_rss_bytes"] for r in records),
  peak_scratch_bytes=max(r["peak_scratch_bytes"] for r in records),
  interval_method="5000 case-cluster bootstrap resamples of log ratios of three-repeat medians; descriptive fixed-case intervals",
  ratio_cohort="both policies completed all three repeats for each included batch",
  root_policy=frozen["seed_policy"],row_model="cost_training/trained_model.json")
 interruption=HERE/"scheduler_interruption.json"
 if interruption.exists():
  interruption_record=json.loads(interruption.read_text());summary["scheduler_interruption"]=interruption_record
  subset=[r for r in records if r["case"]!=interruption_record["case"]]
  summary["without_resumed_case"]=[comparison(subset,policy,control,size) for policy in
   [frozen["seed_policy"],"row_full",frozen["combined_policy"]] for control in ["stock","native","tight"] for size in [None,32,128]]
 (HERE/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 columns=["case","topology","loops","size","policy","success","status","complete_seconds","completed_targets",
  "attempt_count","initial_success","fallback_attempts","initial_equations","operations","forward_seconds","changed_sources",
  "peak_tree_rss_bytes","peak_scratch_bytes"]
 with (HERE/"trials.csv").open("w",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore");writer.writeheader();writer.writerows(records)
 print(json.dumps(dict(planned=summary["planned"],measured=summary["measured"],completed=summary["completed"],
  counts=counts,comparisons=[c for c in comps if c["left"] in [frozen["seed_policy"],"row_full"] and c["right"]=="native" and c["size"] is None])),flush=True)
if __name__=="__main__":main()
