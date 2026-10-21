# Validation

These records measure strategies at profile 64. The s04_train_test.py script uses them to select one policy for each graph. These records never become reserved test results.

See the [study guide](../README.md) for input definitions, script order, dependencies, limits, and timing scope.

Read a compressed record with Python:

```python
import gzip
import json
with gzip.open("record.json.gz", "rt") as stream:
    record = json.load(stream)
```

These records belong to cost models fitted to individual graph structures. Use matching case identifiers when combining files.
