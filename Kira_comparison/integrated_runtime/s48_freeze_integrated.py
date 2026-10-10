"""Select on validation and freeze before any new reserved reduction."""
import datetime,hashlib,json,math,pathlib,statistics,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (HERE/"freeze.json").exists()
 paths=sorted((HERE/"integrated_validation").glob("*.json.gz"));assert len(paths)==198,len(paths)
 rows=[read_record(p) for p in paths];assert all(r["success"] and r["reference_checked"] for r in rows)
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
 data={}
 for c in cases:
  a=[r for r in rows if r["case"]==c["id"]];v={}
  for kind in ["small","fill_small","row_small:f1_2","row_small:mixed","closure","seed","combined:f1_2","combined:mixed"]:
   for compiled in ([True,False] if kind=="seed" or kind.startswith("combined") else [False]):
    rr=[r for r in a if r["variant"]==kind and r["compiled_seed"]==compiled];assert len(rr)==3
    label=kind+("_compiled" if compiled else "")
    v[label]={f:statistics.median(r[f] for r in rr) for f in ["complete_seconds","operations","forward_seconds","decision_seconds","equations"]}
  data[c["id"]]=v
 row_models={}
 for topology in sorted({c["topology_group"] for c in cases}):
  names=[c["id"] for c in cases if c["topology_group"]==topology]
  scores={m:math.exp(statistics.mean(math.log(data[n]["row_small:"+m]["complete_seconds"]/data[n]["small"]["complete_seconds"]) for n in names)) for m in ["f1_2","mixed"]}
  row_models[topology]=dict(model=min(scores,key=scores.get),validation_ratios=scores)
 recommendations={}
 for c in cases:
  v=data[c["id"]];m=row_models[c["topology_group"]]["model"]
  allowed=["small","fill_small","closure","seed_compiled","row_small:"+m,"combined:"+m+"_compiled"]
  best=min(allowed,key=lambda n:v[n]["complete_seconds"])
  if v[best]["complete_seconds"]>=.98*v["small"]["complete_seconds"]:best="small"
  recommendations[key(c)]=dict(variant=best,validation_seconds={n:v[n]["complete_seconds"] for n in allowed})
 config=dict(row_by_topology=row_models,seed_backend="compiled",unknown_row_model="mixed",unknown_seed_threshold=.01,
  recommendations=recommendations,unknown_recommended_variant="small",gate_margin=.02,
  note="Model-only and combined reserved ablations execute even where the validation recommendation is native; no reserved timing selects the policy.")
 (HERE/"deployment.json").write_text(json.dumps(config,indent=2)+"\n")
 (HERE/"integrated_validation_summary.json").write_text(json.dumps(dict(complete=len(rows),cases=data,selection=config),indent=2)+"\n")
 protocol=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repetitions=5,
  variants=["native","small","fill_small","closure","seed","row","combined"],batches=16,planned=560,
  seed_thresholds="ML_model_seed_selection/runtime_inference/threshold_policy.json",deployment="Kira_comparison/integrated_runtime/deployment.json",
  reference_preparation_timed=False,symbolic_field="Q(d)",max_concurrent_trials=2,
  failure_rule="Retain all outcomes; complete paired comparisons require all five repeats. Exact coefficient disagreements abort learned use. Missing basis integrals trigger fixed fallback.",
  statistics="Per-batch median over five repeats; geometric mean ratios with equal physical-profile weight; descriptive paired bootstrap resamples profiles, retaining both batches.",
  source_revision_before_extension="6a67ffa122d49db079714435bfabbdd112546e5b",sha256={})
 names=[HERE/n for n in ["s02_run.py","s03_records.py","s24_workflow.py","s49_reserved_references.py","s50_reserved_references.sh","s51_reserved_test.py","s52_reserved_test.sh","s56_reduce.py","reserved_families.json","deployment.json","resource_plan.json"]]
 for base in [ROOT/"ML_model_reduction/runtime_training",ROOT/"ML_model_seed_selection/runtime_inference"]:
  names += [p for p in base.rglob("*") if p.is_file() and p.suffix in [".py",".h",".cpp",".bin",".txt"]]
 names += [ROOT/"ML_model_seed_selection/runtime_inference/threshold_policy.json",ROOT/".tools/kira-runtime-final/kira",ROOT/".tools/kira-seed-inference/libseed.so",
  ROOT/"Kira_comparison/multiloop_native/s07_seed.py",ROOT/"Kira_comparison/acceleration/s01_fast_seed.py",ROOT/"ML_model_seed_selection/runtime_inference/compiled_export.json",ROOT/".tools/Ferl7/fer64"]
 for p in names:protocol["sha256"][str(p.relative_to(ROOT))]=sha(p)
 (HERE/"freeze.json").write_text(json.dumps(protocol,indent=2)+"\n")
 print(json.dumps(config),flush=True)
if __name__=="__main__":main()
