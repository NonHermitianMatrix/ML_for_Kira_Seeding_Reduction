# report

This folder contains the research paper and the detailed notes.
`report.tex` and `report.pdf` contain the paper.
`paper_appendices.tex` contains the integral definitions and derivations.
`paper_references.bib` contains the paper's external references.
The paper does not cite the project repository.

`notes.tex` and `notes.pdf` preserve the earlier detailed report.
The other section files, `references.bib` and `figures/` support the notes.
`notes_README.md` explains the archived document and its earlier names.
The notes retain earlier experiments and negative results.

Run `make` in this folder to build both PDFs.
Run `make report.pdf` to build the paper only.
The Makefile uses the existing Tectonic installation and bounded memory.
The tracked figures permit a build without the scientific datasets.

Run `s00_make_paper_figures.py` on Hoffman to regenerate the five original paper figures.
Use the existing environment at `../.tools/seed-model/venv/bin/python`.
The script reads the recorded result summaries.
It does not train a model or repeat a reduction.
`paper_figure_data.json` records plotted values, source paths and SHA-256 file checks.

Run `python s01_check_paper.py` to check the paper files.
The check covers citations, cross-references, figures, PDF headers and compilation errors.
It also checks the original notes text and its supporting files.
`paper_validation.json` records these file checks.
`notes_preservation.json` identifies the preserved notes files.
A file hash checks file identity; it does not prove a reduction.

The paper gives family definitions and generated index ranges.
The full target records remain in the integral folders.
The report does not print all 2,301,272 target records.
The READMEs contain code, commands, storage and file-check details.
Both PDFs and their sources stay on Hoffman, GitHub and the local machine.

## Code files

The entries below follow file-name order.
Each entry gives its purpose and the input or output interface available in the source.

[Makefile](Makefile)

This Makefile builds the paper and notes.

```make

SHELL := /bin/bash
TECTONIC ?= ../.tools/tectonic/tectonic

.PHONY: all
.DELETE_ON_ERROR:
all: report.pdf notes.pdf

report.pdf: report.tex paper_appendices.tex scattering_results.tex paper_references.bib $(wildcard paper_figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . report.tex

NOTES_SECTIONS := $(filter-out report.tex notes.tex paper_appendices.tex scattering_results.tex,$(wildcard *.tex))
notes.pdf: notes.tex references.bib $(NOTES_SECTIONS) $(wildcard figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . notes.tex

```

[s00_make_paper_figures.py](s00_make_paper_figures.py)

The program creates paper figures from frozen result summaries; it does not train models or run reductions.

The module defines these callable interfaces:

```python

def read(name)
def style()
def finish(fig, name)
def ratio_axis(ax, limits)
def point(ax, value, y, interval=None, color=BLUE, marker='o', label=None)
def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'paper_figures'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_bytes()
(HERE / 'paper_figure_data.json').write_text(json.dumps(payload, indent=2) + '\n')
p.read_text()

```

[s01_check_paper.py](s01_check_paper.py)

The file provides bounded checks of the paper and preserved notes, with no research reruns.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'paper_references.bib').read_text()
(HERE / 'notes.tex').read_text()
(HERE / 'paper_validation.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'notes_preservation.json').read_text()
(HERE / 'paper_figure_data.json').read_text()
(HERE / n).read_text()
log.read_text(errors='replace')
(HERE / f).read_bytes()
(HERE / (name + '.pdf')).read_bytes()
(HERE / n).read_bytes()
path.read_bytes()
(HERE / (n + '.pdf')).read_bytes()

```

## Data and supporting files

This folder contains 47 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.bib`: 2 entries.

- `.json`: 3 entries.

- `.md`: 1 entries.

- `.pdf`: 2 entries.

- `.tex`: 39 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.

## Child folders

- [figures](figures/README.md).

- [paper_figures](paper_figures/README.md).

## Additional scattering study

`scattering_results.tex` adds the new scattering training and test results to the paper.
`scattering_figure_data.json` stores the compact measured values used by its figures and tables.
The full data remain in the model folders on Hoffman and GitHub.

Use [the scattering analysis](../ML_model_equation_selection/scattering_training/s02_analyze.py) to create the two additional figures.
Run it on Hoffman after the study tests finish.
Read [the study guide](../ML_model_equation_selection/scattering_training/README.md) for the required inputs and job order.

The main paper now explains each model before its technical details.
Tables compare the model roles, dataset sizes, measured results and equation features.
The appendices retain the integral definitions and derivations.
The archived notes remain unchanged.
