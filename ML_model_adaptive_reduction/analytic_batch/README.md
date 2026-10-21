# Exact triangles and learned target batches

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

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

## Measured outcome

The new batch model is enabled by complete-cost validation.
The reserved test verifies 58 of 58 requests in all three repetitions.
The matched ratio to the preceding method with the same basis is 0.611640 over 58 requests.
The matched ratio to the fixed batch action is 0.975392 over 58 requests.
On the forty native box requests, the new learned batch choice has a time ratio of 0.973323 to the fixed action.
Read summary.json and the paper for group results, failures, repetition intervals, and limits.
A finite comparison does not prove the fastest possible reduction for every integral.
