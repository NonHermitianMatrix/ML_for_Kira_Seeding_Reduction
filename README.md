# Project guide

This project studies machine learning for exact Feynman integral reduction with Kira.
A seed is an integral index vector that supplies integration-by-parts identities.
A master integral is a retained basis integral.
A target is an integral or an expression that must be reduced.

Read [the paper](report/report.pdf) for the methods, derivations, results and limits.
Read [the notes](report/notes.pdf) for the earlier experiments.
The seed model and equation model have separate tested uses.
The retained method uses Kira's native row choices.
The large vacuum speedup also uses exact recurrences and repeated coefficients.
It is not a measured gain from machine learning alone.

For compatible target requests, use [the joint application](ML_model_workflow_selection/README.md).
Its standard route keeps the best fixed training strategy and makes learned choices optional.
The paired-request comparison gives 48.3 percent less time across seven graph structures at one through three loops.
The gain comes mainly from sharing the reduction.

Start with [the integral collection](integrals/README.md).
Then read the model folder for the required task.
Use [early equation selection](ML_model_equation_selection/early_generation/README.md) for the supported native reductions.
Use [the symbolic application](Kira_comparison/generalization/README.md) for the tested new scattering families.

A README describes the files directly inside its folder.
Child folders have their own READMEs.
Script numbers show the recorded development order.
They do not require every historical script to run again.
Archived code and earlier failed experiments remain available for comparison.

The primary project copy is on Hoffman.
Integral data and model data stay on Hoffman and GitHub.
The report and notes also have local copies.
Keep combined project storage below 10,000,000,000 bytes.
Run training and reductions in scheduled jobs.
Keep the limits in each job script and resource plan.

The guides use ASD-STE100 sentence rules and consistent technical terms.
See the [ASD specification](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).
Exact file names, commands, symbols and option values remain unchanged.
JSON files contain named data fields.
JSONL files contain one record per line.
The suffixes `.gz` and `.xz` identify compressed files.
The project readers restore these records without changing the stored files.
NPZ files contain named NumPy arrays.
PT files contain saved PyTorch model data.
A checkpoint contains saved model parameters and, where present, the optimizer state.
A fallback repeats an incomplete selected reduction with native equations.
A SHA-256 value identifies file content for a file check.
A matching file check does not prove a physical or mathematical claim.

## Data and supporting files

- [.gitattributes](.gitattributes): This file supports the calculation described in the parent guide.

- [.gitignore](.gitignore): This file supports the calculation described in the parent guide.

- [rules.md](rules.md): This document gives additional instructions or earlier notes.

## Child folders

- [Kira_comparison](Kira_comparison/README.md).

- [ML_model_equation_selection](ML_model_equation_selection/README.md).

- [ML_model_reduction](ML_model_reduction/README.md).

- [ML_model_seed_selection](ML_model_seed_selection/README.md).

- [ML_model_workflow_selection](ML_model_workflow_selection/README.md).

- [documentation](documentation/README.md).

- [integrals](integrals/README.md).

- [report](report/README.md).

## Additional scattering training

Read [the new scattering study](ML_model_equation_selection/scattering_training/README.md) for training on the three previously unsupported structures.
It contains new seed and equation trees, separate validation and test batches, and full native Kira comparisons.
The original models and negative transfer results remain available.
The updated paper uses simpler explanations and comparison tables.

## Complete reduction cost

The [complete-cost study](ML_model_workflow_selection/README.md)
compares models that choose a full reduction strategy from measured time.
It combines seed bounds, saved seed and equation filters, integral ordering,
and the existing temporary database change.
It also compares separate target requests with their joint reduction.
The study includes full native IBP generation and all fallback costs.
It retains the earlier model weights and results.
Its native cases cover seven graph structures at one through three loops.
The restricted vacuum results through twelve loops remain a separate result.
See that folder for the frozen model, test summaries and application commands.

## Models for each graph type

The graph-specific cost study fits separate policy candidates for seven known graph structures.
It compares full exact Kira reductions, including failed attempts and retries.
See [the study guide](ML_model_workflow_selection/type_specialists/README.md) for code, models, tests, inputs, and limits.
The current paper and notes include the mathematical method and measured results.

<!-- BEGIN GRAPH POLICY RESULTS -->

## Completed graph-policy results

The final fit contains 70 candidates for seven graph types.
It uses 544 training cost records and 408 separate validation records.
The reserved test contains 720 timing trials and 43 further application checks.
All checks pass.
The selected-to-native geometric mean time ratio is 0.936849.
Its descriptive interval is [0.886703, 0.987789].
The selected-to-fixed ratio is 0.944077.
Its descriptive interval is [0.899157, 0.986347].
Each graph has equal weight in these aggregate ratios.
A ratio below one means less complete reduction time.
The selected route has a ratio below one in 5 of the seven graph groups.
The inputs use known graph structures and target patterns at new rational profiles.
These results give no speed guarantee for other inputs.

See the study guide for the graph results and limits.

<!-- END GRAPH POLICY RESULTS -->
