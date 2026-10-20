"""Reduce a bounded request list with the new formula and native policy."""
from s00_triangle_common import *
import argparse,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--output',required=True);p.add_argument('--action',default='integrated');a=p.parse_args()
 source=Path(a.cases);assert source.stat().st_size<2*1024**2;cases=read(source);assert 1<=len(cases)<=128 and len({c['id'] for c in cases})==len(cases)
 from s32_deploy import run
 size=0
 with Path(a.output).open('x') as out:
  for c in cases:
   start=time.perf_counter()
   try:r=run(c,a.action)
   except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
   raw=json.dumps(dict(case=c['id'],result=r,seconds=time.perf_counter()-start),separators=(',',':'))+'\n';size+=len(raw.encode());assert len(raw.encode())<2*1024**2 and size<8*1024**2;out.write(raw);out.flush()
if __name__=='__main__':main()
