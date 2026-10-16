"""Build reviewed evidence and documents after all scientific jobs complete."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def run(path,*args):subprocess.run([sys.executable,str(ROOT/path),*args],cwd=ROOT,check=True)
def main():
    os.environ['MPLCONFIGDIR']=str(ROOT/'.tools/matplotlib-cache')
    os.environ['XDG_CACHE_HOME']=str(ROOT/'.tools/cache')
    application_audit=HERE/'selective_expansion/application_test/validation.json'
    current_application=hashlib.sha256((HERE/'s17_reduce.py').read_bytes()).hexdigest()
    if not application_audit.exists() or json.loads(application_audit.read_text())['source_sha256']!=current_application:
        run('ML_model_adaptive_reduction/s17_reduce.py','--self-test')
    for path in ['Kira_comparison/higher_scattering/s07_analyze.py','Kira_comparison/higher_scattering/s09_validate.py',
                 'ML_model_adaptive_reduction/s06_analyze.py','ML_model_adaptive_reduction/s07_report.py',
                 'ML_model_adaptive_reduction/s10_document.py','ML_model_adaptive_reduction/s16_portfolio_analyze.py',
                 'ML_model_adaptive_reduction/s18_portfolio_report.py']:run(path)
    subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
    run('report/s01_check_paper.py')
    used=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file());assert used<64*1024**2
    d=json.loads((HERE/'summary.json').read_text())
    portfolio=json.loads((HERE/'selective_expansion/summary.json').read_text())
    public=json.loads((HERE/'selective_expansion/application_test/validation.json').read_text())
    assert portfolio['complete'] and portfolio['all_exact'] and public['complete'] and public['all_exact']
    audit=dict(complete=True,all_exact=d['all_exact'],tested_workflows=d['workflows'],
        graph_control_workflows=d['graph_controls']['workflows'],
        deployed_prediction_graphs=d['graph_controls']['enabled_graphs'],
        portfolio_workflows=portfolio['timed_test_workflows'],portfolio_applications=portfolio['applications'],
        portfolio_summary_sha256=hashlib.sha256((HERE/'selective_expansion/summary.json').read_bytes()).hexdigest(),
        portfolio_prediction_graphs=portfolio['enabled_graphs'],portfolio_public_checks=public,
        public_applications=len(d['public_applications']),integration_cases=len(d['integration']),
        failed_integration_controls=[dict(case=c['case'],method=m,failed_seconds=v['failed_seconds'])
            for c in d['integration'] for m,v in c['methods'].items() if not v['complete']],
        retained_bytes=used,combined_upper_bytes=9850000000,generated_data_local=False,
        summary_sha256=hashlib.sha256((HERE/'summary.json').read_bytes()).hexdigest(),
        source_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.glob('s*.py'))},
        paper_sources_and_pdfs_checked=True)
    (HERE/'validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    (ROOT/'report/adaptive_reduction_validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit),flush=True)
if __name__=='__main__':main()
