"""Submit the predeclared application checks when their references are complete."""
import gzip,json,shutil,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def main():
    assert shutil.which('qsub'), 'Run this scheduling step on a login node.'
    assert not (HERE/'application_job.json').exists(), 'An application job is already registered.'
    p=json.loads((HERE/'model_test/protocol.json').read_text())
    cases=[c for c in p['cases'] if c['topology_group'] in ['double_box','ladder3','nonplanar_box','massless4'] and '_h721_' in c['id'] and c['shape']=='all']
    paths=[HERE/'references'/(c['id']+'.json.gz') for c in cases]
    for _ in range(120):
        completed=sum((HERE/f'test_worker_{i}.json').exists() for i in range(4))
        try:
            ready=all('success' in json.loads(gzip.decompress(q.read_bytes())) for q in paths)
        except (OSError,EOFError,ValueError):ready=False
        if ready and completed>=1:break
        time.sleep(10)
    else:raise RuntimeError('Application references are not ready; no job was submitted.')
    command=['qsub','-terse','-q','pod_smp.q,campus2.q','-l','h_rt=01:00:00,h_data=8G,h_vmem=8G',
             '-o',str((HERE/'application_worker_0.log').relative_to(ROOT)),
             str((HERE/'s03_job.sh').relative_to(ROOT)),'s17_application_stage.py']
    job=subprocess.check_output(command,text=True,cwd=ROOT).strip().split('.')[0]
    jobs=json.loads((HERE/'test_jobs.json').read_text())['jobs']
    q=HERE/'parallel_jobs.json';meta=json.loads(q.read_text())
    subprocess.run(['qalter','-hold_jid',','.join(jobs+[job]),str(meta['finish_job'])],check=True)
    meta['application_job']=job;q.write_text(json.dumps(meta,indent=2)+'\n')
    receipt=dict(job=job,completed_reserved_workers=completed,
        physical_requests=[c['id'] for c in cases],maximum_concurrent_native_workers=4,
        freeze_sha256=p['freeze_sha256'],selection_uses_reserved_timings=False,
        finish_job=meta['finish_job'])
    (HERE/'application_job.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
