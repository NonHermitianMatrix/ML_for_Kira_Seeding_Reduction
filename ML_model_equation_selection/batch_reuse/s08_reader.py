"""Fast exact integer-polynomial reader with the previous rational reader as fallback."""
import ast,math
from fractions import Fraction as F
from s00_common import old
from s10_polynomial import parse as general_parse
class GeneralCoefficient(Exception):pass
def trim(p):
 while p and p[-1]==0:p.pop()
 return p
def add(a,b):
 out=list(a)+[0]*max(0,len(b)-len(a))
 for i,v in enumerate(b):out[i]+=v
 return trim(out)
def mul(a,b):
 if not a or not b:return []
 assert len(a)+len(b)<=258
 out=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  if x:
   for j,y in enumerate(b):
    if y:out[i+j]+=x*y
 return trim(out)
def norm(p,d):
 assert d
 if not p:return [],1
 if d<0:p=[-x for x in p];d=-d
 if d!=1:
  g=math.gcd(d,math.gcd(*p))
  if g>1:p=[x//g for x in p];d//=g
 return p,d
def parse(text,symbol):
 assert len(text)<=100000
 root=ast.parse(text.replace("^","**"),mode="eval")
 assert sum(1 for _ in ast.walk(root))<=10000
 def visit(n):
  if isinstance(n,ast.Constant):
   assert type(n.value)==int;return trim([n.value]),1
  if isinstance(n,ast.Name):
   assert n.id==symbol;return [0,1],1
  if isinstance(n,ast.UnaryOp):
   p,d=visit(n.operand)
   if isinstance(n.op,ast.USub):return [-x for x in p],d
   assert isinstance(n.op,ast.UAdd);return p,d
  assert isinstance(n,ast.BinOp)
  a,da=visit(n.left);b,db=visit(n.right)
  if isinstance(n.op,(ast.Add,ast.Sub)):
   if isinstance(n.op,ast.Sub):b=[-x for x in b]
   if da==db:return norm(add(a,b),da)
   return norm(add([x*db for x in a],[x*da for x in b]),da*db)
  if isinstance(n.op,ast.Mult):return norm(mul(a,b),da*db)
  if isinstance(n.op,ast.Div):
   if len(b)>1:raise GeneralCoefficient()
   assert b
   return norm([x*db for x in a],da*b[0])
  assert isinstance(n.op,ast.Pow) and len(b)<=1 and db==1
  n=b[0] if b else 0
  assert -32<=n<=32
  if n<0:raise GeneralCoefficient()
  out=[1];base=a;k=n
  while k:
   if k&1:out=mul(out,base)
   k//=2
   if k:base=mul(base,base)
  return norm(out,da**n)
 try:p,d=visit(root.body)
 except GeneralCoefficient:return general_parse(text,symbol)
 return [F(x,d) for x in p]
