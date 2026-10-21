# Learning which IBP equations to construct

This directory studies selection of equations for specified target integrals. A classifier scores a seed and derivative-operator pair before Kira constructs the full symbolic coefficients. Exact reduction checks whether the retained equations suffice, and recovery costs remain in timing results.

The final combined application disables the additional equation filter after its validation tests. The models and native integrations here remain available for their separate experiments.

## Methods and records

| Folder | Purpose |
|---|---|
| [early_generation](early_generation/README.md) | A 17-feature classifier that acts before coefficient construction. |
| [scattering_training](scattering_training/README.md) | Training and tests on specified nonplanar box, pentagon, and off-shell box structures. |
| [bound_refinement](bound_refinement/README.md) | Refined decisions using seed, operator, and target information. |
| [pre_reduction](pre_reduction/README.md), [integration](integration/README.md) | Earlier native filtering and build experiments. |
| [batch_reuse](batch_reuse/README.md), [polynomial_reuse](polynomial_reuse/README.md) | Shared equations and repeated symbolic coefficients. |
| [higher_loops](higher_loops/README.md), [exact_backend](exact_backend/README.md) | Restricted vacuum families and exact recurrences; these are separate from general native ML tests. |
| [training](training/README.md), [validation](validation/README.md), [model_test](model_test/README.md) | Fitting records, separate selection measurements, and reserved results. |
| [trained_model](trained_model/README.md), [references](references/README.md) | Fitted parameters and exact reference reductions. |

## Inputs, outputs, and execution

Training records connect candidate seed–operator pairs to the equations retained by a reference reduction. Runtime inputs describe the physical family, target indices, and candidate choices. The model returns scores or selected candidates; Kira returns the reduction coefficients and completion status.

Use each experiment’s scheduler wrapper and fixed data split. Native build scripts require the recorded Kira source, compiler, and libraries. The Python environment supplies numerical and exact algebra dependencies. The scripts directly below describe the original equation-selection workflow and its variants; the linked studies have their own code sequences.

## Scripts

| File | Purpose |
|---|---|
| [s00_build.py](s00_build.py) | Compiles equation filtering and collection without changing prior binaries. |
| [s01_build.sh](s01_build.sh) | Scheduler wrapper for build; its header sets the resource limits. |
| [s02_records.py](s02_records.py) | Bounded compressed exact evidence. |
| [s03_run.py](s03_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s04_experiment.py](s04_experiment.py) | Collect native labels and compare frozen filters with exact fallback. |
| [s05_run.sh](s05_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s06_train.py](s06_train.py) | Fit a small target-dependent CART probability model using training groups only. |
| [s07_train.sh](s07_train.sh) | Scheduler wrapper for train; its header sets the resource limits. |
| [s08_develop.sh](s08_develop.sh) | Scheduler wrapper for develop; its header sets the resource limits. |
| [s09_predict.py](s09_predict.py) | Predicts reference-membership probabilities from the documented 24 features. |
| [s10_summarize.py](s10_summarize.py) | Summarize paired timings without dropping failed filtered attempts. |
| [s11_reduce.py](s11_reduce.py) | Applies the third policy with a prescribed basis; target reference coefficients are optional. |
| [s12_freeze.py](s12_freeze.py) | Chooses from completed validation only, then freeze before test reductions. |
| [s13_check_labels.py](s13_check_labels.py) | Repeats a native collection to check labels and features before fitting. |
| [s14_check_fast.py](s14_check_fast.py) | Check that shared features preserve all learned probabilities and equation masks. |
| [s15_build_fast.sh](s15_build_fast.sh) | Scheduler wrapper for build fast; its header sets the resource limits. |
| [s16_validate_fast.sh](s16_validate_fast.sh) | Scheduler wrapper for validate fast; its header sets the resource limits. |
| [s17_audit.py](s17_audit.py) | Compare all completed test coefficients over Q(d). |
| [s18_additional_checks.py](s18_additional_checks.py) | Check composition with existing models, basis-only use, and held-out labels. |
| [s19_test.sh](s19_test.sh) | Scheduler wrapper for test; its header sets the resource limits. |
| [s20_build_cached.sh](s20_build_cached.sh) | Scheduler wrapper for build cached; its header sets the resource limits. |
| [s21_validate_cached.sh](s21_validate_cached.sh) | Scheduler wrapper for validate cached; its header sets the resource limits. |
| [s22_build_compact.sh](s22_build_compact.sh) | Scheduler wrapper for build compact; its header sets the resource limits. |
| [s23_plot.py](s23_plot.py) | Plot measured complete costs, preparation work and held-out label scores. |
| [s24_document.py](s24_document.py) | Write measured results and folder documentation after all checks finish. |
| [s25_build_lazy.sh](s25_build_lazy.sh) | Scheduler wrapper for build lazy; its header sets the resource limits. |
| [s26_validate_lazy.sh](s26_validate_lazy.sh) | Scheduler wrapper for validate lazy; its header sets the resource limits. |
| [s27_report.sh](s27_report.sh) | Scheduler wrapper for report; its header sets the resource limits. |
| [s28_stratify.py](s28_stratify.py) | Stratifies frozen test results by the topology route fixed in validation. |
| [s29_final_report.sh](s29_final_report.sh) | Scheduler wrapper for final report; its header sets the resource limits. |
| [s30_confirmation.py](s30_confirmation.py) | Confirms a restricted deployment on six fresh physical sunrise profiles. |
| [s31_reduce.py](s31_reduce.py) | Applies the confirmed equation policy within its measured target domain. |
| [s32_confirm.sh](s32_confirm.sh) | Scheduler wrapper for confirm; its header sets the resource limits. |
| [s33_confirm_document.py](s33_confirm_document.py) | Document the restricted deployment and independent confirmation. |
| [s34_confirmed_report.sh](s34_confirmed_report.sh) | Scheduler wrapper for confirmed report; its header sets the resource limits. |
| [s35_reduce.py](s35_reduce.py) | Applies equation selection only in its measured beneficial standalone domain. |
| [s36_check_deployment.py](s36_check_deployment.py) | Verify that deployment selects measured successful arms and guards combinations. |
| [s37_finish_documentation.py](s37_finish_documentation.py) | Finalizes deployment documentation without changing either frozen experiment. |
| [s38_plot.py](s38_plot.py) | Plot measured complete costs, preparation work and held-out label scores. |
| [s39_finish_report.sh](s39_finish_report.sh) | Scheduler wrapper for finish report; its header sets the resource limits. |
