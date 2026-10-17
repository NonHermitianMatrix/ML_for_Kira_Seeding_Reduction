"""Resume whole comparison batches with the unchanged frozen timing loop."""
import argparse,inspect
import s12_parallel as schedule
from s00_runtime import HERE,rt,inputs

def manifest():
    m=rt.read(HERE/'resumed_execution.json')
    assert inputs.sha(HERE/'s20_resume_workers.py')==m['source_sha256']
    assert inputs.sha(HERE/'s12_parallel.py')==m['original_runner_sha256']
    assert inputs.sha(HERE/'model_test/protocol.json')==m['protocol_sha256']
    assert inputs.sha(HERE/'trained_model/freeze.json')==m['freeze_sha256']
    schedule.check_source()
    return m

def test(worker):
    m=manifest();source=inspect.getsource(schedule.test)
    old="if c['topology_group'] not in groups(worker):continue"
    new="if c['id'] not in assigned_cases(worker):continue"
    assert source.count(old)==1
    # The replacement changes only batch assignment. All arithmetic, timers,
    # method ordering, recovery, and exact checks remain the frozen code.
    source=source.replace(old,new)
    namespace=dict(vars(schedule))
    namespace['assigned_cases']=lambda i:set(m['case_ids'][str(i)])
    exec(compile(source,str(HERE/'s12_parallel.py')+':resumed_assignment','exec'),namespace)
    namespace['test'](worker)
    inputs.write(HERE/f'test_worker_{worker}.json',dict(complete=True,phase='resumed',case_ids=m['case_ids'][str(worker)]))

def check():
    m=manifest()
    for i in range(4):
        f=rt.read(HERE/f'test_worker_{i}.json')
        assert f['complete'] and f['phase']=='resumed' and f['case_ids']==m['case_ids'][str(i)]
    schedule.check('model_test',True)
    inputs.write(HERE/'model_test/completion.json',dict(complete=True,independent_workers=4,
        resumed_execution=True,retained_complete_batches=True,partial_batches_repeated_together=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['test','check']);p.add_argument('worker',nargs='?',type=int,choices=range(4));a=p.parse_args()
    if a.mode=='test':test(a.worker)
    else:check()
