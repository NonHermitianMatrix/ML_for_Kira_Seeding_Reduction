# Smaller-region failure diagnostic

After completing the frozen comparison, we repeated the 128-target validation_01_double_box calculation with margin zero using the responsive stock executable and the instrumented native executable. Both retain the prescribed reference basis and the same solver memory, scratch and time limits.

Both attempts passed early master admission and then reported std::bad_alloc during back substitution. This failure also occurs without the row-policy hook. The logs alone do not establish physical RAM exhaustion.

summary.json records the purpose and outcomes. The compressed records preserve full logs, inputs and limits through shared payloads; use s04_records.read_record to resolve them. s33_baseline_diagnostic.py and s34_baseline_diagnostic.sh reproduce this diagnostic.

These runs concern failure mechanism. They do not enter primary performance comparisons, alter the frozen models or thresholds, or add reserved test cases.
