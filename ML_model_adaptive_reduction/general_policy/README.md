# Shared structural cost model

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

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

The final matched set contains 43 requests. Learned/native time ratio: 0.900312. Learned/fixed ratio: 0.950590.

Read [preparation/README.md](preparation/README.md) for the cost-and-failure model and the complete preparation comparison. Scripts s14 through s19 implement this extension. Both models and the ML-off controls remain available.

The current public command is `s22_reduce.py --case INPUT.json --output OUTPUT.json.gz`. Add `--basis BASIS.json` when a basis is available. It first checks the exact scalar formula. With a supplied basis, it uses the validation-approved shared model. Without a basis, it follows preparation/deployment.json and includes discovery and recovery. That deployment decision follows the completed candidate comparison; it has no separate timing claim. Use `--method learned` or `--method native` to set the decision explicitly. The alternative cost-and-risk model remains available through s20. `s23_check_optional_basis.py` checks this interface without giving it reference answers.

## Additional scripts

- [s14_prepare.py](s14_prepare.py): Reduce without repeated large reference preparation, using checked basis indices.
- [s15_risk.py](s15_risk.py): Learn action cost and failure risk from completed and failed exact attempts.
- [s16_test_preparation.py](s16_test_preparation.py): Compare completed preparation workflows, keeping failures and all controls.
- [s17_analyze_preparation.py](s17_analyze_preparation.py): Compare full preparation workflows, including every failed first request.
- [s18_document_preparation.py](s18_document_preparation.py): Document cost-aware training and the separately measured preparation change.
- [s19_finish_preparation.py](s19_finish_preparation.py): Finish conclusions and readable guides from completed preparation evidence.
- [s20_prepare_resilient.py](s20_prepare_resilient.py): Recover when a stored index basis is incomplete for new targets.
- [s21_recovery.py](s21_recovery.py): Fresh verification of basis refresh, with frozen models and complete timers.
