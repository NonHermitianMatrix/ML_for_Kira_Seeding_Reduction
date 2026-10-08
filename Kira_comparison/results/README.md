
<!-- main-comparison-records -->
# Main comparison records

Each compressed JSON file contains one bounded trial, identified by family-case number, target-batch size, repeat and method. The public plan fixes 792 trials. Records include fresh model predictions or row paths, attempts, equation counts, full rational target coefficients, exact checks, elapsed time, sampled summed resident memory and archived solver configurations, exports and logs. status and complete files describe array progress; environment files identify the compute node and CPU. No temporary solver databases are retained.

Only these main records enter ../summary.json. Pilot and interrupted adapter versions remain in separately named folders and are excluded. ../validation.json binds each measured record by hash, checks the immutable inputs and independently verifies exports and row operations. Native generation on the same independent bases also appears here as two main controls; the four-method learned-native comparison has its own ../native_seed/results/ records.
