# Threshold validation

These records compare native reductions and three thresholds for each new model.
Three repetitions contribute to each validation median.
The driver chooses the threshold with the lowest geometric mean full-time ratio for each structure.
The rational and symbolic validation batches receive equal weight.
It saves the selected settings in `../freeze.json` before testing.
Reserved test results do not select these settings.

Use `s00_scattering_study.py validate` to produce these records.
Read [the study guide](../README.md) for inputs and limits.
