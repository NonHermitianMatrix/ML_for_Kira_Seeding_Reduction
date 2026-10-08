"""Independent finite-field checks of the symbolic coefficients exported by Kira."""
import ast,functools
@functools.lru_cache(maxsize=8192)
def evaluate(expression,variables,prime):
 values=dict(variables)
 def ev(n):
  if isinstance(n,ast.Constant) and type(n.value)==int:return n.value%prime
  if isinstance(n,ast.Name):return int(values[n.id])%prime
  if isinstance(n,ast.UnaryOp):
   if isinstance(n.op,ast.USub):return -ev(n.operand)%prime
   if isinstance(n.op,ast.UAdd):return ev(n.operand)
  if isinstance(n,ast.BinOp):
   a=ev(n.left)
   if isinstance(n.op,ast.Pow):
    rhs=n.right
    sign=-1 if isinstance(rhs,ast.UnaryOp) and isinstance(rhs.op,ast.USub) else 1
    if isinstance(rhs,ast.UnaryOp):rhs=rhs.operand
    assert isinstance(rhs,ast.Constant) and type(rhs.value)==int
    return pow(a,sign*rhs.value,prime)
   b=ev(n.right)
   if isinstance(n.op,ast.Add):return (a+b)%prime
   if isinstance(n.op,ast.Sub):return (a-b)%prime
   if isinstance(n.op,ast.Mult):return a*b%prime
   if isinstance(n.op,ast.Div):return a*pow(b,-1,prime)%prime
  raise ValueError("Unsupported independent modular expression")
 return ev(ast.parse(str(expression).replace("^","**"),mode="eval").body)
def check_records(records,references):
 checked=0
 for record in records:
  if record["status"]!="exact_match":continue
  ref=references[record["target"]]
  assert len(ref["samples"])==3
  for sample in ref["samples"]:
   point=tuple(sorted(sample["point"].items()));prime=sample["prime"];actual={}
   for term in record["terms"]:
    key=",".join(str(v) for v in term["indices"])
    actual[key]=(actual.get(key,0)+evaluate(term["coefficient"],point,prime))%prime
   expected={k:int(v)%prime for k,v in sample["master_coefficients"].items() if int(v)%prime}
   actual={k:v for k,v in actual.items() if v}
   assert actual==expected,("Independent finite-field disagreement",record["target"],sample)
   checked+=1
 evaluate.cache_clear()
 return checked

def nonzero_witness(expression,samples):
 from s02_common import exact_zero
 for sample in samples:
  point=tuple(sorted(sample["point"].items()));prime=sample["prime"]
  try:value=evaluate(expression,point,prime)
  except (ZeroDivisionError,ValueError):continue
  if value:return dict(point=dict(point),prime=prime,value=value)
 if exact_zero(expression):return None
 raise ValueError("Nonzero symbolic remainder requires a regular nonzero witness")
def reduced(row,basis):
 row=dict(row)
 while row:
  lead=max(row)
  if lead not in basis:return row
  value=row[lead];source=basis[lead]
  for key,c in source.items():
   v=(row.get(key,0)-value*c)%_prime
   if v:row[key]=v
   else:row.pop(key,None)
 return row
def insert_row(row,basis):
 row=reduced(row,basis)
 if row:
  lead=max(row);inv=pow(row[lead],-1,_prime)
  basis[lead]={k:v*inv%_prime for k,v in row.items()}
def check_span_records(family,blocks,records,references):
 """An independent sparse elimination uses integral indices, not Kira weights."""
 global _prime
 masters=set(family["masters"]);byid={t["id"]:t for t in family["targets"]}
 sample_profiles={tuple((s["prime"],tuple(sorted(s["point"].items()))) for s in references[t["id"]]["samples"]) for t in family["targets"]}
 assert len(sample_profiles)==1,"Family requires multiple independent point profiles"
 profiles=next(iter(sample_profiles));assert len(profiles)==3
 checks=0
 for prime,point in profiles:
  _prime=prime
  def vector(terms):
   row={}
   for term in terms:
    a=tuple(term["indices"])
    if a in masters:continue
    v=(row.get(a,0)+evaluate(term["coefficient"],point,prime))%prime
    if v:row[a]=v
    else:row.pop(a,None)
   return row
  background={};seed_rows={}
  for e in family["identities"]:
   row=vector(e["terms"])
   if e["source"]["kind"]=="ibp":seed_rows.setdefault(tuple(e["source"]["seed"]),[]).append(row)
   else:insert_row(row,background)
  target_rows={tid:vector(t["terms"]) for tid,t in byid.items()}
  states={}
  for b in blocks:
   basis=dict(background)
   for pos in b["mask"]:
    for row in seed_rows.get(family["seeds"][pos],[]):insert_row(row,basis)
   for t in b["targets"]:states[b["id"],t["id"]]=not bool(reduced(target_rows[t["id"]],basis))
  for record in records:
   expected=record["status"]=="sufficient"
   assert states[record["block"],record["target"]]==expected,("Independent span disagreement",family["id"],record["target"],prime)
   checks+=1
 evaluate.cache_clear()
 return checks
