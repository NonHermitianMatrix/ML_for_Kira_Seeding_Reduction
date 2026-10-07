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

seed_model.tex and reduction_model.tex describe the two models and their twenty new passes over 1,610,890 training targets. seed_model_test.tex and reduction_test.tex give the frozen results for 690,382 targets in 5137 held-out families. reduction_training.tex records the expanded-data reduction training. The twelve current PDF plots are in figures/. Earlier checkpoints and tests remain in the model archives on Hoffman and GitHub.

The report distinguishes reference-set agreement from seed sufficiency, recorded next-action agreement from complete reductions, and sampled finite-field checks from symbolic reconstruction. The added family domain and shared lower-sector physics limit claims about generic high-loop integrals, unseen loop orders and full Kira speedups.

The bibliography links the expanded data and models to commit 0be1c2b3884bc736e22901a7e2304e3ba6d75497 and the tested outputs to commit 2ed8b26e977fa2dca5f464532ee9891712f7f417. Raw data, models and predictions remain on Hoffman and GitHub; only the complete report is synchronized locally.
