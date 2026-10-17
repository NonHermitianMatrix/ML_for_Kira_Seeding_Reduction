"""Learn a target-dependent sparse seed region from complete Kira cost."""
import contextlib, gzip, hashlib, itertools, json, math, os, sys, tempfile, time
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/learned_seed_bounds'))
import s00_inputs as inputs
import s01_runtime as rt

def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 raw=gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0)
 assert len(raw)<2*1024**2
 used=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
 assert used+len(raw)+4096<20*1024**2,'Study storage cap'
 path.write_bytes(raw)

def compositions(total,n):
 if n==0:
  if total==0:yield ()
 elif n==1:yield (total,)
 else:
  for i in range(total+1):
   for tail in compositions(total-i,n-1):yield (i,)+tail

def seeds(c,basis,bounds,theta,truncation=None):
 """Generate a union of target boxes with a learned transverse radius."""
 n=len(c['definition']['propagators']);tops=c['definition']['top_level_sectors']
 r,s,d=bounds;targets=c['targets'];p=c['definition']['physical_propagators']
 if p>12 or n>20:raise ValueError('Sparse-seed generator domain exceeded')
 maxrank=max(sum(max(-a,0) for a in t) for t in targets)
 maxdots=max(sum(max(a-1,0) for a in t) for t in targets)
 topcount=max(t.bit_count() if hasattr(t,'bit_count') else bin(t).count('1') for t in tops)
 mandatory={tuple(t) for t in targets+basis};out=set();visited=0
 # Each sector keeps its corners. Other seeds obey both native bounds and
 # a learned transverse radius around the target's numerator-power box.
 for sector in range(1,1<<p):
  if not any(sector&top==sector for top in tops):continue
  pos=[i for i in range(p) if sector>>i&1];neg=[i for i in range(n) if not sector>>i&1]
  deficit=topcount-len(pos)
  ds=min(d,r-len(pos),max(0,math.floor(maxdots+theta[5])))
  rankcap=min(s,max(0,math.floor(maxrank+theta[3]-theta[4]*deficit)))
  if truncation is not None:
   same=max([sum(max(0,-v) for v in t) for t in targets if sum(1<<i for i,v in enumerate(t) if v>0)==sector]+[0])
   rankcap=min(rankcap,max(1,len(pos)-truncation+1,same))
  centers=[tuple(max(0,-t[i]) for i in neg) for t in targets]
  for dots in range(ds+1):
   for rank in range(rankcap+1):
    radius=max(0,math.floor(theta[0]+theta[1]*deficit+theta[2]*dots+(theta[6]*rank if len(theta)>6 else 0)))
    for powers in compositions(rank,len(neg)):
     visited+=1
     if visited>600000:raise ValueError('Seed enumeration bound exceeded')
     if min(sum(max(0,v-b) for v,b in zip(powers,t)) for t in centers)>radius:continue
     for extra in compositions(dots,len(pos)):
      a=[0]*n
      for i,v in zip(pos,extra):a[i]=v+1
      for i,v in zip(neg,powers):a[i]=-v
      out.add(tuple(a))
      if len(out)>150000:raise ValueError('Selected seed capacity exceeded')
 # Add admissible master and target seeds; they can lie beyond a sparse tube.
 for a in mandatory:
  sector=sum(1<<i for i,v in enumerate(a) if v>0)
  if sector and any(sector&top==sector for top in tops) and sum(max(0,v) for v in a)<=r and sum(max(0,-v) for v in a)<=s and sum(max(0,v-1) for v in a)<=d:out.add(a)
 return sorted(out),dict(enumerated=visited,selected=len(out),theta=theta)

def action(c):
 return rt.read(ROOT/'ML_model_adaptive_reduction/learned_seed_bounds/trained_model/fixed.json')['fixed_by_graph'].get(c['topology_group'],'native')

def run(c,basis,theta=None,reference=None,timeout=90,recover=True):
 begin=time.perf_counter();first=action(c);attempts=[];info=None
 with tempfile.TemporaryDirectory(prefix='seed_geometry_',dir=os.environ['TMPDIR']) as temporary:
  for j,a in enumerate(dict.fromkeys([first,'native','expanded'])):
   # The first sparse attempt gets an unfiltered retry at the same seed bounds.
   methods=[theta,None] if j==0 and theta is not None else [None]
   for parameters in methods:
    with rt.environment():
     if parameters is not None:
      tick=time.perf_counter()
      selected,info=seeds(c,basis,inputs.bounds(c,a),parameters,inputs.truncation(c,a))
      path=Path(temporary)/'seeds.txt';path.write_text(''.join('F['+','.join(map(str,v))+']\n' for v in selected))
      os.environ.update(KIRA_ML_SEEDS=str(path),KIRA_ML_SEED_AUDIT=str(Path(temporary)/'audit.json'))
      info['prediction_seconds']=time.perf_counter()-tick
     r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=timeout,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=24*1024**2,bounds=inputs.bounds(c,a),ordering=1,threads=1,truncate=inputs.truncation(c,a))
     r.update(seed_action=a,sparse=parameters is not None)
     audit=Path(temporary)/'audit.json'
     if parameters is not None and audit.exists():
      raw=json.loads(audit.read_text());r['seed_audit']={k:v for k,v in raw.items() if k!='used'}
     attempts.append(rt.compact(r))
    if r['success'] or not recover:break
   if r['success'] or not recover:break
 out=dict(case=c['id'],success=r['success'],coefficients=r.get('coefficients',{}),attempts=attempts,fallbacks=len(attempts)-1,seed_policy=info,reference_coefficients_supplied=False)
 if reference:rt.verify(out,reference)
 out['complete_seconds']=time.perf_counter()-begin
 return out
