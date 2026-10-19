# Connected bubble-tree reductions through thirteen loops

Use this application to reduce the supported connected massless bubble trees exactly.
The method first checks the physical denominators and kinematics.
It integrates each two-line subgraph, then integrates the root triangle.
The result gives rational coefficients of the unit-power connected master integral.
The paper appendix derives the formula and explains each assumption.

## Run the application

Use the project Python environment on a compute node.
Run this command from the repository root:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/loop_coverage13/s02_runtime.py --case INPUT.json --output ML_model_adaptive_reduction/loop_coverage13/requests/OUTPUT.json --method integrated
```

The input has definition and targets fields.
The definition lists loop momenta, external momenta, propagators, masses, scalar-product rules, and physical propagator count.
Each target is a full integer index vector in the listed denominator order.
The complete protocol contains examples.
For supported trees, the output names the connected unit-power master and each exact coefficient.
The result keeps the same outer block format as the preceding application.

The supported graph has a one-scale root triangle and a rooted tree of massless two-line insertions.
The two root external momenta are lightlike; their sum has nonzero squared momentum.
All other physical powers are positive. The middle triangle power can be zero or negative.
All auxiliary powers are zero. The current limit is thirteen loops and absolute powers of sixteen.
Masses, cuts, unsupported numerator powers, and other graph structures use the preceding application.
That application retains its own exact methods, checked bases, native limits, and trained policies.
The original models and their training records remain in their existing folders.
This extension does not fit a new model from the test set.

The previous method calls the preceding learned application without the new identity.
The all_fixed method disables the retained native learned choices for the control.
The tree tests compare different displayed master bases by expressing the new master in the native basis.
A failed control has no completed-time speed factor.

## Code order

s00_loop_common.py handles bounded output and loads the preceding application.
s01_bubble_tree.py recognizes the physical domain and evaluates finite Gamma shifts.
s02_runtime.py applies the identity and calls the preceding workflow when needed.
s03_cases.py constructs complete scalar-product coordinates and seven target powers per tree.
s04_checks.py compares the formula with symbolic Gamma expressions and native Kira.
s05_job.sh submits bounded compute work through the cluster scheduler.
s06_protocol.py defines the reserved trees, broad grid, and separate learned controls.
s07_measure.py runs fresh processes and checks the completed coefficients.
s08_analyze.py verifies every repetition and makes the summary and plots.
s09_document.py writes the current scientific sections and both conclusions.
s10_guides.py writes these folder guides.
s11_validate.py checks the evidence and both documents.
s12_finish.py runs analysis, documentation, guides, and validation after both workers finish.
s13_structure_checks.py checks names, momentum signs, and denominator order.
s14_refresh_documents.py rebuilds the documents from completed results without repeating timings.

Run development checks before freezing the protocol.
Run s07_measure.py with worker arguments 0 and 1 after the protocol is complete.
Use at most two workers. Run s12_finish.py when both workers have completed.
Do not overwrite a frozen study to collect new training or test data.
Make a new study if the model, analytic domain, or experiment changes.

## Stored evidence

protocol.json.gz contains all test inputs, controls, bounds, and source versions.
development_checks.json records symbolic checks, native outcomes, and rejection tests.
development/ contains the full native results for those checks.
trees/ contains each timed connected-tree application and its coefficients.
batches/ contains the fresh two-loop ML and fixed-control results.
grid/ contains every bounded broad-coverage attempt, including failures.
outcomes/ contains per-request checks, completion, and timing values.
summary.json contains the final comparisons and coverage counts.
validation.json records source, evidence, and document checks.
requests/ holds small temporary requests and must be empty after the tests.
logs/ holds local scheduler output. Raw scheduler logs are not published.
provenance/ preserves the initial verification recorder and protocol.
verification_revision.json explains the checker import correction and non-pole dimension choices.
The correction changes no timed reduction, model, action, or case. It preserves the first twelve timing records.

## Meaning of the checks

The exact proof uses the Gamma recurrence at arbitrary dimension and nonzero scale.
Five development requests pass native IBP checks through three loops.
One three-loop chain exceeds the native time limit and remains recorded.
All six development requests pass exact symbolic Gamma checks.
The reserved trees use independent complete Gamma evaluations at 80-digit precision.
Their dimension samples are 137/101, 151/103, and 163/107.
These checks are numerical implementation checks, not high-loop native IBP proofs.
Every repeated output also agrees exactly with its first output.

Timers include process loading, internal checks, prediction when used, reduction, recovery, output, and exit.
Independent benchmark comparisons occur after the application timer.
The connected-tree and learned tests use three repetitions.
The broad grid uses one trial per method with a twenty-second limit.
Keep that grid separate from repeated completed-time comparisons.

## Measured results

All 39 connected-tree requests complete. They contain 273 target entries.
The broad grid completes 68 of 110 requests.
On 4 completed tree pairs, the summed median time changes from 4.144 to 0.654 seconds.
The measured speed factor is 6.34.
On sixteen native box batches, retained ML has time ratio 0.938 against fixed choices.
The request interval is 0.856 to 1.021.
These finite results do not establish all integral types or a global minimum runtime.

## Resource bounds

The study has an 8 MiB output cap. Each of two native workers has a 32 MiB scratch cap.
Each worker has a 7 GiB process memory limit inside an 8 GiB scheduled allocation.
The combined publication peak has a conservative bound of 9,988,792,928 bytes.
The project ceiling is 10,000,000,000 bytes.
The resource plan includes reports, local copies, Git storage, and temporary index files.
