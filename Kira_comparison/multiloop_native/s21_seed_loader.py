"""Load unchanged NumPy weights with one filesystem read per archive."""
import io,json,pathlib
from s01_fast_seed import FastSeed,HERE as EXPORT
import s01_fast_seed as legacy
class NativeSeed(FastSeed):
 def __init__(self):
  import numpy as np
  legacy.np=np
  self.cfg=json.loads((EXPORT/"seed_export.json").read_bytes())["config"]
  with np.load(io.BytesIO((EXPORT/"seed_weights.npz").read_bytes()),allow_pickle=False) as f:
   self.w={k:f[k] for k in f.files}
