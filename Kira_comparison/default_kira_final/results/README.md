# Recorded comparisons

Each compressed JSON file records one request, method, and repetition.
The default method uses the original Kira executable.
The method entry uses the frozen final application.
Records contain elapsed time, completion, exact checks, limits, and returned coefficients.
Read all three repetitions before calculating a request median.
Use only pairs verified in all repetitions for a finite speed factor.
Keep unsuccessful records in the completion counts.
Run ../s02_compare.py to produce these files.
Run ../s04_report.py to make the report table.
