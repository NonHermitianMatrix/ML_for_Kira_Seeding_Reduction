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
