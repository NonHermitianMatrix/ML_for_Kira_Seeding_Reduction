# Exact Gamma cancellation

Use this application for the current combined reduction method.
It cancels common Gamma factors before it forms finite products for supported connected bubble trees.
Other inputs use the preceding exact methods and trained native choices.
This extension does not train or replace an ML model.

Run the application from the project root:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/gamma_cancellation/s02_runtime.py --case CASE.json --output ML_model_adaptive_reduction/gamma_cancellation/requests/answer.json.gz --method integrated
```

The input format is the same as in loop_coverage13.
Use the scheduler wrapper for cluster calculations.
Use --method previous to compare the preceding coefficient routine with the same input and output code.
This control keeps the same master basis.
Keep important results before rerunning a study script.

The exact domain consists of massless rooted bubble trees attached to a triangle with two lightlike external momenta.
Their sum must have nonzero squared momentum.
The supported physical powers are positive integers, except for the middle triangle line, whose power can be zero or negative.
All auxiliary powers must be zero.
The implementation accepts one through thirteen loops and absolute powers at most sixteen.
Inputs outside this domain use the preceding application.
The paper derives the formula and states the broader coverage limits.

## Files and execution order

- s00_gamma_common.py loads the preceding exact implementation and limits study output.
- s01_gamma_cancellation.py evaluates the exact coefficient with early Gamma cancellation and shared subtree sizes.
- s02_runtime.py applies this identity or the preceding exact and learned application.
- s03_pilot.py checks development coefficients and times. It also defines fresh power batches.
- s04_job.sh runs one bounded scheduler job. It allows one thread and limits memory.
- s05_protocol.py fixes the reserved targets, comparison settings, and unchanged source and model records.
- s06_measure.py runs five comparisons per method and checks their coefficients. It writes the results and summary.
- s07_document.py writes the paper sections, derivation, plot, and matching notes.
- s08_validate.py checks the fixed study and builds both PDFs.
- s09_guides.py writes the folder guides.
- s10_finish.py runs the document, guide, and final validation steps.

protocol.json.gz records the full reserved inputs.
development.json contains the final development measurements.
provenance/ keeps the first development version and measurements.
results/ stores the completed outputs, times, exact comparisons, and independent Gamma checks.
summary.json combines the measured results without changing the saved measurements.
validation.json identifies the checked sources and rendered documents.
resource_plan.json bounds combined project storage below 10 GB.
requests/ holds temporary application input and output. It is empty after the comparison.
logs/ holds bounded scheduler output on Hoffman. GitHub contains the structured results instead of raw logs.

## Results and limits

All 72 requests complete in five runs per method.
The 68 connected requests cover each loop order from one through thirteen.
They contain a small and a large target batch for each of 34 defined tree structures.
The four other requests check the unchanged analytic and native paths.
The exact coefficients agree across methods and repetitions.
Independent complete Gamma expressions supply 612 numerical checks at 80-digit precision.
The analytic derivation establishes the identity; these checks test its implementation.

The large-batch total decreases from 14.305225 to 6.731007 seconds, using request medians.
The new-to-previous ratio is 0.470528.
The full 72-request total decreases from 23.555584 to 16.099505 seconds.
The small seven-target batches show no resolved improvement; their interval includes equal time.
This saving comes from exact cancellation and shared batch calculations.
The native ML models are unchanged. Their measured contributions remain in the preceding studies.
These results do not cover every integral type or prove minimum possible time.
The main report separates these contributions and keeps failures in the wider grid.
