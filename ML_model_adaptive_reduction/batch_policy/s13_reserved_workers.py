"""Use four independent workers for frozen reserved comparisons only."""
import argparse,subprocess
import s12_parallel as schedule
from s00_runtime import HERE,ROOT,rt,inputs
from s01_cases import GRAPHS,make

def manifest():
 p=HERE/'reserved_execution.json'
 out=dict(workers=4,graphs={str(i):GRAPHS[i::4] for i in range(4)},
          source_sha256=inputs.sha(HERE/'s13_reserved_workers.py'),
          runner_sha256=inputs.sha(HERE/'s12_parallel.py'),
          scope='Graph assignment only changes experiment concurrency. Every batch retains one worker, all five methods, five repetitions and the unchanged timing order.')
 if p.exists():assert rt.read(p)==out
 else:inputs.write(p,out)

def fit_submit():
 manifest();schedule.check_source()
 for i in range(2):assert rt.read(HERE/f'collection_worker_{i}.json')['complete']
 for stage in ['training','validation','validation_off']:schedule.check(stage)
 import s04_fit
 if not (HERE/'trained_model/freeze.json').exists():s04_fit.main()
 f=rt.read(HERE/'trained_model/freeze.json')
 protocol=dict(cases=[c for h in f['test_profiles'] for c in make(h,'reserved')],methods=['previous','off','fixed','fixed_off','learned'],repetitions=f['test_repetitions'],freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'))
 p=HERE/'model_test/protocol.json'
 if p.exists():assert rt.read(p)==protocol
 else:inputs.write(p,protocol)
 jobs=[]
 for i in range(4):
  args=['qsub','-terse','-l','h_rt=04:00:00,h_data=8G,h_vmem=8G','-o',str((HERE/f'test_worker_{i}.log').relative_to(ROOT)),str((HERE/'s03_job.sh').relative_to(ROOT)),'s13_reserved_workers.py','test',str(i)]
  jobs.append(subprocess.check_output(args,text=True).strip().split('.')[0])
 inputs.write(HERE/'test_jobs.json',dict(jobs=jobs,workers=4))
 finish=str(rt.read(HERE/'parallel_jobs.json')['finish_job'])
 subprocess.run(['qalter','-hold_jid',','.join(jobs),finish],check=True)
 print('RESERVED_WORKERS',jobs,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','fit_submit','test','check']);p.add_argument('worker',nargs='?',type=int,choices=range(4));a=p.parse_args()
 manifest()
 if a.mode=='fit_submit':fit_submit()
 elif a.mode=='test':
  schedule.groups=lambda i:GRAPHS[i::4]
  schedule.test(a.worker)
 elif a.mode=='check':
  schedule.check_source()
  for i in range(4):assert rt.read(HERE/f'test_worker_{i}.json')['complete']
  schedule.check('model_test',True)
  inputs.write(HERE/'model_test/completion.json',dict(complete=True,independent_workers=4))
