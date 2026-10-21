# Selective expansion and complete-cost portfolio

This study adds selective numerator-rank expansion and compares the previous workflow on the same fresh targets.
The new selector predicts complete costs for five choices.
It uses 47 training batches, 26 validation batches, and a separate reserved group.
Rational profile 306 and symbolic dot index 3 belong only to the reserved test.
Training and validation do not read the earlier reserved results.

Run these scripts from the project root in the existing seed-model Python environment.
Use a scheduled two-core job with 8 GB total memory.
Keep at most two scientific jobs active, with at most 16 GB reserved in total.
Each native attempt has a 6,144 MiB address limit, a 5,200 MiB RSS limit, and 32 MiB of scratch space.
The whole adaptive study has a 64 MiB retained-output cap.

1. Run `s14_portfolio.py` for the two development checks.
2. Run `s15_portfolio_study.py` to measure training costs, fit models, select settings, and test fresh targets.
3. Run `s17_reduce.py --self-test` to check the public interface and unsupported-graph fallback.
4. Run `s16_portfolio_analyze.py` to audit the evidence and create plots.
5. Run `s18_portfolio_report.py` after the earlier report writers.
6. Build both PDFs and run the report checks. `s11_finalize.py` performs steps 3 through 6.

`s13_previous_server.py` runs the earlier workflow in a separate Python process.
This separates modules with repeated names. It keeps the original model weights.
It uses the same current Kira executable as the new policy and limits worker count to two.
The server stays loaded between requests. Every request still starts fresh Kira processes.
No target coefficients are reused.

`s14_portfolio.py` measures five strategies and includes native recovery.
`adaptive1` and `adaptive2` use the earlier validated cost policy with one or two workers.
`rank1` and `rank2` increase only the numerator-rank limit, with one or two workers.
`published` uses the previous graph, seed, and worker models.
For the new bubble-box graphs, the previous workflow uses its native fallback.
All choices use exact file indexing and zero-sector projection.

The five strategies have complete wall and process CPU time labels.
Training fits global trees and tree ensembles, plus local trees where enough cases exist.
Validation chooses a fixed strategy for each graph.
It enables the new prediction only with at least two percent saving and a saving in both repetitions.
A fixed portfolio strategy can contain an earlier model.
Thus the fixed comparison tests the added outer decision, not the removal of all ML.
The model files contain JSON arrays, not executable serialized objects.

`protocol.json` fixes case definitions, split groups, reference limits, and source versions before testing.
`trained_model/freeze.json` records the selected models and validation guard.
`summary.json` contains checked times and graph-specific results.
The original cost study remains unchanged and has its own reserved group.
Three repetitions give descriptive timing ranges. They do not prove a universal or globally optimal speedup.

## Measured results

All 390 timed test reductions and 26 further applications pass exact checks.
The summed batch median times are 108.028791 seconds for native choices, 95.382178 seconds for the previous workflow, and 85.496543 seconds for the selected portfolio.
The selected/previous ratio is 0.896358.
The selected/fixed-portfolio ratio is 0.984882.
The all-repetition selected/fixed ratio is 1.003527.
The added outer prediction has no stable aggregate saving over the fixed portfolio.
Read `summary.json` for individual graphs, process CPU times, and failed references.
