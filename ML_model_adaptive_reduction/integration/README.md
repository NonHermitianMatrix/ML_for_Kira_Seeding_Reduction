# Integration

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

Source patches and build commands for exact file indexing and the projected zero-sector criterion. The full Kira source and earlier binaries remain unchanged.

Read the [main guide](../README.md) for inputs, outputs, scripts, and resource limits.
Use the documented producer scripts to reproduce these files.
Compressed JSON records use seconds for time and bytes for storage and memory.
Keep completed records unchanged.

## Additional scripts

- [sector_files.patch](sector_files.patch): Source changes for sector files; apply them only to the matching Kira source version.
- [zero_criterion.patch](zero_criterion.patch): Source changes for zero criterion; apply them only to the matching Kira source version.
