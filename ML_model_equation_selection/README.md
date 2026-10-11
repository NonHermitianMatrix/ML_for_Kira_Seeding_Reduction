<!-- early-equation-current -->
The current application is [early_generation/s12_reduce.py](early_generation/s12_reduce.py).

The current early equation policy predicts which seed/operator identities to construct. On eight fresh physical profiles, its complete-time ratio to matched native choices is 0.942907, with descriptive 95% interval [0.915,0.970]. Its preparation ratio is 0.637888, with interval [0.546,0.734]. The complete-time ratio to the previous release is 0.943456, and the ratio to the distance control is 0.933657. All 280 comparisons and eight basis-only applications pass exact checks. The selected route keeps native seed and row choices and preserves the preceding sunrise policy. These results include every fallback cost and cover known two-/three-loop structures at fixed rational kinematics with symbolic d.

See the [extension README](early_generation/README.md). The remaining text describes the preceding frozen release.
<!-- early-equation-current-end -->

# Target-dependent equation selection

The preceding application is s35_reduce.py. It enables the trained equation model for the recorded 21-target two-loop sunrise domain with native seed and row choices. Other target sets, other topologies, and requests for the earlier seed/row models retain native equation choices. The slower three-model combination stays disabled.

On six fresh physical profiles, the equation policy has complete-time ratio 0.994238, descriptive interval [0.9912948654378096, 0.9970062760952034], and equation-preparation ratio 0.784781, interval [0.7763148590933325, 0.7941014613492257]. This is about 0.6% lower complete time and 21.5% lower preparation time within that domain. Generated-equation ratio is 0.413523; selected-equation count is unchanged. Native median complete times range from 0.692 to 0.709 seconds. Preparation occupies about 3.29% of native complete time.

The fresh main comparison has 162 workflows and no failed attempts. It fixes the model and route before testing six new mass/kinematic profiles, with nine alternating repetitions per method. A further 36 workflows compare all three models with the earlier two-model configuration. That composition is 31.7% slower and includes extra fallback. Six applications use prescribed masters without reference target coefficients. All 204 workflows pass the independent exact audit.

The earlier broad test has 280 complete workflows over eight two- and three-loop profiles, plus 48 composition workflows and eight applications. Its initial route is 9.8% slower overall because new vacuum filters require fallback. These results remain in model_test/. They motivated the restricted route before the fresh confirmation began. This work does not establish a general multiloop speedup.

The trained CART model has 233 nodes, maximum depth eight and 23 decision features. It uses 74,692 native training candidates, including 5,978 positive labels, from six physical profiles. A label records integral-support membership in the final native selected system. It is a conservative proxy rather than a necessity or optimality label. Probabilities are smoothed leaf frequencies without a calibration claim.

Native Kira constructs the identities and performs exact algebra. The integration shares seed features, evaluates equation features when the tree needs them, and caches decisions to skip rebuilding omitted equations. An incomplete reduction retries native equations and then a larger seed region. All attempts, model loading, generation, exact checks and cleanup enter the measured workflow time. The experiment driver is already running; independent-reference creation and evidence compression lie outside the timer.

Folders:

- training/: native features, labels, exact reductions and hashes.
- validation/: final threshold comparisons on three validation profiles; earlier validation variants remain in named archives.
- trained_model/: model.json, weights.txt, both experimental freezes, deployment_final.json and deployment_verification.json.
- model_test/: broad tests, labels, composition and application checks, plus confirmation/ for the fresh restricted-domain study.
- integration/: C++ headers, source patches, build hashes and probability/feature parity checks.
- references/: additional native reference reductions. Some unchanged references remain in Kira_comparison and are identified by path in each record.
- development_v1/ and development_v2/: rejected label-collection attempts, with explanations. Training excludes them.

Use s35_reduce.py inside a scheduled Hoffman job with node-local TMPDIR. Required arguments are --family-file, --masters-file, --size and --output. Use the family definition, ordered target list and topology metadata schema in families.json. The output must lie inside this folder. The optional --base accepts native, seed, row or both. That preceding interface prevents an equation-filter combination that the tests found slower.

On the configured cluster installation, s25_build_lazy.sh builds the final native evaluator. s04_experiment.py collects training examples, s06_train.py fits the tree, and s12_freeze.py locks the original broad experiment. s19_test.sh performs the broad tests. s30_confirmation.py prepare defines and freezes the six fresh profiles; s32_confirm.sh runs their comparison and independent audit. These completed experiments must remain fixed; use separate folders and fresh profiles for further policy development.

s36_check_deployment.py verifies that the deployed choices match measured successful arms and disable unsupported combinations. s39_finish_report.sh generates plots, documentation and the report from checked measurements. s38_plot.py preserves the original plotting logic with compatibility for the installed Matplotlib version; the originally frozen s23_plot.py remains unchanged. s31_reduce.py and s11_reduce.py preserve preceding experimental interfaces.

The resource plan permits one experiment trial at a time and bounds the complete project below 10 GB. Generated models, data and tests stay on Hoffman and GitHub. The complete report is also synchronized to the laptop.

<!-- higher-loop-acceleration -->
The higher-loop extension generates exact Euler and mass partial-fraction equations for the restricted coupled vacuum family, then uses Kira's user-defined-system solver. A shared variable z=L(d-2) supports every positive loop order mathematically. Tests cover L=1,...,12, with additional applications at 13, 16, 24 and 32. Across six reserved batches, the deployed route has complete-time ratio 0.155 (descriptive interval 0.132--0.184) to separate full-pool reductions. The learned separate-loop route has ratio 0.911 (descriptive interval 0.815--0.986) to the same full-pool baseline. Learned/shared versus rule/shared has ratio 0.968 (descriptive interval 0.927--1.003). Validation selects the extreme route. These are supplied-identity results, with exact coefficient checks and all runtime costs; they do not establish a generic high-loop native Kira speedup.

See [higher_loops/README.md](higher_loops/README.md).
<!-- higher-loop-acceleration-end -->


<!-- batch-reuse-begin -->
## Learned equation reuse across target batches

The earlier batch interface is [batch_reuse](batch_reuse/README.md). It trains a batch equation-cost model, shares exact coefficient checks across loop orders and combines independent systems in one Kira call. All 460 reserved applications pass exact checks. The selected combined route has complete-time ratio 0.220 to the preceding separate workflow. Matched simple-rule and inference-backend comparisons remain recorded. General high-loop native IBP generation is outside this scope.
<!-- batch-reuse-end -->

<!-- pre-reduction-current -->
Validation selects the simple direct route. On 200 reserved applications, its calculation-time ratio to the preceding combined learned Kira route is 0.306, with descriptive interval [0.246,0.373]. The full-worker ratio is 0.430. All exact checks pass with zero reserved fallbacks. The earlier trained four-tree model remains available with unchanged weights; learned/direct versus simple/direct has calculation ratio 0.982. The comparison does not establish a further complete-time advantage from learned ordering over both direct controls. This is a checked shortcut for the restricted coupled vacuum family. Native IBP generation keeps its earlier supported domains.

See [exact pre-reduction](pre_reduction/README.md).
<!-- pre-reduction-current-end -->

<!-- polynomial-reuse-current -->
The polynomial-reuse interface shares exact loop-order transformations and Taylor factors, with an optional persistent worker. Validation selects both arithmetic changes and preserves the simple extreme ordering. Across eight reserved batches, calculation-time ratio to the preceding direct arithmetic is 0.372, and full-worker ratio is 0.682. Arithmetic plus persistent execution has full-time ratio 0.365 across three specified overlapping streams. All 352 reserved applications pass exact checks; 28860 expanded coefficient positions also match the older loop-dependent formula. These gains come from exact reuse and process startup. The unchanged learned model remains optional. General native high-loop IBP generation retains its earlier scope.

See [exact polynomial reuse](polynomial_reuse/README.md).
<!-- polynomial-reuse-current-end -->

<!-- exact-backend-current -->
The latest restricted vacuum-family route uses compiled expansion and binary output with a fixed recurrence rule. Its complete-process time ratio is 0.850 and its ratio including output decoding is 0.858, with descriptive interval [0.800,0.914]. The persistent-stream ratio including decoding is 0.725. 948 reserved applications across the original and compiled-reader comparisons pass exact checks. Learned versus validation-selected fixed-rule time ratio is 1.017, with interval [0.969,1.070]. This interval includes one, so the reserved comparison does not establish a further time reduction from learned choices. The deployed default uses the fixed validation choice. These results retain the restricted vacuum-family scope; native IBP generation keeps its earlier supported domains.

See [exact arithmetic and batch strategies](exact_backend/README.md).
<!-- exact-backend-current-end -->

<!-- cumulative-results-begin -->
The direct cumulative comparison uses eight new groups of three restricted vacuum mass profiles, loop orders 1--12, and five repetitions of three methods. All 120 workflows pass exact checks. Relative to the original saved Kira binary with the full supplied equation pool and separate loop reductions, the final route has total-time ratio 0.001839, speedup 543.815x (descriptive 95% interval 488.134--605.064), and 99.82% less time, including startup, saving and output reading. Against the earlier full-pool pipeline binary, the speedup is 81.170x. The selected final route uses a fixed recurrence and exact direct arithmetic. The result measures the complete restricted-family replacement; it does not establish a corresponding native general-IBP or ML-only speedup.
<!-- cumulative-results-end -->
