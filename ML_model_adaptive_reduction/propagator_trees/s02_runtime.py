"""Use the exact two-point rule before the retained analytic and learned policy."""
from s00_prop_common import *
from s01_propagator import reduce

def run(c,method='integrated'):
    start=time.perf_counter()
    r=reduce(c) if method!='previous' else None
    if r is not None:
        return dict(success=True,status='completed',application='propagator_tree',blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=r)],model_used=False,total_seconds=time.perf_counter()-start)
    if method=='all_fixed':
        sys.path.insert(0,str(TREE));old=load('prop_fixed_runtime',TREE/'s02_runtime.py')
        r=old.run(c,'all_fixed')
    else:r=previous().run(c)
    r['total_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
    import argparse,traceback
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
    try:r=run(read(a.case),a.method)
    except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
    write(a.output,r)
