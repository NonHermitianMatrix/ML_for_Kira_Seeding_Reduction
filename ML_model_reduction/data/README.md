# Expansion in progress

The next phase adds 250 mass profiles at every loop order from one through twelve, preserves all previous assignments, and will train twenty additional full passes. The previous completed model and optimizer remain in runs/before_expansion_250/. Active trained_model.pt and model_test results still belong to the preceding release until their replacements pass validation. No new training or testing has completed yet.

# Derived reduction training states

The original integral records remain in ../../integrals/. This folder contains only derived features for the expanded 1,463 training families spanning loop orders one through twelve. The current grouped split is defined by ML_model_seed_selection/split_manifest.json.

Each training/<family>.npz contains features, offsets, labels, target_number, step_number, target_ids and action_ids. For state i, features[offsets[i]:offsets[i+1]] gives its candidate features; labels[i] is the local index of the recorded chosen action. The corresponding equation IDs use the same slice of action_ids. target_ids[target_number[i]] and step_number[i] locate the original state.

All arrays use numeric or Unicode dtypes. Load them with numpy.load(..., allow_pickle=False). Matching JSON files record original source hashes, counts and each archive's hash. manifest.json defines feature order, provenance, aggregate counts and the reserved test family IDs. It does not contain held-out matrices or labels.

The after-row and reference choice are used to check the data and supply labels. Model features use the before-row and all candidate identities only. Training code selects states with at least two actions; forced states remain in each archive for auditing.

These files stay on Hoffman and GitHub, not in the local checkout.
