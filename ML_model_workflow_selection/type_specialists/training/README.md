# Training

These records measure strategies on profiles 62 and 63. They include exact coefficients, times, counters, resource peaks, and all failed attempts. The s04_train_test.py script reads them to fit the candidate models.

See the [study guide](../README.md) for input definitions, script order, dependencies, limits, and timing scope.

Read a compressed record with Python:

```python
import gzip
import json
with gzip.open("record.json.gz", "rt") as stream:
    record = json.load(stream)
```
