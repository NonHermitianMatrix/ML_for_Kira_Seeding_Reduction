"""Check frozen evidence, report preservation, exact agreement, and bounded storage."""
from s00_light_common import *
import subprocess,re

def main():
 p=read(HERE/'protocol.json.gz');s=read(HERE/'summary.json');m=read(HERE/'trained_model/policy.json')
 assert s['complete'] and len(s['rows'])==len(p['cases'])==68
 assert s['protocol_sha256']==sha(HERE/'protocol.json.gz')
 assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items())
 assert sha(HERE/'trained_model/policy.json')==p['model_sha256']
 assert sha(PRIOR/'s18_fast_runtime.py')==p['previous_entry_sha256']
 for n in ['checks.json','symbolic_checks.json']:assert read(HERE/n)['complete']
 for c in p['cases']:
  r=read(HERE/'model_test'/(c['id']+'.json.gz'));assert all(len(v)==3 for v in r['times'].values())
  fixed=r['results']['all_fixed'];assert not fixed.get('model_used',False)
  assert all(not b['result'].get('model_used',False) and not b['result'].get('batch_model_used',False) for b in fixed.get('blocks',[]))
  for method,ss in r['success'].items():
   assert len(ss)==3
   if all(ss):assert r['reference_success']
 assert set(r['loops'] for r in s['rows'] if r['group']=='products')==set(range(2,14))
 assert not list((HERE/'requests').glob('*.json*'))
 # Compare prior deployed scientific sources and weights directly with the parent commit.
 names=['ML_model_adaptive_reduction/tensor_reduction/s18_fast_runtime.py','ML_model_adaptive_reduction/tensor_reduction/s17_fast_tensor.py','ML_model_adaptive_reduction/vacuum_learning/trained_model/policy.json']
 for name in names:
  raw=(ROOT/name).read_bytes();oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();record=subprocess.check_output(['git','ls-tree',p['prior_commit'],'--',name],cwd=ROOT,text=True).split()[2];assert oid==record,name
 for path in HERE.glob('s*.py'):compile(path.read_text(),str(path),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text();assert 'Overfull' not in log and 'undefined' not in log.lower(),name
  assert (ROOT/'report'/(name+'.pdf')).stat().st_size<32*1024**2
  bib=(ROOT/'report'/(name+'.blg')).read_text();assert not re.search(r'error message|Repeated entry|I couldn.t|Warning--',bib,re.I),name
 size=sum(f.stat().st_blocks*512 for f in HERE.rglob('*') if f.is_file());assert size<8*1024**2
 plan=read(HERE/'resource_plan.json');assert not plan['provisional'] and plan['publish_peak_upper_bytes']<10_000_000_000
 v=dict(complete=True,prior_models_unchanged=True,preceding_exact_unchanged=True,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json.gz'),source_sha256={f.name:sha(f) for f in HERE.glob('s*.py')},model_sha256=sha(HERE/'trained_model/policy.json'),appendix_sha256=sha(HERE/'lightlike_appendix.tex'),report_source_sha256={f.name:sha(f) for f in (ROOT/'report').glob('*') if f.suffix in ['.tex','.bib']},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},final_entry_point='s05_runtime.py',study_allocated_bytes=size,exact_coefficient_checks=s['checks'],completed=s['all']['new_completed'],resource_plan_sha256=sha(HERE/'resource_plan.json'))
 write(HERE/'validation.json',v);(ROOT/'report/lightlike_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
