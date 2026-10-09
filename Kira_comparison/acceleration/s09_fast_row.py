"""NumPy inference with the unchanged reduction checkpoint."""
import json,pathlib,numpy as np
HERE=pathlib.Path(__file__).resolve().parent
class FastRow:
 def __init__(self):
  self.cfg=json.loads((HERE/"row_export.json").read_text())["config"]
  with np.load(HERE/"row_weights.npz",allow_pickle=False) as f:self.w={k:f[k] for k in f.files}
 def linear(self,x,key):return x@self.w[key+".weight"].T+self.w[key+".bias"]
 def probabilities(self,features):
  h=np.tanh(self.linear(features,"encoder.0"))
  joined=np.concatenate((h,np.broadcast_to(h.mean(0),h.shape),np.broadcast_to(h.max(0),h.shape)),axis=-1)
  logits=self.linear(np.tanh(self.linear(joined,"scorer.0")),"scorer.2").ravel()
  values=np.exp(logits-logits.max());return values/values.sum()
