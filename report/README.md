# Paper and research notes

`report.tex` and `report.pdf` contain the concise research paper, **Learned selection for exact Feynman integral reduction with Kira**. It presents the three model roles, their measured results, the retained seed/equation methods, the exclusion of learned row selection, the overall results and a conclusion. `paper_appendices.tex` contains the IBP, row-operation, target-construction, model-loss, vacuum-recurrence and timing derivations. `paper_references.bib` contains external references only. The paper does not cite this project's GitHub repository.

`notes.tex` and `notes.pdf` preserve the previous detailed report. Its original abstract, technical sections, figures, negative results and bibliography remain available. `references.bib`, the existing section files and `figures/` belong to these notes. `notes_README.md` preserves the earlier documentation history; its historical references to `report.tex` or `report.pdf` describe the document now named `notes`.

The retained seed and equation models have separate validated domains. The supplied-equation seed result and native equation result are not a measured simultaneous two-model gain. The native equation route retains native seed and row choices. The specialized vacuum speedup also includes exact mathematical reuse and implementation changes; it is not an ML-only result.

## Build and verification

Run `make` here to build both PDFs with the existing bounded Tectonic installation. `make report.pdf` builds the paper, and `make notes.pdf` builds the notes. The build uses the tracked figures and therefore works in the local report-only checkout without scientific datasets.

Run `../.tools/seed-model/venv/bin/python s00_make_paper_figures.py` on Hoffman to regenerate the five vector-PDF paper figures. The script reads existing result summaries, checks the headline measurements, and writes `paper_figure_data.json` with source paths, SHA-256 hashes and plotted values. It does not train models or rerun reductions. `paper_figures/` contains only the publication figures. Each caption states the result, baseline, scope and uncertainty convention. Zoomed axes show labelled limits and an equal-time reference; the cumulative time plot uses a labelled logarithmic scale.

Run `python s01_check_paper.py` to check citations, cross-references, self-repository exclusion, figure availability, PDF signatures, compilation logs and the preserved notes abstract. It writes `paper_validation.json`. This report audit does not rerun scientific experiments.

`notes_preservation.json` records the original source/PDF hashes and the preserved abstract hash. The original PDF remains in Git history; the current notes PDF differs only through the notes title and rebuilt PDF metadata. All previous datasets, weights and result files retain their original locations and content.

The complete folder is synchronized between Hoffman, GitHub and the local report folder. Raw integral data and model data stay on Hoffman and GitHub.
