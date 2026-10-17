"""Reserved first-request comparisons with frozen models and exact checks."""
from s00_engine import *
from s05_application import Reducer

def main():
 g=sys.argv[1];freeze=rt.read(HERE/'trained_model'/(g+'_freeze.json'))
 for n,h in freeze['source_sha256'].items():assert inputs.sha(HERE/n)==h,n
 assert inputs.sha(HERE/'trained_model'/(g+'.json'))==freeze['model_sha256']
 assert inputs.sha(HERE/'trained_model'/('fixed_'+g+'.json'))==freeze['fixed_sha256']
 protocol=rt.read(HERE/'protocols'/(g+'.json'));methods=['native','previous','fixed','learned'];count=0
 for i,c in enumerate(protocol['reserved']):
  refp,ref=reference(c);assert ref['success'],c['id']
  for rep in range(protocol['repetitions']):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    path=HERE/'model_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
    if not path.exists():
     r=Reducer(method,reuse=False).reduce(c,ref['masters'],refp)
     r.update(repetition=rep,worker=os.uname().nodename);save(path,r)
     print(json.dumps(dict(case=c['id'],method=method,seconds=r['complete_seconds'],success=r['success'],fallbacks=r.get('fallbacks'))),flush=True)
    r=rt.read(path);assert r['success'] and r['reference_checked'],path.name;count+=1
 save(HERE/'model_test'/(g+'_completion.json'),dict(complete=True,timings=count,model_sha256=freeze['model_sha256'],sources=freeze['source_sha256']))

if __name__=='__main__':main()
