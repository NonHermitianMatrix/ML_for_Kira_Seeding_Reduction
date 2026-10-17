# Application

Fresh-process comparisons with startup, input/output, and exact checks. These are a predeclared subset of the reserved physical requests.

Read [the study guide](../README.md) for the execution order and limits.
Files ending in `.json.gz` contain gzip-compressed JSON.
Use Python `gzip` and `json` to read them.
Trial files contain exact output coefficients, elapsed time, and attempt metadata.
The file name identifies the target batch, method, and repetition.
`protocol.json`, when present, defines all requested inputs before execution.
A completion file records the end of a stage; it does not assert that every request succeeded.
