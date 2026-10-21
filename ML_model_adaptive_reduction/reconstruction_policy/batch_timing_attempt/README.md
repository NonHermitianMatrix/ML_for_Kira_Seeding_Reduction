# Preliminary batch timing

The shared-call timer stopped after process exit. The separate-call timer also included reading returned data and cleanup. We stopped the remaining preliminary repetitions after finding this timing-boundary difference. The preserved verified results and any interrupted files remain here. The complete final comparison repeats all four methods with aligned timers. The reduction application, policies, and physical requests are unchanged. These preliminary times do not enter the final summary.

## Additional scripts

- [s38_prepare_batch.py](s38_prepare_batch.py): Freeze a timing-only implementation comparison on the verified request grid.
- [s39_batch_test.py](s39_batch_test.py): Compare all completed requests with one or separate application processes.
