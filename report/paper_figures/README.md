# Paper figures

<!-- BEGIN PARAMETRIC UPDATE -->

`parametric_results.pdf` compares unchanged learned choices before and after exact preparation changes.
Its second panel compares the added prediction with a fixed portfolio.
`ML_model_adaptive_reduction/s30_analyze_parametric.py` creates this figure.

<!-- END PARAMETRIC UPDATE -->


Each plot uses saved measurements. Lower time ratios mean faster calculations.
The caption states the comparison and the tested scope.

`seed_results.pdf` compares the original seed model with native seed choices.
`row_results.pdf` shows the row-model results and their limits.
`equation_results.pdf` separates equation-preparation savings from full-time savings.
`transfer_results.pdf` shows the original equation model's fallback cost on new graph structures.
`cumulative_results.pdf` shows the restricted vacuum recurrence result at loops one through twelve.
The parent `s00_make_paper_figures.py` creates these five plots.
Their compact values are in `../paper_figure_data.json`.

`scattering_training.pdf` compares full times after training on the three scattering structures.
`scattering_sufficiency.pdf` shows first-attempt completion before and after that training.
The [scattering analysis](../../ML_model_equation_selection/scattering_training/s02_analyze.py)
creates both plots from the values recorded in `../scattering_figure_data.json`.

`workflow_time.pdf` separates gains from the combined Kira integration and learned strategy selection.
The [complete-cost analysis](../../ML_model_workflow_selection/s07_analyze.py) creates this plot.
Its compact values are in `../workflow_figure_data.json`.

`request_batching.pdf` compares two separate requests with their joint reduction.
It includes controls for native choices, the combined integration and the learned strategy.
The [joint-request plotter](../../ML_model_workflow_selection/s12_plot_batching.py) creates this plot.
Its compact values are in `../batching_figure_data.json`.

Read the [report guide](../README.md) for build and check commands.

## type_specialists.pdf

This plot compares complete reduction time for separate graph policies.
The left panel compares three methods with native choices.
The right panel compares the selected route with one fixed strategy for each graph.
The bars show the range across two reserved parameter profiles.
They are not confidence intervals.
The script `ML_model_workflow_selection/type_specialists/s05_analyze.py` generates the plot.
Its input is the completed frozen test record.
See [the study guide](../../ML_model_workflow_selection/type_specialists/README.md).

## Selective seed expansion

`basis_completion.pdf` compares the new route with the previous route and native choices. Ratios below one mean less time. Bars show the range over two reserved parameter profiles. The study script `../../ML_model_workflow_selection/basis_completion/s06_analyze.py` makes the plot from checked full-time records. The axes use the observed ratio ranges and include equal time at one.

## Ordering comparison

`ordering_policy.pdf` compares the new route with the previous route and native choices. Ratios below one mean less time. Bars show the range over two reserved parameter profiles. The study script `../../ML_model_workflow_selection/ordering_policy/s08_analyze.py` makes the plot from checked full-time records. The axes use the observed ratio ranges and include equal time at one.

## Worker-count comparison

`thread_policy.pdf` compares selected and fixed counts with the previous route. A second panel shows the always-four-worker control. Ratios below one mean less time. Bars show the range over two reserved parameter profiles. The study script `../../ML_model_workflow_selection/thread_policy/s08_analyze.py` makes the plot from checked full-time records. The axes use the observed ratio ranges and include equal time at one. The always-four-worker control separates the choice of worker count from extra-core effects.

<!-- BEGIN ADAPTIVE REDUCTION -->

## Adaptive reduction figures

`adaptive_reduction.pdf` compares learned time with native and fixed controls after the same exact improvements.
It divides sums of batch median times within each graph structure.
`adaptive_integration.pdf` separates file indexing, zero-sector projection, and the validated policy.
`adaptive_graph_controls.pdf` compares predictions and the validated policy with the best fixed setting for each graph.
Both figures use matched three-run medians.
Only `adaptive_integration.pdf` uses a logarithmic time axis. The control figure uses linear time ratios.
The producer is `ML_model_adaptive_reduction/s06_analyze.py`.
The figure data are in `report/adaptive_reduction_data.json`.

<!-- END ADAPTIVE REDUCTION -->

<!-- BEGIN HIGHER SCATTERING VERIFICATION -->

## Component comparison figure

`component_ablation.pdf` compares complete strategies and separately disables one learned decision at a time.
The upper panel uses all fourteen target batches.
The lower panel uses the graph subset on which each model is enabled.
Each value divides sums of three-run batch medians.
The panels retain the equal-time reference and use separate readable axis ranges.
The source is `Kira_comparison/higher_scattering/s07_analyze.py`.
The figure gives measured changes on these batches, not a universal ML speedup.

<!-- END HIGHER SCATTERING VERIFICATION -->

<!-- BEGIN PORTFOLIO FIGURES -->

## Portfolio figures

`portfolio_controls.pdf` compares the final portfolio with the previous workflow and the graph-specific fixed portfolio.
Its line segments show the range of three repetition totals, not confidence intervals.
`portfolio_totals.pdf` compares complete wall and process CPU time.
The producer is `ML_model_adaptive_reduction/s16_portfolio_analyze.py`.
The input evidence is `report/portfolio_data.json`.

<!-- END PORTFOLIO FIGURES -->

<!-- BEGIN COVERAGE STUDY -->
`coverage_grid.pdf` shows verified native coverage and its limits.
`coverage_times.pdf` separates complete native requests from restricted vacuum identities.
<!-- END COVERAGE STUDY -->
