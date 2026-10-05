# Derived reduction training states

The original integral records remain in ../../integrals/. This folder contains only derived features for the existing 693 training families. The grouped split remains the one in ML_model_seed_selection/split_manifest.json.

Each training/<family>.npz contains features, offsets, labels, target_number, step_number, target_ids and action_ids. For state i, features[offsets[i]:offsets[i+1]] gives its candidate features; labels[i] is the local index of the recorded chosen action. The corresponding equation IDs use the same slice of action_ids. target_ids[target_number[i]] and step_number[i] locate the original state.

All arrays use numeric or Unicode dtypes. Load them with numpy.load(..., allow_pickle=False). Matching JSON files record original source hashes, counts and each archive's hash. manifest.json defines feature order, provenance, aggregate counts and the reserved test family IDs. It does not contain held-out matrices or labels.

The after-row and reference choice are used to check the data and supply labels. Model features use the before-row and all candidate identities only. Training code selects states with at least two actions; forced states remain in each archive for auditing.

These files stay on Hoffman and GitHub, not in the local checkout.
