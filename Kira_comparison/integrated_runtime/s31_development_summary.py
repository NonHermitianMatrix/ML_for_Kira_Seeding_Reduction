"""Summarize complete trajectory validation without using reserved measurements."""
import collections,hashlib,json,math,pathlib,statistics
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def geo(x):return math.exp(statistics.mean(map(math.log,x)))
def main():
 folder=ROOT/"ML_model_reduction/runtime_training"
 sel=json.loads((folder/"trajectory_selection.json").read_text())
 models=sel["selected"]
 variants=["native","fill"]+["row:"+m for m in models]+["small","seed","closure","combined:"+models[0]]
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
 rows={};hashes={}
 for c in cases:
  for v in variants:
   batch=[]
   for rep in range(3):
    p=HERE/"trajectory_validation"/f'{c["id"]}_{v.replace(":","-")}_r{rep}.json.gz'
    r=read_record(p);assert r["success"],p;batch.append(r);hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
   rows[c["id"],v]={m:statistics.median(r[m] for r in batch) for m in ["complete_seconds","operations","forward_seconds","decision_seconds","equations"]}
 results=[]
 for v in variants:
  groups=collections.defaultdict(list);details=[]
  for c in cases:
   b=rows[c["id"],"native"];r=rows[c["id"],v]
   ratios={m:r[m]/b[m] for m in ["complete_seconds","operations","forward_seconds","equations"] if b[m]>0}
   details.append(dict(case=c["id"],topology=c["topology_group"],median=r,ratios=ratios))
   groups[c["group"]].append(ratios)
  summary={m:geo([geo([r[m] for r in g]) for g in groups.values()]) for m in ["complete_seconds","operations","forward_seconds","equations"]}
  results.append(dict(variant=v,ratios=summary,cases=details))
 row_candidates=[r for r in results if r["variant"].startswith("row:")]
 best=min(row_candidates,key=lambda r:r["ratios"]["complete_seconds"])
 result=dict(validation_batches=len(cases),repetitions=3,variants=len(variants),results=results,selected_row=best["variant"],selected_from="complete validation time; rows trained only on training trajectories",input_sha256=hashes)
 (HERE/"development_summary.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(dict(selected_row=result["selected_row"],results=[dict(variant=r["variant"],ratios=r["ratios"]) for r in results])),flush=True)
if __name__=="__main__":main()
