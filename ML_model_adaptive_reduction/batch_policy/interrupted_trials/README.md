# Interrupted comparison records

The scheduler stopped two jobs at their original one-hour limits.
It had accepted longer limits without extending the running allocations.
Complete comparison batches remain in `../model_test/`.
This folder preserves timings from unfinished batches, original worker logs, and completion records.
Each unfinished batch repeats all methods and repetitions on one new worker.
These archived timings do not enter the matched timing ratios.
Read `../interruption_recovery.json` for the file list and reason.
No outcome or speed determined which batches repeated.
