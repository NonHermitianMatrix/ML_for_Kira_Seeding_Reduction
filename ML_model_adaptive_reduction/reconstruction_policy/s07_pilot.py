"""Compare symbolic and reconstructed coefficients on development requests."""
from s00_reconstruction_common import *
from s06_measure import measured

def main():
 assert os.environ.get('JOB_ID') and read(HERE/'build.json')['complete']
 old=previous();maker=load('reconstruction_development_cases',PREVIOUS/'s03_cases.py')
 cases=maker.cases('development')
 h=helper()
 for c in cases:
  ref=read(PREVIOUS/'references'/(c['id']+'.json.gz'));assert ref['success']
  for method in ['previous','symbolic','firefly','back']:
   p=HERE/'development'/(c['id']+'_'+method+'.json.gz')
   if p.exists():continue
   r,seconds=measured(c,method,0,50)
   ok,n=h.compare(r,ref) if r.get('success') else (False,0)
   r.update(case=c['id'],application_seconds=seconds,verified=ok,coefficient_checks=n,method=method)
   write(p,r)
   print(c['id'],method,round(seconds,4),ok,r.get('status'),flush=True)
 write(HERE/'pilot_complete.json',dict(complete=True))
if __name__=='__main__':main()
