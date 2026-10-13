# paper figures

This folder contains plots of saved results.
The parent plotting script defines the inputs, axes and comparison method.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../README.md).

## Data and supporting files

- [cumulative_results.pdf](cumulative_results.pdf): This file displays a recorded result or document.

- [equation_results.pdf](equation_results.pdf): This file records the source equations or their checks.

- [row_results.pdf](row_results.pdf): This file displays a recorded result or document.

- [seed_results.pdf](seed_results.pdf): This file records seed information or seed checks.

- [transfer_results.pdf](transfer_results.pdf): This file displays a recorded result or document.

## Additional scattering figures

`scattering_training.pdf` compares complete times for native choices, the original equation tree and the newly trained selectors.
`scattering_sufficiency.pdf` shows the number of reductions completed before fallback.
Each method has 45 reserved trials.

Use [the scattering analysis](../../ML_model_equation_selection/scattering_training/s02_analyze.py) on Hoffman to create these figures.
The [paper evidence table](../scattering_figure_data.json) records their measured values.
