# Exact integer arithmetic and learned batch strategies

The latest restricted vacuum-family route uses compiled expansion and binary output with a fixed recurrence rule. Its complete-process time ratio is 0.850 and its ratio including output decoding is 0.858, with descriptive interval [0.800,0.914]. The persistent-stream ratio including decoding is 0.725. 948 reserved applications across the original and compiled-reader comparisons pass exact checks. Learned versus validation-selected fixed-rule time ratio is 1.017, with interval [0.969,1.070]. This interval includes one, so the reserved comparison does not establish a further time reduction from learned choices. The deployed default uses the fixed validation choice. These results retain the restricted vacuum-family scope; native IBP generation keeps its earlier supported domains.

The implementation keeps each exact polynomial as integer coefficients over one positive common denominator. The recurrence and independent Taylor construction use that representation, and GMP 6.0.0 expands z=L(d-2) into every requested loop order. Each output coefficient retains a reduced integer numerator and denominator. A small regression tree selects one of five recurrence rules from measured total cost. Its 49 features include powers, mass differences, loop orders and shared immediate predecessors.

The request schema remains requests=[...], with unique id, family=coupled_vacuum_unit_massless, mass_scale_squared=1, 2--4 distinct positive integer mass_ratios, nonnegative target powers with total 1--14, and positive loop orders. Unit massless powers are required. Limits remain eight profiles, 512 total targets, 128 targets per profile, 32 loop values and 12,000 intermediate equations. These are mass profiles of one restricted topology.

Use the current interface inside a bounded Hoffman scheduler allocation, without Python -O:

    .tools/seed-model/venv/bin/python ML_model_equation_selection/exact_backend/s15_application.py --input request.json --output ML_model_equation_selection/exact_backend/reader_final_test/application.json

The default --mode deployed follows reader_final_deployment.json. Explicit modes baseline, integer, native_json, native_binary and learned support the frozen controls. --policy can select extreme, ascending, descending, mass_gap or first for an explicit comparison. --stream accepts JSON lines with input and output paths and retains the worker for at most 64 commands; --max-requests can lower the cap. Inputs must stay inside the project and outputs inside this module. Each command/input file is capped at 1 MiB. Invalid requests report an error, and later valid commands can continue. The old s03_application.py interface and deployment.json preserve the first frozen comparison.

Every direct calculation compares the recurrence with the independent Taylor construction. A failed check or failed native operation invokes the preserved Kira path, with all failed-attempt costs included. Generated coefficients remain exact. The integer transform cache is bounded to 128 loop orders, and all mass-dependent checks receive fresh inputs.

Coefficient records specify coefficient_format and coefficients_sha256. JSON objects retain the earlier arrays. Binary KXB1 objects contain a small JSON index, common-denominator symbolic polynomials and all expanded reduced fractions as signed base-256 integers. Their SHA256 addresses refer to uncompressed bytes; gzip level 6 stores them. source_choices and raw Kira evidence have separate hashes.

Use load_coeff(record) from s14_reader.py to obtain the identical legacy coefficient dictionaries with the compiled reader. s00_backend.py also provides the portable Python decoder. The compiled reader uses the recorded CPython 3.9 integer interface and must be rebuilt for another Python ABI. build/ records the compiler, Python, GMP version and binary hashes. s17_reader_run.sh records the build command; completed experiment wrappers must not be rerun over their frozen records.

Training uses 96 batches, five rules and three repetitions: 1,440 labels. Each label includes request reading, selection, exact reduction, independent checking and output writing in a warm worker. Training records preserve exact coefficient hashes, costs and inputs; temporary expanded training outputs are removed after each batch to bound scratch space. The tree has maximum depth four, at least six training batches per leaf, 19 fitted nodes and five log-time outputs. All 480 exported training-score comparisons match scikit-learn. The tree scores estimate runtime, without calibrated confidence or globally optimal-path claims.

The first validation has 12 batches and 324 measurements; it selects integer polynomials. Its independent reserved study has 360 cold applications and 144 stream applications. It passes all exact checks but establishes no complete-time gain once output decoding is included. These records remain in validation/ and model_test/.

The slow Python decoding observed during validation motivates the compiled reader. The trained model and arithmetic remain unchanged. reader_validation/ and reader_final_test/ use fresh mass profiles and targets, with a second freeze before testing. Each profile covers loop orders 1--12; the interface checks also cover 13, 16, 24 and 32. The second validation again has 324 measurements. An incomplete 360-application reader run remains in reader_test/ and is excluded because its selection step referenced the earlier validation set and its stream paths were incorrect. Matching source and the original freeze are preserved in development/reader_protocol_v1/. The corrected s21_reader_finish.sh freezes the prescribed choice from reader_validation/ and evaluates fresh reader_final_test/ inputs. The final test contains 300 cold and 144 stream applications. Each stream has four batches; the three streams are disjoint.

complete_seconds includes input reading, model load and inference where used, recurrence selection, exact algebra, required checks and expansion. external_seconds adds process startup and output saving. roundtrip_seconds also includes reading and decoding every coefficient. The same wrapper and writer support matched controls. Independent reference audits and timing-record bookkeeping occur outside these production timers. Median repeat times and geometric ratios weight the twelve batches equally; bootstrap intervals describe this finite test. Stream ratios describe three specified sequences without an inferential interval.

Script sequence:
- s00_backend.py: Exact integer polynomials, bounded binary records and legacy compatibility.
- s01_transform.cpp:  Bounded exact polynomial transformations with GMP.
- s02_engine.py: Shared integer representation with compiled expansion and learned batch routing.
- s03_application.py: Bounded single-batch and persistent interfaces with lossless coefficient output.
- s04_check.py: Check exact arithmetic, binary round trips, worker isolation and Kira fallback.
- s05_study.py: Collect complete runtime labels, validate policies, then freeze independent tests.
- s07_audit.py: Independently audit reserved coefficients, binary readers and fixed policies.
- s08_analyze.py: Summarize frozen complete timings, decoding costs and model comparisons.
- s09_plot.py: Plot exact arithmetic, complete output costs and learned strategy results.
- s10_document.py: Document both frozen comparisons, the new cost model and final deployment.
- s11_release_check.py: Verify both frozen studies, exact evidence, report references and storage bounds.
- s13_reader.cpp:  Lossless coefficient reader for the existing expanded binary format.
- s14_reader.py: Use a compiled lossless reader without changing the first frozen implementation.
- s15_application.py: Public interface for the validated arithmetic and compiled-reader extension.
- s16_reader_study.py: Fresh validation and reserved tests for the compiled coefficient reader.
- s18_reader_audit.py: Independently audit reserved coefficients, binary readers and fixed policies.
- s19_reader_analyze.py: Summarize frozen complete timings, decoding costs and model comparisons.
- s20_reader_plot.py: Plot exact arithmetic, complete output costs and learned strategy results.

s06_run.sh builds/checks the original backend, then runs training, validation, freezing, testing and integration checks. s07_audit.py, s08_analyze.py and s09_plot.py preserve its independent audit, analysis and figures. s17_reader_run.sh preserves the initial reader build and validation launch; its incomplete comparison is documented above. s21_reader_finish.sh runs the corrected freeze and fresh reserved comparison, integration checks, audit, reader-cost comparison and plots. s12_report.sh updates documentation, verifies releases and renders the report; --data-commit pins its immutable citation.

resource_plan.json bounds retained records, scratch, Git copies, report growth and temporary pack/index space below the combined 10 GB ceiling. Only one experiment job runs at a time, using one CPU and a 2,800 MiB address-space cap. Kira fallback retains its 90-second, 1.5 GiB sampled tree-RSS and 64 MiB scratch limits. Scientific data and models stay on Hoffman and GitHub; the report also synchronizes locally. Earlier frozen studies and models remain unchanged.
