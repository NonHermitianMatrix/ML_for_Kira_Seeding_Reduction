# Expansion in progress

The next phase adds 250 mass profiles at every loop order from one through twelve, preserves all previous assignments, and will train twenty additional full passes. The previous completed model and optimizer remain in runs/before_expansion_250/. Active trained_model.pt and model_test results still belong to the preceding release until their replacements pass validation. No new training or testing has completed yet.

# Encoded seed-training examples

This folder contains encoded examples for 266,890 training targets from 1,463 families spanning loop orders one through twelve. Original symbolic inputs, seeds and references remain in ../../integrals/. The current grouped assignment is defined by ../split_manifest.json. Held-out targets and labels do not enter these feature archives.

Each family archive stores target-term features and offsets, binary reference-membership labels, public family features, master-index features and candidate-seed features. The model reuses the public family, master and candidate arrays while its learned weights continue to change. All ordered pairs of distinct terms are constructed during the batched model calculation.

manifest.json identifies every archive, its checksum, input provenance and counts. Load archives with numpy.load(..., allow_pickle=False). s12_prepare_features.py reuses an existing archive only when its original data and encoding hashes agree. The original exact coefficients and mathematical proofs remain in the canonical integral records.

The seed model scores each supplied candidate separately. Positive labels identify seeds used by one recorded sufficient reduction; negative labels identify absence from that record. Labels do not assert globally minimal or unique seed sets.
