"""Show bounded progress information for this study's registered jobs."""
import json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def main():
 out=dict(stages={},workers={},allocated_study_bytes=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file()))
 for name in ['training','validation','validation_off','model_test','application']:
  p=HERE/name;out['stages'][name]=dict(records=len(list(p.glob('*.json.gz'))),complete=(p/'completion.json').exists() or (p/'summary.json').exists())
 jobs=[]
 if (HERE/'parallel_jobs.json').exists():
  d=read(HERE/'parallel_jobs.json');jobs=d['collection_jobs']+[d['fit_job'],d['finish_job']]
  if d.get('application_job'):jobs.append(d['application_job'])
 if (HERE/'test_jobs.json').exists():jobs+=read(HERE/'test_jobs.json')['jobs']
 for p in sorted(HERE.glob('*worker_*.log')):
  lines=p.read_text(errors='replace').splitlines();out['workers'][p.name]=lines[-1] if lines else 'starting'
 q=subprocess.run(['qstat','-u','rushil'],capture_output=True,text=True)
 out['registered_active_jobs']=[s.strip() for s in q.stdout.splitlines() if s.split() and s.split()[0] in jobs]
 if (HERE/'trained_model/freeze.json').exists():
  f=read(HERE/'trained_model/freeze.json');out['model']=dict(enabled=f['enabled'],selected=f['selected'],training_cases=f['training_cases'],validation_cases=f['validation_cases'])
 if (HERE/'validation.json').exists():out['final_audit']=read(HERE/'validation.json')['complete']
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
