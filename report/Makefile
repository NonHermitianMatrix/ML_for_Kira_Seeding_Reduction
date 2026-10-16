SHELL := /bin/bash
TECTONIC ?= ../.tools/tectonic/tectonic

.PHONY: all
.DELETE_ON_ERROR:
all: report.pdf notes.pdf

report.pdf: report.tex paper_appendices.tex scattering_results.tex workflow_results.tex workflow_appendix.tex type_specialist_results.tex type_specialist_appendix.tex basis_completion_results.tex basis_completion_appendix.tex ordering_policy_results.tex ordering_policy_appendix.tex thread_policy_results.tex thread_policy_appendix.tex higher_scattering_results.tex higher_scattering_appendix.tex adaptive_results.tex adaptive_appendix.tex portfolio_results.tex portfolio_appendix.tex parametric_results.tex parametric_appendix.tex paper_references.bib type_specialist_references.bib $(wildcard paper_figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . report.tex

NOTES_SECTIONS := $(filter-out report.tex notes.tex paper_appendices.tex scattering_results.tex,$(wildcard *.tex))
notes.pdf: notes.tex references.bib type_specialist_references.bib $(NOTES_SECTIONS) $(wildcard figures/*.pdf) $(wildcard paper_figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . notes.tex
