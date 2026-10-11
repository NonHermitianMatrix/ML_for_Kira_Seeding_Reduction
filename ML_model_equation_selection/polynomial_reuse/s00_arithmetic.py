"""Shared exact Taylor terms and integer loop-order transformations."""
import collections,gzip,hashlib,importlib.util,json,math,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRE=HERE.parent/"pre_reduction"
sys.path.insert(0,str(PRE))
import s00_contract as prior
base=prior.base
F=base.F
spec=importlib.util.spec_from_file_location("previous_direct",PRE/"s01_application.py")
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
def normalized(values,denominator):
 a=list(values)
 while a and a[-1]==0:a.pop()
 if not a:return ((),1)
 if denominator<0:a=[-x for x in a];denominator=-denominator
 g=math.gcd(denominator,*a)
 return tuple(x//g for x in a),denominator//g
def multiply(left,right,limit):
 a,da=left;b,db=right
 out=[0]*min(limit,max(0,len(a)+len(b)-1))
 for i,x in enumerate(a):
  for j,y in enumerate(b[:max(0,len(out)-i)]):out[i+j]+=x*y
 return normalized(out,da*db)
class TaylorCheck:
 """Cache only algebraic factors within one mass profile, never target answers."""
 def __init__(self,rho,targets):
  self.rho=tuple(rho);self.factors={};self.hits=0;self.builds=0;self.products=[]
  for j,mass in enumerate(rho):
   maximum=max(b[j] for b in targets);polys=[((1,),1)]
   for h in range(1,maximum):
    polys.append(multiply(polys[-1],((2*h,-1),2*h*mass),h+1))
   self.products.append(polys)
 def factor(self,delta,power,length):
  key=(delta,power,length)
  if key in self.factors:self.hits+=1;return self.factors[key]
  assert len(self.factors)<4096
  values=[(-1)**k*math.comb(power+k-1,k)*delta**(length-1-k) for k in range(length)]
  value=normalized(values,delta**(power+length-1));self.factors[key]=value;self.builds+=1
  return value
 def coefficient(self,b):
  out={}
  for j,bj in enumerate(b):
   if bj==0:continue
   series=((1,),1)
   for i,bi in enumerate(b):
    if i!=j and bi:series=multiply(series,self.factor(self.rho[i]-self.rho[j],bi,bj),bj)
   a,da=series;products=self.products[j][:bj];den=math.lcm(*(v[1] for v in products));values=[0]*bj
   for k,(poly,d) in enumerate(products,1):
    scalar=(a[bj-k] if bj-k<len(a) else 0)*(den//d)
    for n,x in enumerate(poly):values[n]+=scalar*x
   values,d=normalized(values,da*den)
   out[j]=tuple(F(x,d) for x in values)
  return out
class Transforms:
 """Bounded LRU cache of exact integer matrices, independent of target coefficients."""
 def __init__(self,capacity=128):
  assert 1<=capacity<=128;self.capacity=capacity;self.cache=collections.OrderedDict();self.hits=0;self.builds=0
 def get(self,L,degree):
  assert 0<=degree<=13
  key=L
  if key in self.cache:self.hits+=1;self.cache.move_to_end(key);return self.cache[key]
  degree=13
  powers=[L**n for n in range(degree+1)]
  matrix=tuple(tuple(math.comb(n,k)*powers[n]*(-2)**(n-k) for n in range(k,degree+1)) for k in range(degree+1))
  if len(self.cache)>=self.capacity:self.cache.popitem(last=False)
  self.cache[key]=matrix;self.builds+=1;return matrix
def expand(rows,loops,transforms):
 converted=[{j:prior.from_fraction(p) for j,p in row.items()} for row in rows]
 out={}
 for L in loops:
  encoded=[]
  for row in converted:
   target={}
   for j,(a,d) in row.items():
    if not a:target[str(j)]=[];continue
    matrix=transforms.get(L,len(a)-1);values=[]
    for k,weights in enumerate(matrix[:len(a)]):
     value=sum(x*y for x,y in zip(a[k:],weights));g=math.gcd(value,d)
     values.append([value//g,d//g])
    while values and values[-1][0]==0:values.pop()
    target[str(j)]=values
   encoded.append(target)
  out[str(L)]=encoded
 return out
def allocated(path):return sum(p.stat().st_blocks*512 for p in path.rglob("*") if p.is_file())
def guard():
 plan=json.loads((HERE/"resource_plan.json").read_text())
 assert allocated(HERE)<plan["new_retained_cap_bytes"]
 assert plan["combined_upper_bytes"]<10000000000
def object_store(value):
 raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode();h=hashlib.sha256(raw).hexdigest()
 p=HERE/"objects"/(h+".json.gz");p.parent.mkdir(exist_ok=True)
 if not p.exists():p.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
 return h
def save(path,result):
 value=dict(result);coeff={k:value.pop(k) for k in ["symbolic_coefficients","coefficients"]}
 evidence={k:value.pop(k) for k in ["source_choices","raw_export"] if k in value}
 if "algebra" in value:
  value["algebra"]=dict(value["algebra"]);evidence["log"]=value["algebra"].pop("log",None)
 value["coefficients_sha256"]=object_store(coeff);value["evidence_sha256"]=object_store(evidence)
 base.write(path,value);guard()
 return value
