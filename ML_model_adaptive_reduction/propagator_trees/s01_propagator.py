"""Integrate connected massless two-point bubble trees exactly."""
from s00_prop_common import tree,TriangleReducer
from fractions import Fraction

def recognize(c):
    d=c['definition'];lm=d['loop_momenta'];em=d['external_momenta'];ps=d['propagators'];L=len(lm);P=d['physical_propagators']
    if not 1<=L<=13 or len(em)!=1 or P!=2*L or len(ps)!=L*(L+1)//2+L:return None
    if d.get('cut_propagators') or d.get('symbolic_ibp') or any(p['mass_squared']!='0' for p in ps):return None
    if not c['targets'] or any(len(a)!=len(ps) or any(type(v)!=int or abs(v)>16 for v in a) or any(a[P:]) for a in c['targets']):return None
    try:
        rules={tuple(sorted(k)):v for k,v in d['scalarproduct_rules']};scale=rules[(em[0],em[0])]
        try:scale=str(Fraction(scale));assert scale!='0'
        except ValueError:
            if scale!='s':return None
        one={};edges={};root=None;last=None
        for i,p in enumerate(ps[:P]):
            v=tree.vector(p['momentum'],lm+em)
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
            elif len(loops)==1 and last is None:
                k,a=next(iter(loops.items()))
                if abs(a)!=1 or ext!={em[0]:-a}:return None
                root=k;last=i
            else:return None
        if set(one)!=set(lm) or root is None or len(edges)!=L-1:return None
        parent={root:None};edge_index={};order=[root]
        for k in order:
            for edge,i in edges.items():
                if k not in edge:continue
                child=edge[1] if edge[0]==k else edge[0]
                if child==parent[k]:continue
                if child in parent:return None
                parent[child]=k;edge_index[child]=i;order.append(child)
        if len(order)!=L:return None
        internal=set(parent.values())-{None}
        positive=[last]+list(edge_index.values())+[one[k] for k in order if k not in internal]
        if any(any(a[i]<1 for i in positive) for a in c['targets']):return None
        return dict(order=order,parent=parent,one=one,edge=edge_index,last=last,scale=scale)
    except (ValueError,KeyError,AssertionError,SyntaxError):return None

class Reducer(TriangleReducer):
    def arguments(self,a):
        sums=[0]*len(self.t['order']);num=[];den=[]
        for i,p,ai,vi,size in self.entries:
            u=a[ai]+sums[i];v=a[vi];sums[p]+=u+v
            num.extend([(u+v,-size),(-u,size),(-v,1)])
            den.extend([(u,1-size),(v,0),(-u-v,1+size)])
        L=len(sums);u=a[self.t['one'][self.t['order'][0]]]+sums[0];v=a[self.t['last']]
        num.extend([(u+v,-L),(-u,L),(-v,1)])
        den.extend([(u,1-L),(v,0),(-u-v,L+1)])
        return num,den

def reduce(c):
    t=recognize(c)
    if t is None:return None
    P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
    reducer=Reducer(master,t);mlabel=tree.label(master)
    try:rows={tree.label(a):{mlabel:reducer.coefficient(a)} for a in c['targets']}
    except ValueError:return None
    return dict(success=True,status='completed',route='exact_propagator_tree',coefficients=rows,masters=[master],model_used=False,attempts=[],connected_loops=len(t['order']))
