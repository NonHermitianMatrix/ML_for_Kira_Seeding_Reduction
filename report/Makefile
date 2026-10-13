SHELL := /bin/bash
TECTONIC ?= ../.tools/tectonic/tectonic

.PHONY: all
.DELETE_ON_ERROR:
all: report.pdf notes.pdf

report.pdf: report.tex paper_appendices.tex paper_references.bib $(wildcard paper_figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . report.tex

NOTES_SECTIONS := $(filter-out report.tex notes.tex paper_appendices.tex,$(wildcard *.tex))
notes.pdf: notes.tex references.bib $(NOTES_SECTIONS) $(wildcard figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . notes.tex
