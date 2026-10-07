# Frozen expanded-data test

The model completed twenty expanded-data training passes. Checkpoint SHA-256: b8fb9cc088bd4e0cbbe1168d1e5fbd733ebea361fd41d3de48827672732ed977. The next test uses 690,382 targets from 5137 held-out families spanning one through twelve loops. Weights, thresholds and confidence maps remain fixed. Training consumed no held-out labels.

Previous tests, figures and source are preserved in archive_before_expansion_250/. Active test scripts now use the expanded manifest and report per-loop results. The seed test measures reference-set membership; the reduction test also replays complete exact target-row paths and compares their three sampled master expansions. Neither test proves globally optimal reductions or a full Kira speedup.
