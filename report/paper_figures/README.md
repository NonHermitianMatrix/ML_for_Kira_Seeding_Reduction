# Plots for the paper and supporting experiments

These PDFs present saved measurements. The figure captions identify the physical workload, reference calculation, timing definition, and uncertainty. A ratio below one means less elapsed time when the plotted quantity is method time divided by reference time.

| Figure | Message | Producer |
|---|---|---|
| `project_labels.pdf` | Seed-label agreement and exact equation sufficiency measure different outcomes. | `../s04_project_figures.py` |
| `project_ml.pdf` | Learned choices must be compared with their matched fixed controls. | `../s04_project_figures.py` |
| `project_cumulative.pdf` | Exact recurrence and reuse accelerate the restricted supplied-identity vacuum calculation. | `../s04_project_figures.py` |
| `project_coverage.pdf` | Native completions and restricted analytic loop coverage have different domains. | `../s04_project_figures.py` |
| `rewrite_total.pdf` | Complete-collection timings compare successive applications. | `../s02_rewrite_figures.py` |
| `rewrite_scope.pdf` | Changes in time depend on the integral structure and triangle-product loop order. | `../s02_rewrite_figures.py` |
| `rewrite_ml.pdf` | Component tests separate accepted learned effects from rejected additions. | `../s02_rewrite_figures.py` |

The remaining PDFs support individual studies and the detailed notes. Their names identify the study, such as `tensor_reduction`, `direct_vacuum`, or `triangle_extension`. `../project_figure_data.json` and `../rewrite_figure_data.json` record the data and sources of the listed plots. Individual study guides identify other plotting scripts.

Run the producers from the report folder in an environment with Matplotlib. They read saved evidence and write PDF figures; they do not train a model or run a reduction. Preserve the stated reference and sampling units when changing a plot. Rebuild the affected LaTeX document after changing a figure.
