# Preparation with learned attempt cost

This comparison reduces repeated master discovery and measures failed work.
It keeps the earlier neural model and adds a model of attempt time and failure.
Kira computes every new coefficient. The cache stores master indices only.

## Run order

Use `.tools/seed-model/venv/bin/python` from the project root on a Hoffman compute node.
Use `../s04_job.sh` to submit scripts. Keep at most two native workers active.

1. Run `../s15_risk.py`. It trains the cost-and-failure model, checks the exported predictions, and calls `../s14_prepare.py` to freeze the cache and test protocol.
2. Run `../s16_test_preparation.py 0` and `../s16_test_preparation.py 1`. Each worker runs its declared requests. It retains failures and repeats initially successful methods twice.
3. Run `../s17_analyze_preparation.py`. It checks exact agreement, keeps matching bases, and creates the result summary and figure.
4. Run `../s18_document_preparation.py` and `../s19_finish_preparation.py` after the shared document writer. They update the paper, notes, and guides.
5. Run `../s13_finish.py` after the preparation and recovery workers finish to collect the full checks and build both PDFs.

## Use the preparation application

Prepare a JSON object with `case` and `method` keys. A case has `id`, `definition`, `targets`, and `size`, as in `protocol.json`.
Choose `cached_learned` for the neural model, `cached_risk` for the cost-and-failure model, `cached_native` to disable ML, or `expanded` for the broad discovery control.
Run `../s14_prepare.py --input REQUEST.json --output RESULT.json.gz` from this folder, using the scientific Python.
Use absolute paths when running from the project root. Use a scheduled compute job for Kira.
The application needs no reference coefficients. It compares two exact reductions internally.
The `s16` timer also includes process start and exit. The application's inner timer does not include its imports.
For an already supplied basis, the public `../s11_reduce.py` interface retains the shared neural policy and applicable exact scalar formulas.

## Training and test separation

Training uses historical training attempts and the initial shared-model profile 1201.
Historical validation requests select the forest and penalty. The fresh profile 1237 stays reserved.
The distinct-mass vacuum benchmark, nonplanar boxes, pentagons, and orders six and above supply no training or validation labels.
The 52 features describe the mathematical structure, requested powers, candidate bounds, basis state, and ordering.
The model receives no family name or stored structure key. Only the separate exact basis cache uses an ordered structure key.
The failure output is a ranking score. It is not a calibrated probability.

## Controls and exact checks

All four controls use `.tools/kira-sector-wide/kira` with bounded sector arrays.
The build procedure is in `ML_model_adaptive_reduction/portfolio_policy/s16_build_wide.py`. Read that folder's guide and source receipt before rebuilding.
The 128-bit setting stores integral-ordering labels. Exact rational coefficients use the same arithmetic in all controls.
The supplied index limit remains 31. Each request has 110 seconds; one native call has at most 60 seconds.
The native process watchdog reserves cleanup time inside that call cap.
Each worker has at most 32 MiB of scratch and a 5,200 MiB process-tree RSS limit.
The project limit remains 10 GB. Read `../resource_plan.json` before adding work.

The compact workflow reuses a previously checked index basis when available.
It recalculates coefficients at the new kinematics and compares a second reduction with a different integral ordering.
If no cache entry exists, compact discovery returns a provisional basis.
This check establishes the requested identities. It does not prove a globally minimal master basis.
Cache construction cost precedes these measurements and is reported separately.
Incomplete attempts can expand bounds. Duplicate native settings are not run again within a request.

## Read the results

`summary.json` retains every first request, failed-call cost, three-repeat completion, and matched time comparison.
Pairwise time ratios require the same master-index set and exact coefficients in all three repetitions.
Different bases and failed requests stay in the outcome counts. They do not receive a successful speedup ratio.
The ML-off compact control separates learned effects from reuse and the changed check.
`basis_cache.json` records the earlier source and check for every stored index basis.
`protocol.json` records the inputs, budgets, frozen models, and cache.
`trained_model/` contains the forest and fitting records. `model_test/` contains measured outputs.
`coverage/` contains each request's outcome. `requests/` holds only temporary running inputs.

Compact preparation without ML compared with expanded discovery gives ratio 0.305 on 13 matched requests, with repeat interval [0.290,0.329]. The neural model within compact preparation gives ratio 0.982 on 22 matched requests, with repeat interval [0.959,1.021]. The cost-and-risk model within compact preparation gives ratio 1.635 on 22 matched requests, with repeat interval [1.604,1.700]. The cost-and-risk model increases time in this broad comparison. The neural preparation result also remains consistent with equal time. We keep the failure model and its records for analysis, while the shared neural model remains the validated supplied-basis default.

## Revised recovery application

Use `../s20_prepare_resilient.py` for the revised preparation workflow. It can discard an incomplete cached basis and discover a new one. Read [the recovery comparison](../recovery/README.md) for its fresh tests. The s14 application remains the frozen original comparison.

The unified `../s22_reduce.py` interface accepts an optional basis. It follows deployment.json when no basis is supplied, while preserving the shared neural model for a supplied basis. The deployment file records a decision made after these candidate tests; it has no independent selector-speedup claim.
