# Kira correctness and timing comparisons

These experiments measure whether the reduction methods return the required coefficients and reduce elapsed time. Each comparison fixes its targets, physical inputs, master basis, timing boundary, and resource limits. A result is successful only after its stated exact checks pass.

## Choose the comparison

| Folder | Question and reference |
|---|---|
| [default_kira_final](default_kira_final/README.md) | Complete retained method versus the original Kira 3.1 executable with default algorithms for the stated jobs. |
| [cumulative_speedup](cumulative_speedup/README.md) | Restricted-vacuum recurrence and reuse versus Kira solving supplied identities. |
| [live_matrix](live_matrix/README.md) | Learned elimination decisions inside Kira’s changing matrix. |
| [integrated_runtime](integrated_runtime/README.md), [acceleration](acceleration/README.md) | Native integration, prediction overhead, shared work, and implementation controls. |
| [multiloop_native](multiloop_native/README.md) | Complete native IBP generation and multiloop reductions. |
| [higher_scattering](higher_scattering/README.md) | Separate contributions and transfer on connected scattering requests. |
| [generalization](generalization/README.md) | Specified new scattering structures, symbolic kinematics, and bounded path studies. |
| [coverage_study](coverage_study/README.md), [extended_coverage](extended_coverage/README.md) | Completion, failures, and interface limits across a defined family grid. |
| [parallel_inference](parallel_inference/README.md), [fast_expression](fast_expression/README.md) | Prediction overhead and shared expression evaluation. |

## Interpret a result

The default-Kira comparison completes 14 matched requests in 266.458 seconds for Kira and 22.109 seconds for the combined method. The ratio is 12.05. These sums use request medians from three repetitions. The method completes all 20 requests; six default runs reach the 60-second limit. Unmatched requests do not enter a finite speed factor.

An earlier native control may share project modifications with its learned counterpart. A fixed control replaces the named learned decision. A previous-application control already contains other optimizations. A supplied-identity control omits native equation generation. Keep these references separate when quoting gains.

Inspect a study’s protocol or frozen inputs, result records, and summary together. Match case identifiers and master bases before comparing coefficients. Check completion counts before reading aggregate times. Logs preserve failed attempts and recovery; a timeout does not prove mathematical irreducibility.

## Reproduce a study

The numbered scripts below describe the original comparison and native seed checks in this directory. Later studies have their own producers and scheduler wrappers in the linked folders. Submit native calculations on Hoffman with the documented resources. Keep frozen weights and reserved inputs fixed while reproducing a test.

Saved result files use JSON, compressed JSON, or JSONL. JSONL contains one record per line. The producing code defines the timing fields and exact-check status. `figures/` contains plots of the recorded comparisons.

## Scripts

| File | Purpose |
|---|---|
| [s00_prepare.py](s00_prepare.py) | Freeze outcome-independent held-out cases, models, and resource limits. |
| [s01_common.py](s01_common.py) | Public inputs and exact coefficient arithmetic for paired Kira comparisons. |
| [s02_worker.py](s02_worker.py) | One isolated symbolic reduction, with live inference and exact fallback. |
| [s03_run.py](s03_run.py) | Run counterbalanced matched trials with bounded processes and archived evidence. |
| [s04_run.sh](s04_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s05_array.sh](s05_array.sh) | Scheduler wrapper for array; its header sets the resource limits. |
| [s06_freeze_inputs.py](s06_freeze_inputs.py) | Records and enforce the exact inputs and executable sources before repeated tests. |
| [s07_audit.py](s07_audit.py) | Check final exports, selected identities, paths and complete trial coverage. |
| [s08_summarize.py](s08_summarize.py) | Summarize matched repetitions, resource outcomes and distinct cost measures. |
| [s09_plot.py](s09_plot.py) | Plot verified matched runtime, solver work, model work and memory. |
| [s10_native_worker.py](s10_native_worker.py) | Native Kira seeding from frozen learned seed envelopes, with default fallback. |
| [s11_native_run.py](s11_native_run.py) | Run counterbalanced matched trials with bounded processes and archived evidence. |
| [s12_native_array.sh](s12_native_array.sh) | Scheduler wrapper for native array; its header sets the resource limits. |
| [s13_native_audit.py](s13_native_audit.py) | Check final exports, selected identities, paths and complete trial coverage. |
| [s14_prepare_native.py](s14_prepare_native.py) | Freeze the native seed-envelope comparison on the same seven independent bases. |
| [s15_native_summary.py](s15_native_summary.py) | Summarize matched repetitions, resource outcomes and distinct cost measures. |
| [s16_native_plot.py](s16_native_plot.py) | Plot the direct native seed-envelope comparison. |
| [s17_native_combine.py](s17_native_combine.py) | Combines native component reductions with exact Fermat algebra through Kira. |
| [s18_native_regression.py](s18_native_regression.py) | Check the previously slow native combination and the learned native envelope. |
| [s19_regression.sh](s19_regression.sh) | Scheduler wrapper for regression; its header sets the resource limits. |
| [s20_finalize.sh](s20_finalize.sh) | Scheduler wrapper for finalize; its header sets the resource limits. |
| [s21_update_report.py](s21_update_report.py) | Write the checked comparison into the paper and preserve the supplied abstract. |
| [s22_readmes.py](s22_readmes.py) | Document the validated comparison without changing models or integral data. |
| [s23_cost_breakdown.py](s23_cost_breakdown.py) | Separates measured stages and family outcomes after exact validation. |
| [s24_resume_native.py](s24_resume_native.py) | Resumes native cases after enlarging only the retained-evidence storage guard. |
| [s25_resume_array.sh](s25_resume_array.sh) | Scheduler wrapper for resume array; its header sets the resource limits. |
| [s26_resume_audit.py](s26_resume_audit.py) | Check the storage-only resumption and preservation of fixed mathematical inputs. |
| [s27_finish_resumed.sh](s27_finish_resumed.sh) | Scheduler wrapper for finish resumed; its header sets the resource limits. |
