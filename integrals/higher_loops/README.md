# Coupled vacuum families at two through twelve loops

Generated and independently validated: 100 mass profiles per loop order, 128 reverse-constructed targets per family. Existing integral files remain intact. Scripts s00_exact.py and s01_generate.py implement exact rational Laurent arithmetic, an independent partial-fraction oracle, and generation with resumable family manifests. s02_run_generation.sh runs bounded jobs on a compute node.

Each integral has L massless lines and R=2,3,4 massive lines carrying the sum of all loop momenta. Distinct positive mass ratios define profiles; profiles share a restricted topology. All massless powers equal one. A master has one massive denominator of power one. Partial fractions and the total Euler IBP reduce the generated scalar domain. This collection does not cover arbitrary multiloop numerators or generic scattering families.

Every target is built from an exact master combination by adding recorded multiples of zero identities in reverse order. Store symbolic coefficients, actual IBP seeds, algebraic partial-fraction steps separately, all source equations, operation counts and reduction traces. Three finite-field samples check row operations. An independent rational-function oracle checks the symbolic result. Reference paths are sufficient; minimality is not established.

A fixed split assigns 70 profiles to training and 30 to testing across every new loop order. Related profiles stay together across loops. Existing family assignments remain fixed. Training and testing views link to canonical files without duplication. All data stays on Hoffman and GitHub.

Candidate Euler seeds have total massive power at most five; their identities and partial-fraction equations reach total massive power six. Scalar target roots have total massive power two through five. Every generated integral expression includes a root with all massive propagators present and at least one additional denominator power. Individual targets also include lower sectors. Shared lower-sector integrals can occur across mass profiles, so profile separation does not imply disjoint lower-sector physics.

s06_run_all_loops.sh runs the bounded pilot, independent checks, complete generation, full validation and catalog/split integration in sequence. Generation resumes only when source hashes match the saved family manifest. A target whose reference pivot vanishes at a verification sample is rejected and its rejection count is recorded.

s07_update_report.py renders the verified mathematical section and updates result-derived model sections and immutable repository citations after both tests pass. s08_finalize_training.py validates both current checkpoints and writes the trained-release READMEs; s09_run_training_validation.sh runs that step after both training jobs. The shared request is recorded in request.json.

s10_validate_collection.py checks all 2,100 canonical family manifests and the links among targets, masters, seeds and traces, while preserving the original 1,000-family mathematical audit. The top-level integrals/s02_validate.py dispatches to this current audit when the expanded catalog is present. The existing integrals/s01_read_data.py reader supports both old and new families without changes.

s03_validate.py checks graph loop counts, source integrands, all reverse and forward records at three finite-field samples, and convergent radial master quadratures. s04_run_validation.sh runs those checks on a compute node. s05_integrate.py extends catalogs and the grouped split after validation; it preserves existing assignments. integration_summary.json records final counts. The new phase uses 266890 training targets and 114382 held-out targets.

The complete-collection hash and linkage audit runs with s10_validate_collection.py through s11_run_collection_audit.sh. The training finalizer reuses the completed audit only when the catalog, split and independent mathematical-validation hashes still agree.

After both frozen tests pass, s12_finalize_tests.py records their metrics and updates the model and split READMEs. s13_build_report.sh runs s07_update_report.py with immutable data/test Git revisions and rebuilds the PDF with bounded resources.

The completed whole-collection audit checked 29,500 manifest files, 3,568,907 source equations by identity linkage, and 2,206,660 recorded elimination steps across 381,272 targets. Its hash and linkage results are in ../validation_summary.json; the separate mathematical checks are retained in validation.json and original_validation_summary.json.

The optional s14_stage_data.sh prepares integral files in the Git index on a bounded compute allocation. With path arguments it stages those supplied project paths instead. Active training outputs must be staged again after final checkpoint validation. It performs no commit or publication; the first publication waits for both trained checkpoints and their checks.

The reduction test uses s10_parallel_test.py to divide held-out families among four single-thread workers on one shared compute allocation. Each family keeps the same frozen model, candidate list, paired policy timing and exact checks. Aggregation starts only after all disjoint family groups complete. The test wrapper requests four CPU slots and 1 GB per slot; each process has a 3 GB virtual-memory ceiling.

The reduction checkpoint can be checked as soon as its training finishes with model_test/s11_validate_trained.sh. This check reads no held-out examples. The combined training finalizer reuses the result only when its twenty-pass status, model hash and frozen test-configuration hash agree.

The original seed allocation reached its three-hour time limit during the final pass. The unchanged training calculation resumed its saved model, optimizer and partial pass in a new allocation. The checkpoint checker rejected the unfinished model before publication; training_validation_scheduler.log retains that earlier check, while training_validation_resume_scheduler.log records the check after resumed completion.

The requested extension, twenty-pass training phases and frozen tests are complete. Both tests cover 114,382 held-out targets and include six plots. The 38-page report derives the added vacuum master bases and target construction, records both training phases, and gives the measured test results and scope. Its 24 tracked files match on Hoffman, GitHub and the local machine. request.json and report_update.json retain the checked artifact revisions, report hashes and completion record. Generated integral data and models remain on Hoffman and GitHub only.
