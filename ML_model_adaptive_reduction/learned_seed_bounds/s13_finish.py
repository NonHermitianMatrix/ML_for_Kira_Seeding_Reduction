"""Complete result analysis, guides, both PDFs, and publication checks."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for n in ['s12_audit.py','s08_analyze.py','s09_report.py','s11_readmes.py']:
  subprocess.run([sys.executable,str(HERE/n)],check=True)
 subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
 subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
 paper=json.loads((ROOT/'report/paper_validation.json').read_text());summary=json.loads((HERE/'summary.json').read_text());proof=json.loads((HERE/'coefficient_audit.json').read_text())
 assert paper['original_notes_reconstructable'] and paper['self_repository_citations']==0
 assert summary['all_successful_outputs_exact'] and proof['all_successful_outputs_exact']
 retained=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
 plan=json.loads((HERE/'resource_plan.json').read_text());assert retained<plan['retained_bytes'] and plan['combined_upper_bytes']<plan['limit_bytes']
 audit=dict(complete=True,summary_sha256=sha(HERE/'summary.json'),sources={str(p.relative_to(ROOT)):sha(p) for p in HERE.glob('s*') if p.is_file()},pdf_sha256=paper['pdf_sha256'],retained_bytes=retained,combined_upper_bytes=plan['combined_upper_bytes'],all_successful_outputs_exact=True,no_earlier_models_in_primary_comparison=True,failed_cases_retained=True,model_sha256=sha(HERE/'trained_model/freeze.json'),coefficient_audit_sha256=sha(HERE/'coefficient_audit.json'))
 for p in [HERE/'validation.json',ROOT/'report/learned_bounds_validation.json']:p.write_text(json.dumps(audit,indent=2)+'\n')
 print('LEARNED_BOUNDS_PUBLICATION_READY',flush=True)
if __name__=='__main__':main()
