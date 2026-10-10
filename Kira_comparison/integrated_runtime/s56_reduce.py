"""Apply the frozen integrated policy to a complete physical-family batch."""
import argparse,json,os,pathlib,sys,time
from s24_workflow import workflow
from s49_reserved_references import verify
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def select(case,size,requested):
 config=json.loads((HERE/"deployment.json").read_text())
 model=config["row_by_topology"].get(case["topology_group"],dict(model=config["unknown_row_model"]))["model"]
 thresholds=json.loads((ROOT/"ML_model_seed_selection/runtime_inference/threshold_policy.json").read_text())["policies"]
 threshold=thresholds.get(key(case,size),dict(threshold=config["unknown_seed_threshold"]))["threshold"]
 choices=dict(native="small",seed="seed",row="row_small:"+model,both="combined:"+model)
 if requested=="auto":
  variant=config["recommendations"].get(key(case,size),dict(variant=config["unknown_recommended_variant"]))["variant"]
  variant=variant.removesuffix("_compiled")
 else:variant=choices[requested]
 return variant,threshold
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--family-file",type=pathlib.Path,required=True,help="One case object with definition, targets, id, group and topology_group")
 ap.add_argument("--size",type=int,required=True);ap.add_argument("--reference",type=pathlib.Path,required=True,help="Exact common master-basis reduction record")
 ap.add_argument("--output",type=pathlib.Path,required=True);ap.add_argument("--policy",choices=["auto","native","seed","row","both"],default="auto")
 a=ap.parse_args();verify();case=json.loads(a.family_file.read_text());case.setdefault("split","application")
 assert 0<a.size<=len(case["targets"])
 variant,threshold=select(case,a.size,a.policy)
 os.environ.update(KIRA_RUNTIME_BINARY=".tools/kira-runtime-final/kira",KIRA_RUNTIME_SCRATCH="node",KIRA_CPP_SEED="1",KIRA_VECTOR_SEED="0",KIRA_SPARSE_FEATURES="1",KIRA_SEED_THRESHOLD=str(threshold))
 result=workflow(case,a.size,variant,a.reference.resolve(),a.output.resolve())
 print(json.dumps(dict(requested_policy=a.policy,applied_policy=variant,threshold=threshold,result=str(a.output),success=result["success"],complete_seconds=result["complete_seconds"])),flush=True)
if __name__=="__main__":main()
