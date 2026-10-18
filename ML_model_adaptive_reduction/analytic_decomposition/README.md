# Exact analytic decomposition and learned Kira selection

This folder adds a scalar one-loop recurrence to the current learned application.
It reduces raised propagator powers with an exact matrix of masses and momentum invariants.
The application uses a prepared master-index set. It stores no answer coefficients in that set.
If the recurrence cannot complete within its domain, the preceding application handles the request.
The existing sparse-seed and cost models remain frozen.

Use s05_job.sh to run calculations on a Hoffman compute node.
Run s04_prepare.py pilot before the independent comparison.
Run s03_cases.py to record the reserved inputs.
Run s04_prepare.py 0 and 1 to prepare independent native references and master indices.
Then run s06_test.py freeze, followed by s06_test.py 0 and 1.
Keep at most two native workers active. Each worker uses one core and at most 8 GiB.
The persistent folder cap is 12 MiB. Each native call uses at most 32 MiB of scratch.
Read resource_plan.json for the combined project bound.

s00_recurrence.py contains the IBP recurrence and exact coefficient arithmetic.
s01_common.py defines the supplied-basis check and bounded output writer.
s02_runtime.py preserves the initial analytic-enabled application.
s03_cases.py defines the physics inputs and comparison scope.
s04_prepare.py checks coefficients with independent native reductions.
s06_test.py records full process and comparison time, including failures.

Rational kinematics give polynomial coefficients in d. Symbolic kinematics use rational functions of the declared invariants and masses.
The current implementation permits up to five scalar denominators and six extra powers for rational kinematics.
Symbolic inputs permit up to three denominators and three extra powers.
A singular required matrix, active numerator, or missing master index returns the request to the existing application. Its interface rejects cut propagators and symbolic indices before reduction.
Independent blocks cover loop orders two through thirteen. They do not represent general connected high-loop scattering.

s07_analyze.py computes paired time ratios, failed costs, and the comparison plot.
s08_document.py writes the paper and notes from the completed measurements.
s09_validate.py repeats exact coefficient comparisons, checks the frozen sources, builds both PDFs, and validates their citations and references.
Run s09_validate.py only after both test workers finish.

## Completed comparison

The combined application completes 41 of 41 requests in all three repetitions.
all, native control: 41 matched requests; time ratio 0.623027; repetition interval [0.5988493787852358, 0.6619194080387993].
all, fixed control: 41 matched requests; time ratio 0.957985; repetition interval [0.8691537859660208, 1.016626490785287].
all, previous control: 41 matched requests; time ratio 0.632830; repetition interval [0.6122108481576477, 0.6776236368020265].
analytic, native control: 30 matched requests; time ratio 0.636495; repetition interval [0.6080737220360324, 0.7478906946248716].
analytic, fixed control: 30 matched requests; time ratio 1.006671; repetition interval [0.7872465240201697, 1.2082597533357378].
analytic, previous control: 30 matched requests; time ratio 0.344694; repetition interval [0.3362998473598915, 0.40989258754786567].
ml_compatibility, native control: 8 matched requests; time ratio 0.602288; repetition interval [0.5682432629121162, 0.6350952112534398].
ml_compatibility, fixed control: 8 matched requests; time ratio 0.936323; repetition interval [0.872857635188526, 0.9881042291498772].
ml_compatibility, previous control: 8 matched requests; time ratio 0.973013; repetition interval [0.9026786220958667, 1.0394856167944835].

The analytic saving comes from the exact recurrence. The learned models retain their earlier weights.
The native control gets the same prepared master indices and old exact formulas, with native choices and the new recurrence disabled.
The fixed control uses the new recurrence and fixed ML-free choices.
The previous control runs the actual preceding hybrid application with its earlier master-index cache.
Its timer includes discovery when that cache lacks a structure. The matched native control receives the same new index set as the analytic method.
Master-index and reference preparation are separate from the supplied-basis timings.
No finite test establishes a speedup for every integral or a globally minimum time.

Use this command in a scheduled job:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/analytic_decomposition/s10_runtime.py --case CASE.json --output ML_model_adaptive_reduction/analytic_decomposition/requests/RESULT.json.gz --method learned
```

The application uses only the master indices in basis_registry.json and the earlier basis cache.
New families without a matching prepared basis use the preceding native discovery path.
The registry contains no reduction coefficients. references/ is for independent validation only.
For an analytic block, recurrence_states counts distinct index vectors and sector_inversions counts the small matrices solved. These counts do not prove a minimum operation count.
No output coefficient is reused across requests. Repeated identical blocks share work within a request.

Optional upstream PyTorch self-test executables were removed to recover storage.
The installed runtime libraries, Python modules, headers, and all model weights remain in place.
Reinstalling the same PyTorch package restores its optional upstream self-tests.
Git object compaction preserved project history. Storage receipts remain in the administrative tools folder.
## Final input rule

The final entry point is s10_runtime.py. It uses the new recurrence for direct rational kinematics.
It keeps the older exact formulas or Kira when the input needs symbolic parsing.
s02_runtime.py preserves the initial analytic-enabled experiment.
s11_guard_test.py checks two development inputs, freezes the rule, and tests nine different requests.
s12_guard_document.py checks these results, writes the paper and notes, and rebuilds both PDFs.
The rule changes no model weights. It addresses the two symbolic regressions in the initial 41-request test.
The final nine-request test is a separate comparison. Do not add its times to the initial test.
Cut propagators and symbolic indices are outside the existing application interface.

The final rule passes all nine reserved requests. Its time ratio on the four symbolic requests is 0.144013 against the initial analytic variant.
