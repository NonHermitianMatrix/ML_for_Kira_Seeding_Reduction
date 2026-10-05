# Testing integrals

This folder contains 72142 targets from 307 complete families in the seed model's test split.

The master_integrals/, target_integrals/ and master_to_target/ folders contain relative directory links to the existing family files. These links form a separate, non-overlapping view; each integral file remains stored once. Each family belongs to exactly one model split. Full box kinematic profiles remain together across mass assignments.

manifest.json lists the family records and paths, relative to integrals/. Stored records retain their original canonical file links and historical split labels. This manifest and the model's split_manifest.json define the current 70:30 model division.

These targets are reserved for later testing. The current training run does not read these examples or update parameters from them.

The authorized held-out model test is now complete for all 72,142 targets. Predictions, metrics and graphs are in ../../ML_model_seed_selection/model_test/. Testing used the saved model and kept the 0.5 threshold fixed; it did not update the weights or change this split.
