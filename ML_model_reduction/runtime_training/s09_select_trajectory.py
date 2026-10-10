"""Rank learned row policies by complete training trajectories, keeping validation separate."""
import collections,hashlib,json,math,pathlib,shutil,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
EXP=ROOT/"Kira_comparison/integrated_runtime";sys.path.insert(0,str(EXP))
from s03_records import read_record
def main():
 cases=[c for c in json.loads((EXP/"families.json").read_text())["cases"] if c["split"]=="training"]
 candidates=json.loads((HERE/"trajectory_candidates.json").read_text())["candidates"]
 results=[];hashes={}
 def read(case,v):
  path=EXP/"trajectory_training"/f'{case["id"]}_{v}.json.gz'
  r=read_record(path);assert r["success"] and r["reference_checked"],path
  hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
  return r
 for candidate in candidates:
  items=[];groups=collections.defaultdict(list)
  for case in cases:
   r=read(case,candidate["id"]);b=read(case,"native")
   def total(x,k):return sum(m.get(k,0) for m in x["metrics"])
   ratio=total(r,"operations")/max(1,total(b,"operations"))
   item=dict(case=case["id"],operations_ratio=ratio,time_ratio=r["complete_seconds"]/b["complete_seconds"],forward_ratio=total(r,"forward_seconds")/total(b,"forward_seconds"))
   items.append(item);groups[case["group"]].append(item)
  result=dict(id=candidate["id"],cases=items)
  for key in ["operations_ratio","time_ratio","forward_ratio"]:
   result[key]=math.exp(sum(sum(math.log(x[key]) for x in g)/len(g) for g in groups.values())/len(groups))
  results.append(result)
 ranked=sorted(results,key=lambda r:(r["operations_ratio"],r["forward_ratio"],r["id"]))
 chosen=ranked[:3]
 selection=dict(objective="Geometric mean committed forward coefficient-operation ratio across physical training families; ordinary/deep batches share family weight.",candidate_count=len(candidates),training_batches=len(cases),selected=[r["id"] for r in chosen],ranking=ranked,input_sha256=hashes,validation_used=False)
 (HERE/"trajectory_selection.json").write_text(json.dumps(selection,indent=2)+"\n")
 print(json.dumps({k:v for k,v in selection.items() if k!="input_sha256"}),flush=True)
if __name__=="__main__":main()
