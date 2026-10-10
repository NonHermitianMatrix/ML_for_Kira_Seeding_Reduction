"""Check exact bounded back substitution and unchanged learned policies."""
import json,pathlib,subprocess,sys,time
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 assert (ROOT/".tools/kira-integrated-runtime/kira").exists()
 out=HERE/"pilot_topological_v2";out.mkdir(exist_ok=True)
 case="validation_01_double_box";size=128
 variants=[("native",False,0),("native",True,0),("native",True,1),("learned",True,0),("learned",True,1),("seed_closed",True,0),("combined_closed",True,0)]
 for policy,compact,margin in variants:
  dest=out/f"{case}_{policy}_c{int(compact)}_m{margin}.json.gz"
  if not dest.exists():
   args=[sys.executable,str(HERE/"s02_run.py"),case,"--size",str(size),"--policy",policy,"--timeout","120","--margin",str(margin),"--output",str(dest),"--reference",str(ROOT/"Kira_comparison/multiloop_native/references"/(case+"_n128.json.gz")),"--weights",str(ROOT/"ML_model_reduction/cost_training/trained_weights.txt"),"--check-masters"]
   if not compact:args.append("--legacy-backsub")
   subprocess.run(args,cwd=ROOT,check=True,timeout=170)
  r=read_record(dest)
  assert not r.get("mismatches"),dest
  print(json.dumps({k:r.get(k) for k in ["policy","compact_back_substitution","margin","success","status","complete_seconds","stage_metrics","metrics","model"]}),flush=True)
if __name__=="__main__":main()
