"""Write folder guides from the completed measured study."""
import json,re
from s00_inputs import HERE,ROOT
def write(p,s):p.write_text(s.rstrip()+'\n')
def block(p,text):
 s=p.read_text();s=re.sub(r'\n<!-- BEGIN LEARNED SEED BOUNDS -->.*?<!-- END LEARNED SEED BOUNDS -->\n','\n',s,flags=re.S)
 write(p,s+'\n<!-- BEGIN LEARNED SEED BOUNDS -->\n'+text+'\n<!-- END LEARNED SEED BOUNDS -->')
def main():
 d=json.loads((HERE/'summary.json').read_text());fit=json.loads((HERE/'trained_model/selection.json').read_text())
 text=f'''# Learned seed bounds

This study selects seed limits before Kira generates IBP equations.
IBP means integration by parts.
A seed is an integral index vector used to generate these identities.
The model predicts the complete cost of ten settings.
It uses the target indices and the graph structure.
It receives no answer coefficients.
Kira performs the exact algebra and checks the supplied master basis.
An insufficient first choice triggers native bounds and then expanded bounds.

The selected model is `{d['model']}`.
The test has {d['matched']} matched nontrivial batches.
The sum of their median times is {d['totals']['native']:.6f} s for native bounds.
It is {d['totals']['fixed']:.6f} s for the tuned fixed control.
It is {d['totals']['learned']:.6f} s for the learned choice.
The learned-to-control ratios are {d['ratios']['native']:.6f} and {d['ratios']['fixed']:.6f}.
A ratio below one means less time.
The interval against tuned fixed settings includes equal time.
The extra learned gain is not reliable on this test.
Read `summary.json` for each graph, failed requests, and timing intervals.
The controls use no learned seed, row, or equation choices.
All methods use the same exact executable.

## Scope

The inputs use ten graph structures at one through four loops.
Kinematic values are rational numbers. The dimension remains symbolic.
Training, validation, and test use separate parameter profiles.
They share graph structures and target patterns.
Some target patterns coincide when no auxiliary numerator exists.
The test does not establish performance for arbitrary new graphs.
The timed reduction starts with a supplied master basis.
It includes equation generation, algebra, parameter loading, prediction, checks, and retries.
The repeated timer excludes initial Python imports and reference construction.
A low score changes the seed choice. Kira checks the resulting reduction.
It reports failure if the bounded recovery attempts do not finish.

## Use the fitted model

Run from the project root in a scheduled Hoffman job.
Supply a case JSON file and a basis JSON file.
The case schema matches an entry in `protocol.json`.
The basis is a list of integer index vectors.
Use the same family and index length for targets and masters.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/learned_seed_bounds/s01_runtime.py --case CASE.json --basis BASIS.json --output RESULT.json.gz --method learned
```

`native` and `fixed` select the two controls.
`learned` uses the saved model and the domain check.
Unknown structures or target complexity outside the saved ranges use native bounds.
The guard checks target count, maximum dots, rank, absolute index, and positive-index sum.
It allows target positions and mean loop-incidence features to change.
The result contains the chosen action, all attempts, times, and exact coefficients.
The application does not require reference coefficients.
The test supplies them only to the check after each reduction.

## Reproduce the study

1. Read `resource_plan.json` and `protocol.json`.
2. Run `s02_development.py` for the saved development comparison.
3. Run `s04_collect.py` for training and validation cost records.
4. Run `s05_train.py` to fit and select the model.
5. Run `s06_test.py` for the frozen reserved comparison.
6. Run `s08_analyze.py` for the summary and plots.
7. Run `s13_finish.py` for the final checks, guides, and documents.

Use `qsub s03_job.sh SCRIPT.py` from the project root with the full script path for the job wrapper.
For example, use `qsub ML_model_adaptive_reduction/learned_seed_bounds/s03_job.sh s04_collect.py`.
The collector resumes from complete result files.
Do not change a frozen model and reuse its test files.
Use a new folder and new reserved inputs for a changed scientific method.

## Code and records

- `s00_inputs.py` defines physical families, target patterns, features, and seed settings.
- `s01_runtime.py` runs the exact reduction and the optional learned choice.
- `s02_development.py` checks candidate settings on development inputs.
- `s03_job.sh` sets scheduler, thread, and memory limits.
- `s04_collect.py` fixes the split and collects complete cost labels.
- `s05_train.py` compares 30 tree and neural models and four decision gates.
- `s06_test.py` rotates three methods through five reserved repetitions.
- `s07_pipeline.py` runs fitting and testing in separate processes.
- `s08_analyze.py` writes checked timing summaries and two figures.
- `s09_report.py` writes the scientific description in both documents.
- `s10_secondary.py` checks fresh application launches against the previous application.
- `s11_readmes.py` writes these folder guides.
- `s12_audit.py` checks saved coefficients, split integrity, and control settings.
- `s13_finish.py` completes analysis, documentation, and PDF checks.
- `protocol.json` fixes the inputs, controls, limits, and primary comparison.
- `resource_plan.json` records the storage reserve and job limits.
- `baseline_basis_check.json` records the source check of early master admission.
- `jobs.json` records scheduler job numbers.
- `summary.json` records all test outcomes and matched aggregate times.
- `validation.json` records the final publication checks.
- Log files record progress and failures.

Child folders contain development records, references, training costs, validation costs, the fitted model, and reserved tests.
Each child folder has its own guide.
The code depends on the existing exact driver `../s23_parametric_runner.py` and `.tools/kira-parametric/kira`.
Fitting uses the existing NumPy and scikit-learn environment.
Analysis uses Matplotlib. Exact coefficient checks use SymPy when needed.
Live prediction uses Python and the saved parameters. It does not load scikit-learn.

## Limits

Use one project job with two allocated cores and 8 GiB of memory.
Each Kira attempt uses one worker.
The address-space limit is 6 GiB. The process-tree limit is 5,200 MiB.
Each attempt has a 32 MiB scratch limit and a 90 s allowance.
Reference attempts have a 120 s allowance.
The driver reserves ten seconds for parsing and cleanup.
The study retains at most 24 MiB of result data.
Keep the complete project below 10,000,000,000 bytes.
Keep generated research data on Hoffman and GitHub.
The report and notes also have local copies.
'''
 write(HERE/'README.md',text)
 for name,purpose in dict(development='Candidate checks before the study was fixed.',references='Exact reference reductions and checks with a larger numerator bound.',training='Measured candidate costs for fitting.',validation='Measured candidate costs for model and gate selection.',trained_model='Saved parameters and the model-selection record.',model_test='Reserved repeated comparisons after model selection.',application_test='Fresh-process comparisons with the previous published application.').items():
  p=HERE/name;p.mkdir(exist_ok=True)
  s='# '+name.replace('_',' ').capitalize()+'\n\n'+purpose+'\nRead [the parent guide](../README.md) for commands, limits, and the full method.\n'
  if name=='trained_model':s+='\n`freeze.json` contains the selected parameters, feature names, domain limits, and provenance.\n`fixed.json` contains only fixed action names. It contains no model weights.\n`selection.json` contains all candidate validation scores and fit settings.\nThe runtime reads these files with `s01_runtime.py`.\nDo not change them after the reserved test.\n'
  else:s+='\nEach compressed JSON record stores a request, its timing, and its exact result.\nTraining and test records include every recovery attempt.\nA reference record stores the common basis and comparison coefficients.\nThe runtime reads compressed records without keeping an uncompressed copy.\nCompletion files mark finished stages.\nExclusion records retain failed reference checks.\nEquivalent training configurations can point to the same measured record.\nSuch aliases carry the field `identical_configuration_from`.\nThey are not extra timing measurements.\n'
  write(p/'README.md',s)
 block(ROOT/'ML_model_adaptive_reduction/README.md','Read [learned seed bounds](learned_seed_bounds/README.md) for the new cost-trained comparison.\nIts native and fixed controls disable every earlier model.\nRead its domain limits before use.\nThe earlier portfolio remains available for comparison.')
 p=ROOT/'ML_model_adaptive_reduction/README.md';s=p.read_text()
 s=s.replace('The current interface is `s24_parametric_runtime.py`.','The previous interface is `s24_parametric_runtime.py`.')
 s=s.replace('Use [the current portfolio guide](selective_expansion/README.md) for the final model and application.','Use [the earlier portfolio guide](selective_expansion/README.md) for that model and application.')
 s=s.replace('The current entry point is `s17_reduce.py`.','The earlier entry point is `s17_reduce.py`.')
 match=re.search(r'<!-- BEGIN LEARNED SEED BOUNDS -->.*?<!-- END LEARNED SEED BOUNDS -->',s,re.S)
 if match:
  text=match.group(0);s=s.replace(text,'');head,rest=s.split('\n',1);s=head+'\n\n'+text+'\n'+rest
 write(p,s)
 block(ROOT/'report/README.md','`learned_bounds_results.tex` describes the new model and matched controls.\n`learned_bounds_appendix.tex` defines the inputs and derives the cost formulas.\n`learned_bounds_data.json` contains the compact test evidence.\n`learned_bounds_validation.json` records the completed checks.\nThe figures show complete-time effects and generated-equation counts.\nBoth PDFs include these results.')
 block(ROOT/'report/paper_figures/README.md','`learned_bounds_times.pdf` compares graph times and total matched workload time.\n`learned_bounds_effects.pdf` shows all batch ratios and equation counts.\nRun `ML_model_adaptive_reduction/learned_seed_bounds/s08_analyze.py` to regenerate them.')
 p=ROOT/'README.md';s=p.read_text();new='''<!-- BEGIN ADAPTIVE REDUCTION -->

## Current reduction method

Read [learned seed bounds](ML_model_adaptive_reduction/learned_seed_bounds/README.md) for the new controlled comparison.
It chooses seed limits before native Kira equation generation.
It compares complete reduction time against controls with all ML disabled.
Its additional gain over tuned fixed settings remains within timing variation.
Read its measured graph results and domain limits.
The [earlier exact preparation and portfolio](ML_model_adaptive_reduction/parametric_preparation/README.md) remain available.
The new application keeps the exact preparation improvements.

<!-- END ADAPTIVE REDUCTION -->'''
 s=re.sub(r'<!-- BEGIN ADAPTIVE REDUCTION -->.*?<!-- END ADAPTIVE REDUCTION -->',lambda _:new,s,count=1,flags=re.S);write(p,s)
 print('Study and parent guides written',flush=True)
if __name__=='__main__':main()
