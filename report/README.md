# Report copies

This folder contains the LaTeX sources, bibliography, build file and rendered PDF. The current copies must agree on Hoffman, GitHub and the local machine.

The local folder is /home/physics/projects/ML_for_Kira_SeedReduction/report. The Hoffman folder is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction/report. GitHub stores the same folder on the main branch.

The local project is a shallow, partial Git checkout. Its sparse file selection includes report/, rules.md and .gitignore. Integral datasets and model-training files are not checked out or downloaded.

After report changes on Hoffman, rebuild the PDF and publish the sources and PDF together. From the local project root, update the local copy with:

    git -c merge.stat=false pull --ff-only --no-stat

The local Git connection uses the existing Hoffman SSH authentication and Hoffman's existing GitHub access. Its helper is .tools/report-sync/s00_git_via_hoffman.py, configured through core.sshCommand. No credentials are stored in this repository. The helper relays Git's SSH arguments through Hoffman. The connection requires network access to Hoffman.

Preserve local edits before pulling, and resolve any differences before declaring the report synchronized. Compare the report file hashes when checking the three copies. Git synchronization runs when requested or when the report is updated; no background synchronization service is installed.

The earlier local report and rules are retained in .tools/report-sync/before-link/ on the local machine.

The report now includes the completed ten-pass seed-model training and held-out results for 72,142 targets. seed_model_test.tex contains the test section, and figures/ contains the six PDF figures. Raw predictions and metric data remain in ML_model_seed_selection/model_test/ on Hoffman and GitHub. The local report copy contains these report figures but no raw model-test records.

reduction_model.tex describes the reduction-propagation model, matrix inputs, allowed elementary row operations and next-step confidence. reduction_training.tex gives the completed thirty-pass training measurements, including the twenty-pass continuation. The corresponding model code, derived training states, checkpoints and logs remain in ML_model_reduction/ on Hoffman and GitHub.

<!-- reduction-test:start -->
reduction_test.tex contains the thirty-epoch reduction-model test and six replacement PDF figures in figures/. The report covers recorded-choice agreement, confidence, complete sampled reductions, operation counts and timing. Raw probability archives and exact trajectories stay in ML_model_reduction/model_test/ on Hoffman and GitHub. The sources, bibliography, figures and rendered PDF are also synchronized locally.
<!-- reduction-test:end -->
