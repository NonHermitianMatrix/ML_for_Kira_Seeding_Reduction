"""Choose from completed validation only, then freeze before test reductions."""
import hashlib,json,math,pathlib
from s10_summarize import aggregate,ratio
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def main():
 assert not (HERE/"trained_model/freeze.json").exists(),"Use a new experiment directory to change a frozen model."
 assert not list((HERE/"model_test").glob("*.json.gz")),"Existing test evidence must be preserved."
 assert json.loads((HERE/"integration/lazy_verification.json").read_text())["all_passed"]
 batches,rows=aggregate(HERE/"validation");assert len(batches)==5 and all(r["success"] and r["reference_checked"] for r in rows)
 grid=json.loads((HERE/"validation_grid.json").read_text());assert len(rows)==5*3*len(grid)
 keys=sorted({k for b in batches for k in b["methods"]});assert all(all(z["repeats"]==3 for z in b["methods"].values()) for b in batches)
 def best(prefix,bs):
  options=[(ratio(bs,k,"complete_seconds")["ratio"],k) for k in keys if k.startswith(prefix)]
  return min(options)[1]
 learned=best("learned:",batches);distance=best("distance:",batches)
 routes={}
 for topology in sorted({b["topology"] for b in batches}):
  bs=[b for b in batches if b["topology"]==topology];key=best("learned:",bs);rr=ratio(bs,key,"complete_seconds")
  # A 2% development margin avoids enabling a model for negligible changes.
  routes[topology]=dict(mode="learned" if rr["ratio"]<.98 else "off",threshold=float(key.split(":")[1]),validation_ratio=rr["ratio"])
 config=dict(runtime_binary=".tools/kira-equation-selection/kira-lazy",threshold=float(learned.split(":")[1]),distance_threshold=float(distance.split(":")[1]),by_topology=routes,unknown_mode="off",selection="Grouped complete-time ratios on validation only; forced learned and deterministic test arms remain separate.")
 (HERE/"trained_model/deployment.json").write_text(json.dumps(config,indent=2)+"\n")
 files=list(HERE.glob("s*.py"))+list(HERE.glob("s*.sh"))+list((HERE/"integration").glob("*.h"))+[HERE/"families.json",HERE/"trained_model/model.json",HERE/"trained_model/weights.txt",HERE/"trained_model/deployment.json",ROOT/".tools/kira-equation-selection/kira",ROOT/".tools/kira-equation-selection/kira-lazy"]
 frozen=dict(sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},test_profiles=8,test_batches=14,repetitions=5,test_workflows=280,validation_complete_workflows=len(rows),deployment=config)
 (HERE/"trained_model/freeze.json").write_text(json.dumps(frozen,indent=2)+"\n")
 print(json.dumps(config,indent=2))
if __name__=="__main__":main()
