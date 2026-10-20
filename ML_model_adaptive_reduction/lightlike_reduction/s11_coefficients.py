"""Read rational functions of d without evaluating arbitrary expressions."""
from s00_light_common import K,D
import ast

def coefficient(text):
 if len(str(text))>200000:raise ValueError('coefficient length limit')
 tree=ast.parse(str(text).replace('^','**'),mode='eval')
 def integer(n):
  if isinstance(n,ast.Constant) and type(n.value)==int:return n.value
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -integer(n.operand)
  raise ValueError('integer exponent required')
 def visit(n):
  if isinstance(n,ast.Constant) and type(n.value)==int:return K(n.value)
  if isinstance(n,ast.Name) and n.id=='d':return D
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -visit(n.operand)
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.UAdd):return visit(n.operand)
  if isinstance(n,ast.BinOp):
   a=visit(n.left)
   if isinstance(n.op,ast.Pow):
    k=integer(n.right)
    if abs(k)>128:raise ValueError('exponent limit')
    out=K.one
    for _ in range(abs(k)):out*=a
    return out if k>=0 else K.one/out
   b=visit(n.right)
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Div):return a/b
  raise ValueError('unsupported coefficient syntax')
 return visit(tree.body)
