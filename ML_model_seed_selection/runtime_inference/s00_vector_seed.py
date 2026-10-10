"""Construct unchanged seed index features with bounded NumPy arrays."""
import json,math,pathlib,sys
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Kira_comparison/multiloop_native"))
sys.path.insert(0,str(ROOT/"Kira_comparison/acceleration"))
from s21_seed_loader import NativeSeed
from s01_fast_seed import text_features
def index_batch(indices,cfg):
 a=np.asarray(indices,dtype=np.int32)
 assert a.ndim==2 and len(a)>0 and 0<a.shape[1]<=cfg["max_indices"]
 n=a.shape[1];maximum=int(np.abs(a.astype(np.int64)).max())
 assert maximum<=10000
 signed=np.asarray([math.copysign(math.log1p(abs(i)),i) if i else 0. for i in range(-maximum,maximum+1)],np.float32)
 limit=cfg["max_indices"];out=np.zeros((len(a),3*limit+5),np.float32)
 out[:,:n]=signed[a+maximum]
 positive=a>0;out[:,limit:limit+n]=positive;out[:,2*limit:2*limit+n]=1
 r=np.maximum(a,0).sum(1,dtype=np.int64);s=-np.minimum(a,0).sum(1,dtype=np.int64);t=positive.sum(1)
 counts=np.column_stack((r,s,t,r-t,np.full(len(a),n,np.int64)))
 table=np.asarray([math.log1p(i) for i in range(int(counts.max())+1)],np.float32)
 out[:,-5:]=table[counts]
 return out
class VectorSeed(NativeSeed):
 def shared(self,definition,masters,seeds):
  c=self.cfg
  family={k:definition[k] for k in ("loop_momenta","external_momenta","propagators","invariants","scalarproduct_rules")}
  fv=list(text_features(json.dumps(family,sort_keys=True,separators=(",",":")),c["hash_bins"]))
  fv += [math.log1p(x) for x in (len(family["loop_momenta"]),len(family["propagators"]),len(family["external_momenta"]),len(family["invariants"]))]
  master=self.embed(index_batch(masters,c),"master").mean(0)
  seed=self.embed(index_batch(seeds,c),"seed")
  return self.embed(np.array(fv,np.float32),"family"),master,seed
