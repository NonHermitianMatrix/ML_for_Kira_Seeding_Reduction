"""Run frozen, counterbalanced full-workflow ablations on new physical profiles."""
import json,os,pathlib,sys,subprocess
from s69_workflow_pair import workflow
from s03_records import read_record,write_record
from s49_reserved_references import verify as verify_parent
import hashlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def verify():
 verify_parent()
 frozen=json.loads((HERE/"pair_freeze.json").read_text())
 assert hashlib.sha256((HERE/"freeze.json").read_bytes()).hexdigest()==frozen["parent_freeze_sha256"]
 for n,h in frozen["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 return frozen
def main():
 frozen=verify();manifest=json.loads((HERE/"reserved_families.json").read_text())
 config=json.loads((HERE/"deployment.json").read_text());thresholds=json.loads((ROOT/frozen["seed_thresholds"]).read_text())["policies"]
 task=int(os.environ["SGE_TASK_ID"])-1
 groups=list(dict.fromkeys(c["group"] for c in manifest["cases"]));cases={c["id"]:c for c in manifest["cases"]}
 batches=[b for b in manifest["batches"] if cases[b["case"]]["group"]==groups[task]]
 os.environ.update(KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=".tools/kira-runtime-pair/kira",KIRA_SPARSE_FEATURES="1",KIRA_ROW_PAIR_FASTPATH="1",KIRA_CPP_SEED="1",KIRA_VECTOR_SEED="0")
 variants=frozen["variants"]
 for b in batches:
  c=cases[b["case"]];size=b["size"];name=c["id"];ref=HERE/"reserved_references"/f"{name}_n{size}.json.gz";assert read_record(ref)["success"]
  model=config["row_by_topology"].get(c["topology_group"],dict(model=config["unknown_row_model"]))["model"]
  threshold=thresholds.get(key(c,size),dict(threshold=config["unknown_seed_threshold"]))["threshold"];os.environ["KIRA_SEED_THRESHOLD"]=str(threshold)
  for repeat in range(frozen["repetitions"]):
   offset=(repeat+task)%len(variants);ordered=variants[offset:]+variants[:offset]
   if repeat%2:ordered=list(reversed(ordered))
   for variant in ordered:
    p=HERE/"pair_reserved_test"/f"{name}_n{size}_{variant}_r{repeat}.json.gz"
    actual=("row_small:"+model if variant=="row" else "combined:"+model if variant=="combined" else variant)
    if p.exists():r=read_record(p)
    else:
     subprocess.run([sys.executable,str(HERE/"s69_workflow_pair.py"),name,"--size",str(size),"--variant",actual,"--reference",str(ref),"--output",str(p)],check=True,timeout=540)
     r=read_record(p)
    print(json.dumps(dict(case=name,size=size,variant=variant,repeat=repeat,status=r["status"],seconds=r["complete_seconds"],operations=r["operations"],attempts=r["attempt_count"])),flush=True)
    for a in r["attempts"]:
     assert not read_record(ROOT/a).get("mismatches"),"Exact disagreement aborts this physical profile"
    old=read_record(HERE/"reserved_test"/f"{name}_n{size}_{variant}_r{repeat}.json.gz")
    for field in ["operations","equations","attempt_count"]:assert r[field]==old[field],(name,size,variant,field)
    for an,bn in zip(r["attempts"],old["attempts"]):
     a=read_record(ROOT/an);b=read_record(ROOT/bn)
     assert a.get("raw_export")==b.get("raw_export") and a["status"]==b["status"]
     if "predictions" in a:assert a["predictions"]["selection_bits_base64"]==b["predictions"]["selection_bits_base64"]
     for field in ["groups","changed_sources","updates","operations"]:
      assert [m[field] for m in a.get("metrics",[])]==[m[field] for m in b.get("metrics",[])],(name,size,variant,field)

if __name__=="__main__":main()
