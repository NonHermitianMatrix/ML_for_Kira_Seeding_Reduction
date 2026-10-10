# Equation selection before construction

This extension develops the existing third model. It scores a seed and operator before Kira constructs that identity's coefficients. Decisions share seed features and stay cached for repeated generation. Native symmetry relations, preferred-basis relations, exact algebra and output-basis admission remain active.

Use `s12_reduce.py` for the current application. Validation selected the depth-twelve tree for double-box batches and the depth-eight tree for vacuum and ladder batches, with threshold 0.01. Native seed and row choices remain active. The earlier equation model remains active for the recorded 21-target sunrise batch. Other structures and ordered target lists use the previous guarded route. Both small trees and all previous models remain saved separately.

The trees use 17 features available before construction. Training contains 153,124 candidates and 12,270 positive labels from fourteen batches in eight physical profiles. Labels record integral-support membership in the final native regenerated equation set. They do not identify uniquely necessary equations or globally optimal paths. Probabilities are smoothed leaf frequencies; calibration is not established. Training/validation/test profiles are distinct, while topologies, ordered target lists and some lower-sector structure are shared.

The fixed test has 280 workflows, fourteen batches, eight new physical profiles and five alternating repeats for native, previous-release, deployed and distance-control methods. Eight additional applications receive prescribed masters without reference target coefficients. Ratios use median times per batch, equal weight per physical profile and 10,000 profile-bootstrap samples. Times include routing, input generation, inference, Kira startup, exact algebra, admission/coefficient checks, cleanup and every fallback. The experiment driver is already running. Reference/basis construction, the post-run audit and evidence compression lie outside the timer. The known two-/three-loop structures use fixed rational kinematics and symbolic d. These tests do not establish general multiscale or high-loop speedups.

Application from the project root inside a scheduled Hoffman job with node-local TMPDIR:

```bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s12_reduce.py --family-file FAMILY.json --masters-file MASTERS.json --size 128 --output ML_model_equation_selection/early_generation/application/RESULT.json.gz
```

Use the case schema in `families_test.json`: definition, topology metadata and ordered target indices. Supply the master list in the same form as the reference record's `masters` field, or an object containing that list. The output must be a new file under this extension. `--policy native` and `--policy previous` select controls. Incomplete filtered attempts retry native equations and then an enlarged seed region. Coefficient mismatches are errors. The application needs no reference target coefficients.

Code sequence:

- `s00_build.py` compiles native integration and saves patches/hashes. `s01_develop.sh` is the first build/collection wrapper; its excluded pilot is retained below.
- `s02_train.py` fits both trees. `s03_early_run.py` runs bounded native attempts. `s04_workflows.py` handles collection, fallback, checks, limits and shared storage. `s05_develop_fresh.sh` collects the corrected training and pilot.
- `s06_validate.py` compares candidates and controls; `s07_validate.sh` runs repeated validation. `s08_parity.py` checks 918,744 Python/C++ decisions with recomputed seed features.
- `s09_compact.py` converts evidence to verified shared storage. `s10_composition.py` and `s11_composition.sh` compare the existing row model.
- `s16_seed_composition.py` and `s17_seed_composition.sh` compare early, early+seed and early+seed+row routes. Selection requires at least 1% complete-time saving, 5% preparation saving and no fallback. Adding another model requires at least 1% incremental saving and no fallback.
- `s12_reduce.py` is the application. `s13_freeze.py` fixes models, code, routing and the reserved protocol. `s14_test.py` runs independent tests and audits. `s15_test.sh` runs the cached selection, freezes once, tests and summarizes. Completed freezes must remain fixed.
- `s18_analyze.py` summarizes all results. `s19_plot.py` draws plots. `s20_check_release.py` checks the deployed route and preceding frozen hashes.
- `s21_document.py` writes documentation; `--data-commit COMMIT` also writes the report and immutable citation. `s22_finish.sh` runs analysis, plots, release checks and documentation. Compile the report after data publication.

Data folders:

- `training/` contains four added ladder batches; ten unchanged batches remain in the parent training folder. Models list all paths and hashes.
- `validation/` retains 77 initial candidate/control workflows, 84 repeated candidate workflows, 72 row-composition workflows and 96 seed-composition workflows, including rejected configurations and fallback costs.
- `trained_model/` contains trees, deployment rules, freeze and deployment audit. `model_test/` contains fixed tests, eight applications, exact audit, summary and plots.
- `references/` holds new native references; earlier references remain at their recorded paths.
- `objects/` stores repeated exact payloads once. Load `early-shared-v1` workflows with `s04_workflows.read` to restore complete data and verify object SHA256 hashes. Every save checks a lossless round trip.
- `development_overlap/` retains the excluded initial pilot whose added profiles overlapped earlier reserved definitions. None of its rows, models or outcomes enters final training or claims. `split_audit.json` records corrected separation.
- `bottleneck_audit/` preserves twelve diagnostics and original scripts from `.tools/bottleneck-audit/`. Those scripts retain original execution paths. Logged intervals include wrapper overhead and must not replace final internal-stage timings.

Each native attempt uses one thread, a 70-second limit (90 seconds for references), a 2,400 MiB address-space cap, a 2,100 MiB sampled process-tree RSS cap and a 16 MiB scratch cap. One experiment job runs at a time. `resource_plan.json` bounds combined project storage below 10,000,000,000 bytes. Scientific data stay on Hoffman and GitHub; the report also stays locally.

<!-- checked-results -->
The current early equation policy predicts which seed/operator identities to construct. On eight fresh physical profiles, its complete-time ratio to matched native choices is 0.942907, with descriptive 95% interval [0.915,0.970]. Its preparation ratio is 0.637888, with interval [0.546,0.734]. The complete-time ratio to the previous release is 0.943456, and the ratio to the distance control is 0.933657. All 280 comparisons and eight basis-only applications pass exact checks. The selected route keeps native seed and row choices and preserves the preceding sunrise policy. These results include every fallback cost and cover known two-/three-loop structures at fixed rational kinematics with symbolic d.

The audit checks 94,970 coefficient pairs, including 1,915 distinct pairs. It retains 0 failed attempts from all methods. Maximum observed process-tree RSS is 53.46 MiB; maximum scratch is 1.39 MiB.
<!-- checked-results-end -->
