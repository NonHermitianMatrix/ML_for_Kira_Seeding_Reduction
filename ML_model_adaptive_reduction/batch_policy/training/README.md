# Training

Complete candidate costs used to fit the partition predictor. The protocol fixes the physical requests and repetitions.

Read [the study guide](../README.md) for the execution order and limits.
Files ending in `.json.gz` contain gzip-compressed JSON.
Use Python `gzip` and `json` to read them.
Trial files contain exact output coefficients, elapsed time, and attempt metadata.
The file name identifies the target batch, method, and repetition.
`protocol.json`, when present, defines all requested inputs before execution.
A completion file records the end of a stage; it does not assert that every request succeeded.
