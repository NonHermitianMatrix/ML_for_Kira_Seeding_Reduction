"""Export the frozen row model and check numeric equivalence on bounded feature arrays."""
import hashlib,json,pathlib,sys
import numpy as np,torch
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_reduction"))
from s03_model import ReductionSelector
from s09_fast_row import FastRow
torch.set_num_threads(1)
path=ROOT/"ML_model_reduction/trained_model.pt";saved=torch.load(path,map_location="cpu",weights_only=False)
model=ReductionSelector(saved["feature_dim"],saved["config"]);model.load_state_dict(saved["model"]);model.eval()
np.savez(HERE/"row_weights.npz",**{k:v.detach().numpy() for k,v in saved["model"].items()})
(HERE/"row_export.json").write_text(json.dumps(dict(config=saved["config"],feature_dim=saved["feature_dim"],
 checkpoint_sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2)+"\n")
fast=FastRow();rng=np.random.default_rng(6841);records=[]
for n in (2,6,20,100,500):
 f=rng.normal(size=(n,saved["feature_dim"])).astype(np.float32)
 with torch.inference_mode():p=torch.softmax(model(torch.from_numpy(f)[None],torch.ones((1,n),dtype=torch.bool))[0],0).numpy()
 q=fast.probabilities(f);difference=float(np.max(np.abs(p-q)))
 assert difference<1e-5 and p.argmax()==q.argmax()
 records.append(dict(actions=n,max_probability_difference=difference,selected_action_equal=True))
(HERE/"row_export_validation.json").write_text(json.dumps(dict(scope="Implementation equivalence on seeded feature arrays; physical live-state validation follows in native trials.",records=records),indent=2)+"\n")
print("Row export verified",flush=True)
