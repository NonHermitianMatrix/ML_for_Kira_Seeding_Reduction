# Exact pre-reduction and checked direct execution

The earlier learned equation policy supplies a terminating dependency graph for the restricted coupled scalar vacuum family. Exact polynomial substitutions solve this graph, and an independent Taylor construction checks every coefficient. Kira remains the fallback. The model is reused without retraining.

Validation selects the simple direct route. On 200 reserved applications, its calculation-time ratio to the preceding combined learned Kira route is 0.306, with descriptive interval [0.246,0.373]. The full-worker ratio is 0.430. All exact checks pass with zero reserved fallbacks. The earlier trained four-tree model remains available with unchanged weights; learned/direct versus simple/direct has calculation ratio 0.982. The comparison does not establish a further complete-time advantage from learned ordering over both direct controls. This is a checked shortcut for the restricted coupled vacuum family. Native IBP generation keeps its earlier supported domains.

The request schema matches batch_reuse/s17_application.py: requests contains objects with a unique id, family=coupled_vacuum_unit_massless, 2--4 distinct positive integer mass_ratios, unique targets with nonnegative powers and total power 1--14, positive loops and mass_scale_squared=1. Limits are eight profiles, 512 total targets, 128 targets per profile, 32 requested loop values and 12,000 selected intermediate equations. Unit massless powers are required. These profiles share topology; they are not arbitrary graph families.

Run inside a bounded scheduler allocation, without Python -O:

    .tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s01_application.py --input request.json --output ML_model_equation_selection/pre_reduction/model_test/application.json

The default --mode deployed uses the frozen validation choice. Other modes are baseline (preceding learned Kira route), model (pre-reduce, then Kira), direct_model (compiled unchanged forest and exact recurrence), direct_extreme (simple recurrence), and direct_analytic (Taylor construction checked by the simple recurrence). Retained extreme and analytic modes submit completed relations to Kira and occur only in the development pilot. Scores estimate log weighted equation cost, without a confidence-calibration claim.

Each direct result must equal the independent exact formula in Q[z] before substitution z=L(d-2). A failed check retries Kira with all costs included. Invalid requests are rejected. Returning a completed direct reduction avoids invoking Kira for this supported case. The new direct path does not accelerate native IBP generation.

The earlier model and training evidence remain in ../batch_reuse/. Validation uses six groups, mass ratios 503--796 and 90 applications. The frozen test uses eight further groups, masses 809--1296 and 200 applications. The ranges are disjoint from prior model training. Five methods have five repetitions per test group. Validation fixes the default before the reserved test. The analytic control includes an independent recurrence check.

Calculation time includes input reading, loading, inference, preparation, exact algebra, checks, loop substitution and fallback. external_seconds adds interpreter startup and evidence saving. Ratios use geometric means of batch median ratios and descriptive bootstrap intervals over eight groups.

All exact source choices, coefficients and raw Kira outputs reside in objects/, addressed by SHA256 of decompressed JSON. Identical payloads share one file. Direct outputs contain an empty raw Kira export because no Kira process ran. Every record hash is verified. The independent audit checks each distinct expanded batch against the older loop-specific oracle and reads every raw Kira coefficient with the earlier reader.

The initial eight pilot runs and their matching source remain in pilot/ and development_pilot/. The storage guard interrupted the first reserved run after two complete applications; the completed coefficient record from the interrupted serialization remains in model_test/interrupted/. Its missing worker time excludes it from timing. The remaining frozen trials resumed with unchanged code, inputs and policy after increasing the reserved storage allowance within 10 GB.

Script order:
- s00_contract.py: Exact polynomial pre-reduction of the restricted vacuum identities.
- s01_application.py: Pre-reduce selected exact identities, then finish and check with Kira.
- s02_study.py: Fresh disjoint validation and reserved comparisons of exact pre-reduction.
- s04_check.py: Independent arithmetic, application, fallback and final-output checks.
- s06_analyze.py: Matched complete-time ratios and exactness summaries.
- s07_plot.py: Standalone plots from matched independent measurements.
- s08_document.py: Update scientific text and READMEs from checked measurements.
- s09_release_check.py: Verify frozen code, exact evidence, report references and resource bounds.
- s12_check_deployed.py: Verify the public deployed interface and its exact expanded output.

s03_run.sh preserves the pilot launch. s05_run.sh runs arithmetic checks, validation, freeze, testing, fallback checks and the independent audit. The saved s11_resume.sh continues an interrupted test without changing the freeze. s10_report.sh runs analysis, plots, documentation, release checks and the PDF build after testing. Preserve completed experiments; use a new directory for further policy selection.

The resource plan bounds the complete project below 10 GB. One experiment job runs at a time with a 2,800 MiB address-space limit. Kira retains its 90-second, 1.5 GiB sampled tree-RSS and 64 MiB scratch limits. Generated data stay on Hoffman and GitHub. Report files also synchronize locally.
