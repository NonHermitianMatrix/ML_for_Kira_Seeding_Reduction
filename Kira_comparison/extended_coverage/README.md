# Extended tests of the frozen application

This folder tests the published application on more integral types and loop orders one through twelve. It does not train or change a model.

The native grid contains vacuum, two-point, and scattering integrals. New rational profiles differ from earlier profiles. Symbolic cases keep the independent invariants as symbols. A complete scalar-product basis can exceed the current interface limit of 31 indices. The coverage files record this limit. They do not assign a calculation time to rejected inputs.

Each eligible case first runs Kira with expanded seeds and no given master basis. A second calculation changes the integral ordering and raises the numerator bound. The application then receives the checked basis. Its three methods run in new processes. The measured time includes model loading, equation generation, reduction, checking, retries, and process start. All methods load the common application modules. The native method uses fixed settings with no learned decision. These are interface timings, not isolated executable timings. The previous and selected methods use the frozen applications. The reference calculation time is separate.

Each native attempt has a 30-second limit and a 32 MiB scratch limit. Use at most two workers. Each worker has an 8 GiB memory allocation. Keep all failures. Stop further repetitions of a method after its first failure. Compare times only when every paired repetition passes the exact checks. Identity-only answers do not show a reduction gain.

The analytic tests use scalar massless two-point integrals with one parallel line per loop plus one line. They test every loop order from one through twelve at rational and symbolic momentum. These cases use the exact formula already in the application. An independent raising recurrence checks the coefficients. These results do not establish a learned gain or native Kira coverage at high loop order.

The scale tests use four preselected cases and three common momentum scales. They include the first complete solve. Only existing supported scale rules can reuse a result.

Run the scripts in this order:

1. Run `s00_protocol.py` to freeze the physical inputs, models, source files, and limits.
2. Submit `s03_job.sh s02_study.py --pilot` for the small trial.
3. Submit `s03_job.sh s02_study.py --worker 0` and worker `1` after the trial passes.
4. Run the analytic and scale tests after the native workers finish.
5. Run the analysis and document scripts. Build and check both PDFs.

`s01_call.py` runs one calculation. `s02_study.py` controls references, repeated measurements, and failure records. `s03_job.sh` supplies the cluster job limits. Later scripts generate the analytic checks, scale checks, figures, and report text.

`protocol.json` stores the cases and frozen settings. `resource_plan.json` gives a conservative storage bound below the user's combined 10 GB limit. Its remote starting value is a bound, not a fresh whole-folder measurement. Generated data stay on Hoffman and GitHub.

Use GCC 9.5, Python 3.9.6, Git 2.40, and the existing project Python environment. The job wrapper loads these modules. The older default Git on compute nodes cannot read this repository format.

Completed scripts: `s04_analytic.py` checks the scalar recurrence. `s05_scale.py` tests scale sequences. `s06_analyze.py` makes summaries and the figure. `s07_document.py` writes the new report sections. `s08_finish.py` checks the results and writes folder guides. `s09_complete.py` runs analysis, builds both PDFs, and checks the documents after the measurements finish.

Native coverage: {"reference_check_failed": 5, "reference_failed": 14, "unsupported_index_count": 36, "verified": 29}. The matched nontrivial set has 29 cases. All 24 analytic batches pass. See `summary.json` for measured times and the full failure list.
