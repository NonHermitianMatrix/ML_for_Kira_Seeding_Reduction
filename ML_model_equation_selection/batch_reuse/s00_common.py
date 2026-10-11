"""Batch equation choices for the restricted, exact vacuum coefficient system."""
import hashlib,itertools,json,math,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=HERE.parent/"higher_loops"
sys.path.insert(0,str(OLD))
import s00_math as old
from s00_math import F,canonical,compositions,children,pairs,write,validate
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def options(r):return list(itertools.permutations(range(r))) if r>2 else [(0,1)]
def dependency(targets,permutation):
 rows={};pending=list(map(tuple,targets))
 while pending:
  b=pending.pop()
  if sum(b)==1 or b in rows:continue
  p=tuple(j for j in permutation if b[j])[:2];rows[b]=p
  pending.extend(children(b,p))
 return rows
def cost(rows):
 # Upper count of rational coefficient additions/scalings during substitution.
 return sum(3*sum(b)-2 for b in rows)
def feature(targets,p):
 n=len(targets);r=len(p);out=[n,r,max(map(sum,targets)),sum(map(sum,targets))/n]
 for j in list(p)+[None]*(4-r):
  v=[b[j] for b in targets] if j is not None else [0]*n
  out.extend([sum(v)/n,sum(x*x for x in v)/n,max(v),sum(x>0 for x in v)/n])
 for i,j in itertools.combinations(range(4),2):
  out.extend([sum(min(b[p[i]],b[p[j]]) for b in targets)/n if j<r else 0,
              sum(b[p[i]]*b[p[j]] for b in targets)/n if j<r else 0])
 return out
def predict(model,x):
 value=0
 for nodes in model["trees"]:
  i=0
  while nodes[i][0]>=0:
   f,t,l,r,_=nodes[i];i=l if x[f]<=t else r
  value+=nodes[i][4]
 return value/len(model["trees"])
def select(targets,mode,model=None):
 r=len(targets[0]);choices=options(r)
 if r==2:return choices[0],[]
 if mode=="model":
  base=feature(targets,tuple(range(r)));pairlist=list(itertools.combinations(range(4),2))
  def remap(p):
   x=base[:4]
   for j in list(p)+list(range(r,4)):x.extend(base[4+4*j:8+4*j])
   for i,j in pairlist:
    if j>=r:x.extend([0,0]);continue
    k=pairlist.index(tuple(sorted((p[i],p[j]))));x.extend(base[20+2*k:22+2*k])
   return x
  scores=[predict(model,remap(p)) for p in choices]
  return choices[min(range(len(scores)),key=lambda i:(scores[i],choices[i]))],scores
 if mode=="sum_ascending":return tuple(sorted(range(r),key=lambda j:(sum(b[j] for b in targets),j))),[]
 if mode=="sum_descending":return tuple(sorted(range(r),key=lambda j:(-sum(b[j] for b in targets),j))),[]
 if mode=="first":return tuple(range(r)),[]
 if mode=="exhaustive":
  scores=[cost(dependency(targets,p)) for p in choices]
  return choices[min(range(len(scores)),key=lambda i:(scores[i],choices[i]))],scores
 raise ValueError(mode)
def make_case(stage,k,r,B,n):
 rng=random.Random({"training":72001,"validation":82001,"test":92001}[stage]+k*1009+r*71+B)
 pool=[b for s in range(max(2,B-4),B+1) for b in compositions(s,r)]
 rng.shuffle(pool)
 # Include both dispersed targets and targets with one frequently raised denominator.
 if k%2:
  j=rng.randrange(r);pool.sort(key=lambda b:-(b[j]+rng.random()*2))
 targets=pool[:min(n,len(pool))]
 rho=rng.sample(range({"training":3,"validation":101,"test":211}[stage],{"training":83,"validation":197,"test":397}[stage]),r)
 return dict(id=stage+"_"+str(k)+"_r"+str(r)+"_b"+str(B),family="coupled_vacuum_unit_massless",mass_ratios=rho,targets=targets,loops=list(range(1,13)),mass_scale_squared=1)
def symbolic_oracle(rho,b):
 # Taylor partial fractions followed by Euler recurrence directly in Q[z].
 out={}
 for j,bj in enumerate(b):
  if not bj:continue
  series=[F(1)]+[F(0)]*(bj-1)
  for i,bi in enumerate(b):
   if i==j or not bi:continue
   delta=rho[i]-rho[j]
   t=[F((-1)**k*math.comb(bi+k-1,k),delta**(bi+k)) for k in range(bj)]
   series=[sum(series[h]*t[k-h] for h in range(k+1)) for k in range(bj)]
  product=[F(1)];result=[F(0)]*bj
  for k in range(1,bj+1):
   for v,x in enumerate(product):result[v]+=series[bj-k]*x
   if k<bj:
    nxt=[F(0)]*(len(product)+1)
    for v,x in enumerate(product):
     nxt[v]+=x/F(rho[j]);nxt[v+1]-=x/F(2*k*rho[j])
    product=nxt
  out[j]=canonical(result)
 return out
def substitute(p,L):
 # A common integer denominator avoids Fraction normalization in the inner loop.
 if not p:return ()
 denominator=math.lcm(*(v.denominator for v in p))
 a=[v.numerator*(denominator//v.denominator) for v in p]
 out=[0]*len(a)
 for n,c in enumerate(a):
  for k in range(n+1):out[k]+=c*math.comb(n,k)*L**k*(-2*L)**(n-k)
 return canonical([F(v,denominator) for v in out])
def encode(rows):
 return [{str(j):[[v.numerator,v.denominator] for v in p] for j,p in row.items()} for row in rows]
def decode(rows):
 return [{int(j):tuple(F(*v) for v in p) for j,p in row.items()} for row in rows]

def load_model(name):
 import gzip,struct
 data=gzip.decompress((HERE/"trained_model"/name.replace(".json",".bin.gz")).read_bytes())
 pos=0
 def size():
  nonlocal pos
  n=struct.unpack_from("<I",data,pos)[0];pos+=4;return n
 nt=size();assert 1<=nt<=16;trees=[]
 fmt=struct.Struct("<hdiid")
 for k in range(nt):
  n=size();assert 0<n<8192
  trees.append([list(fmt.unpack_from(data,pos+i*fmt.size)) for i in range(n)]);pos+=n*fmt.size
 assert pos==len(data)
 return {"trees":trees}
