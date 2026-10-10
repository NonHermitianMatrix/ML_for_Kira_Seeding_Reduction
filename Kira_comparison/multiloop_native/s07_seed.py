"""Apply the saved seed model to a finite native Laporta seed region."""
import struct,base64,functools,hashlib,itertools,json,pathlib,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"acceleration"))
from s21_seed_loader import NativeSeed as FastSeed
_NATIVE_CACHE=None
_SHARED_CACHE={}
@functools.lru_cache(maxsize=None)
def distribute(total,n):
 if not n:return [()] if total==0 else []
 if n==1:return [(total,)]
 return [(a,)+b for a in range(total+1) for b in distribute(total-a,n-1)]
@functools.lru_cache(maxsize=2)
def _candidates(n,physical,r,s,d):
 out=[]
 for mask in range(1,1<<physical):
  pos=[j for j in range(physical) if mask&(1<<j)];neg=[j for j in range(n) if j not in pos]
  for dots in range(min(d,r-len(pos))+1):
   for extra in distribute(dots,len(pos)):
    for numerator in range(s+1):
     for powers in distribute(numerator,len(neg)):
      a=[0]*n
      for j,x in zip(pos,extra):a[j]=x+1
      for j,x in zip(neg,powers):a[j]=-x
      out.append(tuple(a))
      if len(out)>300000:raise ValueError("Native seed candidate capacity")
 return out
def candidates(definition,r,s,d):
 return _candidates(len(definition["propagators"]),definition["physical_propagators"],r,s,d)
def choose(definition,masters,targets,spec,closure=False,use_model=True,threshold=.01):
 global _NATIVE_CACHE
 begin=time.perf_counter();seeds=candidates(definition,spec["r"],spec["s"],spec["d"]);enumeration=time.perf_counter()-begin
 if not seeds or not masters:raise ValueError("Seed prediction requires candidates and a prescribed basis")
 t=time.perf_counter();load=0.;model_hit=False;shared_hit=False
 if use_model:
  import numpy as np
  model_hit=_NATIVE_CACHE is not None
  if _NATIVE_CACHE is None:_NATIVE_CACHE=FastSeed()
  model=_NATIVE_CACHE;load=time.perf_counter()-t;t=time.perf_counter()
  key=(json.dumps(definition,sort_keys=True),tuple(map(tuple,masters)),spec["r"],spec["s"],spec["d"])
  shared_hit=key in _SHARED_CACHE
  if shared_hit:shared=_SHARED_CACHE[key]
  else:
   shared=model.shared(definition,masters,seeds)
   if len(_SHARED_CACHE)>=2:_SHARED_CACHE.pop(next(iter(_SHARED_CACHE)))
   _SHARED_CACHE[key]=shared
  target=dict(id="batch_sum",terms=[dict(indices=a,coefficient="1") for a in targets])
  probabilities=model.predict(target,shared).astype("<f4",copy=False).tolist()
 else:probabilities=[0.0]*len(seeds)
 # Every corner is retained. Actual targets and prescribed masters are also
 # retained when they occur in the candidate region.
 mandatory=set(map(tuple,targets))|set(map(tuple,masters))
 mask=[float(p)>=threshold or a in mandatory or all(x in (0,1) for x in a) or (closure and sum(max(0,x-1)+max(0,-x) for x in a)<=1)
                for a,p in zip(seeds,probabilities)]
 selected=[a for a,keep in zip(seeds,mask) if keep]
 bits=bytearray((len(mask)+7)//8)
 for i,b in enumerate(mask):
  if b:bits[i//8]|=1<<(i%8)
 data=dict(candidate_count=len(seeds),candidate_sha256=hashlib.sha256(struct.pack("<"+"h"*(len(seeds)*len(seeds[0])),*(x for a in seeds for x in a))).hexdigest(),
  probabilities_float32_base64=base64.b64encode(struct.pack("<"+"f"*len(probabilities),*probabilities)).decode(),
  selection_bits_base64=base64.b64encode(bits).decode(),
  threshold=threshold,closure=closure,learned_model_used=use_model,context="ordered sum of the supplied target integrals with coefficient one",
  mandatory_rule="sector corners, requested targets and prescribed masters; when closure is enabled, all seeds with total dots plus numerator power at most one")
 timing=dict(model_cache_hit=model_hit,shared_cache_hit=shared_hit,enumeration_seconds=enumeration,load_seconds=load,inference_seconds=time.perf_counter()-t,
  candidates=len(seeds),selected=len(selected))
 return selected,data,timing
