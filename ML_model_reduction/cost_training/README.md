# Row choices trained on measured Kira cost

This folder preserves three cost models and leaves the original neural checkpoint unchanged.

immediate_cost_v1/ ranks sources by immediate insertion time. Its sample has 804 training candidates in 354 states and 496 validation candidates in 217 states. The fit changed one validation choice and had a local time ratio of 0.999431 to native choices.

linear_continuation_v2/ fits the remaining forward coefficient-operation count after one source choice and native continuation. It retained the native choice in all nine validation states.

The current trained_model.json and trained_weights.txt contain a regression tree fitted to the same continuations. Training has 68 candidates in 24 states from six families; validation has 30 candidates in nine states from three families. All 98 complete exact Kira reductions matched their references.

The tree has 21 nodes, depth four and at least two examples per leaf. Its target is the cost change relative to Kira's source, divided by the within-state candidate-cost range, with minimum denominator one. Training gives each family equal weight. Single-choice continuation ratios are 0.998602 on training and 0.999967 on validation. The reserved experiment now tests repeated use in Kira's changing matrix; its complete-time and operation-count results are summarized below.

## Action and confidence

Candidates are equations with the same leading integral. Kira retains pivot and group order and performs every operation exactly. Eighteen relative features describe coefficient lengths, row sizes, overlaps and update work. The tree chooses the lowest predicted cost change; native-source score zero supplies a fallback. Two-row groups and groups with more than 32 rows retain native choices.

Confidence is an uncalibrated softmax of negative scores. s04_predict.py returns probabilities, the selected candidate, confidence and scores, and identifies a deterministic native guard separately.

The continuation count adds 1 + 2 * source_nonzeros per committed forward insertion. This measured insertion-sequence estimate excludes Fermat's polynomial operations and back substitution. It does not prove global path optimality.

## Files

- s00_cost_policy.h implements native counting, local probes, forced continuations and the earlier linear model.
- s01_build.py and s02_build.sh build the isolated hook. build.json and reduction_cost.patch describe it.
- s03_train.py and s05_fit.sh fit immediate insertion time.
- s04_predict.py provides the Python prediction interface.
- s06_train_continuation.py and s07_fit_continuation.sh fit the linear continuation model.
- s08_train_tree.py and s09_fit_tree.sh fit the nonlinear candidate using training and validation only. tree_candidate_* preserves that fit.
- s10_tree_policy.h evaluates the tree inside Kira and skips feature work for guarded groups.
- s11_build_tree.sh builds a separate executable, recorded in tree_build.json and reduction_tree.patch.
- s12_promote_tree.py preserves the earlier model and installs the tree. tree_promotion.json records its lineage.

The complete experiment, physical definitions, exact training records and resource plan are in ../../Kira_comparison/multiloop_native/. Raw continuations are shared there rather than copied here.

Integration checks verified unchanged seed probabilities and 510 C++ row decisions against Python, with exact master-coefficient matches. All 140 final validation workflows passed exact checks. Reserved testing used fixed weights and policies. Complete-calculation results and exact checks are in model_test/.

<!-- native-multiloop-results-begin -->
## Reserved outcomes

The fixed complete-generation experiment has 324 planned workflows, 324 measured workflows and 324 exact completions.

The selected seed policy's complete-time ratio to responsive stock Kira is 0.741945 (12 paired batches).

Seed-to-stock time ratios are 0.563457 for two-loop boxes, 1.265710 for three-loop vacua, 0.572691 for three-loop ladders. The aggregate seed time interval includes one; gains are specific to the tested family classes. The row-time interval also includes one.

The cost-trained row policy's complete-time ratio to instrumented native Kira is 1.007901 (12 paired batches); its forward coefficient-operation ratio is 1.003162 (12 paired batches).

These are paired, three-repeat comparisons at rational kinematics with symbolic d. Results include inference, native generation, exact algebra, verification and fallback. The common reference basis is prepared separately.

The independent audit passed. Family-level results and completion counts must accompany aggregate ratios; none establishes a universal speedup.
<!-- native-multiloop-results-end -->
