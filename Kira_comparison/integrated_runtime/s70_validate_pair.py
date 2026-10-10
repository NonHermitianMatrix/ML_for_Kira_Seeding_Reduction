"""Check two-row shortcut parity and full workflow cost on validation profiles only."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_seed_selection/runtime_inference"))
from s10_fit_thresholds import key
def main():
 task=int(os.environ["SGE_TASK_ID"])-1
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="validation"]
 bases=[c["id"] for c in cases if not c["id"].endswith("_deep")]
 cases=[c for c in cases if c["id"] in [bases[task],bases[task]+"_deep"]]
 config=json.loads((HERE/"deployment.json").read_text());thresholds=json.loads((ROOT/"ML_model_seed_selection/runtime_inference/threshold_policy.json").read_text())["policies"]
 env=dict(os.environ,KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=".tools/kira-runtime-pair/kira",KIRA_SPARSE_FEATURES="1",KIRA_CPP_SEED="1",KIRA_VECTOR_SEED="0")
 for case in cases:
  name=case["id"];size=min(32,len(case["targets"]));model=config["row_by_topology"][case["topology_group"]]["model"]
  threshold=thresholds[key(case)]["threshold"]
  ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
  variants=["small","fill_small","row_small:"+model,"combined:"+model]
  for rep in range(3):
   for v in variants[rep:]+variants[:rep]:
    rows=[]
    for flag in ([0,1] if (rep+task)%2==0 else [1,0]):
     out=HERE/"pair_validation"/f"{name}_{v.replace(':','-')}_c{flag}_r{rep}.json.gz"
     if not out.exists():
      e=dict(env,KIRA_SEED_THRESHOLD=str(threshold),KIRA_ROW_PAIR_FASTPATH=str(flag))
      subprocess.run([sys.executable,str(HERE/"s69_workflow_pair.py"),name,"--size",str(size),"--variant",v,"--reference",str(ref),"--output",str(out)],env=e,check=True,timeout=540)
     r=read_record(out);assert r["success"] and r["reference_checked"];rows.append(r)
     if flag and v!="small":assert sum(m.get("pair_fast_groups",0) for a in r["attempts"] for m in read_record(ROOT/a).get("metrics",[]))>0
     print(json.dumps(dict(case=name,variant=v,cache=flag,repeat=rep,seconds=r["complete_seconds"],forward=r["forward_seconds"],decision=r["decision_seconds"])),flush=True)
    a,b=rows;assert a["operations"]==b["operations"] and a["equations"]==b["equations"] and a["attempt_count"]==b["attempt_count"]
    for an,bn in zip(a["attempts"],b["attempts"]):
     aa=read_record(ROOT/an);bb=read_record(ROOT/bn)
     assert aa.get("raw_export")==bb.get("raw_export") and aa["status"]==bb["status"]
     for field in ["groups","changed_sources","updates","operations","choice_digest"]:
      assert [m[field] for m in aa.get("metrics",[])]==[m[field] for m in bb.get("metrics",[])],(name,v,field)
if __name__=="__main__":main()
