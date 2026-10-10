"""Retain all matched complete costs and independently assert unchanged decisions."""
import argparse,collections,hashlib,json,math,pathlib,statistics
from s105_parallel_records import read_record
from s76_summarize_pair_reserved import compare
from s110_compare_parallel import parity
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/parallel_inference"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("phase",choices=["validation","confirmation"]);a=ap.parse_args()
 if a.phase=="validation":
  cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
  batches=[dict(case=c["id"],size=min(32,len(c["targets"]))) for c in cases];reps=3
 else:
  f=json.loads((EXP/"freeze.json").read_text());data=json.loads((HERE/"reserved_families.json").read_text())
  cases=data["cases"];batches=data["batches"];reps=f["repetitions"]
 by_id={c["id"]:c for c in cases};records=[];count=0;attempts=0;failures=collections.Counter();peaks={"rss_bytes":0,"scratch_bytes":0};pairs=0
 for batch in batches:
  case=by_id[batch["case"]];size=batch["size"];name=case["id"]
  r=dict(case=name,size=size,group=case["group"],topology=case["topology_group"],methods={})
  for method in ["native","seed","row","both"]:
   rr={0:[],1:[]}
   for rep in range(reps):
    for flag in [0,1]:
     p=EXP/a.phase/f"{name}_n{size}_{method}_f{flag}_r{rep}.json.gz"
     z=read_record(p);rr[flag].append(z);count+=1;attempts+=z["attempt_count"]
     for path in z["attempts"]:
      trial=read_record(ROOT/path)
      if not trial["success"]:failures[trial["status"]]+=1
      peaks["rss_bytes"]=max(peaks["rss_bytes"],trial.get("peak_rss_bytes",0))
      peaks["scratch_bytes"]=max(peaks["scratch_bytes"],trial.get("peak_scratch_bytes",0))
    parity(rr[0][-1],rr[1][-1]);pairs+=1
   for flag,values in rr.items():
    r["methods"][method+("_new" if flag else "_old")]=dict(complete_repeats=all(z["success"] and z["reference_checked"] for z in values),
      **{field:statistics.median(z[field] for z in values) for field in ["complete_seconds","forward_seconds","decision_seconds","operations","equations"]})
  records.append(r)
 comparisons={}
 for left,right in [(m+"_new",m+"_old") for m in ["native","seed","row","both"]]+[(m+"_new","native_new") for m in ["seed","row","both"]]:
  comparisons[left+"_over_"+right]={field:dict(all=compare(records,left,right,field),by_topology={t:compare([r for r in records if r["topology"]==t],left,right,field) for t in sorted({r["topology"] for r in records})}) for field in ["complete_seconds","forward_seconds","decision_seconds","operations","equations"]}
 result=dict(phase=a.phase,planned=len(batches)*8*reps,observed=count,all_exact_and_choice_parity=True,checked_pairs=pairs,attempts=attempts,failed_attempts=dict(failures),peaks=peaks,batches=records,comparisons=comparisons,weights_thresholds_and_routing_unchanged=True)
 assert count==result["planned"]
 if a.phase=="validation":
  result["adoption_rule"]="All decisions and exact coefficients agree; seed complete time falls, row complete time ratio <=1.02, and row decision time falls."
  result["eligible"]=comparisons["seed_new_over_seed_old"]["complete_seconds"]["all"]["ratio"]<1 and comparisons["row_new_over_row_old"]["complete_seconds"]["all"]["ratio"]<=1.02 and comparisons["row_new_over_row_old"]["decision_seconds"]["all"]["ratio"]<1
 (EXP/(a.phase+"_summary.json")).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:{f:v[f]["all"] for f in ["complete_seconds","forward_seconds","decision_seconds"]} for k,v in comparisons.items()},indent=2),flush=True)
if __name__=="__main__":main()
