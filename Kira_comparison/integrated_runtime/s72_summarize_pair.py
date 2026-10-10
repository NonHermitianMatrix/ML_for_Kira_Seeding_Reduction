"""Assess a numerically identical two-row shortcut using validation only."""
import collections,json,math,pathlib,statistics
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
def gm(xs):return math.exp(statistics.mean(math.log(x) for x in xs))
def main():
 paths=list((HERE/"pair_validation").glob("*.json.gz"));assert len(paths)==144,len(paths)
 fast_groups=0;checked_pairs=0
 for p in paths:
  if "_c0_" not in p.name:continue
  a=read_record(p);b=read_record(p.with_name(p.name.replace("_c0_","_c1_")))
  for field in ["operations","equations","attempt_count"]:assert a[field]==b[field],p
  for an,bn in zip(a["attempts"],b["attempts"]):
   aa=read_record(HERE.parents[1]/an);bb=read_record(HERE.parents[1]/bn)
   assert aa.get("raw_export")==bb.get("raw_export") and aa["status"]==bb["status"],p
   for field in ["groups","changed_sources","updates","operations","choice_digest"]:
    assert [m[field] for m in aa.get("metrics",[])]==[m[field] for m in bb.get("metrics",[])],(p,field)
   fast_groups+=sum(m.get("pair_fast_groups",0) for m in bb.get("metrics",[]))
  checked_pairs+=1
 assert checked_pairs==72 and fast_groups>0
 rows=[read_record(p) for p in paths];assert all(r["success"] and r["reference_checked"] for r in rows)
 cases=sorted({r["case"] for r in rows});details=[]
 for case in cases:
  variants=sorted({r["variant"] for r in rows if r["case"]==case})
  for v in variants:
   pair=[]
   for flag in [0,1]:
    rr=[read_record(p) for p in paths if p.name.startswith(case+"_"+v.replace(":","-")+"_c"+str(flag)+"_")]
    assert len(rr)==3
    pair.append(dict(group=rr[0]["group"],medians={f:statistics.median(r[f] for r in rr) for f in ["complete_seconds","forward_seconds","decision_seconds","operations"]}))
   assert pair[0]["medians"]["operations"]==pair[1]["medians"]["operations"]
   ratios={k:pair[1]["medians"][k]/pair[0]["medians"][k] for k in pair[0]["medians"] if pair[0]["medians"][k]>0}
   details.append(dict(case=case,group=pair[0]["group"],variant=v,ratios=ratios,shortcut_off=pair[0]["medians"],shortcut_on=pair[1]["medians"]))
 models=[r for r in details if r["variant"].startswith(("row_small:","combined:"))]
 totals={}
 for f in ["complete_seconds","forward_seconds","decision_seconds","operations"]:
  groups=collections.defaultdict(list)
  for r in models:
   if f in r["ratios"]:groups[r["group"]].append(r["ratios"][f])
  totals[f]=gm([gm(v) for v in groups.values()])
 eligible=totals["forward_seconds"]<.98 and totals["complete_seconds"]<=1.01
 result=dict(checked_pairs=checked_pairs,fast_groups=fast_groups,complete_workflows=144,all_pair_parity_passed=True,model_ratios=totals,eligible_for_separate_confirmation=eligible,deployed=False,validation_only=True,cases=details)
 (HERE/"pair_summary.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="cases"}),flush=True)
if __name__=="__main__":main()
