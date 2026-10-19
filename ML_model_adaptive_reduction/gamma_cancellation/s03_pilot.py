"""Compare equivalent analytic reductions on development targets only."""
from s00_gamma_common import *
from s01_gamma_cancellation import reduce
import random,statistics

def case(L,shape,profile,count,max_power):
    c=load('tree_cases_for_cancellation',BASE/'s03_cases.py').tree_case(L,shape,profile,True)
    P=c['definition']['physical_propagators'];N=len(c['definition']['propagators'])
    rng=random.Random(profile*1000+L)
    targets={tuple(x) for x in c['targets']}
    limit=min(count,max_power**(P-1)*(max_power+2))
    while len(targets)<limit:
        a=[rng.randint(1,max_power) for _ in range(P)]+[0]*(N-P)
        a[1]=rng.randint(-1,max_power);targets.add(tuple(a))
    c['targets']=[list(a) for a in sorted(targets)];c['size']=len(targets)
    c['id']+=f'_n{len(targets)}_p{max_power}'
    return c

def main():
    rows=[]
    for L,shape,count,power in [(1,'star',20,3),(3,'chain',64,3),(7,'chain',128,3),(13,'chain',256,4),(13,'star',256,4),(13,'branched',256,4)]:
        c=case(L,shape,4001,count,power);times={'previous':[],'integrated':[]};outputs={}
        for rep in range(5):
            for name,fn in ([('previous',tree.reduce),('integrated',reduce)] if rep%2 else [('integrated',reduce),('previous',tree.reduce)]):
                begin=time.perf_counter();outputs[name]=fn(c);times[name].append(time.perf_counter()-begin)
        assert outputs['previous']['coefficients']==outputs['integrated']['coefficients'],c['id']
        r=dict(case=c['id'],loops=L,targets=c['size'],seconds={k:statistics.median(v) for k,v in times.items()},times=times,exact_equal=True)
        rows.append(r);print(json.dumps(r),flush=True)
    write(HERE/'development.json',dict(complete=True,rows=rows))
if __name__=='__main__':main()
