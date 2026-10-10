# Trained model

model.json contains the tree, feature order, training provenance and empirical leaf probabilities. weights.txt exports the same tree to the C++ filter. s09_predict.py returns both class probabilities and the thresholded label. These probabilities have not been calibrated on independent data.

Validation chooses a threshold based on complete runtime. freeze.json will record the model and implementation hashes before testing. Native Kira determines the exact reduction coefficients.
