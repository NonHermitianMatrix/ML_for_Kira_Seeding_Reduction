SHELL := /bin/bash
TECTONIC ?= ../.tools/tectonic/tectonic

.PHONY: all
.DELETE_ON_ERROR:
all: report.pdf

report.pdf: report.tex background.tex higher_loops.tex seed_model.tex seed_model_test.tex seed_kira_test.tex reduction_model.tex reduction_training.tex reduction_test.tex references.bib $(wildcard figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . report.tex
