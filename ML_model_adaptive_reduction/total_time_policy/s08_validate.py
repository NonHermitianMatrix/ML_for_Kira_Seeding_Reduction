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
The study cap is 16 MiB. Each native call has a 32 MiB scratch cap and a 45-second limit.
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

The existing factorized_policy folder supplies exact formulas, block splitting, and the checked basis cache.
The learned_seed_bounds folder supplies the native Kira runner. Its learned algebra switches stay off here.
Python needs NumPy, SymPy, and Matplotlib. The existing project virtual environment supplies them.
The build uses the existing bounded Kira executable, Fermat, and Tectonic installation.

s09_native_control.py adds unadjusted native bounds to the initial six candidates before fitting.

## Execute

From the repository root, submit two collection workers:

```sh
qsub ML_model_adaptive_reduction/total_time_policy/s04_job.sh s02_collect.py 0
qsub ML_model_adaptive_reduction/total_time_policy/s04_job.sh s02_collect.py 1
```

Wait for both completion receipts. Run both s09_native_control.py workers. Then submit s03_train.py with the same wrapper.
Then submit s05_test.py with worker arguments 0 and 1. Run s08_validate.py after both test receipts exist.
Existing records are reused. Do not delete claims or replace frozen files during a run.
Use a new study directory for a changed model after reserved testing.

Run the integrated application from a scheduled job:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/total_time_policy/s01_runtime.py --case CASE.json --output RESULT.json.gz --method learned
```

Use `raw_native` to disable the selector and use the original native bounds.
Use `native` for bounds enlarged to contain the supplied master basis. Use `fixed` for the validation-selected common setting.
Both controls retain identical exact formulas, basis checks, and recovery code.
The test method `previous` runs factorized_policy/s08_reduce.py without changing that historical application.
CASE.json follows the existing definition, targets, size, split, and topology_group fields.
The output lists exact component master expansions, native attempts, actions, checks, and elapsed time.
A product remains factored. Different loop blocks may use different methods.

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
A range guard sends unsupported features to native settings. This guard does not certify generalization.

The cached master basis contains indices only. Coefficients are recomputed at the current parameters.
Reference preparation, earlier basis calibration, and collection of training labels are separate from deployment timing.
The new timed application includes imports, prediction, equation generation, algebra, recovery, output, and exact checks.
The native controls use the same bounded modified executable. They are not an unmodified Kira distribution.

## Scope and results

'''
 text+=f"The reserved grid has {s['requested']} requests. The learned application verifies {s['totals']['learned']['verified_requests']} in all three repetitions.\n"
 for m in ['previous','native','fixed']:
  v=s['comparisons']['all'][m]
  if v['cases']:text+=f"On {v['cases']} matched completions, the learned/{m} total-time ratio is {v['ratio']:.6f}.\n"
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
  block=start+'\n\nThe current complete-time selector is in ML_model_adaptive_reduction/total_time_policy/.\nRead its README for the integrated command, exact routes, trained model, controls, and limits.\nThe report and notes include the frozen comparison and retain failed outcomes.\n\n'+end
  if start in t:t=t[:t.index(start)]+block+t[t.index(end)+len(end):]
  else:t+='\n\n'+block+'\n'
  p.write_text(t)

def main():
 analysis=inputs.module('total_time_analysis',HERE/'s06_analyze.py');docs=inputs.module('total_time_document',HERE/'s07_document.py')
 analysis.main();s=READ(HERE/'summary.json');f=READ(HERE/'trained_model/freeze.json');p=READ(HERE/'test_protocol.json')
 assert s['model_sha256']==p['model_sha256']==sha(HERE/'trained_model/freeze.json')
 assert all(sha(HERE/n)==h for n,h in p['sources'].items())
 assert sha(BLOCK/'extension/basis_cache.json')==p['basis_sha256']
 assert all(sha(BLOCK/n)==h for n,h in p['previous_sources'].items())
 assert sum(v['requested'] for v in s['by_loop'].values())==s['requested']
 train=READ(HERE/'protocol.json');ids=[{c['id'] for c in train[k]} for k in ['training','validation']]+[{c['id'] for c in p['cases']}];assert all(not ids[i]&ids[j] for i in range(3) for j in range(i))
 assert all('pentagon' not in c['topology_group'] for k in ['training','validation'] for c in train[k])
 for group in s['comparisons'].values():
  for m,v in group.items():
   if v['cases']:
    assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    assert all(r['complete']['learned'] and r['complete'][m] for r in s['rows'] if r['case'] in v['case_ids'])
 # A meaningful small check of the cost objective and action rule.
 import numpy as np
 model=inputs.module('total_time_model_check',HERE/'s03_train.py')
 X=np.array([[0.],[0.],[1.],[1.]]);C=np.array([[1.,8.],[1.,8.],[8.,1.],[8.,1.]])
 tree=model.fit_tree(X,C,np.arange(4),1,2,np.random.RandomState(0));assert np.argmin(model.leaf(tree,[0.])['cost'])==0 and np.argmin(model.leaf(tree,[1.])['cost'])==1
 docs.main();guides(s)
 report=ROOT/'report';checker=report/'s01_check_paper.py';t=checker.read_text();marker='    result=dict(general_model_test_complete=True'
 if "total_time=json.loads" not in t:
  extra="""    total_time=json.loads((HERE/'total_time_data.json').read_text())
    assert total_time['complete'] and total_time['requested']==len(total_time['rows'])
    assert 'sec:total-time' in labels and 'app:total-time' in labels
    for group in total_time['comparisons'].values():
        for v in group.values():
            if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/total_time_policy/summary.json'
    if q.exists():assert json.loads(q.read_text())==total_time
"""
  assert marker in t;t=t.replace(marker,extra+marker);checker.write_text(t)
 subprocess.run(['make','-C',str(report),'all'],check=True,timeout=600)
 subprocess.run([sys.executable,str(checker)],check=True,timeout=180)
 v=dict(complete=True,all_matched_results_exact=True,summary_sha256=sha(HERE/'summary.json'),model_sha256=sha(HERE/'trained_model/freeze.json'),protocol_sha256=sha(HERE/'test_protocol.json'),source_sha256={p.name:sha(p) for p in HERE.glob('s*.py')},pdf_sha256={n:sha(report/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file()))
 assert v['study_allocated_bytes']<CAP
 write(HERE/'validation.json',v);(report/'total_time_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
