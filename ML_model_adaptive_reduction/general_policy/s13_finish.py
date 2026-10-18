"""Complete application checks, scientific documents, and human-readable guides."""
from s00_common import *
import subprocess

def main():
 for base in [HERE,HERE/'refit']:
  for w in [0,1]:
   v=READ(base/('test_'+str(w)+'_complete.json'));assert v['complete'] and v['model_sha256']==inputs.sha(base/'trained_model/freeze.json')
 for script in ['s09_check_model.py','s12_application_checks.py','s05_analyze.py','s10_document.py']:
  subprocess.run([sys.executable,str(HERE/script)],check=True)
 if (HERE/'preparation/protocol.json').exists():
  if (HERE/'recovery/protocol.json').exists():
   subprocess.run([sys.executable,str(HERE/'s21_recovery.py'),'analyze'],check=True)
  for script in ['s17_analyze_preparation.py','s18_document_preparation.py','s19_finish_preparation.py']:
   subprocess.run([sys.executable,str(HERE/script)],check=True)
  subprocess.run([sys.executable,str(HERE/'s23_check_optional_basis.py')],check=True)
 summary=READ(HERE/'summary.json');m=READ(HERE/'refit/trained_model/freeze.json')
 for base,log in [(HERE,'train.log'),(HERE/'refit','refit.log')]:
  (base/'trained_model/training_diagnostics.txt').write_text((HERE/'logs'/log).read_text())
 readme='''# Shared structural cost model

This folder trains and tests a shared model for Kira seed choices.
The model uses the integral structure and target powers. It does not use family names or a per-family deployment rule.
The model predicts complete cost for ten seed configurations. Kira performs exact algebra and retries incomplete choices.

## Inputs and separation

Historical training costs come from `../learned_seed_bounds/training/` and `../portfolio_policy/training/`.
Historical validation costs remain separate. No earlier test measurement becomes a training label.
The distinct-mass vacuum benchmark family, nonplanar boxes, pentagons, and every loop order above three are excluded from fitting and selection.
The new grid defines 110 requests through twelve loops. Unsupported inputs and failures remain in the coverage records.
A prediction for an unsupported input is not a completed reduction.

## Model versions

`trained_model/` contains the initial fit. Its reserved profile is 1201.
An audit found inconsistent output scaling in the installed neural-network objective and gradient.
`refit/trained_model/` contains the corrected fit. Its fresh reserved profile is 1213.
The corrected loss passes a finite-difference gradient check.
Both trials remain available. Neither trial supplies training labels to the corrected fit.
The final tests keep the corrected weights, action set, and margin fixed.

## Run the code

Use the Hoffman scientific Python at `.tools/seed-model/venv/bin/python` from the project root.
Load GCC 9.5.0 and Python 3.9.6. Use `s04_job.sh` for cluster calculations.
The executable `.tools/kira-sector-storage/kira` comes from `../portfolio_policy/s06_build_sector_storage.py`.
Read that folder's guide before rebuilding the executable. Both new controls use the same bounded sector storage.
The wrapper uses the runtime in `../learned_seed_bounds/` and the exact scalar formula in `../massless_banana/`.
Keep at most two native comparison workers active. Each worker uses one Kira thread.
The scripts cap solver memory, temporary storage, and attempt time.
The full project must remain below 10 GB. Read `resource_plan.json` before new work.

1. Read `s00_common.py` for the inputs, structural features, physical holdouts, and storage guards.
2. Run `s01_train.py` for the initial model comparison. `s02_application.py` evaluates its saved parameters.
3. Run `s03_test.py 0` and `s03_test.py 1` after training to complete the initial grid.
4. Run `s06_refit.py` to check the corrected gradient and fit the final candidates from the same original inputs.
5. Run `s08_test.py 0` and `s08_test.py 1` after refitting. These use `s07_application.py` and the new grid.
6. Run `s09_check_model.py` to check index, loop-name, and target-order invariance.
7. Run `s12_application_checks.py` to check the public interface against independent coefficients.
8. Run `s05_analyze.py` to collect exact timing results and create plots.
9. Run `s10_document.py` to update the result text, abstract, conclusion, and notes.
10. Run `s13_finish.py` to repeat the required checks, update these guides, and build both documents.

`jobs.json` records the scheduler submissions. `logs/` contains local scheduler output.
Training diagnostics are also copied into the model folders and published.
Run the steps from the project root, using their paths inside this folder.

## Use the public interface

Run `s11_reduce.py --case INPUT.json --basis BASIS.json --output OUTPUT.json.gz` in the scientific Python environment.
The input contains `id`, `definition`, `targets`, and `size`. The basis is a JSON list of integral-index vectors.
The model needs no reference coefficients. The test runner compares exported coefficients afterward.
The public interface first checks the exact scalar massless two-point formula's physical assumptions.
For other supported inputs, the default uses the shared model only when its frozen validation score passes the deployment threshold.
Otherwise it uses native choices. Exact Kira recovery remains active.
Use `--method native` or `--method fixed` for matching controls. Use `--method learned` to test the frozen candidate explicitly.

## Interpret results

`summary.json` contains all outcomes, paired times, loop coverage, physical holdouts, and timing intervals.
`refit/coverage/` retains every requested case. Read it before using a speedup ratio.
`refit/model_test/` contains three rotated repeats of native, fixed, learned, and preceding applications.
Both main controls share the exact bounded-sector implementation. The preceding application retains its earlier complete method.
Master discovery and the enlarged-region reference check precede the supplied-basis timer and have separate totals.
A reported timing ratio includes imports, prediction, equation generation, algebra, checks, retries, output, and process exit.
The native interface still rejects more than 31 integral coordinates. This is not a mathematical limit on IBP.
The exact scalar checks through twelve loops use no learned decisions and do not establish general high-loop scattering reduction.

'''
 overall=summary['overall'];readme+=f"The final matched set contains {overall['cases']} requests. Learned/native time ratio: {overall['ratios']['native']:.6f}. Learned/fixed ratio: {overall['ratios']['fixed']:.6f}.\n"
 if (HERE/'preparation/summary.json').exists():
  readme+='\nRead [preparation/README.md](preparation/README.md) for the cost-and-failure model and the complete preparation comparison. Scripts s14 through s19 implement this extension. Both models and the ML-off controls remain available.\n'
  readme+='\nThe current public command is `s22_reduce.py --case INPUT.json --output OUTPUT.json.gz`. Add `--basis BASIS.json` when a basis is available. It first checks the exact scalar formula. With a supplied basis, it uses the validation-approved shared model. Without a basis, it follows preparation/deployment.json and includes discovery and recovery. That deployment decision follows the completed candidate comparison; it has no separate timing claim. Use `--method learned` or `--method native` to set the decision explicitly. The alternative cost-and-risk model remains available through s20. `s23_check_optional_basis.py` checks this interface without giving it reference answers.\n'
 (HERE/'README.md').write_text(readme)
 guides={
 'trained_model':'Saved candidate weights, fixed settings, source records, selection scores, and diagnostics. The initial version uses the installed multi-output training loss. Read the corrected fit under refit/trained_model before deployment.',
 'refit':'The corrected fit and fresh reserved test. Training and validation remain the original historical split. Profile 1213 is reserved. The gradient check explains the correction.',
 'refit/trained_model':'The corrected trained candidates and frozen selection. freeze.json records the weights, training sources, candidate scores, and global decision margin. selection.json is the compact summary. No family-name input or per-family gate is used.',
 'references':'Initial exact references and enlarged-region checks. Failures remain stored. Reference coefficients enter only the final answer comparison.',
 'refit/references':'Fresh exact references and enlarged-region checks for the corrected-model grid. Failures remain stored. The repeated applications receive a common master basis.',
 'model_test':'Initial trial measurements. Each successful matched request has three rotated repeats. Complete process time includes exact checks and recovery.',
 'refit/model_test':'Final measurements from the frozen corrected model. Native, fixed, learned, and preceding controls use the same physical targets. Compare matching requests and retain failed cases.',
 'coverage':'One initial-trial outcome per requested input. A score for an unsupported input does not count as a native reduction.',
 'refit/coverage':'One corrected-model outcome per input. Each record gives loop order, coordinate count, holdout membership, and completion status.',
 'requests':'Temporary input requests for the initial worker. Completed calculations remove these files.',
 'refit/requests':'Temporary input requests for the final worker. Completed calculations remove these files.',
 'application_checks':'Public-interface inputs, bases, exact outputs, and independent checks. Scalar checks cover loops one through twelve. Native public checks use a predefined subset of completed reserved requests.',
 'logs':'Scheduler output stays on Hoffman. The model folders retain published training diagnostics. Scientific result records contain errors and failures.'}
 for name,body in guides.items():
  folder=HERE/name;folder.mkdir(parents=True,exist_ok=True);(folder/'README.md').write_text('# '+name.split('/')[-1].replace('_',' ').capitalize()+'\n\n'+body+'\n\nRead the main [guide]('+('../'*len(Path(name).parts))+'README.md) for the producer, inputs, and run order.\n')
 # Every new data folder receives a guide; do not alter earlier experiments.
 for folder in sorted([p for p in HERE.rglob('*') if p.is_dir() and '__pycache__' not in p.parts]):
  if not (folder/'README.md').exists():(folder/'README.md').write_text('# Supporting records\n\nThese records support the shared cost comparison. Read the general_policy README for the inputs, producer, and limits.\n')
 for n in ['report.tex','paper_abstract.tex','paper_conclusion.tex','general_policy_results.tex']:
  assert 'PROVISIONAL' not in (ROOT/'report'/n).read_text()
 figure_guide=ROOT/'report/paper_figures/README.md';old=figure_guide.read_text();new='''## Current concise-paper figures

`paper_local_results.pdf` shows the retained seed and equation savings and the unresolved row-policy result.
Each row uses its own stated workload and control. The ratios cannot be multiplied.
`general_policy_times.pdf` compares the corrected shared model with native and fixed choices.
It separates training domains from physical holdouts and shows paired repetition intervals.
`general_policy_coverage.pdf` shows every requested loop order and completion category.
Unsupported inputs and failed references remain visible.
The producer is `ML_model_adaptive_reduction/general_policy/s05_analyze.py`.

''';figure_guide.write_text(old if old.startswith(new) else new+old)
 for name in ['README.md','ML_model_adaptive_reduction/README.md']:
  p=ROOT/name;text=p.read_text();prefix='''<!-- BEGIN SHARED STRUCTURAL MODEL -->
The current shared cost model is in `ML_model_adaptive_reduction/general_policy/`.
It uses structural features and tests whole-family and higher-loop transfer.
Read its guide and coverage records for the measured domain and failures.
The concise paper is `report/report.pdf`; the detailed history is `report/notes.pdf`.
<!-- END SHARED STRUCTURAL MODEL -->

'''
  p.write_text(text if '<!-- BEGIN SHARED STRUCTURAL MODEL -->' in text else prefix+text)
 env=dict(os.environ,XDG_CACHE_HOME=str(ROOT/'.tools/cache'))
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True,env=env,timeout=540)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],check=True)
 files=[p for p in HERE.glob('s*.py')]+[HERE/'s04_job.sh']
 evidence=dict(complete=True,model_sha256=inputs.sha(HERE/'refit/trained_model/freeze.json'),protocol_sha256=inputs.sha(HERE/'refit/protocol.json'),summary_sha256=inputs.sha(HERE/'summary.json'),source_sha256={p.name:inputs.sha(p) for p in files},pdf_sha256={n:inputs.sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},all_matched_results_exact=True,coverage_requests=summary['requested'],matched=overall['cases'],invariance=READ(HERE/'invariance_check.json'),application_checks=READ(HERE/'application_checks/summary.json'))
 if (HERE/'preparation/summary.json').exists():
  evidence['preparation']={n:inputs.sha(HERE/'preparation'/n) for n in ['summary.json','protocol.json','basis_cache.json','deployment.json','trained_model/freeze.json']}
  evidence['preparation_matched_exact']=READ(HERE/'preparation/summary.json')['all_same_basis_matched_outputs_exact']
 if (HERE/'recovery/summary.json').exists():
  evidence['recovery']={n:inputs.sha(HERE/'recovery'/n) for n in ['summary.json','protocol.json']}
  evidence['recovery_matched_exact']=READ(HERE/'recovery/summary.json')['all_matched_exact']
  evidence['optional_basis_checks']=READ(HERE/'optional_basis_checks/summary.json')
 write(HERE/'validation.json',evidence);write(ROOT/'report/general_policy_validation.json',evidence)
 print('FINISHED',overall['cases'],flush=True)
if __name__=='__main__':main()
