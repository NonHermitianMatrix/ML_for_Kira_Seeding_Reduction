"""Apply the unchanged neural seed model without NumPy startup in production."""
import array,base64,ctypes,hashlib,json,math,pathlib,struct,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"Kira_comparison/acceleration"));sys.path.insert(0,str(ROOT/"Kira_comparison/multiloop_native"))
from s01_fast_seed import text_features
from s07_seed import candidates
_MODEL=None
class CompiledSeed:
 def __init__(self):
  self.cfg=json.loads((HERE/"compiled_export.json").read_text())["config"]
  self.lib=ctypes.CDLL(str(ROOT/".tools/kira-seed-inference/libseed.so"))
  self.lib.seed_create.argtypes=[ctypes.c_char_p];self.lib.seed_create.restype=ctypes.c_void_p
  self.lib.seed_error.restype=ctypes.c_char_p
  f=ctypes.POINTER(ctypes.c_float);i=ctypes.POINTER(ctypes.c_int)
  self.lib.seed_predict.argtypes=[ctypes.c_void_p,f,f,i,ctypes.c_uint,i,ctypes.c_uint,i,ctypes.c_uint,ctypes.c_uint,f];self.lib.seed_predict.restype=ctypes.c_int
  self.handle=self.lib.seed_create(str(HERE/"compiled_weights.bin").encode())
  if not self.handle:raise RuntimeError(self.lib.seed_error().decode())
 def probabilities(self,definition,masters,targets,seeds):
  c=self.cfg;n=len(definition["propagators"]);assert all(len(a)==n for a in masters+targets+seeds)
  family={k:definition[k] for k in ("loop_momenta","external_momenta","propagators","invariants","scalarproduct_rules")}
  fv=list(text_features(json.dumps(family,sort_keys=True,separators=(",",":")),c["hash_bins"]))
  fv += [math.log1p(x) for x in (len(family["loop_momenta"]),len(family["propagators"]),len(family["external_momenta"]),len(family["invariants"]))]
  ff=(ctypes.c_float*len(fv))(*fv);cv=text_features("1",c["hash_bins"]);cc=(ctypes.c_float*len(cv))(*cv)
  def indices(rows):
   data=array.array("i",(v for a in rows for v in a));assert data.itemsize==4
   return data,(ctypes.c_int*len(data)).from_buffer(data)
  mm,mp=indices(masters);tt,tp=indices(targets);ss,sp=indices(seeds)
  out=(ctypes.c_float*len(seeds))()
  rc=self.lib.seed_predict(self.handle,ff,cc,mp,len(masters),tp,len(targets),sp,len(seeds),n,out)
  if rc:raise RuntimeError(self.lib.seed_error().decode())
  return list(out)
def choose(definition,masters,targets,spec,closure=False,use_model=True,threshold=.01):
 global _MODEL
 begin=time.perf_counter();seeds=candidates(definition,spec["r"],spec["s"],spec["d"]);enumeration=time.perf_counter()-begin
 assert seeds and masters
 load=0.;hit=_MODEL is not None;t=time.perf_counter()
 if use_model:
  if _MODEL is None:_MODEL=CompiledSeed()
  load=time.perf_counter()-t;t=time.perf_counter()
  probabilities=_MODEL.probabilities(definition,masters,targets,seeds)
 else:probabilities=[0.]*len(seeds)
 mandatory=set(map(tuple,targets))|set(map(tuple,masters))
 mask=[p>=threshold or a in mandatory or all(x in (0,1) for x in a) or (closure and sum(max(0,x-1)+max(0,-x) for x in a)<=1) for a,p in zip(seeds,probabilities)]
 selected=[a for a,keep in zip(seeds,mask) if keep];bits=bytearray((len(mask)+7)//8)
 for i,b in enumerate(mask):
  if b:bits[i//8]|=1<<(i%8)
 raw=array.array("f",probabilities);indices=array.array("h",(v for a in seeds for v in a))
 if sys.byteorder!="little":raw.byteswap();indices.byteswap()
 data=dict(candidate_count=len(seeds),candidate_sha256=hashlib.sha256(indices.tobytes()).hexdigest(),probabilities_float32_base64=base64.b64encode(raw.tobytes()).decode(),selection_bits_base64=base64.b64encode(bits).decode(),threshold=threshold,closure=closure,learned_model_used=use_model,context="ordered sum of the supplied target integrals with coefficient one",mandatory_rule="sector corners, requested targets and prescribed masters; closure retains all seeds with total dots plus numerator power at most one",backend="compiled float32 neural network")
 timing=dict(model_cache_hit=hit,shared_cache_hit=False,enumeration_seconds=enumeration,load_seconds=load,inference_seconds=time.perf_counter()-t,candidates=len(seeds),selected=len(selected))
 return selected,data,timing
