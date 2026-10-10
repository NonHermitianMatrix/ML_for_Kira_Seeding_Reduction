"""Summarize paired timings without dropping failed filtered attempts."""
import argparse,collections,hashlib,json,math,pathlib,statistics
import numpy as np
from s02_records import read
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def stage(r):
 return sum(m["seconds"] for a in r["attempts"] for m in a.get("stage_metrics",[]) if m["stage"] in ("generation_modular","equation_selection","equation_selection_coeff","modular_solve","equation_regeneration"))
def aggregate(folder):
 groups=collections.defaultdict(list);allrows=[]
 for p in sorted(folder.glob("*.json.gz")):
  r=read(p)
  if "mode" not in r:continue
  r["equation_preparation_seconds"]=stage(r)
  groups[(r["case"],r["size"],r["mode"],r["threshold"])].append(r);allrows.append(r)
 batches={}
 for (case,n,mode,t),rows in groups.items():
  key=(case,n)
  if key not in batches:batches[key]=dict(case=case,size=n,group=rows[0]["group"],topology=rows[0]["topology"],methods={})
  batches[key]["methods"][f"{mode}:{t:g}"]={**{f:statistics.median(r[f] for r in rows) for f in ["complete_seconds","equation_preparation_seconds","forward_seconds","back_substitution_seconds","filter_seconds","generated_equations","selected_equations","attempt_count"]},"repeats":len(rows),"all_exact":all(r["success"] and r["reference_checked"] for r in rows)}
 return list(batches.values()),allrows
def ratio(batches,key,field):
 pergroup=collections.defaultdict(list)
 for b in batches:
  a=b["methods"].get(key);n=b["methods"].get("off:0")
  if a and n and a["all_exact"] and n["all_exact"] and a[field]>0 and n[field]>0:pergroup[b["group"]].append(math.log(a[field]/n[field]))
 values=np.array([np.mean(v) for v in pergroup.values()])
 if not len(values):return None
 rng=np.random.default_rng(8721);boot=np.exp(np.mean(rng.choice(values,(10000,len(values)),replace=True),axis=1))
 return dict(ratio=float(np.exp(values.mean())),interval95=[float(x) for x in np.quantile(boot,[.025,.975])],groups=len(values))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("phase",choices=["validation","model_test"]);a=ap.parse_args()
 batches,rows=aggregate(HERE/a.phase);keys=sorted({k for b in batches for k in b["methods"] if k!="off:0"})
 result=dict(workflows=len(rows),all_exact=all(r["success"] and r["reference_checked"] for r in rows),failed_attempts=sum(not z["success"] for r in rows for z in r["attempts"]),batches=batches,comparisons={k:{f:ratio(batches,k,f) for f in ["complete_seconds","equation_preparation_seconds","generated_equations","selected_equations"]} for k in keys})
 (HERE/a.phase/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="batches"},indent=2))
if __name__=="__main__":main()
