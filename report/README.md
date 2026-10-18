# Paper and notes

`report.tex` and `report.pdf` contain the research paper.
`notes.tex` and `notes.pdf` contain the detailed notes and earlier experiments.
Keep both documents on Hoffman, GitHub, and the local machine.
Keep integral data and trained weights on Hoffman and GitHub only.

## Read the paper

The paper explains the physical problem, the three learned decisions, and their direct timing comparisons.
It then tests a shared cost model with whole families and higher loop orders held out.
The paper separates learned savings from fixed tuning and exact mathematical shortcuts.
All native test outcomes remain in the coverage table, including failures and unsupported inputs.

`paper_abstract.tex` and `paper_conclusion.tex` state the final measured results.
`paper_derivations.tex` derives the identities, model equations, and timing measures.
`paper_extra_kinematics.tex` defines the additional scattering inputs.
`general_policy_results.tex` reports the new shared-model test.
`general_policy_data.json` contains its compact result summary.
`paper_references.bib` contains external scientific references. The paper does not cite this repository.

## Read the notes

The notes preserve the earlier models, data construction, exact recurrences, and secondary timing studies.
`notes_supplement.tex` contains the unique historical material moved from the preceding paper.
The original paper remains in Git history.
`notes_additional_references.bib` adds the external references needed by this supplement.
The other result and appendix files support the notes and preserve their original controls and limits.

Current additions use explicit markers. `notes_revision.json` and `notes_preservation.json` allow the checker to reconstruct the original notes.
Do not remove historical measurements when a later model changes the deployed method.

## Build and check

Run `make` in this folder to build both PDFs with Tectonic.
Run `python s01_check_paper.py` after the build.
The checker reads actual included sections. It checks citations, references, figures, result ratios, and historical preservation.
It retains the earlier result checks and adds the shared-model coverage checks.
`paper_validation.json` records the outcome.

The Makefile limits memory, output size, and build time.
The saved figures permit a build without downloading the integral datasets.

## Generate the retained shared-model figures

Run `../ML_model_adaptive_reduction/general_policy/s05_analyze.py` on Hoffman after both model trials finish.
Use the existing scientific Python environment described in that folder's README.
The script reads saved results and does not train models or repeat Kira reductions.
It writes the shared-model time and coverage plots, and the compact retained-model plot.
`paper_figures/README.md` explains each plot's message and controls.

Older scripts can overwrite current prose with historical result text.
Use `factorized_policy/s13_document.py` for the current extension.
Read its output before replacing edited prose.

Read [ARCHIVED_CODE_GUIDE.md](ARCHIVED_CODE_GUIDE.md) for earlier report generators and their evidence files.
Use the current writer for the concise paper. Older writers can replace its text.

## Complete preparation comparison

`preparation_results.tex` reports all outcomes and matched full workflow times.
`preparation_appendix.tex` derives the cost-and-failure objective and defines the test inputs.
`preparation_data.json` contains the compact comparison evidence.
`notes_general_methods.tex` places the shared model and physical definitions in the notes.
Scripts s17 through s19 in `general_policy/` produce these files and the preparation figure.
The earlier `s13_finish.py` writer runs them after the shared-model writer. Use the current extension writer for new changes.

## Thirteen-loop extension

`factorized_results.tex` gives the corrected method and measured results.
`factorized_appendix.tex` derives block factorization and the vacuum and massless numerator formulas.
`factorized_data.json` stores compact checked results.
`factorized_initial_notes.tex` preserves the initial grid and the basis correction.
`notes_factorized_appendix.tex` gives the same derivation with note references.
Run scripts s12 through s14 in `factorized_policy` to update this extension.
The older report writers can replace current prose.
Use the current writer and check both PDFs after changes.
