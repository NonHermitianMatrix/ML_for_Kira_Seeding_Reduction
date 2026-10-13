# Scattering seed trees

This folder contains three new seed-selection trees for scattering integrals.
The structures are the nonplanar two-loop box, pentagon, and box with one external virtuality.
These trees extend the native seed-selection tests.
They do not replace the earlier neural checkpoint.

Each seed receives a separate membership score.
A seed has training label one when one or more of its equations appear in the native selected-support records.
The tree uses sixteen family, target and seed features.
It excludes the operator index and all equation-coefficient features.
Thus all operators of one seed receive the same score.
Kira skips coefficient construction for rejected seeds and retains native row choices.

The [shared study folder](../../ML_model_equation_selection/scattering_training/README.md) contains the code and data.
Read that guide for execution order, dependencies, split definitions and resource limits.
The data are stored once in that folder.

[trained_model](trained_model/README.md) contains a JSON model and native text weights for each structure.
[model_test](model_test/README.md) contains the seed-specific summary.
The full timing and exact-check records remain in the shared study folder.

The fit uses training data only.
Validation sets the retention threshold before testing.
The models estimate reference-set membership, not a calibrated probability of successful reduction.
Use the basis check and native fallback for every reduction.
Read the measured timing results before activating a policy.

The new seed trees complete all 45 first attempts without fallback.
Their full-time ratio to native Kira is 1.0271, with a descriptive interval from 0.9952 to 1.0859.
This test gives no established overall time saving.
Native choices remain the application default for these scattering cases.
