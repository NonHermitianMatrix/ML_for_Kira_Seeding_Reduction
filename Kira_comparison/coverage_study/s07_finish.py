"""Build and audit the completed coverage study without rerunning calculations."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for n in ['s10_audit_coefficients.py','s05_analyze.py','s06_report.py']:subprocess.run([sys.executable,str(HERE/n)],check=True)
    subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
    subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
    paper=json.loads((ROOT/'report/paper_validation.json').read_text());summary=json.loads((HERE/'summary.json').read_text())
    assert paper['original_notes_reconstructable'] and paper['self_repository_citations']==0
    retained=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
    plan=json.loads((HERE/'resource_plan.json').read_text());assert retained<plan['retained_bytes'] and plan['combined_upper_bytes']<plan['limit_bytes']
    audit=dict(complete=True,summary_sha256=sha(HERE/'summary.json'),sources={str(p.relative_to(ROOT)):sha(p) for p in HERE.glob('s*') if p.is_file()},pdf_sha256=paper['pdf_sha256'],retained_bytes=retained,combined_upper_bytes=plan['combined_upper_bytes'],native_cases=summary['native_cases'],native_timed=summary['native_timed'],vacuum_requests=summary['vacuum_requests'],all_successful_outputs_exact=summary['all_successful_outputs_exact'],failed_cases_retained=True)
    for p in [HERE/'validation.json',ROOT/'report/coverage_validation.json']:p.write_text(json.dumps(audit,indent=2)+'\n')
    print('COVERAGE_PUBLICATION_READY',flush=True)
if __name__=='__main__':main()
