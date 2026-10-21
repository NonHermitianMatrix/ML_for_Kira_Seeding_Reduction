# Wide integration

s16_build_wide.py rebuilds the same exact implementation with 128-bit Kira weights. s17_wide_checks.py repeats the predefined storage grid. This width changes an internal ordering representation and leaves the algebra exact.

Read the main folder guide for execution order and limits.

## Additional scripts

- [sector_storage.patch](sector_storage.patch): Source changes for sector storage; apply them only to the matching Kira source version.
- [sector_weights.patch](sector_weights.patch): Source changes for sector weights; apply them only to the matching Kira source version.
- [zero_terms.patch](zero_terms.patch): Source changes for zero terms; apply them only to the matching Kira source version.
