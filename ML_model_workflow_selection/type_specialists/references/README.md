# References

These files contain independent native reductions with seed bounds expanded by one. The runner uses their master indices for basis admission. Timed comparisons also check their exact coefficients. Application checks withhold these coefficients until after reduction.

See the [study guide](../README.md) for input definitions, script order, dependencies, limits, and timing scope.

Read a compressed record with Python:

```python
import gzip
import json
with gzip.open("record.json.gz", "rt") as stream:
    record = json.load(stream)
```
