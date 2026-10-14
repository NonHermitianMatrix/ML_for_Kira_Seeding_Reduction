# Fitted cost models

`candidates.json` contains twelve models fitted from training batches only.
It gives feature names, training identifiers and model coefficients.
`freeze.json` contains the selected model, validation scores, margin and best fixed strategy.
It also identifies the input protocol, reduction driver, executable and saved filter weights.
Validation selects ridge regression with penalty 10 and saving margin zero.
The validation ratio is 0.992688 relative to integrated native choices.
Reserved tests do not alter these values or coefficients.

Read [the parent guide](../README.md) for model equations, commands and application inputs.
Read [the paper](../../report/report.pdf) for the derivations and completed results.
