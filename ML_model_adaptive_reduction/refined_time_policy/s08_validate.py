"""Validate the frozen evidence, write guides, and build both documents."""
from s00_cost_common import *
import subprocess

def guides(s):
 f=READ(HERE/'trained_model/freeze.json')
 text='''# Complete-time Kira selection

This folder trains a model to choose a Kira seed setting from complete reduction time.
The application first applies exact formulas and splits independent loop blocks.
It uses the model only for the remaining native reductions within the trained feature ranges.
Kira computes exact coefficients. A basis check can trigger recovery.

Run all native calculations on scheduled Hoffman compute nodes. Use no more than two workers.
Keep data and model weights on Hoffman and GitHub. Do not copy them to the local report folder.
The persistent study cap is 16 MiB. Two application workers share a separate 16 MiB temporary output reserve.
Each native call has a 32 MiB scratch cap and a 45-second limit.
The request limit is 110 seconds. The application-process limit is 125 seconds.
The native process tree must stay below 5200 MiB RSS. The job reserves 8 GiB.
The combined project limit remains 10 GB. Read resource_plan.json before expansion.

## Code and order

1. s00_cost_common.py defines paths, resource guards, physical features, and basis-compatible seed bounds.
2. s01_runtime.py is the integrated application. It accepts a target case and writes the exact result.
3. s02_collect.py defines the training and validation cases. It records each candidate time and exact check.
4. s03_train.py fits cost-sensitive trees and forests. It selects the model and fixed control on validation only.
5. s04_job.sh loads the required modules and starts one scheduled worker.
6. s05_test.py freezes the test protocol and measures four methods on fresh inputs.
7. s06_analyze.py checks completion and computes matched ratios, attempt costs, and the report figure.
8. s07_document.py writes the current paper sections and preserves earlier evidence in the notes.
9. s08_validate.py checks the evidence, writes these guides, builds both PDFs, and checks citations and references.
10. s09_check_storage.py checks concurrent storage accounting, replacement, removal, and recovery after an interrupted write.

The existing factorized_policy folder supplies exact formulas, block splitting, and the checked basis cache.
The learned_seed_bounds folder supplies the native Kira runner. Its learned algebra switches stay off here.
Python needs NumPy, SymPy, and Matplotlib. The existing project virtual environment supplies them.
The build uses the existing bounded Kira executable, Fermat, and Tectonic installation.

## Execute

From the repository root, submit two collection workers:

```sh
qsub ML_model_adaptive_reduction/refined_time_policy/s04_job.sh s02_collect.py 0
qsub ML_model_adaptive_reduction/refined_time_policy/s04_job.sh s02_collect.py 1
```

Wait for both completion receipts. Then submit s03_train.py with the same wrapper.
Then submit s05_test.py with worker arguments 0 and 1. Run s08_validate.py after both test receipts exist.
Existing records are reused. Do not delete claims or replace frozen files during a run.
Use a new study directory for a changed model after reserved testing.

Run the integrated application from a scheduled job:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/refined_time_policy/s01_runtime.py --case CASE.json --output ML_model_adaptive_reduction/refined_time_policy/requests/RESULT.json.gz --method learned
```

Use `raw_native` to disable the selector and use the original native bounds.
Use `native` for bounds enlarged to contain the supplied master basis. Use `fixed` for the validation-selected common setting.
Both controls retain identical exact formulas, basis checks, and recovery code.
The test method `previous` runs factorized_policy/s08_reduce.py without changing that historical application.
CASE.json follows the existing definition, targets, size, split, and topology_group fields.
The output lists exact component master expansions, native attempts, actions, checks, and elapsed time.
A product remains factored. Different loop blocks may use different methods.
Output files must stay inside this study folder. The writer uses a locked allocation counter.
It scans persistent study files only on first use or after an interrupted write. It reserves 2 MiB for guides and logs.
Temporary requests and outputs use their separate reserve. Inputs are limited to 256 KiB; each output is limited to 3 MiB.
The local counter and lock are not published. A fresh copy creates its own counter.

## Data and timing

protocol.json records the training and validation splits. test_protocol.json records the frozen test inputs and source checks.
training/ and validation/ store action measurements. references/ stores independent coefficient checks.
trained_model/freeze.json stores the selected tree or forest. fixed.json stores the common control.
model_test/ stores every timed reserved attempt. coverage/ records every requested outcome.
claims/ prevents two workers from measuring the same request. logs/ contains scheduler output.
summary.json and validation.json connect the final measurements to the documents.

The training loss sums complete process and exact-check time. Failed completions receive a declared 220-second penalty.
The results use measured seconds and report failures separately. They do not substitute training penalties into speedups.
The model uses 51 physical and basis features. It receives no family identifier or parameter-profile identifier.
The pentagon graph is absent from training and validation. Other tests use new parameters and additional target shapes.
Model selection needs at least 1.5 percent less validation cost than the fixed candidate to enable prediction.
When prediction is enabled, a range guard sends unsupported features to native settings. It does not certify generalization.

The cached master basis contains indices only. Coefficients are recomputed at the current parameters.
Reference preparation, earlier basis calibration, and collection of training labels are separate from deployment timing.
The new timed application includes imports, prediction, equation generation, algebra, recovery, output, and exact checks.
The native controls use the same bounded modified executable. They are not an unmodified Kira distribution.

## Scope and results

'''
 text+=f"The reserved grid has {s['requested']} requests. The learned application verifies {s['totals']['learned']['verified_requests']} in all three repetitions.\n"
 for m in ['previous','native','fixed']:
  v=s['comparisons']['all'][m]
  if v['cases']:text+=f"On {v['cases']} matched completions, the learned/{m} refined-time ratio is {v['ratio']:.6f}.\n"
 text+='''
Read summary.json for ML-only comparisons, repetition intervals, failed calls, first-pass totals, and per-loop coverage.
The coupled native cases reach three loops. The analytic families and independent products reach thirteen loops.
Independent products contain blocks with at most two loops. These results do not cover all high-loop scattering integrals.
The exact formulas require their stated mass, momentum, and numerator structures. They do not evaluate the master integrals.
No measured result proves a globally fastest reduction or an optimal path.
'''
 (HERE/'README.md').write_text(text)
 descriptions={'training':'Training candidate measurements and the combined training rows. Read s02_collect.py and s03_train.py.','validation':'Independent model-selection timings. These inputs select settings before reserved tests.','trained_model':'Frozen fitted model, selected fixed control, and selection results. Read s03_train.py.','model_test':'Reserved application attempts with exact coefficient checks. Read s05_test.py and s06_analyze.py.','references':'Independent exact coefficient references. The runtime receives basis indices but does not read these coefficients.','coverage':'Requested outcomes and completion status. Keep unsuccessful cases. Read s02_collect.py and s05_test.py.','claims':'Exclusive worker claims. Each claim identifies one requested calculation. Do not remove active claims.','logs':'Scheduler logs. Scientific results are stored in the structured measurement files.','requests':'Temporary application inputs. This folder is empty after completed workers.','figures':'Study plots. The paper figure is also stored in report/paper_figures/.'}
 for p in [HERE]+[q for q in HERE.rglob('*') if q.is_dir() and '__pycache__' not in q.parts]:
  if p==HERE:continue
  branch=p.relative_to(HERE).parts[0]
  (p/'README.md').write_text(descriptions.get(branch,'Supporting records for the complete-time comparison.')+'\n\nRead the parent study README for inputs, outputs, execution order, dependencies, and limits.\nKeep these data on Hoffman and GitHub.\n')
 for p in [ROOT/'README.md',ROOT/'ML_model_adaptive_reduction/README.md',ROOT/'report/README.md']:
  t=p.read_text();start='<!-- BEGIN COMPLETE TIME SELECTION -->';end='<!-- END COMPLETE TIME SELECTION -->'
  block=start+'\n\nThe current complete-time selector is in ML_model_adaptive_reduction/refined_time_policy/.\nRead its README for the integrated command, exact routes, trained model, controls, and limits.\nThe report and notes include the frozen comparison and retain failed outcomes.\n\n'+end
  if start in t:t=t[:t.index(start)]+t[t.index(end)+len(end):]
  t=t.replace('Use `ML_model_adaptive_reduction/factorized_policy/s08_reduce.py` for the checked block extension.','The earlier checked block extension uses `ML_model_adaptive_reduction/factorized_policy/s08_reduce.py`.')
  t=t.replace('Use `factorized_policy/s13_document.py` for the current extension.','Use `../ML_model_adaptive_reduction/refined_time_policy/s08_validate.py` for the current paper and notes.')
  p.write_text(block+'\n\n'+t.lstrip())
 previous=ROOT/'ML_model_adaptive_reduction/total_time_policy/README.md';t=previous.read_text()
 if '## Later revision' not in t:
  previous.write_text(t+'\n## Later revision\n\nThis folder preserves the seven-candidate comparison.\nUse ../refined_time_policy/ for the current application and its fresh comparison.\nThe PDF file checks in this folder describe the documents before that later revision.\nUse ../refined_time_policy/validation.json to check the current PDFs.\nOlder document writers can replace current prose.\n')
 p=ROOT/'report/README.md';t=p.read_text()
 if '## Complete-time method selection' not in t:
  t+='\n## Complete-time method selection\n\nrefined_time_results.tex gives the current nine-candidate method and reserved results.\nrefined_time_appendix.tex derives the tighter master-basis cutoff.\ntotal_time_appendix.tex gives the shared cost objective, features, and target definitions.\nrefined_time_data.json contains the compact checked measurements.\nrefined_time_validation.json records the checks and current PDF file checks.\nThe notes preserve total_time_results.tex, its earlier comparison, and both detailed parameter records.\n'
 p.write_text(t)
 p=ROOT/'report/paper_figures/README.md';t=p.read_text()
 if '`refined_time_selection.pdf`' not in t:
  t+='\n`refined_time_selection.pdf` compares the current method with native, fixed, and previous choices.\nIts left panel shows matched total-time ratios and repetition variation.\nIts right panel includes one attempt for every request and gives completion counts.\n`total_time_selection.pdf` gives the same comparison for the earlier seven-candidate study in the notes.\n'
 p.write_text(t)

def main():
 analysis=inputs.module('refined_time_analysis',HERE/'s06_analyze.py');docs=inputs.module('refined_time_document',HERE/'s07_document.py')
 analysis.main();s=READ(HERE/'summary.json');f=READ(HERE/'trained_model/freeze.json');p=READ(HERE/'test_protocol.json')
 assert s['model_sha256']==p['model_sha256']==sha(HERE/'trained_model/freeze.json')
 assert all(sha(HERE/n)==h for n,h in p['sources'].items())
 assert sha(BLOCK/'extension/basis_cache.json')==p['basis_sha256']
 assert all(sha(BLOCK/n)==h for n,h in p['previous_sources'].items())
 assert sum(v['requested'] for v in s['by_loop'].values())==s['requested']
 train=READ(HERE/'protocol.json');ids=[{c['id'] for c in train[k]} for k in ['training','validation']]+[{c['id'] for c in p['cases']}];assert all(not ids[i]&ids[j] for i in range(3) for j in range(i))
 assert all('pentagon' not in c['topology_group'] for k in ['training','validation'] for c in train[k])
 # Check the derived bound against Kira's cutoff inequality, including ranks
 # admitted by the constant term or an explicit sector limit.
 cutoff_checks=0
 for lines in range(1,7):
  for rank in range(6):
   for explicit in range(6):
    for proposed in range(-2,9):
     bound=min(proposed,lines+1-rank) if rank>max(1,explicit) else proposed
     assert rank<=max(1,lines-bound+1,explicit)
     if bound<proposed:assert rank>max(1,lines-(bound+1)+1,explicit)
     cutoff_checks+=1
 cache=READ(BLOCK/'extension/basis_cache.json');basis_settings_checked=0
 for case in train['training']+train['validation']+p['cases']:
  for block in split_blocks(case):
   case_block=block['case'];basis=basis_for(case_block,cache)
   if basis is None:continue
   for action in ACTIONS:
    if action=='raw_native':continue
    bounds,truncation=settings(case_block,action,basis);basis_settings_checked+=1
    for master in basis:
     positive=sum(max(a,0) for a in master);rank=sum(max(-a,0) for a in master);dots=sum(max(a-1,0) for a in master)
     assert all(v<=b for v,b in zip([positive,rank,dots],bounds))
     if truncation is not None:
      sector=sum(1<<i for i,a in enumerate(master) if a>0)
      explicit=bounds[1] if sector in case_block['definition']['top_level_sectors'] else 0
      assert rank<=max(1,sum(a>0 for a in master)-truncation+1,explicit)
 for group in s['comparisons'].values():
  for m,v in group.items():
   if v['cases']:
    assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    assert all(r['complete']['learned'] and r['complete'][m] for r in s['rows'] if r['case'] in v['case_ids'])
 assert basis_settings_checked>0
 # A meaningful small check of the cost objective and action rule.
 import numpy as np
 model=inputs.module('refined_time_model_check',HERE/'s03_train.py')
 X=np.array([[0.],[0.],[1.],[1.]]);C=np.array([[1.,8.],[1.,8.],[8.,1.],[8.,1.]])
 tree=model.fit_tree(X,C,np.arange(4),1,2,np.random.RandomState(0));assert np.argmin(model.leaf(tree,[0.])['cost'])==0 and np.argmin(model.leaf(tree,[1.])['cost'])==1
 subprocess.run([sys.executable,str(HERE/'s09_check_storage.py')],check=True,timeout=60)
 docs.main();guides(s)
 report=ROOT/'report';checker=report/'s01_check_paper.py';t=checker.read_text();marker='    result=dict(general_model_test_complete=True'
 if "refined_time=json.loads" not in t:
  extra="""    refined_time=json.loads((HERE/'refined_time_data.json').read_text())
    assert refined_time['complete'] and refined_time['requested']==len(refined_time['rows'])
    assert 'sec:refined-time' in labels and 'app:refined-time' in labels
    for group in refined_time['comparisons'].values():
        for v in group.values():
            if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/refined_time_policy/summary.json'
    if q.exists():assert json.loads(q.read_text())==refined_time
"""
  assert marker in t;t=t.replace(marker,extra+marker);checker.write_text(t)
 subprocess.run(['make','-C',str(report),'all'],check=True,timeout=600)
 subprocess.run([sys.executable,str(checker)],check=True,timeout=180)
 v=dict(complete=True,all_matched_results_exact=True,cutoff_inequalities_checked=cutoff_checks,basis_settings_checked=basis_settings_checked,summary_sha256=sha(HERE/'summary.json'),model_sha256=sha(HERE/'trained_model/freeze.json'),protocol_sha256=sha(HERE/'test_protocol.json'),source_sha256={p.name:sha(p) for p in HERE.glob('s*.py')},pdf_sha256={n:sha(report/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file()))
 assert v['study_allocated_bytes']<CAP
 write(HERE/'validation.json',v);(report/'refined_time_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
