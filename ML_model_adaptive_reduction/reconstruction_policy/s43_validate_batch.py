"""Check the batch comparison, rendered documents, and retained experiments."""
from s00_reconstruction_common import *

def main():
 p=read(HERE/'batch_protocol.json.gz');s=read(HERE/'batch_summary.json')
 assert s['complete'] and not s['failed_applications'] and not s['changed_reconstruction_actions']
 assert s['requests']==75 and s['applications']==900
 assert len(s['worker_hosts'])==1
 assert s['protocol_sha256']==sha(HERE/'batch_protocol.json.gz')
 assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items())
 assert all(sha(HERE/'trained_model'/n)==h for n,h in p['model_sha256'].items())
 assert sha(TOOLS/'kira')==p['binary_sha256']
 for c in p['cases']:
  assert sha(HERE/'test_references'/(c['id']+'.json.gz'))==p['reference_sha256'][c['id']]
 for rep in range(p['repetitions']):
  for method in p['methods']:
   r=read(HERE/'batch_test'/f'{rep}_{method}.json.gz')
   assert not r['failed'] and all(x['verified'] for x in r['results'].values())
   assert r['total_seconds']==s['methods'][method]['seconds'][rep]
   assert r['order']==[c['id'] for c in p['cases'][::(-1 if rep%2 else 1)]]
 assert not list((HERE/'requests').glob('*.json*'))
 plan=read(HERE/'batch_resource_plan.json')
 assert plan['peak_upper_bytes']<10_000_000_000
 assert allocated(HERE)<STUDY_LIMIT
 subprocess.run([sys.executable,str(HERE/'s32_validate.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text().lower()
  assert 'multiply defined' not in log and 'multiply-defined' not in log,name
 v=read(HERE/'validation.json')
 v.update(batch_protocol_sha256=sha(HERE/'batch_protocol.json.gz'),
  batch_summary_sha256=sha(HERE/'batch_summary.json'),
  batch_resource_plan_sha256=sha(HERE/'batch_resource_plan.json'),
  batch_entry_point='s37_batch.py',batch_exact_coefficient_checks=s['coefficient_checks'],
  batch_completed_applications=s['applications'])
 write(HERE/'validation.json',v)
 (ROOT/'report/reconstruction_validation.json').write_text(json.dumps(v,indent=2)+'\n')
 print(json.dumps(dict(complete=True,batch_entry=v['batch_entry_point'],applications=s['applications'],checks=s['coefficient_checks'],pdf_sha256=v['pdf_sha256'])),flush=True)

if __name__=='__main__':main()
