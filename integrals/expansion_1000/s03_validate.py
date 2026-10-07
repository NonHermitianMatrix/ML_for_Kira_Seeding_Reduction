"""Independent identity and reverse-record checks, including convergent radial integrals."""
import argparse,ast,collections,lzma,hashlib,json,time,os,concurrent.futures
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent;DATA=HERE.parent
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def rows(p):
 with lzma.open(p,"rt",encoding="utf-8") as f:
  for line in f:yield json.loads(line)
@lru_cache(maxsize=16384)
def parse(text):return ast.parse(text,mode="eval").body
def rational(text,point):
 def run(n):
  if isinstance(n,ast.Constant):assert type(n.value)==int;return F(n.value)
  if isinstance(n,ast.Name):return F(point[n.id])
  if isinstance(n,ast.UnaryOp):
   v=run(n.operand);return -v if isinstance(n.op,ast.USub) else v
  if isinstance(n,ast.BinOp):
   a,b=run(n.left),run(n.right)
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Div):return a/b
   if isinstance(n.op,ast.Pow):assert b.denominator==1;return a**int(b)
  raise ValueError("Unsupported coefficient")
 return run(parse(text))
@lru_cache(maxsize=65536)
def mod(text,d,m,p):
 v=rational(text,dict(d=d,m2=m));return v.numerator*pow(v.denominator,-1,p)%p
def field(terms,s):
 p=s["prime"];point=s["point"];out={}
 for term in terms:
  k=",".join(map(str,term["indices"]));v=(out.get(k,0)+mod(term["coefficient"],point["d"],point["m2"],p))%p
  if v:out[k]=v
  else:out.pop(k,None)
 return out
def addrow(row,src,f,p):
 out=dict(row)
 for k,v in src.items():
  z=(out.get(k,0)+f*v)%p
  if z:out[k]=z
  else:out.pop(k,None)
 return out
def source_poly(text):
 def plus(a,b):
  out=dict(a)
  for k,v in b.items():out[k]=out.get(k,F(0))+v
  return {k:v for k,v in out.items() if v}
 def product(a,b):
  out={}
  for (i,j),v in a.items():
   for (k,l),w in b.items():out[i+k,j+l]=out.get((i+k,j+l),F(0))+v*w
  return {k:v for k,v in out.items() if v}
 def run(n):
  if isinstance(n,ast.Constant):assert type(n.value)==int;return {(0,0):F(n.value)} if n.value else {}
  if isinstance(n,ast.Name):return {{"d":(1,0),"m2":(0,1)}[n.id]:F(1)}
  if isinstance(n,ast.UnaryOp):
   out=run(n.operand);return {k:-v for k,v in out.items()} if isinstance(n.op,ast.USub) else out
  if isinstance(n,ast.BinOp):
   a,b=run(n.left),run(n.right)
   if isinstance(n.op,ast.Add):return plus(a,b)
   if isinstance(n.op,ast.Sub):return plus(a,{k:-v for k,v in b.items()})
   if isinstance(n.op,ast.Mult):return product(a,b)
   if isinstance(n.op,ast.Div):
    assert set(b)=={(0,0)};return {k:v/b[(0,0)] for k,v in a.items()}
   if isinstance(n.op,ast.Pow):
    assert not b or set(b)=={(0,0)}
    power=b.get((0,0),F(0));assert power.denominator==1 and power>=0
    out={(0,0):F(1)}
    for _ in range(int(power)):out=product(out,a)
    return out
  raise ValueError("Invalid source polynomial")
 return run(parse(text))
def exact_source_form(e,L,rho):
 actual={tuple(t["indices"]):source_poly(t["coefficient"]) for t in e["terms"]}
 assert len(actual)==len(e["terms"])
 s=e["source"]
 if s["kind"]=="ibp":
  a=tuple(s["seed"]);b=a[L:];assert a[:L]==(1,)*L
  expected={a:{(1,0):F(L),(0,0):F(-2*(L+sum(b)))}}
  assert s["operator"]["canonical_operator_decomposition"]==[dict(k=i,v=i,multiplier=1) for i in range(L)]
  for j,bj in enumerate(b):
   if bj:
    raised=list(a);raised[L+j]+=1;expected[tuple(raised)]={(0,1):F(2*bj*rho[j])}
 else:
  assert s["kind"]=="partial_fraction" and s["ibp_seed"] is None
  a=tuple(e["leading_indices"]);i,j=s["mass_slots"];assert a[L+i]>0 and a[L+j]>0
  loweri=list(a);loweri[L+i]-=1;lowerj=list(a);lowerj[L+j]-=1
  expected={a:{(0,1):F(rho[i]-rho[j])},tuple(loweri):{(0,0):F(-1)},tuple(lowerj):{(0,0):F(1)}}
 assert actual==expected

def identity_check(e,L,rho):
 exact_source_form(e,L,rho)
 # Direct rational integrands verify mass differences and the radial Euler derivative.
 z=F(7,3);d=F(2)+F(1,L);alpha=L*d/2-L
 def integrand(a):
  v=F(1)
  for b,m in zip(a[L:],rho):v/=(z+m)**b
  return v
 got=sum(rational(t["coefficient"],dict(d=d,m2=1))*integrand(t["indices"]) for t in e["terms"])
 source=e["source"]
 if source["kind"]=="partial_fraction":assert got==0
 else:
  b=source["seed"][L:];f=integrand(source["seed"])
  expected=2*f*(alpha-z*sum(F(bj)/(z+m) for bj,m in zip(b,rho)))
  assert got==expected
def quadrature(definition,basis):
 import mpmath as mp
 mp.mp.dps=55;L=len(definition["loop_momenta"]);rho=definition["mass_ratios"]
 D=mp.mpf(1)+mp.mpf(1)/(2*L);alpha=L*(D-1);c=D-alpha
 convolution=mp.gamma(c)*mp.gamma(D-1)**L/mp.gamma(alpha)
 recursive=mp.mpf(1)
 for n in range(1,L):
  cn=n-(n-1)*D
  recursive*=mp.gamma(cn+1-D)*mp.gamma(D-cn)*mp.gamma(D-1)/(mp.gamma(cn)*mp.gamma(2*D-cn-1))
 recurrence_error=float(abs(recursive/convolution-1));assert recurrence_error<1e-45
 errors=[]
 for mass in (rho[0],rho[-1]):
  numeric=convolution/mp.gamma(D)*mp.quad(lambda t:2/(t*t+mass),[0,1,mp.inf])
  analytic=mp.mpf(mass)**(alpha-1)*mp.gamma(c)*mp.gamma(D-1)**L*mp.gamma(1-alpha)/mp.gamma(D)
  errors.append(float(abs(numeric/analytic-1)))
 assert max(errors)<1e-45,errors
 return dict(loops=L,mass_ratios=rho,maximum_relative_error=max(errors),convolution_recurrence_relative_error=recurrence_error,precision_digits=55,
  method="Convergent radial quadrature after independent massless convolution; d=2+1/L.")
def check_family(path,numeric=False):
 parse.cache_clear();mod.cache_clear()
 manifest=read(path);fid=manifest["family"];summary=manifest["summary"];L=summary["loops"]
 for name,info in manifest["files"].items():assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==info["sha256"]
 master=DATA/"master_integrals/families"/fid;target=DATA/"target_integrals/families"/fid;rel=path.parent
 definition=read(master/"definition.json");basis=read(master/"masters.json");rho=definition["mass_ratios"]
 graph=definition["graph"];assert len(graph["edges"])-len(graph["vertices"])+1==L
 reached={0}
 while True:
  old=set(reached)
  for e in graph["edges"]:
   if reached.intersection(e["vertices"]):reached.update(e["vertices"])
  if old==reached:break
 assert reached==set(graph["vertices"])
 identities={e["id"]:e for e in rows(rel/"identities.jsonl.xz")}
 for e in identities.values():identity_check(e,L,rho)
 inp=list(rows(target/"inputs.jsonl.xz"));refs=list(rows(rel/"references.jsonl.xz"))
 cons=list(rows(rel/"construction_proofs.jsonl.xz"));traces=list(rows(rel/"elimination_traces.jsonl.xz"))
 assert len(inp)==len(refs)==len(cons)==len(traces)==128
 eqcache={s["sample"]:{eid:field(e["terms"],s) for eid,e in identities.items()} for s in refs[0]["samples"]}
 count=0;stepcount=0
 for t,r,c,tr in zip(inp,refs,cons,traces):
  assert t["id"]==r["id"]==c["id"]==tr["id"]
  actualseeds={tuple(identities[s["pivot_equation"]]["source"]["seed"]) for s in tr["steps"] if identities[s["pivot_equation"]]["source"]["kind"]=="ibp"}
  assert actualseeds=={tuple(s) for s in r["sufficient_seeds"]}
  for sample in r["samples"]:
   p=sample["prime"];pt=sample["point"];row=field(c["initial_master_coefficients"],sample)
   eq=eqcache[sample["sample"]]
   for step in c["steps"]:
    f=mod(step["multiplier"],pt["d"],pt["m2"],p);row=addrow(row,eq[step["source_equation"]],f,p)
   assert row==field(t["terms"],sample)==field(c["final_terms"],sample)
   for step in tr["steps"]:
    src=eq[step["pivot_equation"]];pivot=",".join(map(str,step["pivot_indices"]))
    f=row[pivot]*pow(src[pivot],-1,p)%p
    if sample["sample"]==0:assert row==step["before"] and f==step["factor_mod_p"]
    row=addrow(row,src,-f,p)
    if sample["sample"]==0:assert row==step["after"]
   assert row==sample["master_coefficients"]==field(r["master_coefficients"],sample)
  count+=1;stepcount+=len(tr["steps"])
 return dict(family=fid,targets=count,identities=len(identities),steps=stepcount,
   quadrature=quadrature(definition,basis) if numeric else None)
def check_task(item):return check_family(*item)
def checked_tasks(tasks,workers):
 if workers==1:
  for item in tasks:yield check_task(item)
 else:
  with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
   yield from pool.map(check_task,tasks,chunksize=1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--pilot",action="store_true");ap.add_argument("--group",type=int,choices=(1,2,3));args=ap.parse_args()
 paths=sorted(p for p in (DATA/"master_to_target/families").glob("vacuum_L*/manifest.json") if 351<=int(p.parent.name.split("profile")[1])<=1350);start=time.time();result=[]
 if args.pilot:
  paths=[p for p in paths if p.parent.name in tuple("vacuum_L%02d_profile%03d"%(L,p) for L in (1,2,12) for p in (351,352))]
  assert len(paths)==6
 else:assert len(paths)==12000
 if args.group:
  assert not args.pilot
  first=1+4*(args.group-1)
  paths=[p for p in paths if first<=int(p.parent.name.split("_L")[1].split("_")[0])<first+4]
  assert len(paths)==4000
 workers=1 if args.pilot else min(12,int(os.environ.get("NSLOTS","1")))
 tasks=[(path,args.pilot or i in (0,len(paths)-1)) for i,path in enumerate(paths)]
 for i,checked in enumerate(checked_tasks(tasks,workers)):
  result.append(checked)
  if i%25==0:print("Independent checks",i+1,len(paths),flush=True)
 out=HERE/("pilot_validation.json" if args.pilot else "validation_group_%d.json"%args.group if args.group else "validation.json")
 out.write_text(json.dumps(dict(status="passed",families=result,targets=sum(r["targets"] for r in result),
   source_identities=sum(r["identities"] for r in result),three_sample_reverse_and_forward_replay=True,
   direct_rational_integrand_identity_checks=True,source_formulas_verified_exactly=True,elapsed_seconds=time.time()-start,workers=workers,validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+"\n",encoding="utf-8")
 print("Validation passed",len(result),flush=True)
if __name__=="__main__":main()
