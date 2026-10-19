"""Apply exact Gamma cancellation and retain the frozen native ML workflow."""
from s00_gamma_common import *
from s01_gamma_cancellation import reduce

def run(c,method='integrated'):
    start=time.perf_counter()
    result=reduce(c) if method=='integrated' else tree.reduce(c)
    if result is not None:
        return dict(success=True,status='completed',application='connected_bubble_tree',blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=result)],model_used=False,total_seconds=time.perf_counter()-start)
    return load('previous_connected_runtime',BASE/'s02_runtime.py').run(c)

if __name__=='__main__':
    import argparse,traceback
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
    try:r=run(read(a.case),a.method)
    except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
    write(a.output,r)
