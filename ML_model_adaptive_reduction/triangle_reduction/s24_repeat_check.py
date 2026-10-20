"""Repeat the disputed probe setting with saved outputs and symbolic references."""
from s00_triangle_common import *
from s02_triangle_cases import native_cases
from s04_triangle_measure import measured,compare

def main():
 assert os.environ.get('JOB_ID');cases=[c for c in native_cases('training') if c['id'].rsplit('_',1)[0]=='triangle_native_training_vacuum3' and int(c['id'].rsplit('_',1)[1]) in [7,9,11,13]];out=[]
 for c in cases:
  ref,t=measured(c,'symbolic_prior',8);write(HERE/'diagnostic_repeats'/(c['id']+'_reference.json.gz'),dict(case=c,result=ref,seconds=t));assert ref.get('success')
  for rep in range(6):
   r,t=measured(c,'ff8',8);rec=dict(case=c,result=r,seconds=t,repetition=rep);dest=HERE/'diagnostic_repeats'/(c['id']+'_'+str(rep)+'.json.gz');write(dest,rec);ok,n=compare(c,r,ref);rec.update(verified=ok,checks=n);write(dest,rec);out.append(dict(case=c['id'],repetition=rep,verified=ok,checks=n));print(c['id'],rep,ok,flush=True)
 write(HERE/'repeat_diagnostic_summary.json',dict(complete=True,checks=out,all_verified=all(v['verified'] for v in out)))
if __name__=='__main__':main()
