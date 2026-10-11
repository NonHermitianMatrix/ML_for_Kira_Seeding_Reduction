SHELL := /bin/bash
TECTONIC ?= ../.tools/tectonic/tectonic

.PHONY: all
.DELETE_ON_ERROR:
all: report.pdf

report.pdf: report.tex background.tex higher_loops.tex seed_model.tex seed_model_test.tex seed_kira_test.tex reduction_model.tex reduction_training.tex reduction_test.tex kira_comparison.tex kira_live_matrix.tex kira_acceleration.tex kira_acceleration_results.tex kira_adaptive_development.tex kira_transfer_results.tex kira_expression_results.tex kira_expression_matched.tex kira_fast_expression.tex kira_multiloop_methods.tex kira_multiloop_results.tex kira_integrated_methods.tex kira_integrated_results.tex kira_integrated_pair.tex kira_shared_evaluation.tex kira_parallel_inference.tex equation_selection.tex equation_selection_results.tex equation_selection_domain.tex equation_selection_confirmation.tex equation_selection_early.tex higher_loop_acceleration.tex references.bib $(wildcard figures/*.pdf)
	ulimit -v 1572864; ulimit -f 131072; XDG_CACHE_HOME="$(abspath ../.tools/cache)" timeout 180s "$(TECTONIC)" --keep-logs --outdir . report.tex
