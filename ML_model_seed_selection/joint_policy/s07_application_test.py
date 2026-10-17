"""Check independent scaled requests, model guards, and fresh processes."""
import copy,subprocess,statistics
from fractions import Fraction
from s00_engine import *
from s05_application import Reducer,policy
from s04_reuse import ScaleCache

def scaled(c,factor):
 c=copy.deepcopy(c);c['id']+='_scale'+str(factor).replace('/','over')
 c['definition']['scalarproduct_rules']=[[a,str(Fraction(v)*factor)] for a,v in c['definition']['scalarproduct_rules']]
 # Parameters are display metadata; remove stale values after the physical change.
 c['definition']['parameters']={}
 return c

def main():
 g=sys.argv[1];assert rt.read(HERE/'model_test'/(g+'_completion.json'))['complete']
 proto=rt.read(HERE/'protocols'/(g+'.json'))
 chosen=[c for c in proto['reserved'] if c['id'].split('_h')[-1] in ['931_single4','932_distributed4']]
 assert len(chosen)==2
 protocol=dict(cases=chosen,factors=['1','3/2','2'],methods=['previous','learned','fixed_reuse','learned_reuse'],repetitions=3,fresh_processes=True)
 save(HERE/'application_test'/(g+'_protocol.json'),protocol)
 parts=int(os.environ.get('JOINT_APP_PARTS','1'));part=int(os.environ.get('JOINT_APP_PART','0'))
 assert parts in [1,2] and 0<=part<parts
 for ci,c in enumerate(chosen):
  if parts==2 and ci!=part:continue
  requests=[];refs=[]
  for factor in [Fraction(1),Fraction(3,2),Fraction(2)]:
   q=scaled(c,factor);refp,ref=reference(q);assert ref['success']
   requests.append(dict(case=q,basis=ref['masters']));refs.append(refp)
  assert all(x['basis']==requests[0]['basis'] for x in requests),'Scale changed master identifiers'
  # Explicit guard checks precede timed requests and never change the frozen model.
  fixed=rt.read(HERE/'trained_model'/('fixed_'+g+'.json'));cache=ScaleCache(max_bytes=1024,max_entries=1)
  base=requests[0];identity=cache.identify(c,base['basis'],[fixed['signature']]);assert identity
  q=copy.deepcopy(c);q['definition']['propagators'][0]['mass_squared']='1';assert cache.identify(q,base['basis'],[fixed['signature']]) is None
  q=copy.deepcopy(c);q['definition']['scalarproduct_rules'][1][1]='symbol';assert cache.identify(q,base['basis'],[fixed['signature']]) is None
  q=copy.deepcopy(c);q['definition']['scalarproduct_rules']=[[a,str(-Fraction(v))] for a,v in q['definition']['scalarproduct_rules']];assert cache.identify(q,base['basis'],[fixed['signature']])[0]!=identity[0]
  q=copy.deepcopy(c);q['targets'][0][0]=2;assert policy(q,'learned')[0]=='previous'
  q=copy.deepcopy(c);q['targets'][0][-1]=-10;assert policy(q,'learned')[0]=='previous'
  for rep in range(3):
   methods=protocol['methods'][rep:]+protocol['methods'][:rep]
   for method in methods:
    path=HERE/'application_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
    if path.exists():continue
    with tempfile.TemporaryDirectory(prefix='joint_app_',dir=os.environ['TMPDIR']) as td:
     req=Path(td)/'requests.json';out=Path(td)/'out.json.gz';req.write_text(json.dumps(requests))
     args=[sys.executable,str(HERE/'s05_application.py'),'--requests',str(req),'--output',str(out),'--method',method.replace('_reuse','')]
     if not method.endswith('_reuse'):args+=['--no-reuse']
     tick=time.perf_counter();p=subprocess.run(args,capture_output=True,text=True,timeout=300)
     elapsed=time.perf_counter()-tick;assert p.returncode==0,p.stderr[-2000:]
     r=rt.read(out);checks=0;verify_start=time.perf_counter()
     for item,refp in zip(r['results'],refs):
      rt.verify(item,refp);assert item['success'] and item['reference_checked'];checks+=item['coefficient_checks']
     r.update(exact_check_seconds=time.perf_counter()-verify_start,complete_seconds=elapsed+time.perf_counter()-verify_start,method=method,case=c['id'],repetition=rep,worker=os.uname().nodename,coefficient_checks=checks,all_exact=True,first_request_included=True)
     save(path,r);print('APPLICATION',c['id'],method,rep,r['complete_seconds'],flush=True)
 completion=dict(complete=True,sequences=24//parts,requests=72//parts,guard_checks=10//parts)
 if parts==1:save(HERE/'application_test'/(g+'_completion.json'),completion)
 else:
  save(HERE/'application_test'/(g+'_part'+str(part)+'.json'),completion)
  paths=[HERE/'application_test'/(g+'_part'+str(j)+'.json') for j in range(parts)]
  if all(p.exists() for p in paths):
   pieces=[rt.read(p) for p in paths];assert all(p['complete'] for p in pieces)
   completion.update(sequences=sum(p['sequences'] for p in pieces),requests=sum(p['requests'] for p in pieces),guard_checks=sum(p['guard_checks'] for p in pieces),parallel_parts=parts)
   save(HERE/'application_test'/(g+'_completion.json'),completion)

if __name__=='__main__':main()
