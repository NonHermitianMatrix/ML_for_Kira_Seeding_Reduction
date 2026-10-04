# Seed-selection model

This folder contains the implemented, untrained System 1 model and its data preparation, training, prediction and comparison code. No optimizer updates or trained predictions have been run. The integral collection remains in ../integrals; this folder stores manifests and checks rather than duplicate integral data.

The model receives a target expression, its ordered terms with exact coefficient strings, the public family definition, the chosen master basis, and a candidate seed list. It returns a separate sigmoid probability for each candidate. The label means membership in the target's recorded sufficient seed set. It does not identify a proven globally optimal seed or label all other seeds as mathematically useless. A reduction can require several seeds.

The model processes all stored terms and every ordered pair of distinct terms. Positions preserve the stored order. "Ordered combinations" in this implementation means these ordered pairs; longer subsets and all permutations are not enumerated. The coefficient strings enter through fixed signed token 1-, 2- and 3-gram counts in 64 components. This includes every token but permits hash collisions. It is a compressed symbolic description, not a symbolic algebra engine or an exact coefficient encoding. Modular residues are not used as real coefficient magnitudes.

Shared 32-component maps encode terms, pairs, family structure, master indices and candidate seeds. A seed-dependent weighted average of target terms joins the mean and maximum term descriptions, pair mean, family, basis and seed descriptions. A 64-component hidden layer and scalar output give the sigmoid score. All hidden layers use tanh. There are 28,097 trainable parameters. The same weights score every candidate; candidate order does not change individual scores. Inputs use family structure, not family IDs, split labels, reference master coefficients, construction history or operation counts.

The candidate set is the stored bounded family pool. It is not the infinite lattice of possible IBP seeds. Optional public seed lists can be supplied for prediction within the implemented size limits. The chosen basis contains all family masters, not the reference subset used by a target.

The model-specific split contains 168,330 training targets across 693 families and 72,142 test targets across 307 families (69.99983% training). Each complete target and its candidate-label vector stay together. All mass assignments of a box kinematic zero/equality pattern stay together, including matching original box profiles. Two complete two-loop families are assigned to training and one to test using the fixed random seed. The assignment then finds whole groups whose combined target count is nearest to 70%. The split is based only on family definitions and target counts.

The existing integral split labels are historical and remain unchanged. Only split_manifest.json controls this model. Lower-sector integrals can occur on both sides. The 997 one-loop and three two-loop families do not establish high-loop generalization; most families share the box topology. The report states these limits. No accuracy, speedup or optimality result is claimed.

s00_prepare_data.py checks all target/reference IDs, labels, candidate membership, input bounds and source hashes, then writes split_manifest.json, data_audit.json and source_hashes.json. It prepares data only. These files are already present.

s01_data.py provides bounded streaming, fixed feature construction, strict public-input selection and source verification. It reads target/reference files together only for supervised examples. Prediction reads only the public target, family, basis and candidate files.

s02_model.py defines the network and unweighted binary cross-entropy objective. The loss averages over candidates within a target, then over targets during gradient accumulation. Labels absent from the recorded set are membership negatives, not proofs of seed invalidity.

s03_train.py is the future CPU training entry point. It shuffles training families and uses a 32-target shuffle buffer within each family. The default is ten epochs, AdamW with learning rate 0.001 and weight decay 0.0001, gradients averaged over eight targets, and gradient norm capped at 1. It never iterates over test examples. Only one completed checkpoint is retained, capped at 8 MiB. --resume continues a matching checkpoint. Training has not been run.

s04_predict.py requires a trained checkpoint and returns all supplied candidates in probability order. It accepts --target FAMILY:ID and optional --seeds FILE containing {"indices": [...]}. It does not read the target's reference answer. Only load trusted checkpoints created by this project.

s05_evaluate.py is the future test comparison. It records average precision, recall and complete reference-set coverage at 1, 5, 10 and 20 candidates; recall at the reference-set size; Jaccard overlap at probability 0.5; binary cross-entropy; and Brier score. It averages over targets, target type and families. Empty reference sets remain in the data; metrics with a positive-set denominator exclude them and report denominators. Agreement with reference seeds does not prove reduction success or measure distance from an unknown optimum. This script does not call Kira.

s06_check.py checks shapes across the original families and representative expanded families, split grouping, candidate permutation, block-size agreement, input boundaries, coefficient/order handling, reference-information exclusion, gradients and known metric values. The derivative check changes no parameter and constructs no optimizer. implementation_checks.json records the result.

s07_run.sh is the bounded Hoffman scheduler wrapper. Its default action is check. prepare only prepares data. train and evaluate must be selected explicitly and remain later user-authorized steps.

s08_setup_environment.sh installs the pinned CPU PyTorch wheel in .tools/seed-model/venv using the Hoffman Python 3.9.6 module and its NumPy/SymPy packages. This environment is already installed on Hoffman. It avoids the incomplete shared torch installation. Dependencies and caches stay outside Git history. requirements.txt records the direct dependencies.

From the repository root, the completed preparation and checks can be reproduced with:

~~~bash
mkdir -p .tools/seed-model/logs
qsub -l h_rt=00:20:00 ML_model_seed_selection/s07_run.sh prepare
# Submit the check after preparation finishes.
qsub -l h_rt=00:10:00 ML_model_seed_selection/s07_run.sh check
~~~

The following commands are for the later training instruction. They have not been executed:

~~~bash
qsub ML_model_seed_selection/s07_run.sh train
# After training completes:
qsub ML_model_seed_selection/s07_run.sh evaluate \
  --checkpoint ML_model_seed_selection/runs/latest.pt
~~~

For a future trained checkpoint, run prediction in a compute allocation with the same Python environment:

~~~bash
.tools/seed-model/venv/bin/python ML_model_seed_selection/s04_predict.py \
  --checkpoint ML_model_seed_selection/runs/latest.pt \
  --target box_profile_0001:T00001
~~~

Jobs use one CPU thread, request 4 GiB RAM and cap virtual memory at 3 GiB. Checks and preparation have shorter time limits; training/evaluation stop within 23 hours. Pair blocks contain at most 256 pairs and candidate blocks at most 128 seeds. The current data use at most 33 terms and 1,671 candidates. Configured bounds are 512 terms, 10,000 candidates, 16 indices and 32,768 coefficient characters. Oversized inputs raise an error; no terms are silently truncated. Pair computation grows quadratically with the number of terms. Larger problems and integration with Kira require later work.

The 10 GB project storage ceiling includes tools, Git history and temporary files. A storage guard leaves at least 1 GB headroom and reserves 100 MB for the original local workspace. No data or dependency files were copied to the local machine.

The architecture explanation and equations appear in Section 7 of [the report](../report/report.pdf). Related methods are [Deep Sets](https://arxiv.org/abs/1703.06114), [scaled dot-product attention](https://arxiv.org/abs/1706.03762) and [AdamW](https://arxiv.org/abs/1711.05101).
