"""Bounded, nonrecursive parsing of Kira rational expressions."""
import functools,re
TOKEN=re.compile(r"\s*(\*\*|[()+*/^-]|[0-9]+|[A-Za-z][A-Za-z_0-9]*)")
OPS={"+":1,"-":1,"*":2,"/":2,"u+":3,"u-":3,"**":4}
def parse(expression):
 expression=str(expression).strip()
 if len(expression)>2097152:raise ValueError("Output coefficient exceeds 2 MiB")
 output=[];operators=[];position=0;operand=True
 while position<len(expression):
  match=TOKEN.match(expression,position)
  if match is None:raise ValueError("Unsupported coefficient token")
  token=match.group(1);position=match.end()
  if token=="^":token="**"
  if token=="(":
   if not operand:raise ValueError("Missing operator")
   operators.append(token);continue
  if token==")":
   if operand:raise ValueError("Missing operand")
   while operators and operators[-1]!="(":output.append(operators.pop())
   if not operators:raise ValueError("Unmatched parenthesis")
   operators.pop();operand=False;continue
  if token in OPS:
   if operand:
    if token not in ("+","-"):raise ValueError("Missing operand")
    operators.append("u"+token);continue
   while operators and operators[-1]!="(" and (OPS[operators[-1]]>OPS[token] or (OPS[operators[-1]]==OPS[token] and token!="**")):
    output.append(operators.pop())
   operators.append(token);operand=True;continue
  if not operand:raise ValueError("Missing operator")
  output.append(int(token) if token.isdecimal() else ("name",token));operand=False
 if operand:raise ValueError("Incomplete expression")
 while operators:
  token=operators.pop()
  if token=="(":raise ValueError("Unmatched parenthesis")
  output.append(token)
 # Track literal exponents and expression arity, without recursion.
 stack=[]
 for token in output:
  if type(token)==int:stack.append(token)
  elif isinstance(token,tuple):stack.append(None)
  elif token in ("u+","u-"):
   if not stack:raise ValueError("Unary arity")
   if stack[-1] is not None and token=="u-":stack[-1]=-stack[-1]
  else:
   if len(stack)<2:raise ValueError("Binary arity")
   b=stack.pop();stack.pop()
   if token=="**" and (b is None or abs(b)>256):raise ValueError("Nonliteral or oversized exponent")
   stack.append(None)
 if len(stack)!=1:raise ValueError("Expression arity")
 return tuple(output)
@functools.lru_cache(maxsize=512)
def small_parse(expression):return parse(expression)
def tokens(expression):return small_parse(expression) if len(expression)<4096 else parse(expression)
def validate_output(expression):tokens(expression)
def modular(expression,variables,prime):
 values=dict(variables);stack=[]
 for token in tokens(str(expression)):
  if type(token)==int:stack.append((token%prime,token))
  elif isinstance(token,tuple):stack.append((int(values[token[1]])%prime,None))
  elif token in ("u+","u-"):
   a,k=stack.pop()
   stack.append(((-a)%prime,-k if k is not None else None) if token=="u-" else (a,k))
  else:
   b,k=stack.pop();a,_=stack.pop()
   if token=="+":v=(a+b)%prime
   elif token=="-":v=(a-b)%prime
   elif token=="*":v=a*b%prime
   elif token=="/":v=a*pow(b,-1,prime)%prime
   elif token=="**":v=pow(a,k,prime)
   else:raise ValueError("Unknown operation")
   stack.append((v,None))
 return stack[0][0]
