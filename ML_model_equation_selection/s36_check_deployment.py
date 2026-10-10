"""Verify that deployment selects measured successful arms and guards combinations."""
import hashlib,json,pathlib
from s35_reduce import choose
from s02_records import read
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def main():
 config=json.loads((HERE/"trained_model/deployment_final.json").read_text())
 cases=json.loads((HERE/"families_confirmation.json").read_text())["cases"]
 checks=[]
 for c in cases:
  for base in ["native","both"]:
   mode,t=choose(c,21,base,config)
   out=HERE/"model_test/confirmation"/("" if base=="native" else "composition")/f'{c["id"]}_{mode}_r0.json.gz'
   r=read(out);assert r["success"] and r["reference_checked"] and r["base"]==base and r["mode"]==mode and r["threshold"]==t
   checks.append(dict(case=c["id"],base=base,selected_mode=mode,measured_record=str(out.relative_to(HERE))))
  for base in ["seed","row"]:assert choose(c,21,base,config)==("off",0)
  assert choose(c,20,"native",config)==("off",0)
 for c in json.loads((HERE/"families.json").read_text())["cases"]:
  if c["topology_group"]!="sunrise":assert choose(c,min(32,len(c["targets"])),"native",config)==("off",0)
 files=[HERE/"s35_reduce.py",HERE/"trained_model/deployment_final.json",HERE/"trained_model/model.json",HERE/"trained_model/weights.txt"]
 result=dict(all_passed=True,measured_arm_matches=len(checks),checks=checks,unsupported_targets_and_model_combinations_guarded=True,sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
 (HERE/"trained_model/deployment_verification.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(dict(all_passed=True,measured_arm_matches=len(checks))),flush=True)
if __name__=="__main__":main()
