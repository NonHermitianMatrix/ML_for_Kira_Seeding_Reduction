# Parallel seed evaluation and exact row features

The production entry is ../integrated_runtime/s108_reduce.py. It retains the trained weights, thresholds, candidate regions, exact Kira algebra and validation-selected routing. Seed arithmetic evaluates independent output components together while preserving the addition order of each float32 result. Row features use exact Euclidean modular inverses, direct evaluation of short integer literals, and contiguous coefficient storage.

All 144 final-candidate validation workflows and 640 confirmation workflows preserve exact coefficients, seed probabilities, source-row digests and committed operation counts. The complete-time new/preceding ratios for seed, row and combined execution are 0.989778, 0.989961, 0.984075. All fallback costs are included. All three complete-time intervals include one, so the component gain is clearer than the full-workflow change. Seed and combined aggregate costs remain above the native control; the row-only interval against native also includes one. See confirmation_summary.json for descriptive intervals and topology results.

The initial Euclidean-only candidate failed the fixed validation conditions. rejected_euclid/ preserves its code/build snapshots, 144 workflow records, summary and component tests. Its complete row ratio was 1.02739 and row-decision ratio 1.01713. The final candidate changes arithmetic/storage only and uses fresh validation records with literal_ attempt names. No confirmation outcomes select its changes.

The final validation uses three physical profiles, six batches, four methods and three repetitions for each implementation. The frozen confirmation uses eight previously defined physical profiles, sixteen batches and five repetitions. It repeats implementation measurements on existing profiles and adds no independent-family evidence. Both implementations use identical wrappers, exact checks, resource bounds and evidence storage.

The timing interval includes preparation, model loading, predictions, fresh IBP generation, exact elimination, back substitution, reference checks and every fallback. Reference preparation, interpreter startup, release-hash verification, initial routing lookup and evidence compression remain outside it. Summary ratios use per-batch medians and equal physical-profile geometric weighting. Bootstrap intervals are descriptive and keep related batches together. Implementation savings and ML-versus-native savings answer separate questions.

All successful outputs receive independent rational-coefficient verification over Q(d). Eight further application checks supply only family definitions, targets and master indices; postrun comparisons verify their coefficients. The model does not require known target coefficients during production. Its basis-admission check triggers the fixed fallback when necessary.

A bounded production invocation is:

    .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s108_reduce.py --family-file CASE.json --masters-file MASTERS.json --size 32 --policy auto --verify-release --output Kira_comparison/parallel_inference/application/CASE.json.gz

Run on a scheduled node with one arithmetic worker, h_data=3G, h_vmem=6G and outer address limit 2800 MiB. At most two trials run together; each gets 128 MiB scratch and a 2400 MiB native-child address limit. resource_plan.json reserves 9,893,372,928 combined bytes, below the user's decimal 10 GB ceiling. New retained evidence is capped at 12 MiB, new tools at 24 MiB. Tools stay outside Git. Earlier data and old shared-content hashes remain immutable. Rebuilds change binary hashes and require a new freeze.

Read workflow files with integrated_runtime/s105_parallel_records.read_record. Their attempts live in attempts/; large fields resolve SHA256-named gzip payloads in this folder's shared/ or the older integrated_runtime/shared/. Every raw failed attempt remains available.

The execution order in integrated_runtime/ is s109_build_parallel.sh, s111_validate_parallel.sh, s118_freeze_parallel.sh, s114_confirm_parallel.sh and s116_finalize_parallel.sh. After exact checks, s122_document_parallel_readmes.py updates guides, s119_document_parallel.py writes the scientific text from summaries, and s121_build_parallel_report.sh builds plots and the PDF.

Script roles:
- s105_parallel_records.py writes bounded immutable records and reuses existing field payloads.
- s106_run_parallel.py runs one native attempt and selects old/new arithmetic.
- s107_workflow_parallel.py executes fixed fallbacks and includes all attempt costs.
- s108_reduce.py exposes native, seed, row, both and automatic production modes.
- s109_build_parallel.sh compiles both components, runs their fixtures and builds native Kira.
- s110_compare_parallel.py alternates old/new execution and checks decision parity.
- s111_validate_parallel.sh runs the three validation profiles.
- s112_summarize_parallel.py includes every planned workflow and computes paired statistics.
- s113_freeze_parallel.py enforces the predefined adoption conditions and hashes the implementation.
- s114_confirm_parallel.sh runs the eight-profile confirmation with at most two jobs.
- s115_audit_parallel.py independently parses exports and compares exact rational coefficients.
- s116_finalize_parallel.sh summarizes confirmation and runs application and coefficient checks.
- s117_check_parallel_application.py checks eight basis-only production calls.
- s118_freeze_parallel.sh summarizes validation and freezes only an eligible candidate.
- s119_document_parallel.py writes equations, results and the report conclusion.
- s120_plot_parallel.py plots complete timing against the previous implementation and native choices.
- s121_build_parallel_report.sh renders the report and its plot.
- s122_document_parallel_readmes.py writes these guides and the release record.
- s123_prepare_parallel_report.sh checks completed jobs and bounds, publishes data and builds the report for review.

This folder's s00_check_arithmetic.cpp checks 100,000 inverses, short literal edge cases and 1,000 row-feature groups. s01_check_seed.py checks bitwise probability parity and all six threshold masks in 36 development contexts. build.json identifies the native patch and headers; freeze.json fixes code, binaries, weights and test inputs; verification.json and application_verification.json retain independent checks.
