"""Preserve interrupted evidence and submit balanced whole-batch recovery jobs."""
import gzip,hashlib,json,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def prepare():
    assert not (HERE/'resumed_execution.json').exists()
    protocol=read(HERE/'model_test/protocol.json');archive=HERE/'interrupted_trials';archive.mkdir(exist_ok=True)
    archived=[];invalid=[];remaining=[];complete=[];failed_refs=[]
    for p in (HERE/'references').glob('*.json.gz'):
        try:read(p)
        except (OSError,EOFError,ValueError):
            dest=archive/('invalid_reference_'+p.name);invalid.append(dict(original=str(p.relative_to(HERE)),archived=str(dest.relative_to(HERE)),sha256=sha(p)));p.rename(dest)
    for c in protocol['cases']:
        ref=HERE/'references'/(c['id']+'.json.gz')
        if ref.exists() and not read(ref)['success']:failed_refs.append(c['id']);continue
        paths=[HERE/'model_test'/(c['id']+'_'+m+f'_r{j}.json.gz') for j in range(protocol['repetitions']) for m in protocol['methods']]
        valid=all(p.exists() for p in paths)
        if valid:
            try:
                for p in paths:assert 'success' in read(p)
            except (OSError,EOFError,ValueError,AssertionError):valid=False
        if valid:complete.append(c['id']);continue
        moved=[]
        for p in paths:
            if p.exists():
                dest=archive/p.name;moved.append(dict(original=str(p.relative_to(HERE)),archived=str(dest.relative_to(HERE)),sha256=sha(p)));p.rename(dest)
        if moved:archived.append(dict(case=c['id'],trials=moved))
        remaining.append(c)
    # Balance only from validation costs. Reserved outcome times are not read.
    def estimate(c):
        paths=list((HERE/'validation').glob(c['topology_group']+'_h712_batch_'+c['shape']+'_whole_r*.json.gz'))
        values=[read(p)['complete_seconds'] for p in paths]
        return 60+25*(statistics.median(values) if values else 5.)
    groups={str(i):[] for i in range(4)};loads=[0.]*4
    for c in sorted(remaining,key=lambda c:(-estimate(c),c['id'])):
        i=min(range(4),key=lambda i:(loads[i],i));groups[str(i)].append(c['id']);loads[i]+=estimate(c)
    preserved=[]
    for i in range(4):
        for suffix in ['json','log']:
            p=HERE/f'test_worker_{i}.{suffix}'
            if p.exists():
                dest=archive/('original_'+p.name);p.rename(dest);preserved.append(str(dest.relative_to(HERE)))
    (archive/'README.md').write_text('# Interrupted comparison records\n\nThe scheduler stopped two jobs at their original one-hour limits.\nIt had accepted longer limits without extending the running allocations.\nComplete comparison batches remain in `../model_test/`.\nThis folder preserves timings from unfinished batches, original worker logs, and completion records.\nEach unfinished batch repeats all methods and repetitions on one new worker.\nThese archived timings do not enter the matched timing ratios.\nRead `../interruption_recovery.json` for the file list and reason.\nNo outcome or speed determined which batches repeated.\n')
    recovery=dict(reason='Two original allocations ended with execd-enforced h_rt after 3600 seconds despite acknowledged qalter changes. Preserve complete batches and repeat every unfinished batch as a whole.',
        archived_batches=archived,archived_trial_count=sum(len(x['trials']) for x in archived),
        invalid_reference_files=invalid,original_worker_records=preserved,
        retained_complete_cases=complete,retained_failed_references=failed_refs,
        remaining_cases=[c['id'] for c in remaining],models_changed=False,scientific_protocol_changed=False,
        assignment_basis='Greedy balancing using validation whole-batch costs only; unchanged global method rotation.',
        accounting_file='interrupted_job_accounting.json')
    write(HERE/'interruption_recovery.json',recovery)
    manifest=dict(case_ids=groups,estimated_worker_seconds=loads,workers=4,
        source_sha256=sha(HERE/'s20_resume_workers.py'),original_runner_sha256=sha(HERE/'s12_parallel.py'),
        protocol_sha256=sha(HERE/'model_test/protocol.json'),freeze_sha256=sha(HERE/'trained_model/freeze.json'),
        recovery_sha256=sha(HERE/'interruption_recovery.json'))
    write(HERE/'resumed_execution.json',manifest)
    print(json.dumps(dict(retained_batches=len(complete),failed_references=len(failed_refs),remaining=len(remaining),archived_trials=recovery['archived_trial_count'],loads=loads)),flush=True)

def submit():
    assert shutil.which('qsub') and not (HERE/'resumed_jobs.json').exists()
    m=read(HERE/'resumed_execution.json');meta=read(HERE/'parallel_jobs.json');app=str(meta['application_job'])
    old=read(HERE/'test_jobs.json');jobs=[]
    for i in range(4):
        cmd=['qsub','-terse','-hold_jid',app,'-q','pod_smp.q,campus2.q','-l','h_rt=04:00:00,h_data=8G,h_vmem=8G',
             '-o',str((HERE/f'test_worker_{i}.log').relative_to(ROOT)),str((HERE/'s03_job.sh').relative_to(ROOT)),
             's20_resume_workers.py','test',str(i)]
        jobs.append(subprocess.check_output(cmd,text=True,cwd=ROOT).strip().split('.')[0])
        write(HERE/'resumed_jobs.json',dict(jobs=jobs,original_jobs=old['jobs'],submission_complete=False,application_dependency=app))
    write(HERE/'resumed_jobs.json',dict(jobs=jobs,original_jobs=old['jobs'],submission_complete=True,application_dependency=app,initial_wall_seconds=14400,requested_memory_gib=8))
    write(HERE/'test_jobs.json',dict(jobs=jobs,original_jobs=old['jobs'],workers=4,resumed=True))
    subprocess.run(['qalter','-hold_jid',','.join(jobs+[app]),str(meta['finish_job'])],check=True)
    subprocess.run(['qrls','-h','u',str(meta['finish_job'])],check=True)
    print('RESUMED_JOBS',jobs,flush=True)

if __name__=='__main__':
    prepare();submit()
