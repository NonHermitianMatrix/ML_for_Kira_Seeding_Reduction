"""Masked batch execution of the existing seed scorer, with identical features and weights."""
import math
import numpy as np
import torch
def collate(z,items):
 lengths=[int(z["offsets"][i+1]-z["offsets"][i]) for i in items];n=max(lengths)
 x=np.zeros((len(items),n,z["terms"].shape[1]),np.float32);mask=np.zeros((len(items),n),bool)
 for j,i in enumerate(items):
  lo,hi=z["offsets"][i:i+2];x[j,:hi-lo]=z["terms"][lo:hi];mask[j,:hi-lo]=True
 shared={k:torch.from_numpy(z[k]) for k in ("family","masters","seeds")}
 return torch.from_numpy(x),torch.from_numpy(mask),shared,torch.from_numpy(z["labels"][items].astype(np.float32))
def forward(model,x,mask,shared):
 t=model.term(x);B,n,h=t.shape
 pair_sum=t.new_zeros((B,h));count=mask.sum(1);pairs=(count*(count-1)).clamp_min(1)
 for start in range(0,n*n if n>1 else 0,model.cfg["pair_chunk"]):
  pos=torch.arange(start,min(n*n,start+model.cfg["pair_chunk"]));i=pos//n;j=pos%n
  valid=mask[:,i]&mask[:,j]&(i!=j)[None,:]
  a=t[:,i];b=t[:,j]
  pair_sum=pair_sum+(model.pair(torch.cat((a,b,a-b,a*b),-1))*valid[:,:,None]).sum(1)
 avg=(t*mask[:,:,None]).sum(1)/count[:,None]
 maximum=t.masked_fill(~mask[:,:,None],-torch.inf).max(1).values
 family=model.family(shared["family"]).expand(B,-1);masters=model.master(shared["masters"]).mean(0).expand(B,-1)
 context=torch.cat((avg,maximum,pair_sum/pairs[:,None],family,masters),-1)
 scores=[]
 layer=model.score[0]
 context_part=torch.nn.functional.linear(context,layer.weight[:,:5*h],layer.bias)
 for block in shared["seeds"].split(model.cfg["candidate_chunk"]):
  seed=model.seed(block);attention=torch.einsum("ch,bnh->bcn",seed,t)/math.sqrt(h)
  attention=attention.masked_fill(~mask[:,None,:],-torch.inf).softmax(-1)
  attended=attention@t
  seed_part=torch.nn.functional.linear(seed,layer.weight[:,5*h:6*h])
  attended_part=torch.nn.functional.linear(attended,layer.weight[:,6*h:])
  hidden=model.score[1](context_part[:,None,:]+seed_part[None,:,:]+attended_part)
  scores.append(model.score[2](hidden).squeeze(-1))
 return torch.cat(scores,1)
def verify(model,z):
 # Actual variable-length training examples verify output, BCE and parameter gradients.
 items=list(range(min(4,len(z["labels"]))))
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
  if gradients[k] is None:
   assert p.grad is None;errors[k]=0.;continue
  errors[k]=float((gradients[k]-p.grad).abs().max())
  assert torch.allclose(gradients[k],p.grad,atol=3e-5,rtol=3e-4),k
 model.zero_grad(set_to_none=True)
 return dict(targets=len(items),maximum_logit_difference=float((actual-expected).abs().max()),maximum_gradient_difference=max(errors.values()))
