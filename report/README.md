# Paper and notes

`report.tex` and `report.pdf` contain the research paper.
`notes.tex` and `notes.pdf` contain the detailed notes and earlier experiments.
Both documents include the new complete-cost study.
The paper cites external sources and derives the model equations in its appendices.
It does not cite this repository.

## Build and check

Run `make` in this folder to build both PDFs.
Run `make report.pdf` or `make notes.pdf` to build one document.
The `Makefile` uses the existing Tectonic installation with memory, output and time limits.
The saved figures permit a build without the integral datasets.

Run `python s01_check_paper.py` after the build.
This script checks citations, cross-references, figures, measured ratios and PDF files.
It checks the retained historical files and reconstructs the original notes from the recorded changes.
`paper_validation.json` contains the check results.
A file hash checks file identity; it does not prove a reduction.

Run `s00_make_paper_figures.py` on Hoffman to rebuild the five original paper figures.
Use `../.tools/seed-model/venv/bin/python` with the Python module loaded.
The script reads saved results and does not repeat a reduction or train a model.
`paper_figure_data.json` records its values and source files.

## Scientific sections

`paper_appendices.tex` gives the original integral definitions, model derivations and checks.
`scattering_results.tex` gives the additional scattering training study.
`workflow_results.tex` gives the complete-cost selector, full reduction tests and joint-request results.
`workflow_appendix.tex` derives the cost models and specifies parameter points and target lists.
`paper_references.bib` contains the paper's bibliography.
The remaining section files and `references.bib` support the detailed notes.

`scattering_figure_data.json`, `workflow_figure_data.json` and `batching_figure_data.json`
contain compact values for the added tables and figures.
`workflow_validation.json` records the complete experiment and application checks.
The full scientific records and model weights remain on Hoffman and GitHub.
The report specifies the integral families and target-generation rules.
It does not print all 2,301,272 original target records.

The original notes remain in Git history.
`notes_preservation.json` identifies their source and supporting files.
`notes_revision.json` records the requested changes in terminology.
`notes_README.md` explains the document names and preservation checks.
Current additions have explicit boundaries that permit reconstruction of the earlier source.

## Figure sources

The [scattering analysis](../ML_model_equation_selection/scattering_training/s02_analyze.py)
creates the two scattering figures.
The [complete-cost analysis](../ML_model_workflow_selection/s07_analyze.py)
creates the full reduction comparison.
The [joint-request plotter](../ML_model_workflow_selection/s12_plot_batching.py)
creates the batching comparison.
The [paper figure guide](paper_figures/README.md) explains each plot.
The [earlier figure guide](figures/README.md) describes the figures in the notes.

Keep the sources, bibliography, figures and both PDFs on Hoffman, GitHub and the local machine.
