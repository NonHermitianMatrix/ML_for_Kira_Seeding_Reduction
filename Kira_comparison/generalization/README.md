# Scattering, symbolic kinematics and certified paths

The extension contains seven new scattering batches with 88 targets and 70 exact comparison workflows. It includes a nonplanar two-loop box, a one-loop pentagon with five independent symbolic invariants, and a one-loop box with an independent external virtuality. The frozen equation filter has a complete-time ratio of 1.251829 to native choices, including all 35 native fallbacks. The existing native guard remains active for these unsupported inputs. Separate exact certificates enumerate every sufficient source subset and every allowed pivot path for a bubble and a tadpole. Each has a joint minimum of seven counted coefficient operations, within its specified finite pool. These certificates do not prove unrestricted IBP or wall-time optimality.

## Contents and physical scope

- [scattering_families](scattering_families/) defines four numerical-profile batches on new nonplanar four-point and five-point graphs.
- [symbolic_kinematics](symbolic_kinematics/) defines three batches with all specified invariants symbolic. The fields are Q(d,s,t), Q(d,s12,s23,s34,s45,s51), and Q(d,s,t,q2). All internal scattering propagators are massless.
- [optimal_paths](optimal_paths/) contains exact source equations, seeds, master coefficients, complete state graphs, all sufficient source subsets, optimal paths, operation counts and independent certificates. These are two small one-loop systems, with three nonmaster columns each.
- references/ contains enlarged native reductions. model_test/ retains all 70 workflows, their failed attempts, exact coefficients, full native inputs, resource samples, solver logs, and independent larger-seed/specialization checks.
- development/ retains four feasibility pilots and the initial symbolic-name parsing failure. Symbolic feasibility pilots share some final targets but select neither a model nor a threshold.
- freeze.json fixes the case list, solver, model and timing sources before reserved timings. runner_provenance.json records the existing native adapter and the symbolic-invariant extension. summary.json and verification.json contain the checked results.

The nonplanar family is the massless limit of topo4 in the original Kira paper, arXiv:1705.05610. The pentagon has five massless external legs. The box virtuality q2 denotes (p1+p2-p3)^2, displayed as v in the report. The complete independent denominator ranks are nine, five and four. Numerical profiles and all target indices are in cases.json.

## Comparison and checks

The unchanged depth-twelve early equation tree uses threshold 0.01. Every comparison starts a fresh native Kira process inside an already running driver. Complete time includes input generation, model work, native IBP generation, exact symbolic algebra, coefficient comparisons, cleanup, every rejected attempt and fallback. Enlarged reference discovery, post-run audits, compression and figure generation lie outside this timer.

Both methods start at the target seed limits and use a common prescribed master basis. A failed learned attempt retries native equations; an incomplete native attempt uses a larger region. All 35 learned workflows needed the native fallback. No test result is used to fit or activate a new policy. Five alternating repetitions give a case-weighted geometric mean learned/native ratio of 1.251829. This is a transfer limit, with no new speedup claim.

The independent audit checks 5600 coefficient pairs, including 560 distinct pairs, from raw native exports. All seven larger-seed checks agree, and fresh rational specializations of all three symbolic results agree with separately generated native reductions. Native Kira also confirms the six coefficients in the two certified systems. The mathematical certificates count rational-function operations; they do not measure Fermat polynomial work or runtime.

## Execution order

Run scientific commands only in scheduled jobs with node-local TMPDIR.

1. s00_native_run.py supplies the bounded native adapter; s01_cases.py defines the physical inputs and verifies independent scalar products.
2. Submit s03_job.sh prepare to create cases and run feasibility pilots. s02_study.py supplies prepare, pilot, freeze and test actions.
3. Submit s06_pipeline.sh after the pilot. It runs frozen comparisons, s04_optimal_paths.py and s05_verify_certificates.py.
4. Submit s09_audit_job.sh after comparisons. It runs s07_audit.py and s08_analyze.py for independent coefficient checks and a timing plot.
5. s11_finish.sh regenerates and verifies the final joint equation/pivot certificates, then refreshes the summary. The original fixed-pool certificates and code remain in optimal_paths/fixed_pool/.
6. Run s10_document.py to update READMEs. After publishing the data commit, use --data-commit COMMIT to update the LaTeX, bibliography and conclusion. Build with make -C report and synchronize the complete report locally.

Scientific records stay on Hoffman and GitHub. The report also stays locally. resource_plan.json gives a conservative combined ceiling of 9,958,476,224 bytes, below the 10 GB limit. Each native attempt has a 150-second limit, a 2400 MiB address-space limit, a 2100 MiB sampled process-tree RSS limit and a 32 MiB scratch limit. Only one scientific job runs at once. The fresh storage audit found 8,676,072,960 allocated bytes remotely and 392,683,520 locally before this extension.
