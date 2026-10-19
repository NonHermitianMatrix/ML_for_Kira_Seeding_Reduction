"""Check exact evidence, rebuild both documents, and record a final receipt."""
from s00_fast_common import *
import subprocess

def main():
 from s09_analyze import main as analyze
 from s10_document import main as document
 recorder=read(HERE/'audit_recorder.json');assert recorder['source_sha256']==sha(HERE/'s16_resume_audit.py')
 p=read(HERE/'protocol.json');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 assert sha(HERE/'trained_model/recurrence.json')==p['new_model_sha256']
 assert sha(PRIOR/'basis_registry.json')==p['prior_basis_sha256'];assert sha(PRIOR/'test_protocol.json')==p['prior_protocol_sha256']
 old=legacy();h=old.h
 assert sha(old.PREVIOUS/'trained_model/freeze.json')==p['prior_model_sha256'];assert sha(old.PREVIOUS/'trained_model/expert.json')==p['prior_expert_sha256']
 checks=0;records=0;disagreements=[]
 for c in p['timing']:
  ref=read(HERE/'references'/(c['id']+'.json.gz'))
  for q in (HERE/'model_test').glob(c['id']+'_*.json.gz'):
   r=read(q);ok,n=h.compare(r,ref) if ref['success'] else (False,0)
   assert ok==r['independently_verified'];assert n==r['coefficient_checks'];checks+=n;records+=1
   if r['success'] and ref['success'] and not ok:disagreements.append(q.name)
 assert not disagreements,disagreements
 audit_checks=0;scaleless_proofs=[]
 for c in p['coverage']:
  row=read(HERE/'audit'/(c['id']+'.json'));a=read(HERE/'audit_records'/(c['id']+'_learned_r0.json.gz'));b=read(HERE/'audit_records'/(c['id']+'_previous_r0.json.gz'))
  ok,n=h.compare(a,b) if a['success'] and b['success'] else (False,0)
  assert ok==row['paired_verified'];assert n==row['coefficient_checks'];audit_checks+=n
  if a['success'] and b['success']:assert ok,c['id']
  if a['success'] and not b['success']:
   assert c['scope']=='coverage_scaleless' and not c['definition']['external_momenta']
   assert all(prop['mass_squared']=='0' for prop in c['definition']['propagators'])
   assert all(block['result'].get('route')=='scaleless_vacuum' and not block['result']['masters'] and all(not row for row in block['result']['coefficients'].values()) for block in a['blocks'])
   scaleless_proofs.append(dict(case=c['id'],loops=len(c['definition']['loop_momenta']),total_index_powers=[sum(t) for t in c['targets']],identity='(L*d-2*sum(a))*I_a=0 at generic d'))
 assert {r['loops'] for r in scaleless_proofs}==set(range(8,14))
 write(HERE/'audit_scaleless_proofs.json',dict(complete=True,cases=scaleless_proofs))
 analyze();document()
 from s15_deployment_document import main as deploy_document
 deployment_validation=deploy_document();s=read(HERE/'summary.json')
 assert sum(t['coefficient_checks'] for t in s['totals'].values())==checks
 assert set(s['coverage']['by_loop'])==set(map(str,range(1,14)))
 # Preserve all previous evidence checks and add the current study.
 q=ROOT/'report/s01_check_paper.py';t=q.read_text();marker='    result=dict(general_model_test_complete=True'
 block='''    fast=json.loads((HERE/'fast_decomposition_data.json').read_text())
    assert fast['complete'] and fast['requests']==len(fast['rows'])==65
    assert fast['coverage']['total']['requests']==len(fast['coverage']['rows'])==110
    assert set(fast['coverage']['by_loop'])==set(map(str,range(1,14)))
    assert 'sec:fast-results' in labels and 'app:fast-method' in labels
    for group in fast['comparisons'].values():
        for value in group.values():
            if value['cases']:assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/fast_decomposition/summary.json'
    if p.exists():assert json.loads(p.read_text())==fast
    deployment=json.loads((HERE/'fast_deployment_data.json').read_text())
    assert deployment['complete'] and deployment['requests']==12
    assert 'sec:fast-deployment' in labels and 'app:fast-deployment' in labels
    for group in deployment['comparisons'].values():
        for value in group.values():
            if value['cases']:assert abs(value['ratio']-value['final_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/fast_decomposition/deployment/summary.json'
    if p.exists():assert json.loads(p.read_text())==deployment
'''
 if "fast=json.loads((HERE/'fast_decomposition_data.json')" not in t:q.write_text(t.replace(marker,block+marker))
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 size=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file());assert size<CAP
 assert not list((HERE/'requests').glob('*.json')) and not list(HERE.rglob('*.pending.gz'))
 assert not list((PRIOR/'requests').glob('fast_*.pending.gz'))
 sys.path.insert(0,str(ROOT/'.tools/fast-arithmetic'));import gmpy2
 assert gmpy2.__version__==p['gmpy2_version'];assert os.environ.get('SYMPY_GROUND_TYPES')=='python'
 v=dict(complete=True,timed_records=records,coefficient_checks=checks,audit_coefficient_checks=audit_checks,scaleless_proof_cases=len(scaleless_proofs),scaleless_proof_sha256=sha(HERE/'audit_scaleless_proofs.json'),coefficient_disagreements=disagreements,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json'),new_model_sha256=sha(HERE/'trained_model/recurrence.json'),prior_models_unchanged=True,basis_unchanged=True,sources_frozen=True,audit_recorder_sha256=sha(HERE/'audit_recorder.json'),source_sha256={q.name:sha(q) for q in HERE.glob('s*.py')},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=size,gmpy2_version=gmpy2.__version__,final_entry_point='s12_deploy.py',deployment_validation=deployment_validation)
 write(HERE/'validation.json',v);(ROOT/'report/fast_decomposition_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
