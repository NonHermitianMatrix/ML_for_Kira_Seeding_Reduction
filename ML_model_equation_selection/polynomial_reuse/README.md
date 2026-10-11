# Exact polynomial reuse and persistent workers

The current restricted vacuum-family interface shares exact loop-order transformations and Taylor factors, with an optional persistent worker. Validation selects both arithmetic changes and preserves the simple extreme ordering. Across eight reserved batches, calculation-time ratio to the preceding direct arithmetic is 0.372, and full-worker ratio is 0.682. Arithmetic plus persistent execution has full-time ratio 0.365 across three specified overlapping streams. All 352 reserved applications pass exact checks; 28860 expanded coefficient positions also match the older loop-dependent formula. These gains come from exact reuse and process startup. The unchanged learned model remains optional. General native high-loop IBP generation retains its earlier scope.

This extension retains the exact selected recurrence and the independent Taylor check. It builds integer matrices for z=L(d-2) once per loop order, converts each polynomial to a common denominator once, and reuses Taylor factors within each physical mass profile. The preceding frozen pre_reduction, batch_reuse and native policies remain unchanged. No model was trained in this extension.

The input schema follows ../pre_reduction/: a requests list with unique id values, family=coupled_vacuum_unit_massless, 2--4 distinct positive integer mass_ratios, mass_scale_squared=1, nonnegative target powers with total 1--14, and positive integer loop orders. It requires unit massless powers. Limits remain eight profiles, 512 total targets, 128 targets per profile, 32 loop values and 12,000 intermediate equations. This is one restricted vacuum topology with mass profiles.

Use a bounded Hoffman scheduler allocation, without Python -O:

    .tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s02_application.py --input request.json --output ML_model_equation_selection/polynomial_reuse/model_test/application.json

--variant deployed uses the frozen validation result. The alternatives baseline, transforms, taylor and both isolate each arithmetic change. --policy extreme is the preceding validation-selected default; --policy model uses the unchanged compiled four-tree model from ../batch_reuse/. A failed exact comparison invokes the preserved Kira route and includes the failed attempt in its calculation time.

For several batches, start the same command with --stream and send one JSON object per line, with input and output paths. Paths resolve from the project working directory; absolute project paths also work. The input must stay within the project and the output within this module. Each response reports success or the request error. The worker keeps at most 128 transforms and one unchanged model, while each new mass profile gets fresh mass-dependent Taylor terms. It accepts at most 64 commands by default; --max-requests can lower that limit. Each command and input file is limited to 1 MiB. An invalid request reports an error and permits later requests; exceeding the line or command cap stops the process.

Validation uses four new batches, masses 2003--3000, four variants and three repetitions (48 applications). It selects both arithmetic changes before the reserved test. The test uses eight new batches, masses 4001--6006, four variants and five repetitions (160 applications). Each batch contains profiles with two, three and four massive denominators and loops 1--12. The total massive power is at most 14, and requested targets per profile are 16, 48 or 96, limited by the available distinct vectors.

The stream study runs four configurations on sequences of four, four and eight batches, with three repetitions: 36 process-sequence runs and 192 batch applications. The eight-batch sequence reuses the two four-batch inputs. Its descriptive aggregate has no statistical interval. The frozen test and stream comparisons use the same default simple ordering. Model retention is checked separately in the integration tests.

complete_seconds includes request reading, model loading if enabled, selection, exact recurrence, independent verification, loop expansion and fallback. external_seconds also includes Python startup and saving results. The matched baseline and all arithmetic variants use the same content-addressed output writer. Ratios use geometric means of within-batch median ratios; descriptive cold-test intervals resample eight groups. These matched ratios must not be multiplied into earlier full-worker results with a different writer or input set.

objects/ contains gzip JSON blocks addressed by the SHA256 of canonical decompressed JSON. Coefficient blocks and source evidence are separate so variants share identical outputs. Per-application records refer to these hashes. The independent audit verifies 352 applications, identical method outputs and every distinct expanded coefficient against the older loop-dependent formula. The 2,126 arithmetic checks cover exact substitution, Taylor construction and cache eviction. Integration tests cover changed masses and loop orders, invalid input, request limits, retained model evaluation and a forced Kira fallback.

Script order:
- s00_arithmetic.py: Shared exact Taylor terms and integer loop-order transformations.
- s01_engine.py: Preserve exact reduction and verification while reusing arithmetic work.
- s02_application.py: Single-request and bounded persistent-worker interfaces.
- s03_check.py: Independent arithmetic and persistent-interface checks.
- s04_study.py: Fresh validation and reserved single-request and stream comparisons.
- s06_audit.py: Audit stored exact results against the older loop-dependent formula.
- s07_analyze.py: Separate arithmetic and process-reuse effects in the complete measurements.
- s08_plot.py: Export standalone figures for exact arithmetic and persistent processing.
- s09_document.py: Update the report and READMEs from frozen arithmetic-reuse measurements.
- s10_release_check.py: Check frozen methods, exact evidence, report references and resource bounds.

s05_run.sh is the original validation, freeze and test scheduler wrapper. Preserve its completed records; new policy development requires fresh inputs and a separate module. s11_finish.sh documents and checks the frozen results and builds the PDF; --data-commit pins their immutable GitHub citation. s06_audit.py, s07_analyze.py and s08_plot.py independently reconstruct the audit, summaries and figures from preserved results.

resource_plan.json starts from a fresh full-project allocation audit and reserves retained evidence, Git copies, pack/index space, PDF output, local report growth and drift below the combined 10 GB ceiling. Experiments use one CPU and a 2,800 MiB address-space limit. Kira fallback retains its 90-second, 1.5 GiB sampled tree-RSS and 64 MiB scratch limits. Generated scientific records stay on Hoffman and GitHub; only the report also synchronizes locally.
