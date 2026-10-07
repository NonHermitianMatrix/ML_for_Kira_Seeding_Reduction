# Frozen expanded-data test

The model completed twenty expanded-data training passes. Checkpoint SHA-256: 0b6b51597329a1cade4642f066cf2b39dadd4339ec53927d0a1c3a150a627452. The next test uses 690,382 targets from 5137 held-out families spanning one through twelve loops. Weights, thresholds and confidence maps remain fixed. Training consumed no held-out labels.

Previous tests, figures and source are preserved in archive_before_expansion_250/. Active test scripts now use the expanded manifest and report per-loop results. The seed test measures reference-set membership; the reduction test also replays complete exact target-row paths and compares their three sampled master expansions. Neither test proves globally optimal reductions or a full Kira speedup.
