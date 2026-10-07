# Testing integrals

This folder contains 690382 targets from 5137 complete families in the seed model's test split.

The master_integrals/, target_integrals/ and master_to_target/ folders contain relative directory links to the existing family files. These links form a separate, non-overlapping view; each integral file remains stored once. Each family belongs to exactly one model split. Full box kinematic profiles remain together across mass assignments. Added vacuum mass profiles stay together across loop orders.

manifest.json lists the family records and paths, relative to integrals/. Stored records retain their original canonical file links and historical split labels. This manifest and the model's split_manifest.json define the current 70:30 model division.

These targets are reserved for frozen-model testing. Training does not read these examples or update parameters from them.

<!-- expanded-model-use -->
Both models completed twenty passes over the fixed expanded training division. The frozen test covers all 690,382 targets in the separate testing division. Model outputs and exact checks are stored in each model's model_test/ folder. Training used no held-out labels.
