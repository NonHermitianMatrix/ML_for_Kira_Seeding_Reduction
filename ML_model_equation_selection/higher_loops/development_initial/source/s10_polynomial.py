"""Bounded exact reading of Kira's univariate rational coefficients."""
import ast
from fractions import Fraction as F
def trim(a):
 a=list(a)
 while a and a[-1]==0:a.pop()
 return a
def add(a,b):
 c=[F(0)]*max(len(a),len(b))
 for i,x in enumerate(a):c[i]+=x
 for i,x in enumerate(b):c[i]+=x
 return trim(c)
def mul(a,b):
 if not a or not b:return []
 assert len(a)+len(b)<=258,"Polynomial degree cap"
 c=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return trim(c)
def norm(a,b):
 a=trim(a);b=trim(b);assert b,"Zero denominator"
 if not a:return [],[F(1)]
 if len(b)==1:return [x/b[0] for x in a],[F(1)]
 if a==b:return [F(1)],[F(1)]
 return a,b
def ratadd(x,y):return norm(add(mul(x[0],y[1]),mul(y[0],x[1])),mul(x[1],y[1]))
def ratmul(x,y):return norm(mul(x[0],y[0]),mul(x[1],y[1]))
def ratpow(x,n):
 assert -32<=n<=32
 if n<0:x=(x[1],x[0]);n=-n
 out=([F(1)],[F(1)])
 while n:
  if n&1:out=ratmul(out,x)
  n//=2
  if n:x=ratmul(x,x)
 return out
def parse(s,symbol):
 assert len(s)<=100000,"Coefficient length cap"
 root=ast.parse(s.replace("^","**"),mode="eval")
 assert sum(1 for _ in ast.walk(root))<=10000,"Expression node cap"
 def visit(n):
  if isinstance(n,ast.Constant):
   assert type(n.value)==int
   return [F(n.value)],[F(1)]
  if isinstance(n,ast.Name):
   assert n.id==symbol
   return [F(0),F(1)],[F(1)]
  if isinstance(n,ast.UnaryOp):
   x=visit(n.operand)
   if isinstance(n.op,ast.USub):return [-v for v in x[0]],x[1]
   assert isinstance(n.op,ast.UAdd);return x
  assert isinstance(n,ast.BinOp)
  a,b=visit(n.left),visit(n.right)
  if isinstance(n.op,ast.Add):return ratadd(a,b)
  if isinstance(n.op,ast.Sub):return ratadd(a,([-v for v in b[0]],b[1]))
  if isinstance(n.op,ast.Mult):return ratmul(a,b)
  if isinstance(n.op,ast.Div):return ratmul(a,(b[1],b[0]))
  assert isinstance(n.op,ast.Pow) and len(b[0])<=1 and len(b[1])==1
  k=(b[0][0] if b[0] else F(0))/b[1][0];assert k.denominator==1
  return ratpow(a,int(k))
 a,b=norm(*visit(root.body))
 if not a:return []
 assert len(a)>=len(b),"Expected polynomial coefficient"
 result=[F(0)]*(len(a)-len(b)+1)
 while a and len(a)>=len(b):
  k=len(a)-len(b);c=a[-1]/b[-1];result[k]+=c
  for j,x in enumerate(b):a[k+j]-=c*x
  a=trim(a)
 assert not a,"Nonzero remainder; coefficient is outside the supported polynomial domain"
 return trim(result)
