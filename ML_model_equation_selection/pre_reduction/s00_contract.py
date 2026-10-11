"""Exact polynomial pre-reduction of the restricted vacuum identities."""
import sys,importlib.util,math,json,hashlib,gzip,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BATCH=HERE.parent/"batch_reuse"
sys.path.insert(0,str(BATCH))
import s00_common as base
F=base.F
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pack=module("prior_pack",BATCH/"s11_pack.py")
def normalize(a,d):
 while a and a[-1]==0:a.pop()
 if not a:return ((),1)
 if d<0:a=[-v for v in a];d=-d
 g=math.gcd(d,math.gcd(*a))
 return (tuple(v//g for v in a),d//g)
def from_fraction(p):
 d=math.lcm(*(v.denominator for v in p)) if p else 1
 return normalize([v.numerator*(d//v.denominator) for v in p],d)
def fractions(p):return tuple(F(v,p[1]) for v in p[0])
def subtract(a,b,delta):
 x,da=a;y,db=b;g=math.gcd(da,db);ca=db//g;cb=da//g
 v=[(x[k]*ca if k<len(x) else 0)-(y[k]*cb if k<len(y) else 0) for k in range(max(len(x),len(y)))]
 return normalize(v,da*ca*delta)
def euler(a,k,rho):
 x,d=a;v=[0]*(len(x)+1)
 for i,c in enumerate(x):v[i]+=2*k*c;v[i+1]-=c
 return normalize(v,d*2*k*rho)
def selected(request,mode,model):
 targets=list(map(tuple,request["targets"]))
 if mode=="model":
  from s16_native import select_native
  p,scores=select_native(targets,"model",model) if "function" in model else base.select(targets,"model",model)
  rows=base.dependency(targets,p)
 else:
  rows,_=base.old.closure(targets,"extreme");p=None;scores=[]
 return rows,dict(permutation=p,predicted_log_costs=scores,equations=len(rows),weighted_cost=base.cost(rows))
def recurrence(request,rows):
 rho=request["mass_ratios"];r=len(rho)
 values={tuple(int(i==j) for i in range(r)):{j:((1,),1)} for j in range(r)}
 # Each child has total power B-1, so this is a topological exact elimination.
 for b in sorted(rows,key=lambda b:(sum(b),b)):
  pair=rows[b];children=base.children(b,pair)
  if len(pair)==1:
   j=pair[0];a=values[children[0]]
   values[b]={j:euler(a[j],b[j]-1,rho[j])}
  else:
   a,c=(values[x] for x in children);delta=rho[pair[0]]-rho[pair[1]]
   values[b]={j:subtract(a.get(j,((),1)),c.get(j,((),1)),delta) for j in set(a)|set(c)}
 return [{j:fractions(p) for j,p in values[tuple(b)].items() if p[0]} for b in request["targets"]]
def expression(p):
 a,d=from_fraction(p);terms=[]
 for k,c in enumerate(a):
  if c:terms.append("("+str(c)+")"+("*z" if k==1 else "*z^"+str(k) if k else ""))
 return "("+("+".join(terms) or "0")+")/"+str(d)
def allocated(p):return sum(x.stat().st_blocks*512 for x in p.rglob("*") if x.is_file())
def guard():
 plan=json.loads((HERE/"resource_plan.json").read_text())
 assert allocated(HERE)<plan["new_retained_cap_bytes"]
 assert plan["combined_upper_bytes"]<10000000000
def save(path,result):
 result=dict(result)
 payload={k:result.pop(k) for k in ["raw_export","source_choices","symbolic_coefficients","coefficients"] if k in result}
 if "algebra" in result:
  result["algebra"]=dict(result["algebra"]);payload["log"]=result["algebra"].pop("log",None)
 data=json.dumps(payload,sort_keys=True,separators=(",",":")).encode();h=hashlib.sha256(data).hexdigest()
 dest=HERE/"objects"/(h+".json.gz");dest.parent.mkdir(exist_ok=True)
 if not dest.exists():dest.write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
 result["payload_sha256"]=h;base.write(path,result);guard()
