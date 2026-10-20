"""Reduce a bounded collection while retaining loaded formulas and policies."""
from s00_reconstruction_common import *
import argparse,traceback

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--cases',required=True)
 p.add_argument('--output',required=True)
 p.add_argument('--method',default='integrated',choices=['integrated','fixed','previous','before_formulas'])
 a=p.parse_args()
 source=Path(a.cases)
 assert source.stat().st_size<2*1024**2
 cases=read(source)
 assert isinstance(cases,list) and 1<=len(cases)<=128
 assert len({c['id'] for c in cases})==len(cases)
 # Import once. Each request still computes its own reduction coefficients.
 from s15_deploy import run
 total_bytes=0
 with Path(a.output).open('x') as out:
  for c in cases:
   start=time.perf_counter()
   try:r=run(c,a.method)
   except Exception as e:
    r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-2000:])
   row=dict(case=c['id'],result=r,seconds=time.perf_counter()-start)
   raw=json.dumps(row,separators=(',',':'))+'\n'
   total_bytes+=len(raw.encode())
   assert len(raw.encode())<2*1024**2 and total_bytes<8*1024**2
   out.write(raw);out.flush()

if __name__=='__main__':main()
