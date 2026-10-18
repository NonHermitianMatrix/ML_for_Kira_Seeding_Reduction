"""Complete the measured extension, build both documents, and check evidence."""
from s00_common import *
import subprocess

def main():
 s12_analyze=module('thirteen_analysis',HERE/'s12_analyze.py');s13_document=module('thirteen_document',HERE/'s13_document.py')
 s12_analyze.main();s13_document.main()
 s=READ(HERE/'summary.json');report=ROOT/'report'
 assert s['complete']
 for phase in ['initial','final']:
  data=s[phase]
  assert len(data['rows'])==data['requested']
  assert sum(x['requested'] for x in data['by_loop'].values())==data['requested']
  for v in data['comparisons'].values():
   if not v['cases']:continue
   assert len(v['case_ids'])==v['cases']
   totals=v['summed_median_seconds'];control=next(k for k in totals if k!='learned')
   assert abs(v['ratio']-totals['learned']/totals[control])<1e-12
   for row in data['rows']:
    if row['case'] in v['case_ids']:assert row['complete']['learned'] and row['complete'][control]
 assert all(READ(p)['native_equal'] is not False for folder in ['formula_checks','massless_formula_checks'] for p in (HERE/'extension'/folder).glob('*.json.gz'))
 # Extend the report checker without changing its historical reconstruction checks.
 p=report/'s01_check_paper.py';text=p.read_text();marker='    result=dict(general_model_test_complete=True'
 if "factorized=json.loads" not in text:
  extra='''    factorized=json.loads((HERE/'factorized_data.json').read_text())
    assert factorized['complete'] and factorized['initial']['requested']==131
    assert set(factorized['initial']['by_loop'])==set(map(str,range(1,14)))
    assert 'app:blocks13' in labels and 'sec:blocks13' in labels
    for phase in ['initial','final']:
        d=factorized[phase]
        assert d['requested']==len(d['rows'])
        for v in d['comparisons'].values():
            if not v['cases']:continue
            totals=v['summed_median_seconds'];b=next(k for k in totals if k!='learned')
            assert abs(v['ratio']-totals['learned']/totals[b])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/factorized_policy/summary.json'
    if q.exists():assert json.loads(q.read_text())==factorized
'''
  assert marker in text;text=text.replace(marker,extra+marker);p.write_text(text)
 subprocess.run(['make','-C',str(report),'all'],check=True,timeout=600)
 subprocess.run([sys.executable,str(report/'s01_check_paper.py')],check=True,timeout=180)
 v=dict(complete=True,all_matched_results_exact=True,initial_requested=s['initial']['requested'],final_requested=s['final']['requested'],summary_sha256=sha(HERE/'summary.json'),model_sha256=sha(HERE/'trained_model/freeze.json'),deployment_model_sha256=sha(HERE/'extension/deployment/freeze.json'),basis_sha256=sha(HERE/'extension/basis_cache.json'),source_sha256={p.name:sha(p) for p in HERE.glob('s*.py')},pdf_sha256={n:sha(report/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file()))
 assert v['study_allocated_bytes']<CAP
 write(HERE/'validation.json',v);(report/'factorized_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)

if __name__=='__main__':main()
