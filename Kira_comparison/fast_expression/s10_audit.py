"""Independently check raw Kira coefficients and unchanged seed decisions."""
import argparse,gzip,hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];ACC=HERE.parent/"acceleration"
sys.path[:0]=[str(ACC),str(HERE.parent)]
import s80_expression_test_audit as independent
import s36_evidence as archive
archive.HERE=HERE
from s13_records import read_record
def mapped(p):
 r=read_record(p);r["policy"]="stored_ml_lower" if r["policy"].endswith("_ml") else "stored_pool";return r
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--stage",required=True);a=ap.parse_args()
 if a.stage=="test":
  frozen=json.loads((HERE/"freeze.json").read_text())
  for name,h in frozen["sha256"].items():assert sha(ROOT/name)==h,name
  assert len(list((HERE/"test").glob("*.json.gz")))==frozen["expected_trials"]
 independent.HERE=HERE;independent.read_record=mapped;independent.unpack=archive.unpack
 sys.argv=[sys.argv[0],"--stage",a.stage];independent.main()
 records=[read_record(p) for p in sorted((HERE/a.stage).glob("*.json.gz"))]
 groups={(r["case"],r["size"],r["repetition"],r["policy"]):r for r in records}
 comparisons=0;identical_raw=0;probability_pairs=0
 for key,r in groups.items():
  if not r["policy"].startswith("exit_"):continue
  other=groups[key[:3]+("stock_"+r["policy"].split("_",1)[1],)]
  if "model" in r and "model" in other:
   assert r["model"].get("selected_seeds")==other["model"].get("selected_seeds")
   assert r["model"].get("probabilities")==other["model"].get("probabilities")
   if r["policy"].endswith("_ml"):probability_pairs+=1
  if not (r["success"] and other["success"] and r["status"]==other["status"]=="completed"):continue
  assert r["targets"]==other["targets"] and r["fallback"]==other["fallback"]
  assert len(r["attempts"])==len(other["attempts"])
  for left,right in zip(r["attempts"],other["attempts"]):
   if "input_sha256" in left or "input_sha256" in right:
    assert left["input_sha256"]==right["input_sha256"]
    assert left["source_ids"]==right["source_ids"]
    assert left["counters"]==right["counters"]
  comparisons+=1
  identical_raw+=int(r["attempts"][-1]["export_sha256"]==other["attempts"][-1]["export_sha256"])
 validation=json.loads((HERE/(a.stage+"_validation.json")).read_text())
 validation.update(binary_pair_checks=comparisons,identical_raw_export_pairs=identical_raw,unchanged_prediction_pairs=probability_pairs,
  original_binary_preserved=sha(ROOT/".tools/kira/bin/kira")==json.loads((HERE/"build.json").read_text())["original_binary_sha256"])
 assert validation["original_binary_preserved"]
 (HERE/(a.stage+"_validation.json")).write_text(json.dumps(validation,indent=2)+"\n")
 print(json.dumps({k:v for k,v in validation.items() if k not in ["result_sha256","incomplete"]}),flush=True)
if __name__=="__main__":main()
