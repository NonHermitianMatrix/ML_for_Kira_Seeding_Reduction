"""Run independent graph groups on two workers, keeping each comparison together."""
import argparse,json,subprocess,time
from s00_runtime import HERE,ROOT,FILTER,ACTIONS,rt,inputs,save,run,reduce,partition
from s01_cases import GRAPHS,make,initialize,reference

def groups(worker):return GRAPHS[worker::2]

def prepare():
 initialize()
 for stage,h in [('training',711),('validation',712),('validation_off',712)]:
  cases=make(h,stage);canonical={}
  for c in cases:
   seen={};mapping={}
   for a in ACTIONS:
    key=(stage!='validation_off' and a!='whole_off',tuple(tuple(map(tuple,q['targets'])) for q in partition(c,a)))
    mapping[a]=seen.setdefault(key,a)
   canonical[c['id']]=mapping
  proto=dict(cases=cases,actions=ACTIONS,repetitions=2 if stage=='training' else 3,profile=h,canonical_partitions=canonical,equivalent_costs='Identical ordered target parts share one measured cost; no repeated timing is claimed for aliases.')
  p=HERE/stage/'protocol.json'
  if p.exists():assert rt.read(p)==proto
  else:inputs.write(p,proto)
 manifest=dict(workers=2,graphs={str(i):groups(i) for i in range(2)},source_sha256=inputs.sha(HERE/'s12_parallel.py'),
  scope='Only independent graphs run concurrently. All methods and repetitions of each reserved batch use one worker. Candidate definitions, ordering, checks and timers are unchanged.',
  original_sources={n:inputs.sha(HERE/n) for n in ['s00_runtime.py','s01_cases.py','s02_collect.py','s04_fit.py','s05_test.py','s06_pipeline.py']})
 p=HERE/'parallel_execution.json'
 if p.exists():assert rt.read(p)==manifest
 else:inputs.write(p,manifest)

def check_source():
 p=rt.read(HERE/'parallel_execution.json');assert p['source_sha256']==inputs.sha(HERE/'s12_parallel.py')
 for n,h in p['original_sources'].items():assert inputs.sha(HERE/n)==h,n

def collect(worker):
 check_source()
 for stage in ['training','validation','validation_off']:
  protocol=rt.read(HERE/stage/'protocol.json')
  for ci,c in enumerate(protocol['cases']):
   if c['topology_group'] not in groups(worker):continue
   ref=reference(c)
   if ref is None:print('REFERENCE_FAILED',stage,c['id'],flush=True);continue
   for j in range(protocol['repetitions']):
    for k in [(n+ci+2*j)%len(ACTIONS) for n in range(len(ACTIONS))]:
     action=ACTIONS[k];p=HERE/stage/(c['id']+'_'+action+f'_r{j}.json.gz')
     if protocol['canonical_partitions'][c['id']][action]!=action or p.exists():continue
     tick=time.perf_counter();basis=rt.read(ref)['masters'];r=run(c,basis,action,stage!='validation_off',ref);r['complete_seconds']=time.perf_counter()-tick;save(p,r)
     print('COLLECT',worker,stage,c['id'],action,j,r['success'],round(r['complete_seconds'],4),flush=True)
 inputs.write(HERE/f'collection_worker_{worker}.json',dict(complete=True))

def check(stage,test=False):
 protocol=rt.read(HERE/stage/'protocol.json')
 for c in protocol['cases']:
  ref=HERE/'references'/(c['id']+'.json.gz');assert ref.exists(),c['id']
  if not rt.read(ref)['success']:continue
  actions=protocol['methods'] if test else set(protocol['canonical_partitions'][c['id']].values())
  for action in actions:
   for j in range(protocol['repetitions']):
    p=HERE/stage/(c['id']+'_'+action+f'_r{j}.json.gz');assert p.exists(),str(p);rt.read(p)
 inputs.write(HERE/stage/'completion.json',dict(complete=True,independent_workers=2))

def fit_submit():
 check_source()
 for worker in range(2):assert rt.read(HERE/f'collection_worker_{worker}.json')['complete']
 for stage in ['training','validation','validation_off']:check(stage)
 import s04_fit
 if not (HERE/'trained_model/freeze.json').exists():s04_fit.main()
 f=rt.read(HERE/'trained_model/freeze.json');cases=[c for h in f['test_profiles'] for c in make(h,'reserved')]
 protocol=dict(cases=cases,methods=['previous','off','fixed','fixed_off','learned'],repetitions=f['test_repetitions'],freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'))
 p=HERE/'model_test/protocol.json'
 if p.exists():assert rt.read(p)==protocol
 else:inputs.write(p,protocol)
 jobs=[]
 for worker in range(2):
  cmd=['qsub','-terse','-l','h_rt=04:00:00,h_data=8G,h_vmem=8G','-o',str((HERE/f'test_worker_{worker}.log').relative_to(ROOT)),str((HERE/'s03_job.sh').relative_to(ROOT)),'s12_parallel.py','test',str(worker)]
  j=subprocess.check_output(cmd,text=True).strip().split('.')[0];jobs.append(j)
 inputs.write(HERE/'test_jobs.json',dict(jobs=jobs))
 subprocess.run(['qalter','-hold_jid',','.join(jobs),'15187595'],check=True)
 print('TEST_JOBS',jobs,flush=True)

def test(worker):
 check_source();f=rt.read(HERE/'trained_model/freeze.json');p=rt.read(HERE/'model_test/protocol.json')
 assert inputs.sha(HERE/'trained_model/freeze.json')==p['freeze_sha256']
 for n,h in f['sources'].items():assert inputs.sha(HERE/n)==h,n
 assert inputs.sha(rt.BINARY)==f['native_sha256']
 assert inputs.sha(HERE/'fixed_inputs.json')==f['filter_source_sha256']
 assert inputs.sha(FILTER/'trained_model/freeze.json')==rt.read(HERE/'fixed_inputs.json')['source_freeze_sha256']
 for ci,c in enumerate(p['cases']):
  if c['topology_group'] not in groups(worker):continue
  ref=reference(c)
  if ref is None:print('TEST_REFERENCE_FAILED',c['id'],flush=True);continue
  for j in range(p['repetitions']):
   methods=p['methods'];offset=(ci+2*j)%len(methods)
   for method in methods[offset:]+methods[:offset]:
    dest=HERE/'model_test'/(c['id']+'_'+method+f'_r{j}.json.gz')
    if dest.exists():continue
    tick=time.perf_counter();basis=rt.read(ref)['masters'];r=reduce(c,basis,method,ref);r['complete_seconds']=time.perf_counter()-tick;save(dest,r)
    print('TEST',worker,c['id'],method,j,r['success'],round(r['complete_seconds'],4),r['action'],flush=True)
 inputs.write(HERE/f'test_worker_{worker}.json',dict(complete=True))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','collect','fit_submit','test','check_test']);p.add_argument('worker',nargs='?',type=int,choices=[0,1]);a=p.parse_args()
 if a.mode=='prepare':prepare()
 elif a.mode=='collect':collect(a.worker)
 elif a.mode=='fit_submit':fit_submit()
 elif a.mode=='test':test(a.worker)
 else:
  check_source()
  for worker in range(2):assert rt.read(HERE/f'test_worker_{worker}.json')['complete']
  check('model_test',True)
