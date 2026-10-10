"""Fit execution thresholds from complete native training-workflow cost."""
import collections,hashlib,json,math,pathlib,statistics,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/integrated_runtime"
sys.path.insert(0,str(EXP));from s03_records import read_record
def key(case,size=32):
 targets=case["targets"][:size]
 dots=max(sum(max(0,v-1) for v in a) for a in targets)
 numerator=max(sum(max(0,-v) for v in a) for a in targets)
 return f'{case["topology_group"]}|dots={dots}|numerator={numerator}'
def main():
 cases=[c for c in json.loads((EXP/"families.json").read_text())["cases"] if c["split"]=="training"]
 thresholds=[.003,.01,.03,.1,.3,.5];data=collections.defaultdict(list);hashes={}
 for case in cases:
  base_path=EXP/"seed_threshold_training"/f'{case["id"]}_small.json.gz';base=read_record(base_path);assert base["success"]
  hashes[str(base_path.relative_to(ROOT))]=hashlib.sha256(base_path.read_bytes()).hexdigest()
  for t in thresholds:
   p=EXP/"seed_threshold_training"/f'{case["id"]}_seed_t{t:g}.json.gz';r=read_record(p)
   assert r["success"] and r["reference_checked"],p
   hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
   data[key(case)].append(dict(case=case["id"],group=case["group"],threshold=t,seconds=r["complete_seconds"],native_seconds=base["complete_seconds"],ratio=r["complete_seconds"]/base["complete_seconds"],attempt_count=r["attempt_count"]))
 policies={}
 for feature,rows in sorted(data.items()):
  candidates=[]
  for t in thresholds:
   a=[r for r in rows if r["threshold"]==t]
   candidates.append(dict(threshold=t,ratio=math.exp(statistics.mean(math.log(r["ratio"]) for r in a)),observations=len(a),initial_completions=sum(r["attempt_count"]==1 for r in a)))
  best=min(candidates,key=lambda x:(x["ratio"],x["threshold"]))
  policies[feature]=dict(threshold=best["threshold"],training_ratio=best["ratio"],candidates=candidates,measurements=rows)
 result=dict(objective="Minimum geometric mean complete-workflow time relative to the smaller native region on training profiles; includes failed attempts and fallback.",training_batches=len(cases),thresholds=thresholds,policies=policies,gate_fitted=False,unknown_profile="native smaller region",validation_used=False,input_sha256=hashes)
 (HERE/"threshold_policy.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:dict(threshold=v["threshold"],ratio=v["training_ratio"]) for k,v in policies.items()}),flush=True)
if __name__=="__main__":main()
