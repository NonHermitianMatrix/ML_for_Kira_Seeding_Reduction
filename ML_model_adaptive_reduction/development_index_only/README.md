# Development index only

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

Development build with file indexing in both triangular reduction and back-substitution. It does not project the zero-sector criterion.

Read the [main guide](../README.md) for inputs, outputs, scripts, and resource limits.
Use the documented producer scripts to reproduce these files.
Compressed JSON records use seconds for time and bytes for storage and memory.
Keep completed records unchanged.

## Additional scripts

- [sector_files.patch](sector_files.patch): Source changes for sector files; apply them only to the matching Kira source version.
