"""Freeze the validated policies, integration and reserved protocol before tests."""
import hashlib,json,pathlib,sys
from s04_workflows import HERE,PARENT,ROOT,EARLY,OLD,read,guard
from s06_validate import aggregate,rows
from s12_reduce import structural_key
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 dest=HERE/"trained_model/freeze.json";assert not dest.exists()
 comp=json.loads((HERE/"validation/final_selection.json").read_text())
 parity=json.loads((HERE/"validation/prediction_parity.json").read_text());assert parity["all_passed"] and parity["decisions_checked"]==918744
 split=json.loads((HERE/"split_audit.json").read_text());assert split["all_new_profiles_disjoint"]
 candidates=json.loads((HERE/"validation/candidates.json").read_text())
 manifest=json.loads((HERE/"families_test.json").read_text());routes=comp["by_topology"]
 old=json.loads((ROOT/"Kira_comparison/integrated_runtime/deployment.json").read_text())
 sys.path.insert(0,str(ROOT/"Kira_comparison/integrated_runtime"))
 from s108_reduce import select
 for top,route in routes.items():
  if route["row"]:
   name=old["row_by_topology"].get(top,dict(model=old["unknown_row_model"]))["model"]
   route["row_weights"]=str(pathlib.Path("ML_model_reduction/runtime_training/trajectory_candidates")/name/"weights.txt")
  if route.get("seed"):
   source=next(c for c in manifest["cases"] if c["topology_group"]==top)
   route["seed_thresholds"]={str(n):select(source,n,"seed")[1] for n in [32,128]}
 domains={}
 for c in manifest["cases"]:
  top=c["topology_group"];d=domains.setdefault(top,dict(structure=structural_key(c),targets={}))
  assert d["structure"]==structural_key(c)
  for b in manifest["batches"]:
   if b["case"]==c["id"]:d["targets"][str(b["size"])]=c["targets"][:b["size"]]
 config=dict(by_topology=routes,domains=domains,distance_by_topology={top:int(v["distance"].removeprefix("distance")) for top,v in candidates["by_topology"].items()},runtime_binary=EARLY,previous_binary=OLD,scope="Known two/three-loop family structures with the recorded 21, 32 and 128 target lists. Other inputs retain the previous guarded route.",selection="Frozen from development and validation costs. Model decisions precede equation construction; exact native fallback remains enabled.")
 (HERE/"trained_model/deployment.json").write_text(json.dumps(config,indent=2)+"\n")
 methods=["native","previous","early","deployed","control"] if any(r["row"] or r.get("seed") for r in routes.values()) else ["native","previous","deployed","control"]
 manifest.update(methods=methods,workflows=len(manifest["batches"])*manifest["repetitions"]*len(methods),applications=len(manifest["cases"]))
 (HERE/"families_test.json").write_text(json.dumps(manifest,indent=2)+"\n")
 paths=[HERE/n for n in ["s00_build.py","s02_train.py","s03_early_run.py","s04_workflows.py","s06_validate.py","s08_parity.py","s10_composition.py","s16_seed_composition.py","s12_reduce.py","s13_freeze.py","s14_test.py","integration/s00_early_policy.h","integration/build.json","additional_families.json","families_test.json","reserved_parameters.json","split_audit.json","trained_model/deployment.json"]]
 paths += [HERE/"trained_model"/m/f for m in ["early_d8","early_d12"] for f in ["model.json","weights.txt"]]
 paths += [ROOT/EARLY,ROOT/OLD,PARENT/"trained_model/model.json",PARENT/"trained_model/weights.txt",PARENT/"trained_model/deployment_final.json"]
 paths += [ROOT/r["row_weights"] for r in routes.values() if r["row"]]
 paths += [ROOT/"ML_model_seed_selection/runtime_inference/s14_lane_seed.py",ROOT/".tools/kira-parallel-inference/libseed.so",ROOT/"ML_model_seed_selection/runtime_inference/threshold_policy.json"]
 model_groups=set()
 for m in ["early_d8","early_d12"]:
  model=json.loads((HERE/"trained_model"/m/"model.json").read_text())
  assert model["training_groups"]==8 and model["training_rows"]==153124
  for entry in model["training_files"]:
   p=ROOT/entry["file"];assert sha(p)==entry["sha256"],p
   model_groups.add(read(p)["group"])
 assert all(c["group"] not in model_groups for c in manifest["cases"])
 frozen=dict(sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},workflows=manifest["workflows"],applications=manifest["applications"],repetitions=manifest["repetitions"],methods=methods,exact_checks="All target coefficients in Q(d) compared with an independent native reference; basis-only applications audited after execution.")
 dest.write_text(json.dumps(frozen,indent=2)+"\n");guard();print(json.dumps(dict(frozen=True,methods=methods,workflows=frozen["workflows"],routes=routes),indent=2))
if __name__=="__main__":main()
