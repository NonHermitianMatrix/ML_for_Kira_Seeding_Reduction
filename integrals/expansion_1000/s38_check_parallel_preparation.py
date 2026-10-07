"""Compare parallel preparation with saved training arrays, without model updates."""
import hashlib,json,os,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MODEL=ROOT/"ML_model_reduction"
sys.path.insert(0,str(MODEL))
from s00_common import read,sha,config,SPLIT,write_json
from s02_prepare_data import prepare_selected
def main():
 assert int(os.environ.get("NSLOTS","1"))>=4
 old=read(MODEL/"data/manifest.json")["families"]
 selected=[old[0],old[len(old)//2],old[-1]]
 metas={m["family"]:m for m in read(SPLIT)["families"]}
 before={m["family"]:{} for m in selected}
 for item in selected:
  with np.load(MODEL/item["file"],allow_pickle=False) as z:
   before[item["family"]]={k:z[k].copy() for k in z.files}
 chosen=[metas[m["family"]] for m in selected]
 assert all(m["split"]=="train" for m in chosen)
 cfg=config();signature=dict(split_sha256=sha(SPLIT),config_sha256=sha(MODEL/"config.json"),encoder_sha256=sha(MODEL/"s01_state.py"),preparer_sha256=sha(MODEL/"s02_prepare_data.py"))
 results=list(prepare_selected(chosen,cfg,signature,4));checks=[]
 for item in results:
  with np.load(MODEL/item["file"],allow_pickle=False) as z:
   assert set(z.files)==set(before[item["family"]])
   for key in z.files:assert np.array_equal(z[key],before[item["family"]][key]),(item["family"],key)
  checks.append(dict(family=item["family"],arrays=len(before[item["family"]]),sha256=item["sha256"]))
 result=dict(status="passed",checks=checks,workers=4,arrays_exactly_equal=True,optimizer_updates=0,held_out_examples_read=False,preparer_sha256=sha(MODEL/"s02_prepare_data.py"),common_sha256=sha(MODEL/"s00_common.py"))
 write_json(HERE/"parallel_preparation_validation.json",result);print(json.dumps(result),flush=True)
if __name__=="__main__":main()
