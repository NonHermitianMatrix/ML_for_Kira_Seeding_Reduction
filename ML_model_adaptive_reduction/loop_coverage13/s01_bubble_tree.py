"""Exact scalar reductions of connected massless bubble trees on a triangle."""
from s00_loop_common import label
from fractions import Fraction
from collections import Counter
import ast,math

def vector(text,names):
 def walk(n):
  if isinstance(n,ast.Name) and n.id in names:return {n.id:1}
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return {k:-v for k,v in walk(n.operand).items()}
  if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Sub)):
   a=walk(n.left);sgn=1 if isinstance(n.op,ast.Add) else -1
   for k,v in walk(n.right).items():a[k]=a.get(k,0)+sgn*v
   return {k:v for k,v in a.items() if v}
  raise ValueError('unsupported momentum syntax')
 return walk(ast.parse(text,mode='eval').body)

def recognize(c):
 d=c['definition'];lm=d['loop_momenta'];em=d['external_momenta'];ps=d['propagators'];L=len(lm);P=d['physical_propagators']
 if not 1<=L<=13 or len(em)!=2 or P!=2*L+1 or len(ps)!=L*(L+1)//2+2*L:return None
 if d.get('cut_propagators') or d.get('symbolic_ibp') or any(p['mass_squared']!='0' for p in ps):return None
 if not c['targets'] or any(len(a)!=len(ps) or any(type(v)!=int or abs(v)>16 for v in a) or any(a[P:]) for a in c['targets']):return None
 try:
  vs=[vector(p['momentum'],lm+em) for p in ps[:P]]
  rules={tuple(sorted(k)):v for k,v in d['scalarproduct_rules']}
  if any(Fraction(rules[(p,p)])!=0 for p in em):return None
  scale=rules[tuple(sorted(em))]
  try:scale=str(2*Fraction(scale));assert scale!='0'
  except ValueError:
   if scale not in ['s/2','(s)/2']:return None
   scale='s'
  one={};edges={};root=None;middle=None;last=None
  for i,v in enumerate(vs):
   loops={k:a for k,a in v.items() if k in lm};ext={k:a for k,a in v.items() if k in em}
   if not ext and len(loops)==1:
    k,a=next(iter(loops.items()))
    if abs(a)!=1 or k in one:return None
    one[k]=i
   elif not ext and len(loops)==2:
    if sorted(loops.values())!=[-1,1]:return None
    edge=tuple(sorted(loops))
    if edge in edges:return None
    edges[edge]=i
   elif len(loops)==1:
    k,a=next(iter(loops.items()))
    if abs(a)!=1 or root not in [None,k]:return None
    root=k
    if ext=={em[0]:-a} and middle is None:middle=i
    elif ext=={em[0]:-a,em[1]:-a} and last is None:last=i
    else:return None
   else:return None
  if set(one)!=set(lm) or root is None or middle is None or last is None or len(edges)!=L-1:return None
  parent={root:None};edge_index={};order=[root]
  for k in order:
   for edge,i in edges.items():
    if k not in edge:continue
    child=edge[1] if edge[0]==k else edge[0]
    if child==parent[k]:continue
    if child in parent:return None
    parent[child]=k;edge_index[child]=i;order.append(child)
  if len(order)!=L:return None
  if any(any(a[i]<1 for i in range(P) if i!=middle) for a in c['targets']):return None
  return dict(order=order,parent=parent,one=one,edge=edge_index,middle=middle,last=last,scale=scale)
 except (ValueError,KeyError,AssertionError,SyntaxError):return None

def add(*args):return tuple(sum(v[j] for v in args) for j in [0,1])
def neg(v):return (-v[0],-v[1])
def arguments(a,t):
 # Each pair (A,B) denotes A+B*d/2. Keep Gamma factors unexpanded.
 shifts={k:(0,0) for k in t['order']};num=[];den=[]
 for k in reversed(t['order'][1:]):
  u=add((a[t['one'][k]],0),shifts[k]);v=(a[t['edge'][k]],0)
  sigma=add(u,v,(0,-1));num += [sigma,add((0,1),neg(u)),add((0,1),neg(v))]
  den += [u,v,add((0,2),neg(u),neg(v))]
  p=t['parent'][k];shifts[p]=add(shifts[p],sigma)
 root=t['order'][0];alpha=add((a[t['one'][root]],0),shifts[root]);b=(a[t['middle']],0);c=(a[t['last']],0)
 num += [add(alpha,b,c,(0,-1)),add((0,1),neg(alpha),neg(b)),add((0,1),neg(b),neg(c))]
 den += [alpha,c,add((0,2),neg(alpha),neg(b),neg(c))]
 return num,den

def coefficient(a,master,t):
 ns,ds=arguments(a,t);nr,dr=arguments(master,t);factors=Counter();constant=Fraction(1)
 for left,right,sign in [(ns,nr,1),(ds,dr,-1)]:
  for (A,B),(C,D) in zip(left,right):
   assert B==D
   shift=A-C
   for i in range(min(shift,0),max(shift,0)):
    power=sign*(1 if shift>0 else -1);u=C+i;v=B
    if v==0:
     if u==0:raise ValueError('singular integer Gamma shift')
     constant*=Fraction(u)**power;continue
    g=math.gcd(abs(u),abs(v));g=g if v>0 else -g
    constant*=Fraction(g)**power;factors[(u//g,v//g)]+=power
 num=[str(constant.numerator)];den=[str(constant.denominator)]
 for (u,v),power in sorted(factors.items()):
  if power:(num if power>0 else den).append(f'({u}+({v})*d/2)**{abs(power)}')
 delta=sum(a)-sum(master)
 if delta:(num if delta<0 else den).append(f'({t["scale"]})**{abs(delta)}')
 return '('+'*'.join(num)+')/('+'*'.join(den)+')'

def reduce(c):
 t=recognize(c)
 if t is None:return None
 P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
 try:rows={label(a):{label(master):coefficient(a,master,t)} for a in c['targets']}
 except ValueError:return None
 return dict(success=True,status='completed',route='exact_connected_bubble_tree',coefficients=rows,masters=[master],model_used=False,attempts=[],connected_loops=len(t['order']))
