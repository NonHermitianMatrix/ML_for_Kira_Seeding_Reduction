# Report copies

This folder contains the LaTeX sources, bibliography, build file and rendered PDF. The current copies must agree on Hoffman, GitHub and the local machine.

The local folder is /home/physics/projects/ML_for_Kira_SeedReduction/report. The Hoffman folder is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction/report. GitHub stores the same folder on the main branch.

The local project is a shallow, partial Git checkout. Its sparse file selection includes report/, rules.md and .gitignore. Integral datasets and model-training files are not checked out or downloaded.

After report changes on Hoffman, rebuild the PDF and publish the sources and PDF together. From the local project root, update the local copy with:

    git -c merge.stat=false pull --ff-only --no-stat

The local Git connection uses the existing Hoffman SSH authentication and Hoffman's existing GitHub access. Its helper is .tools/report-sync/s00_git_via_hoffman.py, configured through core.sshCommand. No credentials are stored in this repository. The helper relays Git's SSH arguments through Hoffman. The connection requires network access to Hoffman.

Preserve local edits before pulling, and resolve any differences before declaring the report synchronized. Compare the report file hashes when checking the three copies. Git synchronization runs when requested or when the report is updated; no background synchronization service is installed.

The earlier local report and rules are retained in .tools/report-sync/before-link/ on the local machine.

<!-- expanded-report -->
The current report describes 17,100 family instances, 57,979 family-local master entries and 2,301,272 targets. The later additions contain 1,250 restricted coupled-vacuum mass profiles at each loop order from one through twelve, following the earlier 100 profiles at orders two through twelve. higher_loops.tex derives their master bases, exact identities, reverse target construction and grouped division.

seed_model.tex and reduction_model.tex describe the two models and their twenty new passes over 1,610,890 training targets. seed_model_test.tex and reduction_test.tex give the frozen results for 690,382 targets in 5137 held-out families. reduction_training.tex records the expanded-data reduction training. The fourteen current PDF plots are in figures/. Earlier checkpoints and tests remain in the model archives on Hoffman and GitHub.

The report distinguishes reference-set agreement from seed sufficiency, recorded next-action agreement from complete reductions, and sampled finite-field checks from symbolic reconstruction. The added family domain and shared lower-sector physics limit claims about generic high-loop integrals, unseen loop orders and full Kira speedups.

The bibliography links the expanded data and models to commit 0be1c2b3884bc736e22901a7e2304e3ba6d75497 and the tested outputs to commit 2ed8b26e977fa2dca5f464532ee9891712f7f417. Raw data, models and predictions remain on Hoffman and GitHub; only the complete report is synchronized locally.

The conclusion in report.tex brings together the master-based target construction, both frozen-model tests, the measured reduction cost and the limits of the tested family domains. It includes the new symbolic master-span sufficiency test in Kira and identifies the native equation-generation and total-cost comparisons still needed to assess a solver speedup. The reported test data and model weights remain those of the cited releases.

seed_kira_test.tex describes all 690,382 reserved targets tested for exact membership in their master span with predicted, full and empty IBP seed sets through Kira's user-defined-system interface. Predicted sets suffice for 652,517 targets (94.515%). The full candidate pool suffices for 690,382. The associated results and code are fixed at 097204f4228b5999c4379c8da57db1aa9495c367; the new PDF figures are kira_seed_sufficiency.pdf and kira_seed_sets.pdf. These are exact symbolic membership tests within the stored source pools, with three independent finite-field rank checks. The full experiment does not reconstruct all rational master coefficients. This experiment does not measure native Kira seeding or a total solver speedup.
