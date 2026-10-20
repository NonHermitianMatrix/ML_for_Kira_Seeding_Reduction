"""Preserve a mismatched development case and compare independent algebra."""
from s00_triangle_common import *
from s02_triangle_cases import native_cases
from s04_triangle_measure import measured,compare

def main():
 assert os.environ.get('JOB_ID')
 c=next(c for c in native_cases('training') if c['id']=='triangle_native_training_vacuum3_7')
 records={}
 for action in ['previous','symbolic','ff1','ff8','ff16']:
  r,t=measured(c,action,9);record=dict(case=c,result=r,seconds=t);write(HERE/'diagnostic'/(action+'.json.gz'),record);records[action]=r;print(action,t,r.get('success'),flush=True)
 ref=records['symbolic'];checks=[]
 for action,r in records.items():
  ok,n=compare(c,r,ref);item=dict(action=action,verified=ok,checks=n);checks.append(item);print(item,flush=True)
 write(HERE/'diagnostic_summary.json',dict(case=c['id'],symbolic_success=ref.get('success'),checks=checks))
if __name__=='__main__':main()
