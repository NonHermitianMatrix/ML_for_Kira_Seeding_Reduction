# Runtime bottleneck audit

Diagnostic timings of the current native Kira baseline. The wrapper timestamps line-buffered native output. Existing exact reference checks verify each result. Twelve sequential runs cover sunrise, double-box and two three-loop ladder profiles. No model weights, production code, or report files change. Timings from this diagnostic wrapper are separate from published benchmark timings.

The initial diagnostic invocation stopped at the allowed-binary check before running Kira. The retained diagnostic runner copy adds only this timestamp wrapper to its explicit binary list and uses the existing project paths. Production checks and code remain unchanged.

All twelve diagnostic reductions passed the exact reference checks. s04_summarize.py saves summary.json with nonoverlapping phase intervals, per-run evidence, resource measurements and source hashes. The original benchmark records remain unchanged. Fresh timings include wrapper and logging costs on a different compute node; they supply stage attribution, not a speedup comparison. No report, model weights or production files were changed.
