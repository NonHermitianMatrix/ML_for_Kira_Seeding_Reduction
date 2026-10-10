"""Verify shared feature formulas and native tree scores in exact reductions."""
import json,math,os,pathlib,sys
from s02_run import run
from s03_records import read_record
from s14_runtime_config import configuration
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def score(nodes,x):
 i=0
 while nodes[i]["feature"]>=0:
  n=nodes[i];i=n["left"] if x[n["feature"]]<=n["cut"] else n["right"]
 return nodes[i]["value"]
def main():
 config=configuration();os.environ["KIRA_RUNTIME_SCRATCH"]=config["scratch_location"]
 os.environ["KIRA_RUNTIME_BINARY"]=".tools/kira-runtime-fast/kira";os.environ["KIRA_COST_FEATURE_PARITY"]="1"
 folder=ROOT/"ML_model_reduction/runtime_training/candidates/output_bytes"
 model=json.loads((folder/"model.json").read_text());manifest=json.loads((HERE/"families.json").read_text())
 results=[];checked=0;groups=0
 for case in [c for c in manifest["cases"] if c["split"]=="validation" and c["id"].endswith("_deep")]:
  name=case["id"];size=min(32,len(case["targets"]));ref=HERE/"references"/f"{name}_n{size}.json.gz"
  path=HERE/"fast_row_parity"/f"{name}.json.gz"
  r=read_record(path) if path.exists() else run(case,size,"learned",path,timeout=180,margin=1,reference=ref,weights=folder/"weights.txt",records=True,check_masters=True,compact=True)
  assert r["success"] and r["reference_checked"],(name,r["status"])
  count=sum(m.get("feature_parity_checked",0) for m in r["metrics"]);assert count>0;groups+=count
  for g in r.get("choices",[]):
   f=[c["features"] for c in g["candidates"]]
   scores=[0.]+[score(model["nodes"],[a-b for a,b in zip(row,f[0])]) for row in f[1:]]
   assert all(abs(a-c["score"])<1e-12 for a,c in zip(scores,g["candidates"]))
   q=min(range(len(scores)),key=lambda i:scores[i])
   if scores[q]>-model["minimum_predicted_gain"]:q=0
   assert q==g["selected"],(name,g["group"],q,g["selected"])
   checked+=1
  results.append(dict(case=name,success=True,feature_groups=count,recorded_decisions=len(r.get("choices",[]))))
 result=dict(all_passed=True,feature_groups=groups,python_cpp_decisions=checked,cases=results)
 (HERE/"fast_row_parity.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
