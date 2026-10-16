"""Audit the completed study, build both PDFs, and check publication inputs."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'parametric_preparation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert json.loads((OUT/'completion.json').read_text())['complete']
    assert 'REPLAY_CHECKS_COMPLETE' in (OUT/'replay_checks.log').read_text()
    for name in ['s30_analyze_parametric.py','s31_report_parametric.py']:
        subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
    subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
    subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
    audit=json.loads((ROOT/'report/paper_validation.json').read_text())
    assert audit['original_notes_reconstructable'] and audit['self_repository_citations']==0
    own=sum(p.stat().st_blocks*512 for p in OUT.rglob('*') if p.is_file())
    build=sum(p.stat().st_blocks*512 for p in (ROOT/'.tools/kira-parametric').rglob('*') if p.is_file())
    assert own<16_000_000 and build<12_000_000,(own,build)
    plan=json.loads((OUT/'resource_plan.json').read_text());assert plan['combined_upper_bytes']<10_000_000_000
    validation=json.loads((OUT/'validation.json').read_text())
    names=[p for p in HERE.glob('s*.py') if int(p.name[1:3])>=22]+[HERE/'s25_parametric_job.sh']
    validation.update(paper_checked=True,pdf_sha256=audit['pdf_sha256'],retained_bytes=own,build_bytes=build,
        combined_upper_bytes=plan['combined_upper_bytes'],source_files={str(p.relative_to(ROOT)):sha(p) for p in names})
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    (ROOT/'report/parametric_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print('PARAMETRIC_PUBLICATION_READY',flush=True)
if __name__=='__main__':main()
