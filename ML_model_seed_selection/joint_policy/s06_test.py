"""Reserved first-request comparisons with frozen models and exact checks."""
from s00_engine import *
from s05_application import Reducer

def main():
 g=sys.argv[1]
 if g=='nonplanar_box' and (HERE/'validation_refit_protocol.json').exists():
  refit=rt.read(HERE/'validation_refit_receipt.json');assert refit['complete'] and refit['final_model_sha256']==inputs.sha(HERE/'trained_model'/(g+'.json'))
 freeze=rt.read(HERE/'trained_model'/(g+'_freeze.json'))
 for n,h in freeze['source_sha256'].items():assert inputs.sha(HERE/n)==h,n
 assert inputs.sha(HERE/'trained_model'/(g+'.json'))==freeze['model_sha256']
 assert inputs.sha(HERE/'trained_model'/('fixed_'+g+'.json'))==freeze['fixed_sha256']
 protocol=rt.read(HERE/'protocols'/(g+'.json'));methods=['native','previous','fixed','learned'];count=0
 parts=int(os.environ.get('JOINT_TEST_PARTS','1'));part=int(os.environ.get('JOINT_TEST_PART','0'))
 assert parts in [1,2] and 0<=part<parts
 for i,c in enumerate(protocol['reserved']):
  if parts==2 and i//6!=part:continue
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
 completion=dict(complete=True,timings=count,model_sha256=freeze['model_sha256'],sources=freeze['source_sha256'])
 if parts==1:save(HERE/'model_test'/(g+'_completion.json'),completion)
 else:
  save(HERE/'model_test'/(g+'_part'+str(part)+'.json'),completion)
  paths=[HERE/'model_test'/(g+'_part'+str(j)+'.json') for j in range(parts)]
  if all(p.exists() for p in paths):
   pieces=[rt.read(p) for p in paths];assert all(p['complete'] and p['sources']==freeze['source_sha256'] and p['model_sha256']==freeze['model_sha256'] for p in pieces)
   completion['timings']=sum(p['timings'] for p in pieces);completion['parallel_parts']=parts
   save(HERE/'model_test'/(g+'_completion.json'),completion)

if __name__=='__main__':main()
