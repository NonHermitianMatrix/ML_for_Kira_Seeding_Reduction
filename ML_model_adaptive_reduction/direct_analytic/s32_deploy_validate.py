"""Validate final deployment while preserving the original rejected-model experiment."""
from s00_direct_common import *
from s14_prepare import sha
from s29_deploy_check import check
from s20_validate import value_checks
import subprocess,re

def main():
 p=check();s=read(HERE/'final_summary.json');initial=read(HERE/'protocol.json.gz');assert s['complete'] and len(p['cases'])==69 and len(initial['extended_cases'])==26
 assert s['protocol_sha256']==sha(HERE/'final_protocol.json.gz');assert s['initial_protocol_sha256']==sha(HERE/'protocol.json.gz');assert read(HERE/'checks.json')['complete']
 for c in p['cases']:
  r=read(HERE/'deployment_test'/(c['id']+'.json.gz'));assert r['reference_success'] and all(len(v)==3 for v in r['times'].values());assert not r['results']['fixed'].get('model_used',False)
  if c['test_group']=='native':assert r['results']['integrated'].get('native_policy_source')=='preceding_validated_model'
 for g in ['vacuum_products','connected_vacuum','extended_vacuum','scaleless_vacuum']:assert {r['loops'] for r in s['rows'] if r['group']==g}==set(range(1,14))
 assert not list((HERE/'requests').glob('*.json*'));gamma_checks=value_checks(p,'deployment_test')
 for n in ['ML_model_adaptive_reduction/lightlike_reduction/s05_runtime.py','ML_model_adaptive_reduction/lightlike_reduction/trained_model/policy.json','ML_model_adaptive_reduction/tensor_reduction/s17_fast_tensor.py']:
  raw=(ROOT/n).read_bytes();import hashlib
  oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert subprocess.check_output(['git','ls-tree',p['prior_commit'],'--',n],cwd=ROOT,text=True).split()[2]==oid
 for f in HERE.glob('s*.py'):compile(f.read_text(),str(f),'exec')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True);subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 for name in ['report','notes']:
  log=(ROOT/'report'/(name+'.log')).read_text();assert 'Overfull' not in log and 'undefined' not in log.lower(),name;assert (ROOT/'report'/(name+'.pdf')).stat().st_size<32*1024**2
  bib=(ROOT/'report'/(name+'.blg')).read_text();assert not re.search(r'error message|Repeated entry|I couldn.t|Warning--',bib,re.I),name
 size=sum(f.stat().st_blocks*512 for f in HERE.rglob('*') if f.is_file());assert size<12*1024**2;plan=read(HERE/'resource_plan.json');assert plan['publish_peak_upper_bytes']<10_000_000_000
 v=dict(complete=True,prior_models_unchanged=True,preceding_exact_unchanged=True,summary_sha256=sha(HERE/'final_summary.json'),protocol_sha256=sha(HERE/'final_protocol.json.gz'),initial_summary_sha256=sha(HERE/'summary.json'),source_sha256={f.name:sha(f) for f in HERE.glob('s*.py')},model_sha256=sha(HERE/'trained_model/policy.json'),retained_model_sha256=sha(PRIOR/'trained_model/policy.json'),appendix_sha256=sha(HERE/'direct_final_appendix.tex'),report_source_sha256={f.name:sha(f) for f in (ROOT/'report').glob('*') if f.suffix in ['.tex','.bib']},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},final_entry_point='s23_deploy.py',study_allocated_bytes=size,exact_coefficient_checks=s['checks'],connected_analytic_value_checks=gamma_checks,completed=s['all']['new_completed'],resource_plan_sha256=sha(HERE/'resource_plan.json'))
 write(HERE/'validation.json',v);(ROOT/'report/direct_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
