# Fitted equation trees

Each JSON file stores one graph-specific tree, feature list and training record list.
Its matching text file supplies the same tree to the native Kira filter.
The first text line gives the number of nodes.
Each remaining line gives feature, cut value, left child, right child and leaf probability.
A negative feature index marks a leaf.
The seed models are stored in the separate seed model folder.

The models use training records only.
Validation selects thresholds, which are stored in `../freeze.json`.
Use `s00_scattering_study.py train` to create these files.
Read [the study guide](../README.md) for the model definitions and limits.
