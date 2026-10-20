"""Validate both frozen studies, exact checks, documents, and preserved archives."""
from s00_tensor_common import *
import subprocess

def main():
 p=read(HERE/'protocol.json.gz');q=read(HERE/'fast_protocol.json.gz');s=read(HERE/'summary.json');f=read(HERE/'fast_summary.json')
 assert s['complete'] and f['complete'];assert len(s['rows'])==len(p['cases'])==44;assert len(f['rows'])==len(q['cases'])==44
 assert f['groups']['tensor']['new_completed']==16 and f['groups']['other_masses']['new_completed']==4 and f['groups']['products']['new_completed']==12
 assert set(r['loops'] for r in f['rows'] if r['group']=='products')==set(range(2,14))
 assert q['first_protocol_sha256']==sha(HERE/'protocol.json.gz')
 for protocol,model,summary,name,folder in [(p,'policy.json',s,'protocol.json.gz','model_test'),(q,'fast_policy.json',f,'fast_protocol.json.gz','final_test')]:
  assert all(sha(HERE/n)==v for n,v in protocol['source_sha256'].items())
  assert protocol['model_sha256']==sha(HERE/'trained_model'/model)
  assert protocol['prior_model_sha256']==sha(PRIOR/'trained_model/policy.json')
  assert protocol['prior_entry_sha256']==sha(PRIOR/'s18_fast_runtime.py')
  assert summary['protocol_sha256']==sha(HERE/name)
  for c in protocol['cases']:
   r=read(HERE/folder/(c['id']+'.json.gz'));assert all(len(t)==3 for t in r['times'].values())
   fixed=r['results']['all_fixed'];assert not fixed.get('model_used',False)
   assert all(not b['result'].get('model_used',False) and not b['result'].get('batch_model_used',False) for b in fixed.get('blocks',[]))
 for name in ['pilot.json','development_checks.json','fast_arithmetic_checks.json']:assert read(HERE/name)['complete']
 assert f['model_requests']['native']>0
 assert not list((HERE/'requests').glob('*.json*'))
 assert (ROOT/'report/tensor_reduction_appendix.tex').read_bytes()==(HERE/'tensor_reduction_appendix.tex').read_bytes()
 for path in HERE.glob('s*.py'):compile(path.read_text(),str(path),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text();assert 'Overfull' not in log and 'undefined' not in log.lower(),name
 size=sum(path.stat().st_blocks*512 for path in HERE.rglob('*') if path.is_file());assert size<6*1024**2
 plan=read(HERE/'resource_plan.json');assert not plan['provisional'] and plan['publish_peak_upper_bytes']<10_000_000_000
 v=dict(complete=True,prior_models_unchanged=True,preceding_exact_unchanged=True,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json.gz'),fast_summary_sha256=sha(HERE/'fast_summary.json'),fast_protocol_sha256=sha(HERE/'fast_protocol.json.gz'),model_sha256=sha(HERE/'trained_model/fast_policy.json'),appendix_sha256=sha(HERE/'tensor_reduction_appendix.tex'),source_sha256={p.name:sha(p) for p in HERE.glob('s*.py')},report_source_sha256={p.name:sha(p) for p in (ROOT/'report').glob('*') if p.suffix in ['.tex','.bib']},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},final_entry_point='s18_fast_runtime.py',study_allocated_bytes=size,exact_coefficient_checks=f['checks'],new_tensor_completions=f['groups']['tensor']['new_completed']+f['groups']['other_masses']['new_completed'],independent_product_completions=f['groups']['products']['new_completed'])
 write(HERE/'validation.json',v);(ROOT/'report/tensor_reduction_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
