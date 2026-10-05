# Seed-selection model

<!-- training-status:start -->
Training and held-out testing are complete. The fixed model was tested on 72,142 targets from 307 separate families. Seed precision is 95.734%, recall is 94.112%, and exact reference-set agreement is 81.916%. The two-loop test family gives 11.290% precision and 41.553% recall. Full predictions, graphs and validation are in [model_test](model_test/README.md). The trained weights remain [trained_model.pt](trained_model.pt).
<!-- training-status:end -->

This folder contains the System 1 seed model and its data preparation, training, prediction and comparison code. The user authorized training and the subsequent held-out model test; both are complete. The integral collection remains in ../integrals; this folder stores manifests and checks rather than duplicate integral data.

The model receives a target expression, its ordered terms with exact coefficient strings, the public family definition, the chosen master basis, and a candidate seed list. It returns a separate sigmoid probability for each candidate. The label means membership in the target's recorded sufficient seed set. It does not identify a proven globally optimal seed or label all other seeds as mathematically useless. A reduction can require several seeds.

Each candidate now returns predicted_label (0 or 1), probability_1, probability_0 and confidence. probability_1 is the sigmoid membership probability p; probability_0 is 1-p. The fixed rule assigns label 1 when p >= 0.5 and label 0 otherwise. Confidence is p for a returned label of 1 and 1-p for a returned label of 0. Candidates remain ranked by probability_1. A confident label 0 therefore remains a low-ranked seed. Confidence estimates reference-label agreement, and its empirical calibration remains unmeasured. It does not certify a sufficient or minimum seed set.

A target may use several seeds because equations from one seed can involve further integrals that require equations from other seeds. A reduction can also use one seed or no IBP seeds, depending on the target and chosen basis. All labels of a target remain together. For five candidates with recorded seeds 1 and 3, the supervision vector is [1,0,1,0,0]. The network predicts probabilities before the training code compares them with these labels. Binary cross-entropy uses the continuous probabilities; the 0.5 threshold applies to reported decisions. The optimizer updates the network after averaging gradients over eight targets and repeats the process for ten complete training passes. Training and held-out testing are complete, with the threshold kept at 0.5.

The model processes all stored terms and every ordered pair of distinct terms. Positions preserve the stored order. "Ordered combinations" in this implementation means these ordered pairs; longer subsets and all permutations are not enumerated. The coefficient strings enter through fixed signed token 1-, 2- and 3-gram counts in 64 components. This includes every token but permits hash collisions. It is a compressed symbolic description, not a symbolic algebra engine or an exact coefficient encoding. Modular residues are not used as real coefficient magnitudes.

Shared 32-component maps encode terms, pairs, family structure, master indices and candidate seeds. A seed-dependent weighted average of target terms joins the mean and maximum term descriptions, pair mean, family, basis and seed descriptions. A 64-component hidden layer and scalar output give the sigmoid score. All hidden layers use tanh. There are 28,097 trainable parameters. The same weights score every candidate; candidate order does not change individual scores. Inputs use family structure, not family IDs, split labels, reference master coefficients, construction history or operation counts.

The candidate set is the stored bounded family pool. It is not the infinite lattice of possible IBP seeds. Optional public seed lists can be supplied for prediction within the implemented size limits. The chosen basis contains all family masters, not the reference subset used by a target.

The model-specific split contains 168,330 training targets across 693 families and 72,142 test targets across 307 families (69.99983% training). Each complete target and its candidate-label vector stay together. All mass assignments of a box kinematic zero/equality pattern stay together, including matching original box profiles. Two complete two-loop families are assigned to training and one to test using the fixed random seed. The assignment then finds whole groups whose combined target count is nearest to 70%. The split is based only on family definitions and target counts.

The existing integral split labels are historical and remain unchanged. Only split_manifest.json controls this model. Lower-sector integrals can occur on both sides. The 997 one-loop and three two-loop families do not establish high-loop generalization; most families share the box topology. The report states these limits. No accuracy, speedup or optimality result is claimed.

s00_prepare_data.py checks all target/reference IDs, labels, candidate membership, input bounds and source hashes, then writes split_manifest.json, data_audit.json and source_hashes.json. It prepares data only. These files are already present. The preparation step also recreates the separated directory views with integrals/s05_prepare_model_splits.py.

s01_data.py provides bounded streaming, fixed feature construction, strict public-input selection and source verification. It reads target/reference files together only for supervised examples. During each family pass, it reuses the unchanged numerical descriptions of the family, master basis and candidates; model weights and learned descriptions remain trainable at every step. Prediction reads only the public target, family, basis and candidate files.

s02_model.py defines the network and unweighted binary cross-entropy objective. The loss averages over candidates within a target, then over targets during gradient accumulation. Labels absent from the recorded set are membership negatives, not proofs of seed invalidity.

s03_train.py is the CPU training entry point. It shuffles training families and uses a 32-target shuffle buffer within each family. The default is ten epochs, AdamW with learning rate 0.001 and weight decay 0.0001, gradients averaged over eight targets, and gradient norm capped at 1. It never iterates over test examples and verifies source hashes only for the training split. runs/latest.pt retains the latest resumable checkpoint, capped at 8 MiB. Checkpoints are saved after the first 1,000 targets, each subsequent 5,000-target boundary and every completed epoch. --resume continues the saved target order and optimizer state. A completed run writes trained_model.pt in this folder. The completed training and testing status appears at the start of this README.

s04_predict.py requires a trained checkpoint and returns a 0/1 prediction, both class probabilities and confidence for every supplied candidate, ranked by probability_1. It accepts --target FAMILY:ID and optional --seeds FILE containing {"indices": [...]}. It does not read the target's reference answer. Only load trusted checkpoints created by this project.

s05_evaluate.py is the original compact comparison entry point. The completed test uses model_test/s01_evaluate.py, which also saves predictions, pooled counts and graphs and groups tied probabilities when calculating average precision. It also records binary precision, recall, exact reference-set agreement and confidence reliability separately for returned labels 0 and 1. Reliability groups predictions into confidence intervals and compares mean confidence with the fraction of correct reference labels. Empty precision/recall denominators remain excluded and are reported. It records average precision, recall and complete reference-set coverage at 1, 5, 10 and 20 candidates; recall at the reference-set size; Jaccard overlap at probability 0.5; binary cross-entropy; and Brier score. It averages over targets, target type and families. Empty reference sets remain in the data; metrics with a positive-set denominator exclude them and report denominators. Agreement with reference seeds does not prove reduction success or measure distance from an unknown optimum. This script does not call Kira.

s06_check.py checks shapes across the original families and representative expanded families, split grouping, candidate permutation, block-size agreement, input boundaries, coefficient/order handling, reference-information exclusion, gradients and known metric values. The derivative check changes no parameter and constructs no optimizer. implementation_checks.json records the result.

s07_run.sh is the bounded Hoffman scheduler wrapper. Its default action is check. prepare only prepares data. train and evaluate must be selected explicitly. The completed training used s11_run_training.sh; the completed test used model_test/s02_run_test.sh.

s08_setup_environment.sh installs the pinned CPU PyTorch wheel in .tools/seed-model/venv using the Hoffman Python 3.9.6 module and its NumPy/SymPy packages. This environment is already installed on Hoffman. It avoids the incomplete shared torch installation. Dependencies and caches stay outside Git history. requirements.txt records the direct dependencies.

From the repository root, the completed preparation and checks can be reproduced with:

~~~bash
mkdir -p .tools/seed-model/logs
qsub -l h_rt=00:20:00 ML_model_seed_selection/s07_run.sh prepare
# Submit the check after preparation finishes.
qsub -l h_rt=00:10:00 ML_model_seed_selection/s07_run.sh check
~~~

The training and original compact evaluation commands are shown below. See model_test/README.md for the completed test and graph workflow:

~~~bash
qsub ML_model_seed_selection/s11_run_training.sh
# After training completes:
qsub ML_model_seed_selection/s07_run.sh evaluate \
  --checkpoint ML_model_seed_selection/trained_model.pt
~~~

For the saved trained checkpoint, run prediction in a compute allocation with the same Python environment:

~~~bash
.tools/seed-model/venv/bin/python ML_model_seed_selection/s04_predict.py \
  --checkpoint ML_model_seed_selection/trained_model.pt \
  --target box_profile_0001:T00001
~~~

Jobs use one CPU thread, request 4 GiB RAM and cap virtual memory at 3 GiB. Checks and preparation have shorter time limits; training/evaluation stop within 23 hours. Pair blocks contain at most 256 pairs and candidate blocks at most 128 seeds. The current data use at most 33 terms and 1,671 candidates. Configured bounds are 512 terms, 10,000 candidates, 16 indices and 32,768 coefficient characters. Oversized inputs raise an error; no terms are silently truncated. Pair computation grows quadratically with the number of terms. Larger problems and integration with Kira require later work.

The 10 GB project storage ceiling includes tools, Git history and temporary files. A storage guard leaves at least 1 GB headroom and reserves 100 MB for the original local workspace. No data or dependency files were copied to the local machine.

The architecture explanation and equations appear in Section 7 of [the report](../report/report.pdf). Related methods are [Deep Sets](https://arxiv.org/abs/1703.06114), [scaled dot-product attention](https://arxiv.org/abs/1706.03762) and [AdamW](https://arxiv.org/abs/1711.05101).

s09_check_training_inputs.py checks the separated manifests, shared input encoding and resumed example order using training examples only. It performs no test-set model evaluation and no optimizer updates.

s10_finalize_training.py verifies the final checkpoint, all ten epoch counts, finite model parameters and zero test examples. It writes trained_model.json and updates the model and run READMEs. It does not measure test performance.

s11_run_training.sh runs the training-input checks, starts or resumes training, saves the final model, and publishes the completed artifacts to GitHub. It uses one CPU, 4 GiB requested memory and a 3 GiB address-space limit. Source-code fingerprints and split fingerprints are saved with the checkpoints. Training output stays in runs/scheduler.log. No testing command is included.

The source folders for this run are [training](../integrals/training/README.md) and [testing](../integrals/testing/README.md). Only training is supplied to the optimizer.

A [CPU resource check](runs/resource_check/README.md) compared one, two and four threads during training. The warm two-thread timing differed by about 2.4%, and four threads were slower in the short check. The one-thread training job continued unchanged after this check and has now completed. These checks used training data only and did not update the production model.

trained_model.json and runs/ record the training-completion state before testing. The current evaluation result is model_test/test_results.json. Testing did not modify the model or optimizer and did not tune the threshold.
