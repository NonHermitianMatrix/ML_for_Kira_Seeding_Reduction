# Paper figures

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
