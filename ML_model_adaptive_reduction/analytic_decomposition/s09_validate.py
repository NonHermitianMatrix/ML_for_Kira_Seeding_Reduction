"""Validate frozen evidence, document the study, and rebuild both PDFs."""
from s01_common import *
import subprocess,statistics

def main():
 from s07_analyze import main as analyze
 from s08_document import main as document
 analyze();s=READ(HERE/'summary.json');p=READ(HERE/'test_protocol.json')
 assert s['requests']==len(p['cases'])==41
 assert all(sha(HERE/n)==v for n,v in p['runtime_sources'].items())
 assert sha(HERE/'basis_registry.json')==p['basis_sha256']
 assert sha(PREVIOUS/'trained_model/freeze.json')==p['prior_model_sha256'];assert sha(PREVIOUS/'trained_model/expert.json')==p['prior_expert_sha256']
 checks=0
 for c in p['cases']:
  ref=READ(HERE/'references'/(c['id']+'.json.gz'))
  for q in (HERE/'model_test').glob(c['id']+'_*.json.gz'):
   r=READ(q);ok,n=h.compare(r,ref) if ref['success'] else (False,0);assert ok==r['independently_verified'];checks+=n
 for group in s['comparisons'].values():
  for v in group.values():
   if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
 document()
 # Add current evidence checks to the global paper checker without weakening
 # any historical result or notes-preservation check.
 path=ROOT/'report/s01_check_paper.py';text=path.read_text();marker='    result=dict(general_model_test_complete=True'
 block='''    analytic=json.loads((HERE/'analytic_decomposition_data.json').read_text())
    assert analytic['complete'] and analytic['requests']==len(analytic['rows'])==41
    assert 'sec:analytic-results' in labels and 'app:analytic-decomposition' in labels
    for group in analytic['comparisons'].values():
        for value in group.values():
            if value['cases']:assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/analytic_decomposition/summary.json'
    if p.exists():assert json.loads(p.read_text())==analytic
'''
 if "analytic=json.loads((HERE/'analytic_decomposition_data.json')" not in text:path.write_text(text.replace(marker,block+marker))
 guide=(HERE/'README.md').read_text();guide=guide.split('The study is in progress.')[0].split('s07_analyze.py computes paired time ratios')[0]
 guide+='''s07_analyze.py computes paired time ratios, failed costs, and the comparison plot.
s08_document.py writes the paper and notes from the completed measurements.
s09_validate.py repeats exact coefficient comparisons, checks the frozen sources, builds both PDFs, and validates their citations and references.
Run s09_validate.py only after both test workers finish.

## Completed comparison

'''
 guide+=f"The combined application completes {s['totals']['learned']['verified']} of {s['requests']} requests in all three repetitions.\n"
 for group in ['all','analytic','ml_compatibility']:
  for m,v in s['comparisons'][group].items():
   if v['cases']:guide+=f"{group}, {m} control: {v['cases']} matched requests; time ratio {v['ratio']:.6f}; repetition interval {v['repeat_interval']}.\n"
 guide+='''
The analytic saving comes from the exact recurrence. The learned models retain their earlier weights.
The native control gets the same prepared master indices and old exact formulas, with native choices and the new recurrence disabled.
The fixed control uses the new recurrence and fixed ML-free choices.
The previous control runs the actual preceding hybrid application with its earlier master-index cache.
Its timer includes discovery when that cache lacks a structure. The matched native control receives the same new index set as the analytic method.
Master-index and reference preparation are separate from the supplied-basis timings.
No finite test establishes a speedup for every integral or a globally minimum time.

Use this command in a scheduled job:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/analytic_decomposition/s02_runtime.py --case CASE.json --output ML_model_adaptive_reduction/analytic_decomposition/requests/RESULT.json.gz --method learned
```

The application uses only the master indices in basis_registry.json and the earlier basis cache.
New families without a matching prepared basis use the preceding native discovery path.
The registry contains no reduction coefficients. references/ is for independent validation only.
For an analytic block, recurrence_states counts distinct index vectors and sector_inversions counts the small matrices solved. These counts do not prove a minimum operation count.
No output coefficient is reused across requests. Repeated identical blocks share work within a request.

Optional upstream PyTorch self-test executables were removed to recover storage.
The installed runtime libraries, Python modules, headers, and all model weights remain in place.
Reinstalling the same PyTorch package restores its optional upstream self-tests.
Git object compaction preserved project history. Storage receipts remain in the administrative tools folder.
'''
 (HERE/'README.md').write_text(guide)
 descriptions={'pilot':'Development checks of rational and symbolic coefficients against native Kira. These inputs do not enter reserved timing sums.','references':'Independent native or previously derived analytic references. These coefficients never enter application decisions.','requests':'Temporary application inputs and outputs. Completed jobs remove these files.','model_test':'One compressed record per method and repetition. complete_process_and_check_seconds includes process loading, reduction, cleanup, and exact comparison. independently_verified records the comparison result.','coverage':'One outcome for every requested case. Failed cases remain present.','logs':'Scheduler logs remain on Hoffman. Structured results and this guide are published.'}
 for folder,desc in descriptions.items():
  q=HERE/folder;q.mkdir(exist_ok=True);(q/'README.md').write_text('# '+folder.replace('_',' ').capitalize()+'\n\n'+desc+'\n\nRead ../README.md for the procedure, controls, and resource limits.\n')
 for name in ['README.md','ML_model_adaptive_reduction/README.md','report/README.md']:
  q=ROOT/name;t=q.read_text();heading='## Current exact and learned decomposition\n'
  if heading not in t:
   link='ML_model_adaptive_reduction/analytic_decomposition/README.md' if name=='README.md' else 'analytic_decomposition/README.md' if name.startswith('ML_model') else '../ML_model_adaptive_reduction/analytic_decomposition/README.md'
   t=heading+'\nThe current application adds an exact scalar one-loop recurrence to the frozen learned Kira workflow.\nRead [the method guide]('+link+') for the code, tests, and supported inputs.\nThe paper studies loop-integral decomposition into master integrals. The notes retain earlier methods and results.\n\n'+t;q.write_text(t)
 prior_guide=PREVIOUS/'README.md';prior_text=prior_guide.read_text()
 if '## Historical document receipt' not in prior_text:prior_guide.write_text('## Historical document receipt\n\nThe current application and paper are in the analytic_decomposition study.\nThis folder preserves the earlier hybrid experiment and its model weights.\nIts PDF hashes identify that earlier document version.\nUse ../analytic_decomposition/validation.json for the current paper and notes.\nKeep earlier document writers separate from the current report build.\n\n'+prior_text)
 plotguide=ROOT/'report/paper_figures/README.md';t=plotguide.read_text()
 if 'analytic_decomposition.pdf' not in t:plotguide.write_text(t+'\nanalytic_decomposition.pdf compares the combined method with matched native work and shows all first-attempt costs. Its message is the separate analytic benefit and the completion scope.\n')
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 v=dict(complete=True,coefficient_checks=checks,summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'test_protocol.json'),basis_sha256=sha(HERE/'basis_registry.json'),models_unchanged=True,source_sha256={q.name:sha(q) for q in HERE.glob('s0*.py')},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']})
 write(HERE/'validation.json',v);(ROOT/'report/analytic_decomposition_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
