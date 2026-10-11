# ML for Kira seed selection and reduction

This project studies lightweight models for selecting IBP seeds, equations and allowed elimination steps while exact arithmetic retains responsibility for the reductions.

The [integral collection](integrals/README.md) contains 17,100 family instances, 57,979 family-local master entries and 2,301,272 targets. It includes 2,247 one-loop families, 1,353 two-loop families and 1,350 families at every order from three through twelve. The later additions contain 1,250 new mass profiles per loop order for restricted coupled vacuum integrals, following the previous 100 profiles per order from two through twelve. Their analytic bases, Euler IBP and mass partial-fraction identities give exact reverse constructions. The profiles share a small set of graph structures; the collection does not represent arbitrary high-loop scattering integrals.

[master_integrals/](integrals/master_integrals/README.md) stores definitions and bases; [target_integrals/](integrals/target_integrals/README.md) stores targets; [master_to_target/](integrals/master_to_target/README.md) stores master expansions, seeds, equations, constructions, elimination traces and operation counts. Matching IDs connect all records. [higher_loops/](integrals/higher_loops/README.md) and [expansion_1000/](integrals/expansion_1000/README.md) document the mathematical domain and independent checks.

The grouped split gives 1,610,890 training targets in 11,963 families and 690,382 test targets in 5137 families. Related added mass profiles remain together across loop orders, and prior assignments remain fixed. The separate [training](integrals/training/README.md) and [testing](integrals/testing/README.md) views link to canonical data without copying it. Shared lower-sector physics can occur across profiles.

Both the [seed model](ML_model_seed_selection/README.md) and [reduction model](ML_model_reduction/README.md) completed twenty new passes over the expanded training set, starting from their saved weights and optimizer states. Their previous progress remains recorded separately. Both frozen expanded-data tests are complete; their measurements, exact checks and six plots per model occupy each model_test/ folder. Earlier test artifacts remain in model_test/archive_before_expansion_250/. The scientific report is rebuilt from the current checked results.

The [report PDF](report/report.pdf), [LaTeX source](report/report.tex), [bibliography](report/references.bib) and [rules](rules.md) accompany the project. Hoffman is the primary working location. Generated integral data, encoded examples, trained models and tests stay on Hoffman and GitHub; only report files are also synchronized locally. The combined storage ceiling is 10 GB.

Hoffman Git commands use `module load git/2.40.0`. To keep the project below 10 GB, the repository retains all working files and published history while using a partial Git object cache. GitHub supplies historical file objects when a command needs them; routine evaluation reads the complete working files directly.

<!-- exact-kira-sufficiency -->
The exact Kira sufficiency test is complete for 690,382 reserved targets in 5,137 families. Predicted seeds suffice for 652,517 targets (94.515%). The full candidate pool suffices for 690,382 (100.000%), and background identities without IBP seeds suffice for 26,915 (3.899%). All symbolic decisions agree with three independent finite-field row-space checks. The model and threshold remain unchanged. This test checks existence of a reduction within the stored identity pools; it does not reconstruct all master coefficients or measure a native Kira speedup.

See the [Kira sufficiency test](ML_model_seed_selection/kira_sufficiency_test/README.md) for the equations, fixed protocol, raw symbolic remainders and independent checks.

<!-- kira-cost-comparison -->
[Kira cost comparisons](Kira_comparison/README.md) now measure complete symbolic reductions, exact coefficient checks, model overhead, fallback, equation counts, row-operation counts and memory. The comparison is complete and independently checked. The main experiment contains 792 trials in 19 family cases; the direct native seed-bound comparison contains 84 trials in seven independent-basis families. Against Kira with the full stored source pool, learned seeds have geometric mean complete-process/prepared-input time ratios 1.720/1.116, and learned rows have ratios 1.719/1.205. Learned native seed bounds have ratios 1.596/1.344 against default native bounds and 1.671/1.373 against restricted native bounds. Against the control with seed bounds taken directly from target indices, the native learned ratios are 1.425/1.141. Ratios use matched case medians from three repeats; values below one indicate lower time. Complete-process time includes loading, inference, exact algebra, fallback and coefficient checks. Prepared-input time excludes family and model loading. Completion counts, all resource outcomes, individual cases and operation measures appear in summary.json and native_seed/summary.json. The direct native test learns sector envelopes. The row comparison in that experiment uses fixed source identities and changing target rows; the live-matrix comparison below tests changing identity rows inside Kira.


<!-- kira-live-matrix -->
## Live matrix comparison

Completed 84 final trials in seven held-out independent-basis families, with 0 incomplete trials. The learned/stock complete-time ratio is 1.305. The learned/instrumented-native forward-stage ratio is 276.149, or 62.270 after subtracting recorded model loading. Summed median committed coefficient-operation counts are 5771 for the learned policy and 5070 for the native policy.

The code, frozen protocol, exact operation records and plots are in [Kira_comparison/live_matrix](Kira_comparison/live_matrix/). The model acts inside Kira's symbolic forward phase on changing identity rows. The report distinguishes this test from the earlier fixed-source target-row procedure.

<!-- native-acceleration -->
The native integration in [Kira_comparison/acceleration](Kira_comparison/acceleration) filters individual IBP seeds before generation and evaluates the unchanged row network in Kira's process. The reserved comparison has 720 planned records, 616 measured trials and 590 exact completions; remaining repeats after a failed trial are explicitly skipped. ml_lower: complete-time ratio to restricted native Kira 1.295050 (descriptive 95% interval 1.156164–1.542104, 20 complete paired batches); 100 exact completions, 4 failed trials and 16 skipped repeats. row_cpp: complete-time ratio to restricted native Kira 1.023629 (descriptive 95% interval 0.998189–1.053330, 21 complete paired batches); 105 exact completions, 3 failed trials and 12 skipped repeats. combined: complete-time ratio to restricted native Kira 1.983350 (descriptive 95% interval 1.574863–2.476497, 15 complete paired batches); 75 exact completions, 9 failed trials and 36 skipped repeats. All ratios include complete checked calculation time on complete paired cohorts. The report gives the controls, failures, descriptive intervals and one-loop scope.

<!-- whole-expression-confirmation -->
The whole-expression interface uses the frozen seed model, Kira's early master check, exact supplied-equation reduction and full-pool fallback. The reserved comparison contains 360 planned records, 348 measured trials and 345 exact completions. Its complete-time ratio to the full-pool supplied-equation control is 0.943782 (descriptive 95% interval 0.863046–1.041560; 23 complete paired batches), and its ratio to the fixed 64-seed distance control is 0.603585 (descriptive 95% interval 0.534379–0.677998; 23 complete paired batches). The full-pool control completed 0 additional batches and the learned method completed 0 additional batches. Both comparisons start from the same existing identity pool and include loading, prediction, equation export, exact algebra, failed attempts, fallback and checks. Offline pool generation is outside both measurements. These are constructed targets from twelve original-held-out one-loop box instances in six kinematic groups.

The separate two-loop transfer has 60 exact completions. For 64 targets the compiled learned-row pipeline took a median 12.460 seconds against 12.770 seconds for restricted native Kira, a 2.4% reduction. Its advantage over the deterministic compiled source control remains unresolved, and the full-pool control was faster at 11.773 seconds. Both seed-containing policies required fallback in every 64-target repeat.

Code, raw measurements and checks: [Kira_comparison/acceleration](Kira_comparison/acceleration).

<!-- matched-admission-confirmation -->
The additional matched-admission confirmation applies the same early master check and full-pool fallback to learned seeds and the 64-seed distance control. It contains 360 planned records, 348 measured trials and 345 exact completions. The learned complete-time ratios are 0.931643 (descriptive 95% interval 0.844721–1.030866; 23 complete paired batches) against the full pool and 0.925206 (descriptive 95% interval 0.847770–1.023721; 23 complete paired batches) against the matched distance control. The full-pool control completed 0 additional batches, and the learned method completed 0 additional batches. This repeats the same twelve physical family instances; it is not a new-family test. The first comparison is fully retained, and its distance control lacks the early admission check.

<!-- single-target-result -->
The predefined single-target comparison gives 8.6% lower geometric mean complete time against the full-pool Kira control and 8.7% lower time against the distance control with the same early check. Both descriptive intervals lie below one across all twelve held-out instances, with five exact repeats per method. The earlier confirmation gave 7.8% lower time against the full pool for this batch size. The sixteen-target intervals include one. This measured benefit applies to one constructed target expression at a time using an existing IBP identity pool; it does not establish a native Kira or general high-loop speedup.

<!-- responsive-fermat-exit -->
The responsive Fermat shutdown comparison contains 480 planned records, 416 measured trials and 400 exact completions in twelve new held-out one-loop box instances. For one target, the modified learned workflow has a complete-time ratio of 0.384629 to the original learned workflow (descriptive 95% interval 0.342069–0.452551; 12 paired batches), with geometric mean times 5.528 and 2.126 seconds. For sixteen targets the corresponding ratio is 0.685856 (interval 0.540426–0.844099). Against the full pool with the same shutdown improvement, the single-target learned ratio is 0.690298 (interval 0.423691–0.931312). All completed reductions matched exact references. Both learned methods use the same original weights, threshold, early master check and fallback. The shutdown change preserves symbolic operations and also applies to the full-pool control. These measurements use existing IBP identity pools; they exclude their original generation.

Code, measurements, source patch, frozen inputs and independent checks are in Kira_comparison/fast_expression/. The report explains the separate shutdown and learned-seed effects in kira_fast_expression.tex and figures/responsive_exit_times.pdf.

<!-- native-multiloop-results-begin -->
## Complete multiloop cost comparison

The fixed complete-generation experiment has 324 planned workflows, 324 measured workflows and 324 exact completions.

The selected seed policy's complete-time ratio to responsive stock Kira is 0.741945 (12 paired batches).

Seed-to-stock time ratios are 0.563457 for two-loop boxes, 1.265710 for three-loop vacua, 0.572691 for three-loop ladders. The aggregate seed time interval includes one; gains are specific to the tested family classes. The row-time interval also includes one.

The cost-trained row policy's complete-time ratio to instrumented native Kira is 1.007901 (12 paired batches); its forward coefficient-operation ratio is 1.003162 (12 paired batches).

These are paired, three-repeat comparisons at rational kinematics with symbolic d. Results include inference, native generation, exact algebra, verification and fallback. The common reference basis is prepared separately.

The independent audit passed. Family-level results and completion counts must accompany aggregate ratios; none establishes a universal speedup.

[Methods, raw evidence and outcomes](Kira_comparison/multiloop_native/README.md). Original integral records and neural checkpoints remain unchanged.
<!-- native-multiloop-results-end -->


<!-- integrated-runtime-current -->
The current native-integration extension is in Kira_comparison/integrated_runtime/. It combines compiled seed inference, complete-trajectory row policies and matched native/deterministic controls. The model additions are in ML_model_seed_selection/runtime_inference/ and ML_model_reduction/runtime_training/. The initial comparison completed all 560 workflows. A 400-workflow implementation confirmation on the same eight physical profiles also completed every target with exact reference agreement. In the confirmation, seed, row and combined complete-time ratios to the smaller native control are 1.154805, 0.998979, 1.159119. The seed ratio for boxes is 0.963700; the aggregate row operation ratio is 0.985327, but its forward-stage time ratio is 1.041202. Neither model has a universal runtime advantage. Read summary.json and pair_reserved_summary.json for grouped intervals, topology results and all failed attempts. Earlier data, checkpoints and tests remain preserved. See that folder's README for the integration entry point, exact checks, resources and reproducible execution order.

<!-- shared-evaluation-current -->
The preceding implementation is Kira_comparison/integrated_runtime/s88_reduce.py, described in [the current integration guide](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/main/Kira_comparison/integrated_runtime/fast_evaluation). It reuses seed-network affine prefixes and symmetric row-cancellation calculations while preserving weights and algebraic choices. All 800 implementation-confirmation workflows and 180 validation workflows complete with exact coefficient and decision parity. New/preceding complete-time ratios for seed, row, both and automatic execution are 0.982155, 1.005713, 0.996704, 0.982498. These ratios retain all fallback attempts. Separate comparisons with the new native control appear in confirmation_summary.json; an implementation gain does not itself establish a general ML advantage. Earlier checkpoints and implementations remain preserved.

<!-- parallel-inference-current -->
The latest production entry is Kira_comparison/integrated_runtime/s108_reduce.py. [The current guide](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/main/Kira_comparison/parallel_inference) describes parallel neural outputs, exact modular inverses and reduced row-feature allocation. All 144 final-candidate validation workflows and 640 confirmation workflows preserve exact coefficients, seed probabilities, source-row digests and committed operation counts. The complete-time new/preceding ratios for seed, row and combined execution are 0.989778, 0.989961, 0.984075. All fallback costs are included. All three complete-time intervals include one, so the component gain is clearer than the full-workflow change. Seed and combined aggregate costs remain above the native control; the row-only interval against native also includes one. See confirmation_summary.json for descriptive intervals and topology results. The rejected development candidate and all preceding releases remain preserved.

## Target-dependent equation selection

The trained third model and native integration are in [ML_model_equation_selection](ML_model_equation_selection/README.md). The current s35_reduce.py route uses the recorded 21-target two-loop sunrise domain with native seed and row choices. Six fresh profiles give complete-time ratio 0.9942 and preparation ratio 0.7848. Other domains and combinations with earlier learned policies retain native equation choices. The report preserves the slower broad and combined results, descriptive intervals, exact checks and current limits.

<!-- early-equation-release -->
The current early equation policy predicts which seed/operator identities to construct. On eight fresh physical profiles, its complete-time ratio to matched native choices is 0.942907, with descriptive 95% interval [0.915,0.970]. Its preparation ratio is 0.637888, with interval [0.546,0.734]. The complete-time ratio to the previous release is 0.943456, and the ratio to the distance control is 0.933657. All 280 comparisons and eight basis-only applications pass exact checks. The selected route keeps native seed and row choices and preserves the preceding sunrise policy. These results include every fallback cost and cover known two-/three-loop structures at fixed rational kinematics with symbolic d.

See [early equation selection](ML_model_equation_selection/early_generation/README.md).
<!-- early-equation-release-end -->

<!-- higher-loop-acceleration -->
The higher-loop extension generates exact Euler and mass partial-fraction equations for the restricted coupled vacuum family, then uses Kira's user-defined-system solver. A shared variable z=L(d-2) supports every positive loop order mathematically. Tests cover L=1,...,12, with additional applications at 13, 16, 24 and 32. Across six reserved batches, the deployed route has complete-time ratio 0.155 (descriptive interval 0.132--0.184) to separate full-pool reductions. The learned separate-loop route has ratio 0.911 (descriptive interval 0.815--0.986) to the same full-pool baseline. Learned/shared versus rule/shared has ratio 0.968 (descriptive interval 0.927--1.003). Validation selects the extreme route. These are supplied-identity results, with exact coefficient checks and all runtime costs; they do not establish a generic high-loop native Kira speedup.

See [ML_model_equation_selection/higher_loops/README.md](ML_model_equation_selection/higher_loops/README.md).
<!-- higher-loop-acceleration-end -->


<!-- batch-reuse-begin -->
## Learned equation reuse across target batches

The earlier batch interface is [batch_reuse](ML_model_equation_selection/batch_reuse/README.md). It trains a batch equation-cost model, shares exact coefficient checks across loop orders and combines independent systems in one Kira call. All 460 reserved applications pass exact checks. The selected combined route has complete-time ratio 0.220 to the preceding separate workflow. Matched simple-rule and inference-backend comparisons remain recorded. General high-loop native IBP generation is outside this scope.
<!-- batch-reuse-end -->

<!-- pre-reduction-current -->
Validation selects the simple direct route. On 200 reserved applications, its calculation-time ratio to the preceding combined learned Kira route is 0.306, with descriptive interval [0.246,0.373]. The full-worker ratio is 0.430. All exact checks pass with zero reserved fallbacks. The earlier trained four-tree model remains available with unchanged weights; learned/direct versus simple/direct has calculation ratio 0.982. The comparison does not establish a further complete-time advantage from learned ordering over both direct controls. This is a checked shortcut for the restricted coupled vacuum family. Native IBP generation keeps its earlier supported domains.

See [exact pre-reduction](ML_model_equation_selection/pre_reduction/README.md).
<!-- pre-reduction-current-end -->

<!-- polynomial-reuse-current -->
The polynomial-reuse interface shares exact loop-order transformations and Taylor factors, with an optional persistent worker. Validation selects both arithmetic changes and preserves the simple extreme ordering. Across eight reserved batches, calculation-time ratio to the preceding direct arithmetic is 0.372, and full-worker ratio is 0.682. Arithmetic plus persistent execution has full-time ratio 0.365 across three specified overlapping streams. All 352 reserved applications pass exact checks; 28860 expanded coefficient positions also match the older loop-dependent formula. These gains come from exact reuse and process startup. The unchanged learned model remains optional. General native high-loop IBP generation retains its earlier scope.

See [exact polynomial reuse](ML_model_equation_selection/polynomial_reuse/README.md).
<!-- polynomial-reuse-current-end -->

<!-- exact-backend-current -->
The latest restricted vacuum-family route uses compiled expansion and binary output with a fixed recurrence rule. Its complete-process time ratio is 0.850 and its ratio including output decoding is 0.858, with descriptive interval [0.800,0.914]. The persistent-stream ratio including decoding is 0.725. 948 reserved applications across the original and compiled-reader comparisons pass exact checks. Learned versus validation-selected fixed-rule time ratio is 1.017, with interval [0.969,1.070]. This interval includes one, so the reserved comparison does not establish a further time reduction from learned choices. The deployed default uses the fixed validation choice. These results retain the restricted vacuum-family scope; native IBP generation keeps its earlier supported domains.

See [exact arithmetic and batch strategies](ML_model_equation_selection/exact_backend/README.md).
<!-- exact-backend-current-end -->

<!-- cumulative-results-begin -->
The direct cumulative comparison uses eight new groups of three restricted vacuum mass profiles, loop orders 1--12, and five repetitions of three methods. All 120 workflows pass exact checks. Relative to the original saved Kira binary with the full supplied equation pool and separate loop reductions, the final route has total-time ratio 0.001839, speedup 543.815x (descriptive 95% interval 488.134--605.064), and 99.82% less time, including startup, saving and output reading. Against the earlier full-pool pipeline binary, the speedup is 81.170x. The selected final route uses a fixed recurrence and exact direct arithmetic. The result measures the complete restricted-family replacement; it does not establish a corresponding native general-IBP or ML-only speedup.
<!-- cumulative-results-end -->
