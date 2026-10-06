"""Check batched seed scores and derivatives on mixed-length training examples."""
import hashlib,io,json,resource
from pathlib import Path
import numpy as np
import torch
from s01_data import HERE,config,read
from s02_model import SeedSelector
from s13_batch import collate,forward
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cfg=config();torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
 manifest=read(HERE/"data/manifest.json")
 payload=(HERE/"runs/all_loops_latest.pt").read_bytes()
 saved=torch.load(io.BytesIO(payload),map_location="cpu",weights_only=False)
 model=SeedSelector(cfg);model.load_state_dict(saved["model"]);model.eval()
 selected=[]
 for item in manifest["families"]:
  if item["family"].startswith("vacuum_L"):continue
  with np.load(HERE/item["file"],allow_pickle=False) as archive:
   lengths=np.diff(archive["offsets"])
   if (lengths==1).any() and (lengths>1).any():selected.append(item);break
 assert len(selected)==1
 added=[r for r in manifest["families"] if r["family"].startswith("vacuum_L12_")]
 for item in added:
  with np.load(HERE/item["file"],allow_pickle=False) as archive:
   if len(archive["seeds"])==125:selected.append(item);break
 assert len(selected)==2
 checks=[]
 for item in selected:
  with np.load(HERE/item["file"],allow_pickle=False) as archive:z={k:archive[k] for k in archive.files}
  lengths=np.diff(z["offsets"])
  single=np.flatnonzero(lengths==1);multiple=np.flatnonzero(lengths>1)
  assert len(single) and len(multiple)
  items=list(dict.fromkeys([int(single[0]),int(multiple[0]),int(np.argmax(lengths)),int(multiple[-1])]))
  x,mask,shared,y=collate(z,items)
  model.zero_grad(set_to_none=True)
  expected=torch.stack([model(dict(shared,terms=x[i,mask[i]])) for i in range(len(items))])
  loss=torch.nn.functional.binary_cross_entropy_with_logits(expected,y);loss.backward()
  gradients={k:(p.grad.clone() if p.grad is not None else None) for k,p in model.named_parameters()}
  model.zero_grad(set_to_none=True)
  actual=forward(model,x,mask,shared);other=torch.nn.functional.binary_cross_entropy_with_logits(actual,y);other.backward()
  assert torch.allclose(actual,expected,atol=3e-5,rtol=3e-5)
  assert torch.allclose(loss,other,atol=2e-6,rtol=2e-6)
  errors={}
  for k,p in model.named_parameters():
   if gradients[k] is None:assert p.grad is None;errors[k]=0.;continue
   assert p.grad is not None
   errors[k]=float((gradients[k]-p.grad).abs().max())
   assert torch.allclose(gradients[k],p.grad,atol=3e-5,rtol=3e-4),k
  checks.append(dict(family=item["family"],feature_sha256=sha(HERE/item["file"]),
    target_positions=items,term_lengths=[int(lengths[i]) for i in items],candidates=len(z["seeds"]),
    maximum_logit_difference=float((actual-expected).abs().max()),
    maximum_gradient_difference=max(errors.values())))
 result=dict(status="passed",checks=checks,checkpoint_sha256=hashlib.sha256(payload).hexdigest(),
  checkpoint_completed_epochs=saved["epoch"],source_hashes={n:sha(HERE/n) for n in ("s02_model.py","s13_batch.py","s18_validate_mixed_batches.py")},
  held_out_data_used=False,optimizer_updates=0,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 (HERE/"runs/mixed_batch_validation.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
