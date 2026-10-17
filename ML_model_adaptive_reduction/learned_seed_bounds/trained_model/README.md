# Trained model

Saved parameters and the model-selection record.
Read [the parent guide](../README.md) for commands, limits, and the full method.

`freeze.json` contains the selected parameters, feature names, domain limits, and provenance.
`fixed.json` contains only fixed action names. It contains no model weights.
`selection.json` contains all candidate validation scores and fit settings.
The runtime reads these files with `s01_runtime.py`.
Do not change them after the reserved test.
