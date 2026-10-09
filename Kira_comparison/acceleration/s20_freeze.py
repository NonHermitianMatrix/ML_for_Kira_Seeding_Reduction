"""Choose the adapter on validation costs and freeze it before new cost tests."""
import gzip,hashlib,json,math,pathlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((HERE/"plan.json").read_text())
protocol=json.loads((HERE/"validation_protocol.json").read_text())
assert sha(ROOT/"ML_model_seed_selection/trained_model.pt")==plan["seed_checkpoint_sha256"]
assert sha(ROOT/"ML_model_reduction/trained_model.pt")==plan["row_checkpoint_sha256"]
assert sha(ROOT/"ML_model_seed_selection/split_manifest.json")==plan["split_sha256"]
inputs={}
for part in ("train","validation","test"):
 for case in plan[part]:
  for key in ("definition","masters","inputs","references","seeds"):
   path=ROOT/"integrals"/case["meta"][key]
   if not path.exists() and path.suffix==".gz":path=path.with_suffix(".xz")
   inputs[str(path.relative_to(ROOT))]=sha(path)
records=[json.load(gzip.open(p,"rt")) for p in sorted((HERE/"validation").glob("*.json.gz"))]
assert len(records)==protocol["cases"]*len(protocol["policies"])
bykey={(x["case"],x["policy"]):x for x in records};assert len(bykey)==len(records)
def cost(i,policy):
 x=bykey[i,policy]
 return x["cold_seconds"] if x["success"] and x["status"]=="completed" else plan["timeout_seconds"]
def score(policy):return math.exp(sum(math.log(cost(i,policy)) for i in range(protocol["cases"]))/protocol["cases"])
candidates=["ml_lower","ml_components_halo"];selected=min(candidates,key=lambda p:(score(p),p))
ratio=score("row_source")/score("row_native")
complete=lambda policy:sum(bykey[i,policy]["success"] and bykey[i,policy]["status"]=="completed" for i in range(protocol["cases"]))
row_candidate=ratio<0.98 and complete("row_source")>=complete("row_native")
assert json.loads((HERE/"cpp_equivalence.json").read_text())["passed"]
policies=["trim","tight","pool_filter",selected,"row_cpp","combined"]
files=["s36_evidence.py","s01_fast_seed.py","s03_seed_filter.h","s04_build.py","s06_worker.py","s07_run.py","s09_fast_row.py","s11_row_server.py","seed_weights.npz","row_weights.npz","seed_export.json","row_export.json","plan.json","s23_cpp_model.h","s24_row_weights.h","s25_cpp_live_policy.h","cpp_build.json","validation_protocol.json"]
frozen=dict(selected_seed_policy=selected,policies=policies,validation_scores={p:score(p) for p in protocol["policies"]},
 validation_completions={p:complete(p) for p in protocol["policies"]},row_source_native_score_ratio=ratio,
 python_row_screen_passed=row_candidate,compiled_row_tested_independently=True,row_screen="Complete at least as many cases as native rows and lower capped validation time by at least two percent. This screen only admits the variant to reserved tests.",
 input_sha256=inputs,test_cases=len(plan["test"]),sizes=plan["target_sizes"],repetitions=plan["repetitions"],
 expected_trials=len(plan["test"])*len(plan["target_sizes"])*plan["repetitions"]*len(policies),
 sha256={name:sha(HERE/name) for name in files},
 validation_sha256={str(p.relative_to(HERE)):sha(p) for p in sorted((HERE/"validation").glob("*.json.gz"))},
 deployment="Experimental integration; reserved results determine whether a runtime advantage is supported.")
assert len({x["meta"]["group"] for x in plan["test"]})==6
assert not ({x["meta"]["group"] for x in plan["test"]}&{x["meta"]["group"] for part in ["train","validation"] for x in plan[part]})
path=HERE/"frozen_policy.json"
if path.exists():assert json.loads(path.read_text())==frozen
else:path.write_text(json.dumps(frozen,indent=2)+"\n")
print(json.dumps({k:v for k,v in frozen.items() if k not in ["sha256","validation_sha256"]}),flush=True)
