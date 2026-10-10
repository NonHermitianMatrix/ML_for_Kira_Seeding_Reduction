# Complete native multiloop reductions

This experiment gives Kira physical denominators and indexed targets and includes IBP generation in each timed calculation. It has six training cases, three validation cases and six reserved cases. The families are two-loop sunrise and boxes, fully coupled three-loop vacua, and three-loop propagator ladders. The ladder topology is absent from training and validation. Kinematics are rational numbers in a fixed squared-momentum unit; the dimension remains symbolic.

The original integral collection and neural checkpoints remain unchanged. Targets follow a fixed sector, dot and numerator enumeration. There is no claim of globally optimal seed sets or elimination paths.

## Completed experiment

The fixed complete-generation experiment has 324 planned workflows, 324 measured workflows and 324 exact completions.

The selected seed policy's complete-time ratio to responsive stock Kira is 0.741945 (12 paired batches).

Seed-to-stock time ratios are 0.563457 for two-loop boxes, 1.265710 for three-loop vacua, 0.572691 for three-loop ladders. The aggregate seed time interval includes one; gains are specific to the tested family classes. The row-time interval also includes one.

The cost-trained row policy's complete-time ratio to instrumented native Kira is 1.007901 (12 paired batches); its forward coefficient-operation ratio is 1.003162 (12 paired batches).

These are paired, three-repeat comparisons at rational kinematics with symbolic d. Results include inference, native generation, exact algebra, verification and fallback. The common reference basis is prepared separately.

The independent audit passed. Family-level results and completion counts must accompany aggregate ratios; none establishes a universal speedup.

All 140 final validation workflows passed. The selected seed policy had a validation time ratio of 1.118283 to native Kira. freeze.json fixed its threshold, all weights, executables and scientific settings before reserved tests.

scheduler_interruption.json records a scheduler address-space interruption. Its completed records were preserved, and missing workflows resumed with the same physical-memory, elapsed-time and scratch limits. This event is separate from measured workflow outcomes.

summary.json and trials.csv contain every planned outcome. verification.json records independent exact polynomial checks. report_values.json maps report values to their evidence. model_test/plots/ contains the three PDF figures.

## Procedure

- s00_storage.sh performed the one-time allocated-storage audit. Its result and resource_plan.json define the storage allowance. Repeated full-project scans are unnecessary.
- s01_families.py defines families.json and refuses to overwrite an existing split.
- s02_run.py generates a native job, applies limits, restores identities for explicitly declared master targets, and checks exact coefficients.
- s03_pilot.sh runs initial small checks. pilot/ and pilot_v2/ preserve earlier driver failures; pilot_v3/ contains the corrected pilot.
- s04_records.py shares repeated payloads by SHA-256. Atomic writes and a shared lock protect concurrent results and the retained cap. Use its read_record function to resolve shared compressed records.
- s05_development.py and s06_development.sh collect exact local insertion costs.
- s07_seed.py scores a finite seed region with the unchanged seed network. Optional deterministic coverage retains corners, required integrals and seeds with at most one dot or numerator power in total.
- s08_workflow.py supplies complete fallback sequences and optional groups of 32 targets.
- s09_validate.py and s10_validate.sh preserve the first workflow validation.
- s11_rollouts.py and s12_rollouts.sh measure exact continuations after a forced source choice. Records retain state signatures, candidate features, prefix counts and remaining operation counts.
- s13_audit_families.py checks that denominators span the independent loop scalar products.
- s14_worker.py and s15_fresh.py measure fresh processes and bound the full process tree, including model loading and verification.
- s16_validate_fresh.py and s17_validate_fresh.sh run policies in separate validation processes. validation_seed_safe/ and validation_row/ retain earlier implementations; validation_final/ selects final settings with the cost tree and bounded seed caches.
- s18_freeze.py selects seed settings from validation and records the reserved protocol.
- s19_reserved.py and s20_reserved.sh execute the frozen comparison and expanded-bound reference checks.
- s21_seed_loader.py reads the unchanged weight archive once. s22_install_runtime.py installs it and two-entry per-process caches.
- s23_prepare.sh installs the saved tree and runs s24_check_runtime.py, which verifies seed probabilities and native tree decisions against Python.
- s25_analyze.py summarizes every outcome and paired complete-time comparisons.
- s26_verify.py independently parses exports, cross-multiplies rational polynomials over Q(d), and audits continuation labels and frozen hashes.
- s27_analyze.sh schedules final analysis and independent checks.
- s28_freeze.sh schedules the fixed-protocol manifest.
- s29_plot.py and s30_plot.sh create standalone complete-time, operation-count and completion figures from the checked results.
- s31_document.py writes result prose and report_values.json from summary.json and verification.json.
- s32_build_report.sh renders the full LaTeX report using its bounded Makefile.

The existing Kira toolchain and seed-gate build described in ../acceleration/ are prerequisites. New binaries, objects and scheduler logs remain under ignored .tools/ directories. Published patches and build metadata identify them.

references/, training/, rollouts/, runtime_checks/ and validation directories preserve development evidence. Final references belong in reserved_references/, larger-bound checks in reference_checks/, and measured workflows in model_test/. Each workflow links to individual attempts. shared/ stores configurations, predictions and expansions once.

## Timing and interpretation

Complete times include a fresh process, preparation, model loading and prediction, IBP generation, equation selection, exact algebra, failed attempts, fallback and coefficient checks. Compression follows the stop time. The common reference calculation is reported separately. Each policy uses the same prescribed master basis within a case and batch.

The stock control uses the responsive Fermat shutdown. The instrumented native control uses the same source hook as the model while retaining native choices. Smaller deterministic regions and matched coverage subsets isolate gains that do not require ML. The count 1 + 2 * source_nonzeros per insertion estimates coefficient work; it excludes Fermat's internal polynomial operations and back substitution.

Three repeats are planned for each reserved policy and batch. Failures and skipped repeats remain explicit. Paired ratios require three exact completions from both policies for each included batch. Descriptive intervals resample physical cases, not repeated timings.

## Resources

Keep data and models on Hoffman and GitHub. Only the report is synchronized to the laptop. The managed-storage upper bound is 9,803,429,888 bytes against the 10,000,000,000-byte ceiling. At most three trials run concurrently, each with 128 MiB scratch, one calculation thread, a 2,400 MiB solver address-space limit and a 2,100 MiB solver-tree RSS limit. The enclosing worker also has time and memory limits. The ledger includes tools, publication copies, reports and temporary indexes.

Reserved results must not select thresholds, models, stopping rules or family definitions. Report gains and failures within the stated rational-kinematic, two- and three-loop domain.

One reference calculation at a time may use 256 MiB of scratch while other production trials retain 128 MiB each. A further 128 MiB allowance covers monitoring and write headroom. The common reference is outside the paired production timing.
