"""Recheck exact evidence, retained sources, and both finished documents."""
from s00_batch_common import *
import subprocess

def main():
 p=read(HERE/'protocol.json');h=legacy().h;checks=0;records=0
 assert p['benchmark_environment']==read(HERE/'benchmark_environment.json')
 assert all(read(HERE/f'test_worker_{w}_environment.json')['host'].split('.')[0]==p['benchmark_environment']['host'] for w in [0,1])
 for name,digest in p['source_sha256'].items():assert sha(HERE/name)==digest,name
 for key,path in [('model_sha256',HERE/'trained_model/policy.json'),('fixed_sha256',HERE/'trained_model/fixed.json'),('additional_basis_sha256',HERE/'basis_registry.json'),('basis_validation_sha256',HERE/'basis_validation.json'),('basis_preparation_source_sha256',HERE/'s11_prepare_basis.py'),('native_binary_sha256',ROOT/'.tools/kira-sector-wide/kira'),('basis_sha256',support.PRIOR/'basis_registry.json'),('preceding_admission_sha256',PREVIOUS/'deployment/admission.json'),('preceding_model_sha256',legacy().PREVIOUS/'trained_model/expert.json'),('preceding_outer_model_sha256',legacy().PREVIOUS/'trained_model/freeze.json')]:assert sha(path)==p[key],key
 phases={'application_validation':__import__('s03_cases').batches(3041,'application_validation'),'model_test':p['cases']}
 counts={}
 for phase,cs in phases.items():
  count=0;total=0
  for c in cs:
   ref=read(HERE/'references'/(c['id']+'.json.gz'))
   for q in (HERE/phase).glob(c['id']+'_*.json.gz'):
    r=read(q);ok,n=h.compare(r,ref) if ref['success'] else (False,0)
    assert ok==r['independently_verified'],q.name;assert n==r['coefficient_checks'],q.name
    if r['success'] and ref['success']:assert ok,q.name
    count+=1;total+=n
  counts[phase]=dict(records=count,checks=total)
 assert counts['model_test']['records']==read(HERE/'summary.json')['timed_records']
 assert counts['model_test']['checks']==read(HERE/'summary.json')['coefficient_checks']
 for q in (HERE/'basis_checks').glob('*.json.gz'):
  r=read(q);assert r['verified'];ok,_=h.equal(r['first']['coefficients'],r['second']['coefficients']);assert ok
 from s16_triangle_checks import main as triangle_checks
 structural=triangle_checks()
 # Check sources without creating bytecode, then add report-only evidence checks.
 for q in HERE.glob('s*.py'):compile(q.read_text(),str(q),'exec')
 q=ROOT/'report/s01_check_paper.py';z=q.read_text();marker='    result=dict(general_model_test_complete=True'
 addition='''    batch=json.loads((HERE/'analytic_batch_data.json').read_text())
    assert batch['complete'] and batch['requests']==len(batch['rows'])==58
    assert 'app:analytic-batch' in labels and 'sec:analytic-batch-results' in labels
    for group in batch['comparisons'].values():
        for value in group.values():
            if value['matched']:assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/analytic_batch/summary.json'
    if q.exists():assert json.loads(q.read_text())==batch
'''
 if "batch=json.loads((HERE/'analytic_batch_data.json')" not in z:
  assert marker in z;q.write_text(z.replace(marker,addition+marker))
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(q)],check=True)
 size=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file());assert size<CAP
 assert not list((HERE/'requests').glob('*.json')) and not list(HERE.rglob('*.pending.gz'))
 v=dict(complete=True,counts=counts,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json'),model_sha256=p['model_sha256'],prior_models_unchanged=True,prior_basis_unchanged=True,additional_basis_checked=True,sources_frozen=True,source_sha256={q.name:sha(q) for q in HERE.glob('s*.py')},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=size,final_entry_point='s02_batch_runtime.py')
 v['triangle_structure_checks']=structural
 write(HERE/'validation.json',v);(ROOT/'report/analytic_batch_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
