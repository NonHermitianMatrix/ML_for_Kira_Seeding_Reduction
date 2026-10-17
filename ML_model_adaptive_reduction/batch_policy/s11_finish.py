"""Audit completed experiments and build the paper and archived notes."""
import json,subprocess,sys
from s00_runtime import HERE,ROOT,rt,inputs

def main():
 if (HERE/'resumed_execution.json').exists():subprocess.run([sys.executable,str(HERE/'s20_resume_workers.py'),'check'],check=True)
 elif (HERE/'reserved_execution.json').exists():subprocess.run([sys.executable,str(HERE/'s13_reserved_workers.py'),'check'],check=True)
 elif (HERE/'parallel_execution.json').exists():subprocess.run([sys.executable,str(HERE/'s12_parallel.py'),'check_test'],check=True)
 assert rt.read(HERE/'model_test/completion.json')['complete']
 subprocess.run([sys.executable,str(HERE/'s16_deployment.py'),'--prepare'],check=True)
 for script in ['s08_application.py','s07_analyze.py','s09_document.py','s10_readmes.py']:
  subprocess.run([sys.executable,str(HERE/script)],check=True)
 banana=ROOT/'ML_model_adaptive_reduction/massless_banana'
 assert rt.read(banana/'native_followup/summary.json')['complete']
 for script in ['s05_route_test.py','s06_document.py','s07_readmes.py']:
  subprocess.run([sys.executable,str(banana/script)],check=True)
 subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
 subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
 d=rt.read(HERE/'summary.json');a=rt.read(HERE/'application/summary.json');paper=rt.read(ROOT/'report/paper_validation.json')
 assert d['all_successful_outputs_exact'] and d['controls_disable_all_ml'] and paper['original_notes_reconstructable']
 used=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file());assert used<32*1024**2
 plan=rt.read(HERE/'resource_plan.json');assert plan['combined_upper_bytes']<10_000_000_000
 audit=dict(complete=True,all_successful_outputs_exact=True,controls_disable_all_ml=True,failed_cases_retained=True,summary_sha256=inputs.sha(HERE/'summary.json'),application_sha256=inputs.sha(HERE/'application/summary.json'),freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'),source_sha256={p.name:inputs.sha(p) for p in HERE.glob('s*') if p.is_file()},pdf_sha256=paper['pdf_sha256'],original_notes_reconstructable=paper['original_notes_reconstructable'],retained_bytes=used,combined_upper_bytes=plan['combined_upper_bytes'])
 assert sum(p.stat().st_blocks*512 for p in banana.rglob('*') if p.is_file())<2*1024**2
 assert rt.read(banana/'application/summary.json')['all_successful_outputs_exact']
 audit['analytic_study_sha256']={str(p.relative_to(banana)):inputs.sha(p) for p in banana.rglob('*') if p.is_file() and p.suffix in ['.py','.tex','.json']}
 deployment=rt.read(HERE/'deployment_checks.json');assert deployment['passed']
 assert inputs.sha(HERE/'trained_model/deployment.json')==deployment['deployment_sha256']
 audit['deployment_sha256']=deployment['deployment_sha256']
 for n in ['resumed_execution.json','resumed_jobs.json','interruption_recovery.json']:
  if (HERE/n).exists():audit[n+'_sha256']=inputs.sha(HERE/n)
 for dest in [HERE/'validation.json',ROOT/'report/batch_policy_validation.json']:inputs.write(dest,audit)
 print('BATCH_POLICY_READY_FOR_VISUAL_REVIEW',json.dumps(audit),flush=True)

if __name__=='__main__':main()
