"""Document current execution, data, controls, and measured limits."""
from s00_batch_common import *

def main():
 s=read(HERE/'summary.json');a=s['admission'];v=s['comparisons']['all']['previous_prepared'];f=s['comparisons']['all']['fixed']
 text='''# Exact triangles and learned target batches

This is the current decomposition application.
It extends fast_decomposition without changing that study's code or results.
It applies an exact formula to one-scale massless triangles.
It uses measured cost to choose how native Kira reduces related targets.
All coefficients come from exact algebra.

## Use the application

Use the existing scientific Python environment on Hoffman.
Run scientific work in a scheduled compute job with s06_job.sh.
Keep at most two native workers active.
Use this command from the project root:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/analytic_batch/s02_batch_runtime.py --case path/to/request.json --output ML_model_adaptive_reduction/analytic_batch/result.json --method learned
```

The input is a case object with definition, targets, size, and id fields.
Read protocol.json for the complete reserved input definitions.
The definition gives loop momenta, external momenta, propagators, scalar products, and sectors.
Targets are integer index vectors in that propagator order.
The output stores exact component-master expansions and all reduction attempts.
The output path must be inside this study folder.
The application keeps independent loop products factored.
It reuses an identical component within one request. It does not reuse solved coefficients across requests.

Use --method learned for the admitted workflow.
Use --method fixed to disable the new batch model only.
Use --method all_fixed to disable the new batch model and the retained sparse-seed models.
Use --method previous_prepared for the preceding application with the additional checked master indices.
The benchmark's previous control calls fast_decomposition/s12_deploy.py directly with --method final.
The five named actions are also available for development: prior, sparse_wide, sparse_tight, rank_groups, and single_targets.
The fixed controls do not load the new model weights.

## Code and execution order

1. s00_batch_common.py defines bounded writes, model inputs, prediction, and basis access.
2. s01_triangle.py applies the derived finite-product triangle identity.
3. s02_batch_runtime.py applies exact methods and then the chosen native action.
4. s03_cases.py defines development, training, validation, and reserved inputs.
5. s04_measure.py prepares references and measures complete fresh processes.
6. s05_collect.py collects action costs and performs the triangle development checks.
7. s06_job.sh sets the scheduler, memory, thread, and time limits.
8. s07_train.py fits cost-sensitive trees and ensembles, then selects from validation costs.
9. s08_evaluate.py validates the complete application, freezes admission, and tests reserved requests.
10. s09_pipeline.py collects training and validation only after development and basis checks pass.
11. s10_analyze.py computes paired results, completion counts, and the report figure.
12. s11_prepare_basis.py checks new master indices with two native integral orderings.
13. s12_document.py writes the current paper and notes sections from checked measurements.
14. s13_validate.py rechecks exact outputs, frozen files, references, and both built documents.
15. s14_readmes.py updates these guides.
16. s15_finish.py runs analysis, writing, guide updates, and final checks in that order.
17. s16_triangle_checks.py checks equivalent routings, denominator permutations, and unsupported inputs against the native triangle references.

First run s05_collect.py development 0 and development 1.
Then run s11_prepare_basis.py after both workers finish.
Run s09_pipeline.py 0 and 1 after basis validation passes.
Run s07_train.py after both collections finish.
Run s08_evaluate.py validate 0 and validate 1, then s08_evaluate.py admit.
Run s08_evaluate.py test 0 and test 1 after admission creates protocol.json.
Run s15_finish.py after both tests finish.
Existing result files make these collection stages resumable.
Use a new study directory and new profiles for a changed scientific policy.
Do not replace frozen test results with a retuned model.

## Mathematical scope and controls

The triangle identity requires three massless propagators, two zero external virtualities, and one nonzero invariant.
It accepts integer powers within the implementation bound of sixteen in absolute value.
The middle propagator can have a negative power, which gives a polynomial numerator.
The formula keeps dimension and a symbolic external scale exact.
Unsupported structures continue to the preceding exact or native application.

The measured model domain contains two massless two-loop box structures.
It uses seven physical lines, nine indices, unit positive powers, and numerator ranks one through four.
The runtime also checks structural input ranges before prediction.
Structural input features do not establish transfer to every graph with the same counts.
The independent products through thirteen loops test the exact formula, not general connected scattering.

The additional basis registry contains master indices only.
Its preparation is separate from timed supplied-basis reduction.
The previous_prepared control receives the same registry.
Reference coefficients never enter the runtime or model features.
Every timed result has an independent coefficient check.
Times include process startup, loading, prediction, algebra, checks, retries, output, and exit.
One first unverified outcome stops later repetitions for that method and request.
That outcome remains a failure and receives no completed-time speedup.
Native operation counters cover instrumented elimination work. They do not count all mathematical operations.

## Storage and files

resource_plan.json records the combined project bound below 10,000,000,000 bytes.
The persistent study cap is 12 MiB.
Each native worker has a 32 MiB scratch limit and uses one core.
The job wrapper bounds memory and limits numerical-library threads to one.
No scientific data or trained models are copied to the local laptop.
Only the report and project guides are synchronized locally.
local_compaction.json records verified compaction of local PDF history. It preserves every original object.
scheduled_jobs.json identifies this study's scheduler jobs.
postprocessing_resources.json records the smaller reservation for admission and document work. Native workers retain their original memory limits.
benchmark_environment.json records the fixed reserved-test node selected before testing.
The test_worker environment files record each worker's processor and interpreter.
Use the frozen queue assignment when reproducing this reserved comparison.
The application itself can run on other supported compute nodes.
Previous job records and interrupted trials remain available.
basis_validation.json records the added master-index checks and preparation cost.
admission.json records the complete-cost deployment decision.
protocol.json freezes the reserved cases, methods, sources, model, and basis before testing.
summary.json stores all results and matched comparisons.
validation.json records final evidence and document checks.
visual_review.json records review of the finished PDF pages.
The LaTeX appendix derives the triangle coefficient and defines the complete data split.
The paper uses copies of the compact summaries. These copies contain no training records or model weights.
'''
 text+='\n## Measured outcome\n\n'
 text+=f"The new batch model is {'enabled' if a['enabled'] else 'disabled'} by complete-cost validation.\n"
 text+=f"The reserved test verifies {s['totals']['learned']['verified']} of {s['requests']} requests in all three repetitions.\n"
 text+=f"The matched ratio to the preceding method with the same basis is {v['ratio']:.6f} over {v['matched']} requests.\n"
 text+=f"The matched ratio to the fixed batch action is {f['ratio']:.6f} over {f['matched']} requests.\n"
 native=s['comparisons']['native_all']['fixed']
 text+=f"On the forty native box requests, the new learned batch choice has a time ratio of {native['ratio']:.6f} to the fixed action.\n"
 text+='Read summary.json and the paper for group results, failures, repetition intervals, and limits.\nA finite comparison does not prove the fastest possible reduction for every integral.\n'
 (HERE/'README.md').write_text(text)
 descriptions={
 'development':'Initial triangle checks and complete development action costs. These preceded the new basis preparation.',
 'development_initial':'Preserved first development run. A reference-import error invalidated its references. These records do not train the model.',
 'training':'Complete action costs for 32 requests at profiles 3011 and 3019. Each action has one repetition. rows.json.gz joins the feature and cost labels.',
 'validation':'Complete action costs for sixteen requests at profile 3037. Each action has two repetitions. These costs select the model and fixed action.',
 'application_validation':'Three fresh-process comparisons of the selected model and fixed action at fresh profile 3041 on the fixed test node. These records determine deployment.',
 'trained_model':'initial_policy.json stores the selected candidate. policy.json stores the admitted policy. fixed.json stores the ML-off action. selection.json lists candidate validation costs. A disabled candidate remains recorded.',
 'model_test':'Reserved fresh-process results for five methods. Verified methods have three repetitions. A first failure has one record. Each record includes exact coefficients, time, actions, and native counters.',
 'references':'Independent exact references for collection and tests. Their preparation time is separate from application time. They never supply runtime coefficients.',
 'basis_checks':'Two native orderings check each additional basis against a development reference. The runtime receives only master indices.',
 'requests':'Temporary application inputs and outputs. Completed measurements remove these files.',
 'logs':'Scheduler output during collection and checks. Scientific results are retained in structured records. Routine logs are excluded from Git publication.',
 'interrupted_validation':'Preserved trials at profile 3037 on heterogeneous workers. The collection stopped before admission. These records do not select the final policy.',
 'interrupted_validation/source':'Runtime and measurement sources for the preserved trials. The changed validation driver is omitted from this snapshot. Its initial profile was 3037. Use the parent scripts for the completed comparison at profile 3041.',
 'interrupted_validation/partial_outputs':'Inputs and any output left by the interrupted application. These are not completed timed comparisons.',
 'unprepared_training':'Interrupted collection before the added basis was installed. These trials remain development evidence and do not train the final model.',
 'unprepared_training/source':'Source snapshot for the interrupted collection. Use the study parent scripts for the completed experiment.'}
 for name,description in descriptions.items():
  q=HERE/name;q.mkdir(exist_ok=True);parent='../'*len(Path(name).parts)+'README.md'
  (q/'README.md').write_text('# '+name.split('/')[-1].replace('_',' ').capitalize()+'\n\n'+description+'\n\nRead ['+'the study guide]('+parent+') for execution, controls, and limits.\n')
 prefix='''## Current exact triangle and target-batch method

Use [the current application guide](ML_model_adaptive_reduction/analytic_batch/README.md).
The entry point is analytic_batch/s02_batch_runtime.py. Use --method learned.
It combines exact triangle reduction with complete-cost selection of native target batches.
The guide states the admitted model, fixed controls, measured gains, and supported inputs.
The paper and notes contain the derivation and the 58-request reserved comparison.
Earlier methods and their evidence remain available.

'''
 q=ROOT/'README.md';z=q.read_text()
 if not z.startswith(prefix):z=z.replace('## Current fast exact and learned decomposition','## Preceding fast exact and learned decomposition',1).replace('The final entry point is s12_deploy.py in fast_decomposition. Use --method final.','That version uses s12_deploy.py in fast_decomposition with --method final.',1);q.write_text(prefix+z)
 q=ROOT/'ML_model_adaptive_reduction/README.md';z=q.read_text();head='''## Current analytic batch application

Use [analytic_batch/README.md](analytic_batch/README.md) for the current entry point.
It checks an exact one-scale triangle identity and trains native target-batch choices on complete cost.
It retains matched fixed controls, exact checks, and failed outcomes.
The preceding fast_decomposition application remains unchanged for comparison.

'''
 if not z.startswith(head):q.write_text(head+z)
 q=ROOT/'report/README.md';z=q.read_text().replace('fast_decomposition_validation.json identifies the current PDF checks.','fast_decomposition_validation.json identifies the preceding publication checks.')
 head='''## Current analytic batch report files

analytic_batch_method.tex explains exact triangle reduction and learned target grouping.
analytic_batch_results.tex gives model admission, reserved times, controls, and failures.
analytic_batch_appendix.tex derives the coefficient and defines all training and test inputs.
analytic_batch_data.json contains the compact measured summary.
analytic_batch_validation.json identifies the current evidence and PDF checks.
paper_figures/analytic_batch.pdf compares complete time and the separate batch-model effect.
The notes_analytic_batch files give the same current evidence in the detailed notes.
Use s15_finish.py in analytic_batch to rebuild the current sections and check both PDFs.
Earlier study writers can replace current prose. Use the current writer for this extension.

'''
 if not z.startswith(head):q.write_text(head+z)
 q=ROOT/'report/paper_figures/README.md';z=q.read_text();line='analytic_batch.pdf compares the new workflow with a same-basis control and isolates the batch-model effect.\n'
 if line not in z:q.write_text(z.rstrip()+'\n\n'+line)
 for q in [HERE/'README.md',ROOT/'README.md',ROOT/'ML_model_adaptive_reduction/README.md',ROOT/'report/README.md',ROOT/'report/paper_figures/README.md',*HERE.glob('*/README.md')]:q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 print('Current guides written.',flush=True)
if __name__=='__main__':main()
