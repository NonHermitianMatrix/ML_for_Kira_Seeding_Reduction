"""Frozen inputs, bounded exact rational arithmetic, and seed-filtered systems."""
import ast,collections,functools,gzip,hashlib,json,lzma,math,os,re
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;MODEL=HERE.parent;ROOT=MODEL.parent;DATA=ROOT/"integrals"
WORK=ROOT/".tools/kira-seed-sufficiency"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+".part")
 tmp.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8");os.replace(str(tmp),str(p))
def rows(p):
 p=Path(p);op=lzma.open if p.suffix==".xz" else gzip.open
 with op(str(p),"rt",encoding="utf-8") as f:
  for line in f:
   if line.strip():yield json.loads(line)
def family_file(fid,name):
 p=DATA/"master_to_target/families"/fid/name
 if not p.exists() and p.suffix==".gz":p=p.with_suffix(".xz")
 return p
def index_key(a):
 a=tuple(a);r=sum(max(0,v) for v in a);s=sum(max(0,-v) for v in a)
 return sum(1<<i for i,v in enumerate(a) if v>0),r-sum(v>0 for v in a),s,r,a
def load_family(meta,prediction_entry,limit=None):
 fid=meta["family"];archive=MODEL/"model_test"/prediction_entry["path"]
 assert sha(archive)==prediction_entry["sha256"]
 with np.load(str(archive),allow_pickle=False) as z:
  assert str(z["model_sha256"])==EXPECTED_MODEL
  assert str(z["split_sha256"])==EXPECTED_SPLIT
  probabilities=z["probabilities"];seeds=[tuple(map(int,s)) for s in z["seeds"]]
  ids=[str(x) for x in z["target_ids"]]
 assert seeds==[tuple(s) for s in read(DATA/meta["seeds"])["indices"]]
 inputs=list(rows(DATA/meta["inputs"]))
 assert [t["id"] for t in inputs]==ids and len(inputs)==meta["counts"]["targets"]
 assert probabilities.shape==(len(inputs),len(seeds)) and np.isfinite(probabilities).all()
 assert ((probabilities>=0)&(probabilities<=1)).all()
 identities=list(rows(family_file(fid,"identities.jsonl.gz")))
 masters=[tuple(m["indices"]) for m in read(DATA/meta["masters"])["masters"]]
 assert len(masters)==len(set(masters))
 candidates={s:i for i,s in enumerate(seeds)}
 for e in identities:
  kind=e["source"]["kind"]
  assert kind in ("ibp","partial_fraction","symmetry"),(fid,kind)
  if kind=="ibp":assert tuple(e["source"]["seed"]) in candidates,(fid,e["id"])
  for t in e["terms"]:validate_expression(t["coefficient"])
 for target in inputs:
  for t in target["terms"]:validate_expression(t["coefficient"])
 if limit is not None:
  # Public target order only; pilot covers both individual and expression inputs.
  chosen=list(range(min(limit,len(inputs))))
  if any(t["kind"]=="integral_expression" for t in inputs) and not any(inputs[i]["kind"]=="integral_expression" for i in chosen):
   chosen[-1]=next(i for i,t in enumerate(inputs) if t["kind"]=="integral_expression")
  inputs=[inputs[i] for i in chosen];probabilities=probabilities[chosen]
 return dict(id=fid,meta=meta,targets=inputs,seeds=seeds,probabilities=probabilities,
             masters=masters,identities=identities,prediction_sha256=prediction_entry["sha256"])
EXPECTED_MODEL="b8fb9cc088bd4e0cbbe1168d1e5fbd733ebea361fd41d3de48827672732ed977"
EXPECTED_SPLIT="317c5167fb69424ee39b34c80290e9ed20b0ac6f208eb0adea5c681a494a5bff"
def literal(n):
 if isinstance(n,ast.Constant) and type(n.value)==int:return n.value
 if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
  v=literal(n.operand);return -v if isinstance(n.op,ast.USub) else v
 raise ValueError("Expected integer exponent")
@functools.lru_cache(maxsize=4096)
def validate_expression(s):
 s=str(s).replace("^","**")
 if len(s)>131072:raise ValueError("Coefficient length bound")
 tree=ast.parse(s,mode="eval").body
 def check(n):
  if isinstance(n,ast.Constant) and type(n.value)==int:return
  if isinstance(n,ast.Name) and re.fullmatch(r"[A-Za-z][A-Za-z_0-9]*",n.id):return
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):check(n.operand);return
  if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow)):
   check(n.left)
   if isinstance(n.op,ast.Pow):assert abs(literal(n.right))<=256
   else:check(n.right)
   return
  raise ValueError("Unsupported coefficient syntax")
 check(tree);return tree
# Sparse integer polynomials: a monomial is a tuple of (variable, power) pairs.
ONE={():1}
def add(a,b,sign=1):
 out=dict(a)
 for m,c in b.items():
  v=out.get(m,0)+sign*c
  if v:out[m]=v
  else:out.pop(m,None)
 return out
def mul(a,b):
 if len(a)*len(b)>2000000:raise ValueError("Exact product work bound")
 out={}
 for x,c in a.items():
  for y,d in b.items():
   k=dict(x)
   for v,e in y:k[v]=k.get(v,0)+e
   m=tuple(sorted(k.items()));z=out.get(m,0)+c*d
   if z:out[m]=z
   else:out.pop(m,None)
 if len(out)>20000:raise ValueError("Exact polynomial term bound")
 return out
def power(a,n):
 r=ONE
 while n:
  if n&1:r=mul(r,a)
  n//=2
  if n:a=mul(a,a)
 return r
def normalize(a,b):
 if not b:raise ZeroDivisionError("Zero polynomial denominator")
 if not a:return {},ONE
 # Cancel common monomial and integer content. No approximate arithmetic.
 allterms=list(a)+list(b);common=dict(allterms[0])
 for term in allterms[1:]:
  d=dict(term)
  common={v:min(e,d.get(v,0)) for v,e in common.items() if d.get(v,0)}
 common={v:e for v,e in common.items() if e}
 g=0
 for c in list(a.values())+list(b.values()):g=math.gcd(g,abs(c))
 sign=-1 if b[min(b)]<0 else 1;g*=sign
 def trim(poly):
  return {tuple((v,e-common.get(v,0)) for v,e in m if e-common.get(v,0)):c//g for m,c in poly.items()}
 return trim(a),trim(b)
@functools.lru_cache(maxsize=4096)
def rational(s):
 def ev(n):
  if isinstance(n,ast.Constant):return ({():n.value} if n.value else {}),ONE
  if isinstance(n,ast.Name):return {((n.id,1),):1},ONE
  if isinstance(n,ast.UnaryOp):
   a,b=ev(n.operand);return ({m:-c for m,c in a.items()} if isinstance(n.op,ast.USub) else a),b
  a,b=ev(n.left)
  if isinstance(n.op,ast.Pow):
   k=literal(n.right)
   if k<0:a,b=b,a;k=-k
   return normalize(power(a,k),power(b,k))
  c,d=ev(n.right)
  if isinstance(n.op,ast.Add):return normalize(add(mul(a,d),mul(c,b)),mul(b,d))
  if isinstance(n.op,ast.Sub):return normalize(add(mul(a,d),mul(c,b),-1),mul(b,d))
  if isinstance(n.op,ast.Mult):return normalize(mul(a,c),mul(b,d))
  if isinstance(n.op,ast.Div):return normalize(mul(a,d),mul(b,c))
  raise ValueError("Unsupported operator")
 return ev(validate_expression(str(s)))
def exact_equal(left,right):
 a,b=rational(str(left));c,d=rational(str(right))
 return mul(a,d)==mul(c,b)
def exact_zero(s):return not rational(str(s))[0]
def clear_caches():
 validate_expression.cache_clear();rational.cache_clear()
def selected_blocks(family):
 groups=collections.OrderedDict();n=len(family["seeds"])
 for target,p in zip(family["targets"],family["probabilities"]):
  mask=tuple(int(i) for i in np.flatnonzero(p>=0.5))
  groups.setdefault(mask,{"predicted":[],"full":[],"background":[]})["predicted"].append(target)
 for mask,policy in [(tuple(range(n)),"full"),((),"background")]:
  groups.setdefault(mask,{"predicted":[],"full":[],"background":[]})[policy].extend(family["targets"])
 output=[]
 for number,(mask,policies) in enumerate(groups.items()):
  wanted={family["seeds"][i] for i in mask}
  eqs=[e for e in family["identities"] if e["source"]["kind"]!="ibp" or tuple(e["source"]["seed"]) in wanted]
  # Keep every equation in the connected component of a requested target.
  targets={t["id"]:t for values in policies.values() for t in values}
  incidence=collections.defaultdict(list)
  for i,e in enumerate(eqs):
   for t in e["terms"]:incidence[tuple(t["indices"])].append(i)
  connected={tuple(t["indices"]) for target in targets.values() for t in target["terms"]}
  pending=list(connected);used=set()
  while pending:
   for i in incidence.get(pending.pop(),()):
    if i in used:continue
    used.add(i)
    for term in eqs[i]["terms"]:
     key=tuple(term["indices"])
     if key not in connected:connected.add(key);pending.append(key)
  kept=[e for i,e in enumerate(eqs) if i in used]
  output.append(dict(id=number,mask=list(mask),policies={k:[t["id"] for t in v] for k,v in policies.items()},
                     targets=list(targets.values()),equations=kept,available_equations=len(eqs),
                     ibp_equations=sum(e["source"]["kind"]=="ibp" for e in kept),
                     background_equations=sum(e["source"]["kind"]!="ibp" for e in kept)))
 return output
