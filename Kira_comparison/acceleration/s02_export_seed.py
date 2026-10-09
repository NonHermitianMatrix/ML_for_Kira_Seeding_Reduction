"""Export frozen seed weights and verify inference using training families only."""
import hashlib,importlib.util,json,pathlib,sys,time
import numpy as np
import torch
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import load_case,load_module,sha
from s01_fast_seed import FastSeed
def main():
 torch.set_num_threads(1)
 saved=torch.load(ROOT/"ML_model_seed_selection/trained_model.pt",map_location="cpu",weights_only=False)
 np.savez(HERE/"seed_weights.npz",**{k:v.numpy() for k,v in saved["model"].items()})
 (HERE/"seed_export.json").write_text(json.dumps(dict(config=saved["config"],checkpoint_sha256=sha(ROOT/"ML_model_seed_selection/trained_model.pt")),indent=2)+"\n")
 d=load_module("original_seed_data",ROOT/"ML_model_seed_selection/s01_data.py")
 m=load_module("original_seed_model",ROOT/"ML_model_seed_selection/s02_model.py")
 model=m.SeedSelector(saved["config"]);model.load_state_dict(saved["model"]);model.eval()
 fast=FastSeed();record=[];plan=json.loads((HERE/"plan.json").read_text())
 for case in plan["train"][:4]:
  fam=load_case(case,16);public=d.public_family(fam["definition"],fam["basis"])
  shared=d.encode_shared(public,fam["seeds"],saved["config"])
  shared_fast=fast.shared(fam["definition"],fam["masters"],fam["seeds"])
  for t in fam["targets"]:
   with torch.no_grad():p=model.probabilities(d.encode(t,public,fam["seeds"],saved["config"],shared)).numpy()
   q=fast.predict(t,shared_fast);err=float(np.max(np.abs(p-q)));same=bool(np.array_equal(p>=.5,q>=.5))
   assert err<1e-5 and same,(t["id"],err)
   record.append(dict(target=t["id"],probabilities=len(p),max_absolute_difference=err,decisions_identical=same))
 (HERE/"seed_export_validation.json").write_text(json.dumps(dict(passed=True,partition="train",cases=record,weights_sha256=sha(HERE/"seed_weights.npz")),indent=2)+"\n")
 print(json.dumps(dict(export_verified=True,targets=len(record),max_difference=max(r["max_absolute_difference"] for r in record))),flush=True)
if __name__=="__main__":main()
