# Training integrals

This folder contains 1610890 targets from 11963 complete families in the seed model's train split.

The master_integrals/, target_integrals/ and master_to_target/ folders contain relative directory links to the existing family files. These links form a separate, non-overlapping view; each integral file remains stored once. Each family belongs to exactly one model split. Full box kinematic profiles remain together across mass assignments. Added vacuum mass profiles stay together across loop orders.

manifest.json lists the family records and paths, relative to integrals/. Stored records retain their original canonical file links and historical split labels. This manifest and the model's split_manifest.json define the current 70:30 model division.

The training program reads only this split. The frozen expanded-data models will be evaluated on the separate testing split.
