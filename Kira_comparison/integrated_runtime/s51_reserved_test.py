"""Run frozen, counterbalanced full-workflow ablations on new physical profiles."""
import json,os,pathlib,sys,subprocess
from s24_workflow import workflow
from s03_records import read_record,write_record
from s49_reserved_references import verify
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def main():
 frozen=verify();manifest=json.loads((HERE/"reserved_families.json").read_text())
 config=json.loads((HERE/"deployment.json").read_text());thresholds=json.loads((ROOT/frozen["seed_thresholds"]).read_text())["policies"]
 task=int(os.environ["SGE_TASK_ID"])-1
 groups=list(dict.fromkeys(c["group"] for c in manifest["cases"]));cases={c["id"]:c for c in manifest["cases"]}
 batches=[b for b in manifest["batches"] if cases[b["case"]]["group"]==groups[task]]
 os.environ.update(KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=".tools/kira-runtime-final/kira",KIRA_SPARSE_FEATURES="1",KIRA_CPP_SEED="1",KIRA_VECTOR_SEED="0")
 variants=frozen["variants"]
 for b in batches:
  c=cases[b["case"]];size=b["size"];name=c["id"];ref=HERE/"reserved_references"/f"{name}_n{size}.json.gz";assert read_record(ref)["success"]
  model=config["row_by_topology"].get(c["topology_group"],dict(model=config["unknown_row_model"]))["model"]
  threshold=thresholds.get(key(c,size),dict(threshold=config["unknown_seed_threshold"]))["threshold"];os.environ["KIRA_SEED_THRESHOLD"]=str(threshold)
  for repeat in range(frozen["repetitions"]):
   offset=(repeat+task)%len(variants);ordered=variants[offset:]+variants[:offset]
   if repeat%2:ordered=list(reversed(ordered))
   for variant in ordered:
    p=HERE/"reserved_test"/f"{name}_n{size}_{variant}_r{repeat}.json.gz"
    actual=("row_small:"+model if variant=="row" else "combined:"+model if variant=="combined" else variant)
    if p.exists():r=read_record(p)
    else:
     subprocess.run([sys.executable,str(HERE/"s24_workflow.py"),name,"--size",str(size),"--variant",actual,"--reference",str(ref),"--output",str(p)],check=True,timeout=540)
     r=read_record(p)
    print(json.dumps(dict(case=name,size=size,variant=variant,repeat=repeat,status=r["status"],seconds=r["complete_seconds"],operations=r["operations"],attempts=r["attempt_count"])),flush=True)
    for a in r["attempts"]:
     assert not read_record(ROOT/a).get("mismatches"),"Exact disagreement aborts this physical profile"
if __name__=="__main__":main()
