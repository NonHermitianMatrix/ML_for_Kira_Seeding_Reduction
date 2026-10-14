# Trained model

The candidates.json file contains all seventy fitted predictors.
The freeze.json file records the selected models, fixed controls, feature limits, and validation choices.
The s04_train_test.py script makes the first fit.
The s10_pair_training.py script repeats comparisons that used different workers, then makes the final fit.
It saves the first fit in development/paired_costs/.
Both fits use training costs and validation choices only.
Preserve the final files after reserved testing.

See the [study guide](../README.md) for input definitions, script order, dependencies, and limits.
