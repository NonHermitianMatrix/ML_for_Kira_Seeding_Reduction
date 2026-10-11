"""Exact integer polynomials, bounded binary records and legacy compatibility."""
import sys,ctypes,struct,os,json,math,time,gzip,hashlib,random,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
POLY=HERE.parent/"polynomial_reuse"
sys.path.insert(0,str(POLY))
import s00_arithmetic as old
from s01_engine import apply as old_apply,State as OldState
prior=old.prior;base=old.base;F=old.F
POLICIES=["extreme","ascending","descending","mass_gap","first"]
def read(p):return json.loads(Path(p).read_text())
def write(p,x):base.write(Path(p),x)
def sha(p):return base.sha(Path(p))
def allocated(p):return sum(f.stat().st_blocks*512 for f in Path(p).rglob("*") if f.is_file())
def guard():
 p=read(HERE/"resource_plan.json")
 assert p["combined_upper_bytes"]<10000000000 and allocated(HERE)<p["new_retained_cap_bytes"]
def big(x):
 n=(abs(x).bit_length()+7)//8
 assert n<=1048576
 return bytes([x<0])+struct.pack("<I",n)+abs(x).to_bytes(n,"little")
def u(x):return struct.pack("<I",x)
class Reader:
 def __init__(self,data):self.data=data;self.pos=0
 def take(self,n):
  assert 0<=n<=67108864 and self.pos+n<=len(self.data),"Invalid binary length"
  b=self.data[self.pos:self.pos+n];self.pos+=n;return b
 def u(self):return struct.unpack("<I",self.take(4))[0]
 def big(self):
  s=self.take(1)[0];assert s<2
  n=self.u();assert n<=1048576
  x=int.from_bytes(self.take(n),"little");return -x if s else x
 def done(self):assert self.pos==len(self.data),"Trailing binary bytes"
def common_packet(rows,loops):
 flat=[p for row in rows for j,p in sorted(row.items())]
 chunks=[u(len(flat))]
 for a,d in flat:chunks.extend([u(len(a)),big(d),*(big(x) for x in a)])
 chunks.extend([u(len(loops)),*(big(L) for L in loops)])
 return b"".join(chunks)
def read_common(data):
 r=Reader(data);count=r.u();assert count<=2048;polys=[]
 for _ in range(count):
  n=r.u();assert n<=14;d=r.big();assert d>0
  polys.append((tuple(r.big() for _ in range(n)),d))
 nl=r.u();assert 1<=nl<=32;loops=[r.big() for _ in range(nl)];assert all(L>0 for L in loops);r.done()
 return polys,loops
def native(data,state):
 if "native" not in state:
  lib=ctypes.CDLL(str(HERE/"build/transform.so"))
  f=lib.expand_exact;f.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_void_p),ctypes.POINTER(ctypes.c_size_t)];f.restype=ctypes.c_int
  lib.release_exact.argtypes=[ctypes.c_void_p];lib.release_exact.restype=None;state["native"]=lib
 lib=state["native"];out=ctypes.c_void_p();n=ctypes.c_size_t()
 assert lib.expand_exact(data,len(data),ctypes.byref(out),ctypes.byref(n))==0,"Native transform failed"
 try:return ctypes.string_at(out,n.value)
 finally:lib.release_exact(out)
def python_expand(rows,loops,state):
 cache=state.setdefault("transforms",old.Transforms());result={}
 for L in loops:
  out=[]
  for row in rows:
   rec={}
   for j,(a,d) in row.items():
    matrix=cache.get(L,len(a)-1);p=[]
    for k,weights in enumerate(matrix[:len(a)]):
     v=sum(x*y for x,y in zip(a[k:],weights));g=math.gcd(v,d);p.append([v//g,d//g])
    rec[str(j)]=p
   out.append(rec)
  result[str(L)]=out
 return result
def row_keys(rows):return [sorted(row) for row in rows]
def regroup(polys,keys):
 out=[];n=0
 for js in keys:
  out.append({str(j):polys[n+k] for k,j in enumerate(js)});n+=len(js)
 assert n==len(polys);return out
def decode_expanded(data,keys):
 r=Reader(data);nl=r.u();assert 1<=nl<=32;out={}
 for _ in range(nl):
  L=r.big();count=r.u();assert count<=2048;polys=[]
  for j in range(count):
   n=r.u();assert n<=14;p=[]
   for k in range(n):
    num=r.big();den=r.big();assert den>0;p.append([num,den])
   polys.append(p)
  out[str(L)]=regroup(polys,keys)
 r.done();return out
def symbolic(rows):
 return [{str(j):[[x//math.gcd(x,d),d//math.gcd(x,d)] for x in a] for j,(a,d) in row.items()} for row in rows]
def binary_payload(parts):
 header=json.dumps([dict(id=c,keys=keys) for c,keys,inp,out in parts],sort_keys=True,separators=(",",":")).encode()
 return b"KXB1"+u(len(header))+header+b"".join(u(len(inp))+inp+u(len(out))+out for c,keys,inp,out in parts)
def decode_binary(data):
 r=Reader(data);assert r.take(4)==b"KXB1";header=json.loads(r.take(r.u()));assert 0<len(header)<=8
 result=dict(symbolic_coefficients={},coefficients={})
 for h in header:
  inp=r.take(r.u());out=r.take(r.u());polys,loops=read_common(inp)
  rows=regroup([[[x//math.gcd(x,d),d//math.gcd(x,d)] for x in a] for a,d in polys],h["keys"])
  result["symbolic_coefficients"][h["id"]]=rows;result["coefficients"][h["id"]]=decode_expanded(out,h["keys"])
  assert list(map(int,result["coefficients"][h["id"]]))==loops
 r.done();return result
def object_store(raw,suffix,folder=HERE/"objects"):
 h=hashlib.sha256(raw).hexdigest();folder.mkdir(parents=True,exist_ok=True);p=folder/(h+suffix+".gz")
 if not p.exists():p.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
 return h
def save(path,result,folder=None):
 folder=folder or HERE/"objects";r=dict(result);t=time.perf_counter()
 if "_binary" in r:raw=r.pop("_binary");fmt="binary";h=object_store(raw,".bin",folder)
 else:
  coeff={k:r.pop(k) for k in ["symbolic_coefficients","coefficients"]}
  raw=json.dumps(coeff,sort_keys=True,separators=(",",":")).encode();fmt="json";h=object_store(raw,".json",folder)
 evidence={k:r.pop(k) for k in ["source_choices","raw_export"] if k in r}
 if "algebra" in r:
  r["algebra"]=dict(r["algebra"]);evidence["log"]=r["algebra"].pop("log",None)
 eh=object_store(json.dumps(evidence,sort_keys=True,separators=(",",":")).encode(),".json",folder)
 r.update(coefficients_sha256=h,coefficient_format=fmt,evidence_sha256=eh,coefficient_bytes=len(raw),saving_seconds=time.perf_counter()-t)
 write(path,r);return r
def load_coeff(r,folder=HERE/"objects"):
 suffix=".bin.gz" if r["coefficient_format"]=="binary" else ".json.gz"
 raw=gzip.decompress((folder/(r["coefficients_sha256"]+suffix)).read_bytes())
 assert hashlib.sha256(raw).hexdigest()==r["coefficients_sha256"]
 return decode_binary(raw) if r["coefficient_format"]=="binary" else json.loads(raw)
def dependencies(c,policy):
 targets=list(map(tuple,c["targets"]));rho=c["mass_ratios"];r=len(rho)
 if policy=="extreme":return base.old.closure(targets,"extreme")[0]
 if policy=="ascending":p=tuple(sorted(range(r),key=lambda j:(sum(b[j] for b in targets),j)))
 elif policy=="descending":p=tuple(sorted(range(r),key=lambda j:(-sum(b[j] for b in targets),j)))
 elif policy=="first":p=tuple(range(r))
 elif policy=="mass_gap":
  rows={};pending=list(targets)
  while pending:
   b=pending.pop()
   if sum(b)==1 or b in rows:continue
   active=[j for j in range(r) if b[j]]
   p=tuple(active) if len(active)==1 else max(((i,j) for i in active for j in active if i<j),key=lambda ij:(abs(rho[ij[0]]-rho[ij[1]]),b[ij[0]]+b[ij[1]],ij))
   rows[b]=p;pending.extend(base.children(b,p))
  return rows
 else:raise ValueError(policy)
 return base.dependency(targets,p)
def recurrence(c,rows):
 rho=c["mass_ratios"];r=len(rho)
 values={tuple(int(i==j) for i in range(r)):{j:((1,),1)} for j in range(r)}
 for b in sorted(rows,key=lambda b:(sum(b),b)):
  p=rows[b];child=base.children(b,p)
  if len(p)==1:
   j=p[0];values[b]={j:prior.euler(values[child[0]][j],b[j]-1,rho[j])}
  else:
   a,cc=(values[x] for x in child);delta=rho[p[0]]-rho[p[1]]
   values[b]={j:prior.subtract(a.get(j,((),1)),cc.get(j,((),1)),delta) for j in set(a)|set(cc)}
 return [{j:p for j,p in values[tuple(b)].items() if p[0]} for b in c["targets"]]
class TaylorInteger(old.TaylorCheck):
 def coefficient(self,b):
  out={}
  for j,bj in enumerate(b):
   if not bj:continue
   series=((1,),1)
   for i,bi in enumerate(b):
    if i!=j and bi:series=old.multiply(series,self.factor(self.rho[i]-self.rho[j],bi,bj),bj)
   a,da=series;products=self.products[j][:bj];den=math.lcm(*(v[1] for v in products));values=[0]*bj
   for k,(poly,d) in enumerate(products,1):
    scalar=(a[bj-k] if bj-k<len(a) else 0)*(den//d)
    for n,x in enumerate(poly):values[n]+=scalar*x
   values,d=old.normalized(values,da*den)
   if values:out[j]=(values,d)
  return out
def features(requests):
 # Fixed-size, cheap physical/batch features; no reference coefficients.
 values=[]
 for c in requests:
  b=c["targets"];rho=c["mass_ratios"];n=len(b);r=len(rho);sums=[sum(x) for x in b];gaps=[abs(x-y) for i,x in enumerate(rho) for y in rho[i+1:]]
  sums_by_slot=sorted([sum(x[j] for x in b)/n for j in range(r)],reverse=True)+[0]*(4-r)
  squares=sorted([sum(x[j]**2 for x in b)/n for j in range(r)],reverse=True)+[0]*(4-r)
  predecessors=[]
  for target in b:
   if sum(target)>1:
    for j,v in enumerate(target):
     if v:
      child=list(target);child[j]-=1;predecessors.append(tuple(child))
  shared=[len(set(predecessors)),1-len(set(predecessors))/max(1,len(predecessors))]
  values.append([n,r,min(sums),max(sums),sum(sums)/n,len(c["loops"]),max(c["loops"]),sum(sum(v>0 for v in x) for x in b)/n,
   math.log2(min(rho)),math.log2(max(rho)),math.log2(min(gaps)),math.log2(max(gaps)),sum(math.log2(x) for x in gaps)/len(gaps),max(gaps)/min(gaps)]+sums_by_slot+squares+shared)
 return [len(requests)]+[sum(v[k] for v in values)/len(values) for k in range(len(values[0]))]+[max(v[k] for v in values) for k in range(len(values[0]))]
def predict(requests,state):
 if "cost_model" not in state:state["cost_model"]=read(HERE/"trained_model/cost_tree.json")
 model=state["cost_model"];x=features(requests);i=0
 while model["nodes"][i][0]>=0:
  f,t,l,r,values=model["nodes"][i];i=l if x[f]<=t else r
 predictions=model["nodes"][i][4]
 return model["policies"][min(range(len(predictions)),key=lambda j:(predictions[j],j))],predictions
