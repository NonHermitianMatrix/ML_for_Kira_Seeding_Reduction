# Seed-selection models

This directory contains the original neural seed-membership model and later native seed-cost experiments. The neural model predicts reference-set membership; an exact reduction determines whether its chosen equations suffice. The combined application uses separately validated native policies from the later studies.

This model assigns a separate membership probability to each supplied candidate seed.
Several seeds can receive label one.
The label test uses a probability threshold of 0.5.
The model has 28,097 parameters.
Its input contains target terms, ordered term pairs, family information, master indices and candidate indices.
Reference coefficients and future reduction steps remain outside the input.

`trained_model.pt` contains the current prediction model.
`runs/all_loops_latest.pt` retains the optimizer and resume position.
`data/` contains encoded training inputs.
`model_test/` contains the frozen model tests.
`kira_sufficiency_test/` checks whether predicted sets supply enough equations.

The current training sequence uses `s12_prepare_features.py`, `s13_batch.py` and `s14_train_all_loops.py`.
`s15_run_all_loops.sh` provides the scheduled job.
`s16_validate_all_loops.py` checks the saved training result.
Scripts `s00` through `s11` retain the initial workflow.

The current model completed twenty additional passes over 1,610,890 training targets.
AdamW uses learning rate 0.001 and weight decay 0.0001.
The gradient norm limit is one.
Training uses up to 32 targets per update.
The model accepts at most sixteen indices, 512 terms and 10,000 candidate seeds.
Its 64-component coefficient encoding can assign different expressions to the same component.

Run prediction from the project root in the existing Python environment:

```bash
.tools/seed-model/venv/bin/python ML_model_seed_selection/s04_predict.py --checkpoint ML_model_seed_selection/trained_model.pt --target FAMILY:ID
```

Replace `FAMILY:ID` with a stored target identifier.
The output gives `predicted_label`, `probability_1`, `probability_0` and `confidence`.
The confidence is a model score.
The exact reduction determines whether the selected set is sufficient.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Scripts

| File | Purpose |
|---|---|
| [s00_prepare_data.py](s00_prepare_data.py) | Audit seed supervision and prepare a reproducible grouped 70:30 split; it does not fit a model. |
| [s01_data.py](s01_data.py) | Streaming inputs with a strict boundary between problem features and reference labels. |
| [s02_model.py](s02_model.py) | Small shared neural scorer; every output is a reference-set membership probability. |
| [s03_train.py](s03_train.py) | Train the seed model on the training split only; save resumable and final weights here. |
| [s04_predict.py](s04_predict.py) | Ranks an input target's bounded candidate pool using an explicitly supplied trained checkpoint. |
| [s05_evaluate.py](s05_evaluate.py) | Future held-out comparison with recorded sufficient sets; no exact-reduction claim. |
| [s06_check.py](s06_check.py) | Implementation checks only: no optimizer, learned checkpoint or performance estimate. |
| [s07_run.sh](s07_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s08_setup_environment.sh](s08_setup_environment.sh) | Scheduler wrapper for setup environment; its header sets the resource limits. |
| [s09_check_training_inputs.py](s09_check_training_inputs.py) | Check training input reuse and resume ordering without evaluating the test split. |
| [s10_finalize_training.py](s10_finalize_training.py) | Verify the saved training artifact and update status documentation; never run testing. |
| [s11_run_training.sh](s11_run_training.sh) | Scheduler wrapper for run training; its header sets the resource limits. |
| [s12_prepare_features.py](s12_prepare_features.py) | Prepare bounded immutable features using training families only. |
| [s13_batch.py](s13_batch.py) | Masked batch execution of the existing seed scorer, with identical features and weights. |
| [s14_train_all_loops.py](s14_train_all_loops.py) | Continues saved weights and optimizer for twenty complete passes over expanded training data. |
| [s15_run_all_loops.sh](s15_run_all_loops.sh) | Scheduler wrapper for run all loops; its header sets the resource limits. |
| [s16_validate_all_loops.py](s16_validate_all_loops.py) | Validates the expanded-data checkpoint and preserve its training provenance. |
| [s17_run_batch_pilot.sh](s17_run_batch_pilot.sh) | Scheduler wrapper for run batch pilot; its header sets the resource limits. |
| [s18_validate_mixed_batches.py](s18_validate_mixed_batches.py) | Check batched seed scores and derivatives on mixed-length training examples. |
| [s19_run_batch_validation.sh](s19_run_batch_validation.sh) | Scheduler wrapper for run batch validation; its header sets the resource limits. |

## Data and supporting files

- [config.json](config.json): This file sets the model or calculation options.

- [data_audit.json](data_audit.json): This file records checks of the corresponding calculation.

- [implementation_checks.json](implementation_checks.json): This file records checks of the corresponding calculation.

- [release_manifest.json](release_manifest.json): This file identifies the saved release files.

- [requirements.txt](requirements.txt): This file lists the Python package requirements.

- [source_hashes.json](source_hashes.json): Saved source_hashes.json record for selection of IBP seeds; the producer code defines its fields.

- [split_manifest.json](split_manifest.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [data](data/README.md).

- [kira_sufficiency_test](kira_sufficiency_test/README.md).

- [model_test](model_test/README.md).

- [runs](runs/README.md).

- [runtime_inference](runtime_inference/README.md).

## Additional scattering training

The [scattering seed folder](scattering_training/README.md) stores three new native seed trees.
The shared study contains their training data and full Kira comparisons.
The earlier neural model remains unchanged.

## Complete reduction cost

The [complete-cost study](../ML_model_workflow_selection/README.md)
compares models that choose a full reduction strategy from measured time.
It combines seed bounds, saved seed and equation filters, integral ordering,
and the existing temporary database change.
It also compares separate target requests with their joint reduction.
The study includes full native IBP generation and all fallback costs.
It retains the earlier model weights and results.
Its native cases cover seven graph structures at one through three loops.
The restricted vacuum results through twelve loops remain a separate result.
See that folder for the frozen model, test summaries and application commands.

## Related application

The [combined reduction application](../ML_model_adaptive_reduction/triangle_reduction/README.md) integrates the retained exact and learned methods. The [selective-expansion experiment](../ML_model_adaptive_reduction/selective_expansion/README.md) compares candidate seed and worker settings.

## Independent component checks

The [component and higher-loop study](../Kira_comparison/higher_scattering/README.md) tests each decision with matching targets and exact checks.
It preserves the earlier models and results.
It also records connected scattering tests, initialization costs, and incomplete calculations.
Read its summary for the measured contributions and tested domain.

The [cost geometry study](cost_geometry/README.md) trains seed boundaries from complete Kira times.
It includes fitted models, separate test cases, exact checks, and the complete application.

The [joint-policy study](joint_policy/README.md) tests combined seed and Kira configuration choices using complete reduction time.
Validation retains the preceding ML application for both graphs.
It also implements a separately derived scale transformation for exact reuse.
That guide defines the experiment’s application and comparison controls.
