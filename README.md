# Optimizing Feynman integral reduction with Kira

This repository contains a research implementation for reducing Feynman integrals to master integrals with less elapsed time. It combines exact analytic identities, learned seed choices, and shared calculations with Kira. The intended use is the integral-reduction stage of higher-order QCD and other quantum field theory calculations.

A target is an integral or an expression that must be reduced. A master integral belongs to the basis used to express the answer. A seed is an integral index vector from which integration-by-parts (IBP) identities are generated. The output has the form `I_a = sum_m c_am M_m`, with exact rational coefficients. Evaluating a general master integral is a separate task.

## How the method works

1. Check the propagators and kinematics for an applicable exact formula or recurrence.
2. Reduce accepted structures directly and reuse reductions of independent components.
3. For the remaining supported inputs, choose seed bounds using the retained cost and failure models.
4. Run Kira with validated arithmetic settings and broaden the calculation when the selected equations are insufficient.
5. Return coefficients in the requested basis. The benchmark checks these coefficients against independent references.

The deployed interface is in [triangle_reduction](ML_model_adaptive_reduction/triangle_reduction/README.md). It includes the earlier retained analytic and native methods. The learned row policy and the additional equation filter are disabled in the final comparison. Experimental models remain available for study and reproduction.

## Repository layout

| Folder | Contents and use |
|---|---|
| [integrals](integrals/README.md) | Family definitions, master bases, targets, exact relations, and linked training/test divisions. |
| [ML_model_adaptive_reduction](ML_model_adaptive_reduction/README.md) | Combined application, exact formulas, cost models, validation, and component experiments. |
| [ML_model_seed_selection](ML_model_seed_selection/README.md) | Original neural seed model, native seed-cost models, and sufficiency tests. |
| [ML_model_equation_selection](ML_model_equation_selection/README.md) | Equation classifiers, native integration, and restricted vacuum recurrence experiments. |
| [ML_model_reduction](ML_model_reduction/README.md) | Elimination-step models, training states, and tests of their algebraic and runtime cost. |
| [ML_model_workflow_selection](ML_model_workflow_selection/README.md) | Experiments that choose complete Kira strategies or combine compatible requests. |
| [Kira_comparison](Kira_comparison/README.md) | Default-Kira comparisons, native integration tests, exact checks, and recorded failures. |
| [report](report/README.md) | Scientific paper, derivations, figures, and detailed experiment notes in LaTeX and PDF. |
| [documentation](documentation/README.md) | Checks that repository folders and code files have documentation. |

## Use the application

The recorded environment uses Python 3.9.6 and Kira 3.1. The application needs the project’s native builds and Python dependencies. NumPy and SymPy support numerical and exact operations; the original neural models use PyTorch. Plotting uses Matplotlib. The `.tools` environment and compiled binaries are local dependencies and are excluded from Git.

Run calculations in a scheduled Hoffman job. The recorded finite-field build uses Intel Gold compute nodes. From the repository root, the single-request command is:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/triangle_reduction/s32_deploy.py --case request.json --output ML_model_adaptive_reduction/triangle_reduction/requests/result.json --action integrated
```

`request.json` must contain a supported physical family, targets, and the application fields described in the [input guide](ML_model_adaptive_reduction/triangle_reduction/README.md). A stored training target is a different record format. Single-request output must stay inside the `triangle_reduction/` directory. Check the output’s `success` field before using its coefficients.

For a JSON list of requests, use `s33_batch.py` with `--cases requests.json --output results.jsonl --action integrated`. The output path must be new. A batch accepts 1–128 distinct request IDs and can leave partial output if interrupted.

For data inspection, [the integral reader](integrals/README.md) joins a target to its masters, coefficients, and reduction trace. Reproduction scripts are numbered in their recorded order. Run the steps required by the selected experiment; the repository contains several alternative methods and comparisons.

## Data and physical coverage

The constructed collection contains 17,100 family instances, 57,979 family-local master entries, and 2,301,272 targets. Related mass profiles stay together in the approximately 70:30 training/test division. A change of masses can create a new family instance without creating a new graph structure.

| Range | Demonstrated scope |
|---|---|
| 1–12 loops | Constructed training and test data; higher-loop additions mainly use a restricted coupled-vacuum family. |
| 1–5 loops | Completed cases in an earlier native shared-model comparison; only two matched requests reach five loops. |
| 2–3 loops | The primary direct comparison with default Kira on boxes, massive sunrise integrals, and a massive vacuum family. |
| Through 13 loops | Specified analytic tree, vacuum, and independent-product structures. |

The exact rules have explicit mass, invariant, power, and graph conditions. General connected high-loop scattering remains outside the demonstrated results. See [physical domains and application limits](ML_model_adaptive_reduction/triangle_reduction/README.md).

## Measured performance

The primary reference is the original Kira 3.1 executable with default algorithms for the specified reduction jobs. Both procedures receive the same targets, kinematics, and preferred master basis. Times below sum per-request medians from three repetitions.

| Integral class | Matched requests | Default Kira (s) | Combined method (s) | Speed factor |
|---|---:|---:|---:|---:|
| Two-loop planar double box | 4 | 227.019 | 5.715 | 39.73 |
| Two-loop massive sunrise | 5 | 18.806 | 6.519 | 2.88 |
| Three-loop massive vacuum | 5 | 20.633 | 9.875 | 2.09 |
| Matched total | 14 | 266.458 | 22.109 | 12.05 |

The combined method completes all 20 requested cases. Default Kira completes 14; six reach the 60-second limit, including all five nonplanar cases. The 12.05-fold result applies to the 14 matched requests and includes seed and arithmetic changes. It is not an isolated ML gain. The [comparison protocol](Kira_comparison/default_kira_final/README.md) specifies seed bounds, timing, resource limits, and checks.

An earlier shared-model test saves 4.9% against a matched fixed strategy on 43 completed requests. A restricted-vacuum recurrence gives a separate 534.9-fold gain against Kira solving supplied identities. These experiments use different controls; their factors cannot be combined. Other analytic requests have no matched default-Kira measurement in the primary test.

## Documents and resources

- [report.pdf](report/report.pdf): the scientific problem, methods, derivations, comparisons, and applicability limits.
- [notes.pdf](report/notes.pdf): detailed experiments, including rejected models and unsuccessful calculations.
- [Report build guide](report/README.md): LaTeX sources, figure producers, bibliography, and checks.

Training data, model weights, and native outputs belong on Hoffman and GitHub. The local checkout contains the documents and top-level guides. Keep total project storage below 10,000,000,000 bytes, including temporary files and caches. Use the memory and time limits in each scheduler wrapper. [rules.md](rules.md) records the project’s working conventions.
