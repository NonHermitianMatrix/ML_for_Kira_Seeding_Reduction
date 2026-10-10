"""Check unchanged seed probabilities and C++/Python tree decisions."""
import base64,hashlib,json,pathlib,sys,time
import numpy as np
from s02_run import run
from s04_records import read_record
from s07_seed import choose,candidates
from s21_seed_loader import NativeSeed
from s01_fast_seed import FastSeed
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_reduction/cost_training"))
from s08_train_tree import predict
def main():
 original=FastSeed();new=NativeSeed();assert original.cfg==new.cfg
 assert original.w.keys()==new.w.keys()
 assert all(np.array_equal(original.w[k],new.w[k]) for k in original.w)
 cases=json.loads((HERE/"families.json").read_text())["cases"]
 result=dict(original_seed_weights_unchanged=True,cases=[],tree_cases=[])
 for name in ["training_00_sunrise","training_02_double_box"]:
  c=next(c for c in cases if c["id"]==name);size=min(32,len(c["targets"]));targets=c["targets"][:size]
  ref=read_record(HERE/"references"/(name+f"_n{size}.json.gz"));masters=ref["masters"];d=c["definition"]
  spec=dict(r=max(sum(max(0,x) for x in a) for a in targets),s=max(sum(max(0,-x) for x in a) for a in targets),
     d=max(sum(max(0,x-1) for x in a) for a in targets))
  seeds=candidates(d,spec["r"],spec["s"],spec["d"]);target=dict(terms=[dict(indices=a,coefficient="1") for a in targets])
  want=original.predict(target,original.shared(d,masters,seeds)).astype("<f4").tobytes()
  selected,first,t1=choose(d,masters,targets,spec,closure=True)
  selected2,second,t2=choose(d,masters,targets,spec,closure=True)
  assert selected==selected2 and first==second
  got=base64.b64decode(first["probabilities_float32_base64"]);assert got==want
  result["cases"].append(dict(case=name,candidates=len(seeds),probabilities_sha256=hashlib.sha256(got).hexdigest(),
    first_call=t1,repeat_call=t2))
 model=json.loads((ROOT/"ML_model_reduction/cost_training/trained_model.json").read_text())
 for name in ["validation_00_sunrise","validation_01_double_box"]:
  c=next(c for c in cases if c["id"]==name);size=min(32,len(c["targets"]));ref=HERE/"references"/(name+f"_n{size}.json.gz")
  output=HERE/"runtime_checks"/(name+"_trace.json.gz")
  r=read_record(output) if output.exists() else run(c,size,"learned",output,timeout=180,reference=ref,
    weights=ROOT/"ML_model_reduction/cost_training/trained_weights.txt")
  assert r["success"],r["status"]
  groups=0
  for g in r["choices"]:
   f=np.array([a["features"] for a in g["candidates"]]);scores=np.array([0.]+[predict(model["nodes"],x-f[0]) for x in f[1:]])
   actual=np.array([a["score"] for a in g["candidates"]]);assert np.max(np.abs(scores-actual))<1e-12
   q=int(scores.argmin())
   if scores[q]>-model["minimum_predicted_gain"]:q=0
   assert q==g["selected"]
   probs=np.exp(-(scores-scores.min()));probs/=probs.sum()
   assert abs(probs[q]-g["confidence"])<1e-5
   groups+=1
  result["tree_cases"].append(dict(case=name,exact_reference_match=True,verified_choice_groups=groups,metrics=r["metrics"]))
 result["all_passed"]=True;(HERE/"runtime_check.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(dict(all_passed=True,seed_cases=len(result["cases"]),tree_cases=result["tree_cases"])),flush=True)
if __name__=="__main__":main()
