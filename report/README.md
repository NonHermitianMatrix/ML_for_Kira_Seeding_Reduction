# Scientific paper, notes, and figures

This folder contains the scientific explanation of the reduction method and its measured results. The paper introduces Feynman integrals and Kira, explains the analytic and learned methods, and states the scope of each comparison. The notes contain detailed experiments, including failures and rejected methods.

## Documents and sources

| File or group | Content |
|---|---|
| [report.pdf](report.pdf), [report.tex](report.tex) | Research paper and its main LaTeX source. |
| [notes.pdf](notes.pdf), [notes.tex](notes.tex) | Detailed experiment notes and their main source. |
| `paper_background.tex`, `paper_project_data.tex`, `paper_methods.tex` | Physical notation, training-data construction, and reduction methods. |
| `paper_study_design.tex`, `paper_default_comparison.tex`, `paper_default_rows.tex` | Comparison definitions and the direct default-Kira results. |
| `paper_project_results.tex`, `paper_integral_results.tex` | Component results, physical uses, loop ranges, and analytic domains. |
| `paper_discussion.tex`, `paper_conclusion.tex` | Interpretation, limitations, and conclusions. |
| `focused_derivations.tex` and the mathematical appendices | Derivations and conditions of the formulas used in the paper. |
| [paper_references.bib](paper_references.bib) | External bibliography for the paper. |
| `references.bib`, `notes_additional_references.bib`, `type_specialist_references.bib` | Bibliographies used by the notes and supporting sections. |
| [paper_figures](paper_figures/README.md), [figures](figures/README.md) | Plots and instructions for their source measurements. |

The paper’s Section 3 defines the constructed data and its loop range. Section 6 compares the retained method with default Kira. Section 8 separates results by integral structure. Appendix K defines native families and loop-order limits. The direct default comparison covers specified two- and three-loop requests; restricted analytic tests extend through thirteen loops.

## Render a document

From this folder, use:

```bash
make report.pdf
make notes.pdf
```

The Makefile uses `../.tools/tectonic/tectonic`. Set `TECTONIC` to another installed Tectonic executable if required. Rendering can fetch missing TeX assets into `.tools/cache`. The recipes limit address space to 1.5 GiB and runtime to 240 seconds. Render documents separately within the project’s storage budget. Native integral data and trained weights are not required merely to read the PDFs.

## Reproduce plots and check the paper

`s04_project_figures.py` draws the four `project_*.pdf` figures from saved report evidence. `s02_rewrite_figures.py` draws the three `rewrite_*.pdf` figures. These plotting scripts use Matplotlib and perform no training or reduction. `s06_method_tables.py` creates the integral-type tables from saved summaries.

After a scientific source or figure change, render the affected PDF and run these checks in order:

```bash
python s01_check_paper.py
python s03_check_rewrite.py
python s05_check_project.py
python s07_check_method_tables.py
python s08_check_default_comparison.py
```

The checks cover citations, internal references, measurements, source files, document hashes, and the preserved notes. Some numerical checks require the full Hoffman repository. Compact evidence files support local document checks where implemented. Historical validation files identify the document and experiment versions they checked.

`default_kira_data.json` contains the primary comparison summary. `default_comparison_validation.json`, `rewrite_validation.json`, `project_validation.json`, and `method_table_validation.json` record checks for the published paper. `writing_review.md` explains the claim and writing review. Older experiment writers can replace manuscript sections; inspect their destinations before running them.

## Scripts

| File | Purpose |
|---|---|
| [Makefile](Makefile) | Build targets, dependencies, and compiler or rendering commands. |
| [s00_make_paper_figures.py](s00_make_paper_figures.py) | Create paper figures from frozen result summaries; no training or reductions. |
| [s01_check_paper.py](s01_check_paper.py) | Bounded checks of the paper and preserved notes, with no research reruns. |
| [s02_rewrite_figures.py](s02_rewrite_figures.py) | Draw the paper figures from saved results. Do not run reductions or training. |
| [s03_check_rewrite.py](s03_check_rewrite.py) | Check the rewritten paper against its saved evidence without new experiments. |
| [s04_project_figures.py](s04_project_figures.py) | Make whole-project figures from saved evidence; run no new reductions. |
| [s05_check_project.py](s05_check_project.py) | Verify the whole-project paper against existing evidence after PDF rendering. |
| [s06_method_tables.py](s06_method_tables.py) | Create the study's type-by-type tables from saved measurements only. |
| [s07_check_method_tables.py](s07_check_method_tables.py) | Check the editorial comparison against saved evidence; run after rendering. |
| [s08_check_default_comparison.py](s08_check_default_comparison.py) | Check the primary default-Kira table against the saved measurements. |
