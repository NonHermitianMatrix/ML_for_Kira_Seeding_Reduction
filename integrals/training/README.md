# Training integrals

This folder contains 168330 targets from 693 complete families in the seed model's train split.

The master_integrals/, target_integrals/ and master_to_target/ folders contain relative directory links to the existing family files. These links form a separate, non-overlapping view; each integral file remains stored once. Each family belongs to exactly one model split. Full box kinematic profiles remain together across mass assignments.

manifest.json lists the family records and paths, relative to integrals/. Stored records retain their original canonical file links and historical split labels. This manifest and the model's split_manifest.json define the current 70:30 model division.

The training program reads only this split. Testing remains a later, separately authorized step.
