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
