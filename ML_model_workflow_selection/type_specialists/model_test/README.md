# Model test

These records contain the reserved trials at profiles 65 and 66. The s07_finish.py script runs frozen policies and checks the public application. The s05_analyze.py script creates summary.json and the paper plot. Each compressed record contains exact coefficients and measured costs. Public input files contain the case and master basis. They contain no target reference coefficients. The public_checks.json file records the independent checks.

See the [study guide](../README.md) for input definitions, script order, dependencies, limits, and timing scope.

Read a compressed record with Python:

```python
import gzip
import json
with gzip.open("record.json.gz", "rt") as stream:
    record = json.load(stream)
```

## Completed checks

All 720 reserved timing trials pass.
All 36 basis-only applications and seven public applications pass.
The checks cover 14,040 timing-trial coefficient entries and 945 application entries.
The s08_validate.py script writes evidence_validation.json in the study folder.
See summary.json and the [study guide](../README.md) for time ratios and limits.
