# CPU resource check

The check compared one, two and four CPU threads while training job 15036272 continued unchanged. It used training records only, performed no optimizer updates and never read held-out testing examples. All benchmark outputs remain separate from the production model.

s00_cpu_scaling.py measures gradient calculations on 128 pre-encoded training targets. s01_run_cpu_scaling.sh requests four CPU cores and 8 GiB total memory for that check. cpu_scaling.json records three repetitions per thread count and a repeated one-thread reference. Two threads took 0.834 seconds per group at the median, compared with 0.998 and 1.287 seconds for the two one-thread groups. Four threads took 2.211 seconds. The largest observed gradient difference was 4.66e-10.

s02_end_to_end_scaling.py repeats input preparation and gradient calculations for 1,024 targets from five training families. s03_run_end_to_end.sh requests two CPU cores and 4 GiB total memory. end_to_end_scaling.json records results. The first one-thread pass took 7.850 seconds before the input feature cache was warm. The later one-thread pass took 6.155 seconds, while the later two-thread pass took 6.008 seconds, a throughput ratio of 1.024. Comparing averaged cold and warm timings would overstate the gain. This short result does not establish a useful overall training speedup.

decision.json records the choice to leave the current one-thread training job running. The production code, model parameters, optimizer state and data order were not changed. The checkpoint can support a later resource change without restarting training from initial weights. These timings measure resource use and do not measure seed-selection accuracy or held-out model performance.

The scheduler memory request is per allocated core; see the [Hoffman resource documentation](https://support.idre.ucla.edu/KB/View/2049342-requesting-the-appropriate-amount-of-resources-for-jobs-on-the-hoffman2-cluster). CPU thread controls follow [PyTorch documentation](https://docs.pytorch.org/docs/stable/generated/torch.set_num_threads.html). No GPU timing was performed.
