"""Check the new identity by independent Gamma products and native reductions."""
from s00_prop_common import *
from s01_propagator import reduce,recognize
from s03_prop_cases import case
import copy,mpmath as mp,sympy as sp,random

def gamma_check(c,r,limit=None):
    t=recognize(c);assert t is not None
    P=c['definition']['physical_propagators'];master=[int(i<P) for i in range(len(c['definition']['propagators']))]
    def value(a,d):
        shift={k:mp.mpf(0) for k in t['order']};answer=mp.mpf(1)
        for k in reversed(t['order']):
            u=a[t['one'][k]]+shift[k];v=a[t['edge'][k]] if t['parent'][k] is not None else a[t['last']]
            answer*=mp.gamma(u+v-d/2)*mp.gamma(d/2-u)*mp.gamma(d/2-v)/(mp.gamma(u)*mp.gamma(v)*mp.gamma(d-u-v))
            if t['parent'][k] is not None:shift[t['parent'][k]]+=u+v-d/2
        return answer
    count=0;largest=mp.mpf(0);dd,ss=sp.symbols('d s')
    targets=c['targets'] if limit is None else c['targets'][:limit]
    with mp.workdps(80):
        for an in targets:
            co=next(iter(r['coefficients'][tree.label(an)].values()));f=sp.lambdify((dd,ss),sp.sympify(co),modules='mpmath',cse=False)
            for num,den in [(137,101),(151,103),(163,107)]:
                d=mp.mpf(num)/den;s=mp.mpf(11)/7 if t['scale']=='s' else mp.mpf(t['scale'])
                ref=value(an,d)/value(master,d)*s**(-(sum(an)-P));got=f(d,s)
                error=abs(got-ref)/max(mp.mpf(1),abs(ref));largest=max(largest,error)
                assert error<mp.mpf('1e-60'),(c['id'],an,str(error));count+=1
    return dict(passed=True,checks=count,max_relative_error=str(largest),precision_digits=80,tolerance='1e-60')

def main():
    rows=[];start=time.perf_counter()
    for L in [1,2,3,6,13]:
        for shape in ['star','chain','branched']:
            c=case(L,shape,5001);r=reduce(c);g=gamma_check(c,r)
            rows.append(dict(case=c['id'],gamma=g))
            if L>1:
                t=recognize(c);internal=set(t['parent'].values())-{None}
                test=copy.deepcopy(c);test['targets']=[]
                for k in sorted(internal):
                    for power in [0,-1]:
                        a=c['targets'][0].copy();a[t['one'][k]]=power;test['targets'].append(a)
                rows.append(dict(case=c['id']+'_internal_numerators',gamma=gamma_check(test,reduce(test))))
    native=[];old=load('prop_previous_loop',TREE/'s02_runtime.py').prior();h=old.legacy().h
    for L,shape in [(1,'star'),(2,'star'),(3,'chain')]:
        c=case(L,shape,5003,7,False);c['targets']=c['targets'][:3];c['size']=3
        with h.rt.environment():
            os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
            r=h.rt.compact(h.rt.native.run(c,c['size'],'native',HERE/'unused',timeout=30,margin=0,archive=False,records=False,basis=None,check_masters=False,scratch_cap=32*1024**2,bounds=h.inputs.bounds(c,'expanded'),ordering=2,threads=1))
        checks=0
        if r.get('success'):
            request=copy.deepcopy(c);ms=r['masters'];request['targets']=ms;mr=reduce(request)
            if mr is None:write(HERE/'development_master_domain.json',dict(case=c,masters=ms,result=r))
            assert mr is not None,ms
            expected=reduce(c)['coefficients']
            for target,row in r['coefficients'].items():
                combined=sum(sp.sympify(v)*sp.sympify(next(iter(mr['coefficients'][k].values()))) for k,v in row.items())
                reference=sp.sympify(next(iter(expected[target].values())))
                assert sp.cancel(combined-reference)==0;checks+=1
        native.append(dict(case=c['id'],status=r.get('status'),success=r.get('success'),checks=checks,result=r))
    base=case(3,'chain',5007);rejects=[]
    for name in ['mass','cut','symbolic_index','numerator','zero_line','zero_scale','cycle']:
        c=copy.deepcopy(base)
        if name=='mass':c['definition']['propagators'][0]['mass_squared']='1'
        elif name=='cut':c['definition']['cut_propagators']=[1]
        elif name=='symbolic_index':c['definition']['symbolic_ibp']=[1]
        elif name=='numerator':c['targets'][0][-1]=-1
        elif name=='zero_line':c['targets'][0][1]=0
        elif name=='zero_scale':c['definition']['scalarproduct_rules'][0][1]='0'
        else:c['definition']['propagators'][5]['momentum']='k2-k1'
        assert reduce(c) is None;rejects.append(name)
    write(HERE/'development.json',dict(complete=True,seconds=time.perf_counter()-start,gamma=rows,native=native,rejections=rejects))
    print(json.dumps(dict(complete=True,gamma_checks=sum(x['gamma']['checks'] for x in rows),native_checks=sum(x['checks'] for x in native),native_status=[x['status'] for x in native],rejections=len(rejects))))
if __name__=='__main__':main()
