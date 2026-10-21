# Development

These records contain profile-61 probes. They guide development and do not belong to the reserved test. The scripts s00_study.py and s03_truncate.py create these files.

See the [study guide](../README.md) for input definitions, script order, dependencies, limits, and timing scope.

Read a compressed record with Python:

```python
import gzip
import json
with gzip.open("record.json.gz", "rt") as stream:
    record = json.load(stream)
```

These records belong to cost models fitted to individual graph structures. Use matching case identifiers when combining files.
