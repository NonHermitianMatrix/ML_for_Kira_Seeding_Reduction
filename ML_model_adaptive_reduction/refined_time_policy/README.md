# Complete-time Kira selection

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

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

The reserved grid has 65 requests. The learned application verifies 64 in all three repetitions.
On 64 matched completions, the learned/previous refined-time ratio is 0.914773.
On 64 matched completions, the learned/native refined-time ratio is 0.978533.
On 64 matched completions, the learned/fixed refined-time ratio is 0.994485.

Read summary.json for ML-only comparisons, repetition intervals, failed calls, first-pass totals, and per-loop coverage.
The coupled native cases reach three loops. The analytic families and independent products reach thirteen loops.
Independent products contain blocks with at most two loops. These results do not cover all high-loop scattering integrals.
The exact formulas require their stated mass, momentum, and numerator structures. They do not evaluate the master integrals.
No measured result proves a globally fastest reduction or an optimal path.

## Integrated sparse expert

The later combined application is in ../hybrid_experts/.
It tests a sparse-seed expert on fresh higher-rank nonplanar targets and retains this application for other requests.
This folder preserves its frozen broad comparison. Its PDF checks precede the later document update.
Use ../hybrid_experts/validation.json for the current PDF checks.

## Additional scripts

- [sync_report.py](sync_report.py): Copy only published report files and guides; verify each Git blob locally.
