# Frozen expanded-data test

The model completed twenty expanded-data training passes. Checkpoint SHA-256: 3e8e998cc12325e57ad180d704f6e0b7f4a2bacd9e35fe6c7eee94c055636998. The next test uses 114,382 targets from 637 held-out families spanning one through twelve loops. Weights, thresholds and confidence maps remain fixed. Training consumed no held-out labels.

Previous tests, figures and source are preserved in archive_before_all_loops/. Active test scripts now use the expanded manifest and report per-loop results. The seed test measures reference-set membership; the reduction test also replays complete exact target-row paths and compares their three sampled master expansions. Neither test proves globally optimal reductions or a full Kira speedup.
