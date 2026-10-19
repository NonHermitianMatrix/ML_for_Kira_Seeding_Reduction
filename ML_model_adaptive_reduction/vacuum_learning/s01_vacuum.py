"""Exact connected massless bubble trees with a single massive vacuum root."""
from s00_vac_common import tree,TriangleReducer
from fractions import Fraction

def recognize(c):
 d=c['definition'];lm=d['loop_momenta'];ps=d['propagators'];L=len(lm);P=d['physical_propagators']
 if not 1<=L<=13 or d['external_momenta'] or P!=2*L-1 or len(ps)!=L*(L+1)//2:return None
 if d.get('cut_propagators') or d.get('symbolic_ibp') or not c['targets']:return None
 if any(len(a)!=len(ps) or any(type(v)!=int or abs(v)>16 for v in a) or any(a[P:]) for a in c['targets']):return None
 try:
  one={};edges={};root=None;mass=None
  for i,p in enumerate(ps[:P]):
   v=tree.vector(p['momentum'],lm);m=p['mass_squared']
   if len(v)==1:
    k,a=next(iter(v.items()))
    if abs(a)!=1 or k in one:return None
    one[k]=i
    if m!='0':
     if root is not None:return None
     root=k;mass=m
   elif len(v)==2:
    if sorted(v.values())!=[-1,1] or m!='0':return None
    edge=tuple(sorted(v))
    if edge in edges:return None
    edges[edge]=i
   else:return None
  if root is None or set(one)!=set(lm) or len(edges)!=L-1:return None
  if mass=='m2':scale='-m2'
  else:
   mass=Fraction(mass)
   if mass<=0:return None
   scale=str(-mass)
  parent={root:None};order=[root];edge_index={}
  for k in order:
   for edge,i in edges.items():
    if k not in edge:continue
    child=edge[1] if edge[0]==k else edge[0]
    if child==parent[k]:continue
    if child in parent:return None
    parent[child]=k;edge_index[child]=i;order.append(child)
  if len(order)!=L:return None
  internal=set(parent.values())-{None}
  positive=[one[root]]+list(edge_index.values())+[one[k] for k in order if k not in internal]
  if any(any(a[i]<1 for i in positive) for a in c['targets']):return None
  return dict(order=order,parent=parent,one=one,edge=edge_index,scale=scale)
 except (ValueError,KeyError,SyntaxError,ZeroDivisionError):return None

class Reducer(TriangleReducer):
 def arguments(self,a):
  sums=[0]*len(self.t['order']);num=[];den=[]
  for i,p,ai,vi,size in self.entries:
   u=a[ai]+sums[i];v=a[vi];sums[p]+=u+v
   num.extend([(u+v,-size),(-u,size),(-v,1)])
   den.extend([(u,1-size),(v,0),(-u-v,1+size)])
  L=len(sums);S=sums[0];c=a[self.t['one'][self.t['order'][0]]]
  num.extend([(-S,L),(S+c,-L)]);den.extend([(0,1),(c,0)])
  return num,den

def reduce(c):
 t=recognize(c)
 if t is None:return None
 P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
 r=Reducer(master,t);label=tree.label(master)
 try:rows={tree.label(a):{label:r.coefficient(a)} for a in c['targets']}
 except ValueError:return None
 return dict(success=True,status='completed',route='exact_single_mass_vacuum_tree',coefficients=rows,masters=[master],model_used=False,attempts=[],connected_loops=len(t['order']))
