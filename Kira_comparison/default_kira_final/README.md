# Complete method versus default Kira

This experiment compares the retained reduction method with the original Kira 3.1 executable. It uses 20 connected native requests: five planar double boxes, five nonplanar double boxes, five massive sunrise cases, and five three-loop vacuum cases. The boxes and sunrise have two loops. These physical inputs were used in earlier tests; this comparison changes the reference calculation.

## Compared calculations

The default control is `.tools/kira/bin/kira`. It generates its own IBP equations and uses default symbolic algorithms. Its positive-power, numerator-power, and extra-denominator-power bounds equal the respective target maxima plus one. The positive-power bound also covers the supplied top sectors. These are explicit problem settings. The runner removes project `KIRA_` environment options before starting the original executable.

The method calls `ML_model_adaptive_reduction/triangle_reduction/s32_deploy.py` with its frozen integrated choices. The box and sunrise cases use finite-field reconstruction in batches of eight evaluations. The vacuum cases retain their validated preceding procedure. The added arithmetic model, row model, and extra equation filter are disabled.

Both calculations receive the same family, targets, rational kinematics, symbolic dimension, and preferred master indices. They receive no reference coefficients. Initial master-basis discovery and model training are outside the comparison.

## Timing and verification

Each request starts a fresh process and uses one computational thread. Each pair uses the same Intel Gold node. Three repetitions reverse method and request order in the middle repetition. The resumed comparison uses another node of the same class for remaining pairs.

Timing includes startup, input reading, preparation, model use, equation generation, algebra, output reading, cleanup, and recovery. Independent reference preparation and coefficient checks remain outside both timers. The monitor allows 60 seconds and 8 MiB of temporary reduction files per request. Use one scheduled worker; the completed allocations reserved 4–8 GiB and allowed 8 GiB of virtual memory.

A request enters the time ratio only when both calculations pass in all repetitions. The summary sums each request’s median time. Default Kira completes 14 requests; the method completes 20. The 14 matched requests take 266.458 and 22.109 seconds, respectively, giving a factor of 12.05. Six default requests time out. Their records remain available, and no finite factor is assigned to them. The independent audit performs 2,445 coefficient comparisons.

The other 73 analytic requests in the earlier mixed collection are outside this direct comparison. This experiment measures the combined method; it does not isolate the ML contribution.

## Files and execution order

| File | Use |
|---|---|
| `s00_original_runner.py` | Prepare default-Kira inputs and read the exported coefficients. |
| `s01_request.py` | Run one default or integrated request. |
| `s02_compare.py` | Load fixed inputs, run paired measurements, and check coefficients. |
| `s03_compare.sh` | Schedule the comparison from the repository root. |
| `s04_report.py` | Create the report table and compact evidence after the comparison completes. |
| `protocol.json.gz` | Physical inputs, master indices, frozen sources, and limits. |
| `baseline_provenance.json`, `driver_provenance.json` | Identity of the original executable and measurement-driver versions. |
| `results/` | Compressed per-request outputs, times, limits, and verification outcomes. |
| `summary.json` | Completion counts, matched times, and the aggregate result. |

Submit `qsub Kira_comparison/default_kira_final/s03_compare.sh` from the repository root to reproduce the experiment. Its wrapper declares the environment and limits. Preserve existing measurements before defining a new comparison. `s04_report.py` writes manuscript sections, so inspect its destinations before using it with a revised paper.

## Setup and interruption records

`setup_failed_results/` and `setup_failed_summary.json` preserve launch failures caused by a scheduler file-size limit. `initial_monitor_failure.txt` records a file-removal race during storage monitoring. `interrupted_measurement.log` records a timeout-cleanup interruption. The corresponding protocol snapshots identify those settings. These records are excluded from physical reduction timing. Completed verified pairs survived the cleanup correction; the remaining pairs use unchanged physical inputs and models.
