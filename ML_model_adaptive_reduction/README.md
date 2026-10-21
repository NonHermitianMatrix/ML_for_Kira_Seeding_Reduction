# Combined analytic and learned reduction

This directory implements reductions that use exact formulas where their conditions hold and Kira for the remaining supported inputs. Learned cost models select useful native choices in validated domains. Each result records whether the requested reduction completed.

## Application interface

[triangle_reduction](triangle_reduction/README.md) contains the deployed interface: `s32_deploy.py` for one request and `s33_batch.py` for a list. It retains the accepted earlier analytic routines and native seed policy. The additional arithmetic model and equation filter are disabled by their validation results. Kira uses its native row choices.

The input supplies physical propagators, kinematics, targets, and the required basis. The output contains exact reduction coefficients or a recorded failure. The application checks analytic conditions before selecting a formula and includes recovery when a restricted native attempt is insufficient.

## Exact methods

| Folder | Mathematical role |
|---|---|
| [triangle_reduction](triangle_reduction/README.md) | Massless triangles with two lightlike external legs and one nonzero invariant. |
| [tensor_reduction](tensor_reduction/README.md) | One-loop polynomial numerators and power-lowering identities. |
| [lightlike_reduction](lightlike_reduction/README.md) | Two-point sectors with zero external invariant, including mass limits. |
| [direct_analytic](direct_analytic/README.md) | Tadpole values, vacuum partial fractions, and scaleless sectors. |
| [propagator_trees](propagator_trees/README.md), [loop_coverage13](loop_coverage13/README.md) | Successive exact integrations of supported connected bubble trees. |
| [vacuum_learning](vacuum_learning/README.md) | Trees with a massive vacuum root and a native sparse-seed policy. |
| [gamma_cancellation](gamma_cancellation/README.md) | Cancellation of common Gamma factors before finite expansion. |
| [factorized_policy](factorized_policy/README.md), [fast_decomposition](fast_decomposition/README.md) | Independent loop components and shared exact coefficients. |
| [massless_banana](massless_banana/README.md) | A specified massless two-point family with an exact Gamma-function expression. |
| [analytic_decomposition](analytic_decomposition/README.md), [analytic_batch](analytic_batch/README.md) | Recurrence and target-grouping experiments. |

Tests reach thirteen loops for stated analytic structures. Extra propagators, different invariants, or coupled components can invalidate those formulas. The application checks these conditions instead of selecting a formula from loop count alone.

## Learned choices and component experiments

`general_policy/` predicts seed cost from structural features shared across families. `portfolio_policy/`, `learned_seed_bounds/`, `total_time_policy/`, `refined_time_policy/`, and `hybrid_experts/` compare strategy selectors. `batch_policy/` studies target grouping. `selective_expansion/` and `parametric_preparation/` study basis completion and symbolic preparation. `reconstruction_policy/` compares symbolic and finite-field arithmetic.

These folders contain distinct experiments, training splits, and controls. Their saved models are not all enabled together. Each guide identifies its accepted model, fixed control, failure handling, and measured domain.

## Native integration study in this directory

The scripts directly in this directory build and test an earlier native integration with exact preprocessing and structural cost models. `integration/` contains source changes; `training/` and `validation/` contain separate cost measurements. `trained_model/` stores fitted candidates and the selected policy. `model_test/`, `graph_control_test/`, and `integration_test/` hold reserved comparisons. `references/` supplies the bases and coefficients used for independent checks.

Use the numbered scripts to reproduce that experiment. For a reduction through the retained combined method, use the application interface above. Native jobs require the recorded Kira builds, Python environment, and scheduled memory and time limits.

## Scripts

| File | Purpose |
|---|---|
| [s00_build.py](s00_build.py) | Build an exact file-index improvement without changing the original binary. |
| [s01_native_runner.py](s01_native_runner.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s02_runtime.py](s02_runtime.py) | A single entry point for bounded, exact target-dependent Kira reductions. |
| [s03_pilot.py](s03_pilot.py) | Check file-index parity and measure candidate seed regions on development data. |
| [s04_job.sh](s04_job.sh) | Scheduler wrapper for job; its header sets the resource limits. |
| [s05_study.py](s05_study.py) | Train one complete-cost policy and test it on new target and kinematic profiles. |
| [s06_analyze.py](s06_analyze.py) | Audit results and plot complete costs against native and fixed controls. |
| [s07_report.py](s07_report.py) | Write measured results into both documents without changing archived notes. |
| [s08_reduce.py](s08_reduce.py) | Apply the frozen cost policy to a target batch and a prescribed master basis. |
| [s09_integration_check.py](s09_integration_check.py) | Check public applications and separate exact preprocessing from policy gains. |
| [s10_document.py](s10_document.py) | Maintain short folder guides and application links. |
| [s11_finalize.py](s11_finalize.py) | Build reviewed evidence and documents after all scientific jobs complete. |
| [s12_graph_policy.py](s12_graph_policy.py) | Validate a guard against the best fixed setting for each known graph. |
| [s13_previous_server.py](s13_previous_server.py) | Isolate the published workflow imports and use the current exact Kira build. |
| [s14_portfolio.py](s14_portfolio.py) | Compare selective seed expansion, worker counts, and the published workflow. |
| [s15_portfolio_study.py](s15_portfolio_study.py) | Fit a complete-cost portfolio and compare fresh targets with the published method. |
| [s16_portfolio_analyze.py](s16_portfolio_analyze.py) | Audit the frozen portfolio and plot each gain against its matched control. |
| [s17_reduce.py](s17_reduce.py) | Use the validated portfolio with a target batch and a prescribed master basis. |
| [s18_portfolio_report.py](s18_portfolio_report.py) | Describe the measured final policy, its controls, and its physical scope. |
| [s19_finish_controls.py](s19_finish_controls.py) | Finish independent controls after a bounded failure, preserving failed evidence. |
| [s20_check_initial_report.py](s20_check_initial_report.py) | Check the completed first study's documents while portfolio tests continue. |
| [s21_check_application.py](s21_check_application.py) | Check the public portfolio interface after its model has been frozen. |
| [s22_build_parametric.py](s22_build_parametric.py) | Project unused parameters before constructing the sector polynomials. |
| [s23_parametric_runner.py](s23_parametric_runner.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s24_parametric_runtime.py](s24_parametric_runtime.py) | Apply the frozen learned portfolio with exact sector polynomial projection. |
| [s25_parametric_job.sh](s25_parametric_job.sh) | Scheduler wrapper for parametric job; its header sets the resource limits. |
| [s26_parametric_study.py](s26_parametric_study.py) | Compare unchanged models with earlier or projected parametric preparation. |
| [s27_profile_parametric.py](s27_profile_parametric.py) | Keep bounded phase logs for the development four-loop calculation. |
| [s28_profile_selection.py](s28_profile_selection.py) | Keep the full small development log to locate remaining setup costs. |
| [s29_check_replay.py](s29_check_replay.py) | Check exact selected-equation replay, bypass, and application guards. |
| [s30_analyze_parametric.py](s30_analyze_parametric.py) | Audit complete comparisons and draw figures from the retained measurements. |
| [s31_report_parametric.py](s31_report_parametric.py) | Describe the exact preparation changes and the unchanged learned policies. |
| [s32_finish_parametric.py](s32_finish_parametric.py) | Audit the completed study, build both PDFs, and check publication inputs. |
