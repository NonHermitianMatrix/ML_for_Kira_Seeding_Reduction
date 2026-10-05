# Reduction propagation model

This folder contains the next-step reduction model. It receives a current coefficient matrix and the complete list of steps allowed by the caller. It returns one probability for each step, the selected step, and its confidence. An exact finite-field row operation can apply the selected step.

The current training data describe one target coefficient row reduced against fixed source identities. At each state the available actions use identities whose leading integral equals the target's largest remaining nonmaster integral under the stored ordering. The interface accepts multiple destination rows, but training on these records does not establish performance on Kira's full evolving matrix.

Confidence means the model's uncalibrated probability of matching the recorded reference choice among the supplied actions. These choices give known valid paths. They are not proved optimal. Other listed actions may also be valid or cheaper. A single allowed action has probability one without a learned choice.

## Model and exact arithmetic

For action (q,r,k), use source identity q to cancel integral column k in destination row r:

    A[r,j] <- A[r,j] - (A[r,k] / A[q,k]) * A[q,j]

The source must be a zero identity; the destination can be an identity or a target expression. The pivot must be nonzero in both rows and must not be a protected master column. The caller enforces its ordering and supplies all admissible actions. The optional enforce_reference_order flag additionally checks the stored integral order used by the current training collection.

The model uses 132 features per action: pivot indices and complexity, source and destination row summaries, matrix size and sparsity, one-step cancellations and fill-in, arithmetic counts, and public family information. It performs one sparse modular trial update per action to obtain the local counts. It does not enumerate later reduction paths. Modular residues never enter the model as real-valued magnitudes.

A shared 32-component encoder maps these features to candidate vectors. Their mean and componentwise maximum describe the candidate set. A shared 64-component hidden layer produces a score for each action. A softmax returns probabilities summing to one. The network has 10,529 parameters. Candidate IDs are used only for output and deterministic tie-breaking.

## Data and training

The existing grouped division is unchanged: 693 families and 168,330 targets supply training records; 307 families and 72,142 targets remain held out. All states from a target remain in its family. No held-out integral records are read during preparation or training.

data/training/<family>.npz holds derived float32 features, state offsets, reference-action indices, target IDs, step numbers and candidate equation IDs. Matching JSON files record source hashes, counts and the shard hash. data/manifest.json records the complete preparation. These are derived training features; original matrices and exact identities stay in integrals/.

Every selected reference action is replayed in exact modular arithmetic during preparation. The replay checks the next sampled row, the multiplier, recorded operation counts, trace continuity and final master support. It recomputes fill-in and cancellations from the sampled matrix. The original support counts describe symbolic rows and can differ when a coefficient vanishes at the sample; the preparation records these differences. No future rows, selected equation IDs, final master coefficients, construction histories or future operation counts enter predictive features. All supplied candidate identities contribute in the same way.

Training minimizes mean next-choice cross-entropy over states with at least two actions. Forced states remain in the audit and have zero loss. AdamW uses learning rate 0.001, weight decay 0.0001, batches of up to 256 states, a gradient norm cap of one, and ten passes. Sixteen families form each bounded shuffle group. The final pass defines the saved model. The fixed model has now been tested through complete target-row sequences and confidence reliability measurements in model_test/. Fitting a calibration map and full Kira timing comparisons remain separate tasks.

runs/status.json gives the current stage. runs/history.json records pass losses and reference-choice agreement during updates. These are training measurements, not held-out accuracy. runs/latest.pt contains resumable model and optimizer state. trained_model.pt contains the final model, feature definition and configuration. trained_model.json gives the final counts, provenance, resource use and model hash.

## Scripts and order

1. s00_common.py: paths, hashing, atomic writes and storage guards.
2. s01_state.py: input validation, feature construction and exact row operations.
3. s02_prepare_data.py: training-only preparation and exact replay checks; reuse unchanged family shards on restart.
4. s03_model.py: shared candidate encoder and probability model.
5. s04_train.py: training and checkpoint resume.
6. s05_predict.py: next-step probabilities, confidence and optional exact update.
7. s06_check.py: mathematical and implementation checks with small synthetic matrices.
8. s07_run_training.sh: scheduler wrapper that runs checks, prepares training records and completes training.
9. s08_finalize.py: verifies saved artifacts and updates the scientific report with completed training measurements.
10. s09_finalize_report.sh: bounded scheduler wrapper for final checks and PDF rendering.

From the project root, submit training:

    qsub ML_model_reduction/s07_run_training.sh

The wrapper uses the existing Python environment. It requests one CPU and 4 GiB, limits virtual memory to 3 GiB, and writes checkpoints after each family group. Repeating the wrapper resumes at the last completed group with the same configuration and data hashes. It does not change or retrain the seed model.

After training:

    qsub ML_model_reduction/s09_finalize_report.sh

Use the existing environment for prediction:

    source /u/local/Modules/default/init/modules.sh
    module load python/3.9.6
    .tools/seed-model/venv/bin/python ML_model_reduction/s05_predict.py \
        path/to/current_state.json --apply --output path/to/prediction.json

The JSON input contains:

- prime: a prime below 2^32.
- family: public loop_momenta, external_momenta, propagators, invariants and scalarproduct_rules.
- rows: row IDs mapped to sparse dictionaries of integral column keys and integer field coefficients. Column keys are comma-separated integral indices.
- row_roles: the role identity or target for every row.
- master_columns: the protected master column keys.
- actions: entries with id, source_row, destination_row, and pivot_indices.
- enforce_reference_order: optional; use true for the stored construction order.

runs/example_state.json and runs/example_prediction.json provide a real training-state example after finalization. They demonstrate the interface and do not constitute a held-out evaluation. An empty action list returns no chosen step. It returns complete only when supplied target rows already contain masters alone.

## Resource bounds and copies

The scorer accepts up to 16 indices, 10,000 rows, 10,000 actions, 250,000 matrix nonzeros and 4,096 nonzeros per row. Inputs beyond these limits fail explicitly. Batch padding is capped at 16,384 action positions. Checkpoints are capped at 8 MiB and compressed family shards at 64 MiB. The model folder has a 1.5 GB budget, and the project guard leaves headroom below the user's combined 10 GB ceiling.

Store this folder and its generated artifacts on Hoffman and GitHub only. Keep report sources and PDF synchronized to the local report folder. The report describes the mathematics and the limits of the training data.

<!-- completed-training:start -->
Training completed all ten passes on 455,341 choice states from 693 families, giving 4,553,410 state presentations and 18,006 updates. The preparation checked 585,502 total states, including 130,161 forced states. The final model has 10,529 parameters and occupies 49,122 bytes.

Final-pass mean cross-entropy during updates was 0.11509920 and reference-choice agreement was 99.7387%. These are training measurements. The completed held-out comparison is recorded below; no calibration map has been fitted. Peak training RAM was 245.71 MiB, and the training stage took 408.33 seconds after preparation.
<!-- completed-training:end -->

<!-- completed-testing:start -->
The frozen reduction model was tested on 72,142 targets in 307 held-out families. It matched 95.469% of recorded choices on 194,347 states with at least two actions. Complete learned paths matched all three sampled master expansions for 72,026 targets; the fixed local rule passed 71,463. Mean attempted reduction times were 8.4426 ms and 0.4262 ms, respectively. Reference paths are valid without a proof of minimality. These are target-row tests; no full Kira speedup was measured.

See [model_test/README.md](model_test/README.md) for saved predictions, complete paths, metric definitions, six figures and reproduction commands. The model weights and training records are unchanged. Historical training status files describe the state at training completion. After regenerating training-only report text, run the test report updater to restore the current cross-references.
<!-- completed-testing:end -->
