"""Submit the already frozen tests from a Hoffman login node."""
import json,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def main():
    assert shutil.which('qsub'), 'Run this scheduling step on a login node.'
    assert not (HERE/'test_jobs.json').exists(), 'Preserve existing submitted tests.'
    freeze=json.loads((HERE/'trained_model/freeze.json').read_text())
    assert (HERE/'model_test/protocol.json').exists()
    jobs=[]
    wrapper=str((HERE/'s03_job.sh').relative_to(ROOT))
    def submit(log,args,holds=None):
        command=['qsub','-terse','-l','h_rt=04:00:00,h_data=8G,h_vmem=8G',
                 '-o',str((HERE/log).relative_to(ROOT))]
        if holds:command+=['-hold_jid',','.join(holds)]
        return subprocess.check_output(command+[wrapper]+args,text=True,cwd=ROOT).strip().split('.')[0]
    for i in range(4):
        jobs.append(submit(f'test_worker_{i}.log',['s13_reserved_workers.py','test',str(i)]))
        (HERE/'test_jobs.json').write_text(json.dumps(dict(jobs=jobs,workers=4,submission_complete=False),indent=2)+'\n')
    finish=submit('finish_resumed.log',['s11_finish.py'],jobs)
    (HERE/'test_jobs.json').write_text(json.dumps(dict(jobs=jobs,workers=4,submission_complete=True),indent=2)+'\n')
    p=HERE/'parallel_jobs.json';meta=json.loads(p.read_text());old=meta['finish_job'];meta['finish_job']=finish
    p.write_text(json.dumps(meta,indent=2)+'\n')
    record=dict(reason='Compute-node PATH did not expose qsub after fitting. No reserved test had started. Submit the unchanged frozen comparison from the login node.',
                frozen_utc=freeze['frozen_utc'],previous_finish_job=old,finish_job=finish,test_jobs=jobs,
                training_repeated=False,model_changed=False,test_protocol_changed=False)
    (HERE/'submission_recovery.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record),flush=True)

if __name__=='__main__':main()
