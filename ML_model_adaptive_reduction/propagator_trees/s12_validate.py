"""Check the frozen experiment and build the report and notes."""
from s00_prop_common import *
import subprocess

def main():
    p=read(HERE/'protocol.json.gz');s=read(HERE/'summary.json')
    assert s['complete'] and len(s['rows'])==66 and s['gamma_checks']==714
    assert s['all']['new_completed']==66
    assert sha(HERE/'protocol.json.gz')==s['protocol_sha256']
    assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items())
    assert sha(PREVIOUS/'s01_gamma_cancellation.py')==p['preceding_exact_sha256']
    model=ROOT/'ML_model_adaptive_reduction/analytic_batch/trained_model/policy.json'
    assert sha(model)==p['prior_model_sha256']
    assert all(all(len(v)==3 for v in r['times'].values()) for r in s['rows'])
    assert (ROOT/'report/propagator_trees_appendix.tex').read_bytes()==(HERE/'propagator_trees_appendix.tex').read_bytes()
    assert not list((HERE/'requests').glob('*.json*'))
    for q in HERE.glob('s*.py'):compile(q.read_text(),str(q),'exec')
    subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
    subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
    for name in ['report','notes']:
        log=(ROOT/'report'/(name+'.log')).read_text()
        assert 'Overfull' not in log and 'undefined' not in log.lower(),name
    size=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file());assert size<6*1024**2
    v=dict(complete=True,prior_models_unchanged=True,preceding_exact_unchanged=True,
           summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json.gz'),
           appendix_sha256=sha(HERE/'propagator_trees_appendix.tex'),
           source_sha256={q.name:sha(q) for q in HERE.glob('s*.py')},
           report_source_sha256={q.name:sha(q) for q in (ROOT/'report').glob('*') if q.suffix in ['.tex','.bib']},
           pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},
           final_entry_point='s02_runtime.py',study_allocated_bytes=size,exact_coefficient_checks=s['checks'],independent_gamma_checks=714)
    write(HERE/'validation.json',v);(ROOT/'report/propagator_trees_validation.json').write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps({k:v for k,v in v.items() if 'source_sha256' not in k}),flush=True)
if __name__=='__main__':main()
