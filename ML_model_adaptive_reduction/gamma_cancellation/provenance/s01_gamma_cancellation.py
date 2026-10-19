"""Cancel complete Gamma factors before expanding integer shifts."""
from s00_common import tree
from collections import Counter,defaultdict
from fractions import Fraction
import math

class Reducer:
    def __init__(self,master,t):
        self.master=master;self.t=t;self.base=tree.arguments(master,t)
        self.linear={}
    def coefficient(self,a):
        ns,ds=tree.arguments(a,self.t);nr,dr=self.base
        gamma=Counter(ns);gamma.update(dr);gamma.subtract(ds);gamma.subtract(nr)
        slopes=defaultdict(dict)
        for (A,B),w in gamma.items():
            if w:slopes[B][A]=w
        factors=Counter();cn=cd=1
        for B,ends in slopes.items():
            assert sum(ends.values())==0
            cumulative=0;points=sorted(ends)
            for i,A in enumerate(points[:-1]):
                cumulative+=ends[A];power=-cumulative
                if not power:continue
                for u in range(A,points[i+1]):
                    if B==0:
                        if u==0:raise ValueError('singular integer Gamma shift')
                        g=u
                    else:
                        entry=self.linear.get((u,B))
                        if entry is None:
                            g=math.gcd(abs(u),abs(B));g=g if B>0 else -g
                            entry=(g,(u//g,B//g));self.linear[(u,B)]=entry
                        g,key=entry;factors[key]+=power
                    if power>0:cn*=g**power
                    else:cd*=g**(-power)
        constant=Fraction(cn,cd)
        num=[str(constant.numerator)];den=[str(constant.denominator)]
        for (u,v),power in sorted(factors.items()):
            if power:(num if power>0 else den).append(f'({u}+({v})*d/2)**{abs(power)}')
        delta=sum(a)-sum(self.master)
        if delta:(num if delta<0 else den).append(f'({self.t["scale"]})**{abs(delta)}')
        return '('+'*'.join(num)+')/('+'*'.join(den)+')'

def reduce(c):
    t=tree.recognize(c)
    if t is None:return None
    P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
    reducer=Reducer(master,t)
    try:rows={tree.label(a):{tree.label(master):reducer.coefficient(a)} for a in c['targets']}
    except ValueError:return None
    return dict(success=True,status='completed',route='cancelled_connected_bubble_tree',coefficients=rows,masters=[master],model_used=False,attempts=[],connected_loops=len(t['order']))
