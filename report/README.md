# Report copies

This folder contains the LaTeX sources, bibliography, build file and rendered PDF. The current copies must agree on Hoffman, GitHub and the local machine.

The local folder is /home/physics/projects/ML_for_Kira_SeedReduction/report. The Hoffman folder is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction/report. GitHub stores the same folder on the main branch.

The local project is a shallow, partial Git checkout. Its sparse file selection includes report/, rules.md and .gitignore. Integral datasets and model-training files are not checked out or downloaded.

After report changes on Hoffman, rebuild the PDF and publish the sources and PDF together. From the local project root, update the local copy with:

    git pull --ff-only

The local Git connection uses the existing Hoffman SSH authentication and Hoffman's existing GitHub access. Its helper is .tools/report-sync/s00_git_via_hoffman.py, configured through core.sshCommand. No credentials are stored in this repository. The helper relays Git's SSH arguments through Hoffman. The connection requires network access to Hoffman.

Preserve local edits before pulling, and resolve any differences before declaring the report synchronized. Compare the report file hashes when checking the three copies. Git synchronization runs when requested or when the report is updated; no background synchronization service is installed.

The earlier local report and rules are retained in .tools/report-sync/before-link/ on the local machine.
