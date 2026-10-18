# Family-aware seed-cost model

This study chooses seed bounds before Kira generates IBP equations.
IBP means integration by parts.
Kira performs the exact algebra. Failed choices trigger bounded recovery.
The model predicts the full cost of ten settings.
It receives integral features and no answer coefficients.

The final reserved grid contains 44 batches. The matched set contains 41 nontrivial batches.
The learned-to-fixed time ratio is 0.991397.
The combined-to-previous ratio is 0.961382.
The new target-pattern model deploys on 1 matched batch.
Its learned-to-fixed time ratio is 0.838969.
Its learned-to-native time ratio is 1.005588.
The new model reduces time against the fixed control and gives no clear gain against native bounds in this batch.
The final application's time ratio against native is 0.854882 over all matched batches with a supplied basis.
The final-to-previous interval is [0.934421926392656, 1.0208946712029046]. It includes one, so the added aggregate gain remains uncertain.
Read the deployed subset in summary.json for its isolated model effect.
Inactive learned and fixed conditions use identical choices. Their time differences measure run variation.
A ratio below one means less time.
Read summary.json for intervals, each family, failed references, and active learned decisions.
A combined gain includes exact formula selection and fixed choices.
Do not describe the full combined gain as an ML gain.

## Use

Run from the project root in a Hoffman compute job.
Use the case and basis schema from protocol.json and references/.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/portfolio_policy/s13_optimized.py --case CASE.json --basis BASIS.json --output RESULT.json.gz
```

The combined application keeps the exact scalar formula where valid.
It uses the new choice only when validation improves on the previous application.
A target-shape gate deploys the learned choice where confirmation improves on both fixed and previous controls.
Other inputs use the previous application and its domain guards.
The native index limit still applies to general IBP calculations.
Scalar formula inputs can use the full coordinate representation through twelve tested loops.
The sector-storage executable supplies a separate exact optimization.
The final application uses it only in domains selected by the separate exact validation.
Other inputs retain the previous executable.
A separate wider executable supports the tested 128-bit integral-weight route.
Its matched controls separate the learned gain from the exact gain.
Use KIRA_BOUNDED_SECTOR_ARRAYS=1 with KIRA_RESTRICT_SECTOR_INIT=1 when calling that executable.
Its tests cover cold single-family runs without cuts or symbolic IBP.
The main learned comparison uses the preceding exact executable for all controls.

## Reproduce

1. Read resource_plan.json and protocol.json.
2. Run s02_collect.py training 0 and training 1 through s03_job.sh.
3. Run s02_collect.py validation 0 and validation 1.
4. Run s04_train.py to fit and freeze the models.
5. Run s05_test.py 0 and s05_test.py 1.
6. Run s06_build_sector_storage.py to build the bounded sector arrays.
7. Run s20_check_sector_order.py and s07_sector_checks.py for the separate exact comparison.
Run s23_retry_enlarged_checks.py for the one longer attempt on timed-out enlarged checks.
8. Run s09_scalar_checks.py for the full-coordinate scalar checks.
9. Run s16_build_wide.py and s17_wide_checks.py for the separate 128-bit checks.
10. Run s19_freeze_deployment.py to freeze target-shape gates from confirmation.
11. Run s22_select_storage.py to select and verify exact routes.
12. Run s14_combined_test.py 0 and s14_combined_test.py 1 on fresh profile 1151.
13. Run s12_finish.py to analyze, write, build, and check both documents.

Use at most two project compute jobs at once.
The study uses the existing NumPy, scikit-learn, SymPy, and Matplotlib environment.
C++ compilation uses the existing GCC and Kira build recipes.
The report uses the existing Tectonic installation.

## Files and limits

s00_common.py defines the physical inputs, feature extraction, file format, and storage guard.
s01_application.py runs a fresh measured application or one cost action.
s02_collect.py records full process time and creates independent references.
s03_job.sh sets the scheduler, thread, and memory limits.
s04_train.py compares nine shared models, separate family cost trees, and three decision margins.
It then calls s15_confirm.py on another validation profile.
s05_test.py checks the frozen reserved inputs.
s06_build_sector_storage.py builds the exact storage change and records the patch.
s07_sector_checks.py checks that change on low- and higher-loop inputs.
s08_reduce.py combines the learned policy with the preceding exact implementation.
s13_optimized.py adds bounded sector storage.
s14_combined_test.py tests the final combined implementation.
s09_scalar_checks.py checks the scalar formula through twelve loops.
s16_build_wide.py and s17_wide_checks.py build and check wider integral weights.
s19_freeze_deployment.py selects target-shape deployment from confirmation costs.
s18_debug_storage.py traces the discarded initial storage error and is not part of production.
s20_check_sector_order.py compares the sector ordering and minimum-line count against exhaustive small controls.
s21_cached_storage_checks.py preserves the uncached comparison and checks the exact cache.
s22_select_storage.py selects exact routes from validation and checks the complete application.
s23_retry_enlarged_checks.py retries timed-out enlarged checks once with a longer time budget.
It preserves the original independent check and the initial failures.
s10_analyze.py creates the summaries and timing figure.
s11_document.py writes the method and results in the report and notes.
s12_finish.py writes folder guides, rebuilds both PDFs, and validates publication inputs.

The training profiles differ from validation and test profiles.
The graph structures and target patterns overlap between these sets.
Historical training records use their earlier internal application timer.
New training, validation, and tests include fresh-process cost.
The native, fixed, and learned test controls use the same exact executable.
Reference discovery remains separate from the primary application time.
The repeated timer includes model loads, prediction, algebra, checks, and retries.

Each native attempt uses one worker, a 6 GiB address limit, a 5,200 MiB process-tree limit, and 32 MiB of temporary storage.
Application attempts have 60 seconds. Reference attempts have 90 seconds.
The driver reserves ten seconds for completion and cleanup.
The study retains at most 24 MiB of records. The completed build objects are removed. Recheck the global storage budget before starting a new compilation.
Keep the whole project below 10,000,000,000 bytes.
Keep generated models and data on Hoffman and GitHub.
Keep both reports locally as well.

These tests do not establish a speedup for every integral type or arbitrary loop order.
The twelve-loop scalar checks verify a stated exact identity and use no learned prediction.
