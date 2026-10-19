"""Validate frozen sources, exact evidence, both documents, and archive preservation."""
from s00_vac_common import *
import subprocess

def main():
 p=read(HERE/'protocol.json.gz');s=read(HERE/'summary.json');assert s['complete'] and len(s['rows'])==len(p['cases'])
 assert s['groups']['vacuum']['new_completed']==34 and s['gamma_checks']==714
 assert s['model_requests']>0
 for c in p['cases']:
  if c['test_group']=='native':
   result=read(HERE/'results'/(c['id']+'.json.gz'))['results']['all_fixed']
   assert not result.get('model_used',False)
   assert all(not b['result'].get('batch_model_used',False) for b in result.get('blocks',[]))
 assert sha(HERE/'protocol.json.gz')==s['protocol_sha256']
 assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 assert sha(HERE/'trained_model/policy.json')==p['model_sha256'] and sha(HERE/'trained_model/fixed.json')==p['fixed_sha256']
 assert sha(BATCH/'trained_model/policy.json')==p['prior_model_sha256'] and sha(PRIOR/'s02_runtime.py')==p['prior_entry_sha256']
 assert all(all(len(v)==3 for v in r['times'].values()) for r in s['rows'])
 op=read(HERE/'output_protocol.json.gz');os=read(HERE/'output_summary.json')
 assert os['complete'] and len(os['rows'])==len(op['cases'])==22 and os['all']['new_completed']==22
 assert sha(HERE/'output_protocol.json.gz')==os['protocol_sha256']
 assert op['first_protocol_sha256']==sha(HERE/'protocol.json.gz')
 assert op['model_sha256']==p['model_sha256']==os['model_sha256']
 assert all(sha(HERE/n)==v for n,v in op['source_sha256'].items())
 final_model_requests=0
 for c in op['cases']:
  r=read(HERE/'output_test'/(c['id']+'.json.gz'))
  assert all(len(t)==3 for t in r['times'].values())
  if c['test_group']=='native':
   final_model_requests+=any(b['result'].get('batch_model_used',False) for b in r['results']['fast'].get('blocks',[]))
   ans=r['results']['fast_fixed'];assert not ans.get('model_used',False)
   assert all(not b['result'].get('batch_model_used',False) for b in ans.get('blocks',[]))
 assert final_model_requests>0
 assert not list((HERE/'requests').glob('*.json*'))
 assert (ROOT/'report/vacuum_learning_appendix.tex').read_bytes()==(HERE/'vacuum_learning_appendix.tex').read_bytes()
 for q in HERE.glob('s*.py'):compile(q.read_text(),str(q),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text();assert 'Overfull' not in log and 'undefined' not in log.lower(),name
 size=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file());assert size<4*1024**2
 v=dict(complete=True,prior_models_unchanged=True,preceding_exact_unchanged=True,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json.gz'),model_sha256=sha(HERE/'trained_model/policy.json'),appendix_sha256=sha(HERE/'vacuum_learning_appendix.tex'),source_sha256={q.name:sha(q) for q in HERE.glob('s*.py')},report_source_sha256={q.name:sha(q) for q in (ROOT/'report').glob('*') if q.suffix in ['.tex','.bib']},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},final_entry_point='s18_fast_runtime.py',output_summary_sha256=sha(HERE/'output_summary.json'),output_protocol_sha256=sha(HERE/'output_protocol.json.gz'),final_exact_checks=os['checks'],final_model_requests=final_model_requests,study_allocated_bytes=size,exact_coefficient_checks=s['checks'],independent_gamma_checks=s['gamma_checks'])
 write(HERE/'validation.json',v);(ROOT/'report/vacuum_learning_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
