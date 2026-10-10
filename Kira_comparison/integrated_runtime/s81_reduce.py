"""Reduce new targets with a known master basis; reference answers are optional."""
import argparse,json,os,pathlib,sys,time
from s80_workflow_application import workflow
from s03_records import put,payload
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def select(case,size,requested):
 if requested=="native":return "small",.01
 config=json.loads((HERE/"deployment.json").read_text())
 model=config["row_by_topology"].get(case["topology_group"],dict(model=config["unknown_row_model"]))["model"]
 if requested=="auto":
  variant=config["recommendations"].get(key(case,size),dict(variant=config["unknown_recommended_variant"]))["variant"].removesuffix("_compiled")
 else:variant=dict(seed="seed",row="row_small:"+model,both="combined:"+model)[requested]
 threshold=.01
 if variant=="seed" or variant.startswith("combined"):
  thresholds=json.loads((ROOT/"ML_model_seed_selection/runtime_inference/threshold_policy.json").read_text())["policies"]
  threshold=thresholds.get(key(case,size),dict(threshold=config["unknown_seed_threshold"]))["threshold"]
 return variant,threshold
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--family-file",type=pathlib.Path,required=True);ap.add_argument("--size",type=int,required=True)
 basis_args=ap.add_mutually_exclusive_group(required=True)
 basis_args.add_argument("--masters-file",type=pathlib.Path,help="JSON list of master index vectors; target coefficients are not required")
 basis_args.add_argument("--reference",type=pathlib.Path,help="Optional exact-reference mode used for benchmarks")
 ap.add_argument("--output",type=pathlib.Path,required=True)
 ap.add_argument("--policy",choices=["auto","native","seed","row","both"],default="auto")
 ap.add_argument("--verify-release",action="store_true",help="Run the common release-integrity check before timing")
 a=ap.parse_args()
 assert (HERE/"pair_freeze.json").exists(),"The optimized implementation must pass validation and be frozen"
 if a.verify_release:
  from s74_reserved_pair import verify
  verify()
 start=time.perf_counter();case=json.loads(a.family_file.read_text());case.setdefault("split","application")
 assert 0<a.size<=len(case["targets"])
 basis=None
 if a.masters_file:
  basis=json.loads(a.masters_file.read_text())
  if isinstance(basis,dict):basis=basis["masters"]
  assert isinstance(basis,list)
 reference=a.reference.resolve() if a.reference else None
 output=a.output.resolve();assert output.is_relative_to(HERE) and not output.exists()
 variant,threshold=select(case,a.size,a.policy)
 os.environ.update(KIRA_RUNTIME_BINARY=".tools/kira-runtime-pair/kira",KIRA_RUNTIME_SCRATCH="node",KIRA_CPP_SEED="1",KIRA_VECTOR_SEED="0",KIRA_SPARSE_FEATURES="1",KIRA_ROW_PAIR_FASTPATH="1",KIRA_SEED_THRESHOLD=str(threshold))
 preparation=time.perf_counter()-start
 result=workflow(case,a.size,variant,reference,output,basis=basis)
 routing=dict(case=case["id"],requested_policy=a.policy,applied_policy=variant,seed_threshold=threshold,basis_only=reference is None,
  input_and_routing_seconds=preparation,workflow_seconds=result["complete_seconds"],application_seconds=preparation+result["complete_seconds"],result=str(output.relative_to(ROOT)),
  success=result["success"],basis_admitted=result["basis_admitted"],reference_checked=result["reference_checked"])
 put(output.with_name(output.name.removesuffix(".json.gz")+"_routing.json.gz"),payload(routing))
 print(json.dumps(routing),flush=True)
if __name__=="__main__":main()
