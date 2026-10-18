# Exact blocks and learned Kira seed costs

Use `s08_reduce.py` for this extension.
It checks exact formulas first.
It then reduces each distinct independent block once.
The learned cost model selects seed bounds for the remaining native Kira blocks.
The output keeps products of master expansions in factored form.
The model does not choose elimination rows.

The data cover a finite set through thirteen loops.
High-loop products use one- or two-loop blocks.
General coupled thirteen-loop reductions remain unverified.
Each native block supports at most 31 inverse-propagator coordinates in this interface.
Exact formulas and independent blocks can support a larger total coordinate count.
Read `summary.json` for completed and incomplete requests.
Timing ratios use matched exact completions only.
Each control shares the exact changes.
The initial selection and the final deployment selection are recorded separately.
Read `extension/deployment/selection.json` for the final policy.

Run this command in a scheduled job from the project root:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/factorized_policy/s08_reduce.py \
  --case case.json --output result.json.gz --method learned
```

A case contains `definition`, `targets`, and `size`.
Use a case in `protocol.json` as a format example.
The definition contains loop momenta, external momenta, propagators, and scalar-product rules.
Each target is one ordered integer index vector.
The result records coefficients, block indices, chosen actions, failed attempts, and time.
A false `success` value means that the requested reduction did not complete.
The application never receives reference coefficients.

## Files

- `s00_common.py`: Read shared definitions, exact comparisons, and storage checks.
- `s01_families.py`: Build the initial family grid and find independent loop blocks.
- `s02_model.py`: Fit cost models and select the frozen model on validation data.
- `s03_runtime.py`: Run the initial interface. Keep it for the recorded comparison.
- `s04_checks.py`: Check small native examples and product factorization.
- `s05_job.sh`: Run one bounded task on a scheduled compute node.
- `s06_test.py`: Run one of the two frozen initial test workers.
- `s07_exact_vacuum.py`: Evaluate the derived one-mass vacuum formulas.
- `s08_reduce.py`: Run the corrected public interface.
- `s09_extension.py`: Check vacuum formulas and form one checked basis per structure.
- `s10_validated_runtime.py`: Apply the corrected basis rule and learned seed bounds.
- `s11_extension_test.py`: Run one of two corrected test workers at fresh parameters.
- `s12_analyze.py`: Read every outcome and make paired timing summaries and plots.
- `s13_document.py`: Write this extension into the paper, notes, and guides.
- `s14_validate.py`: Build and check the documents and final evidence.
- `s15_formula_audit.py`: Compare vacuum formulas with saved native coefficients.
- `s16_massless_tensor.py`: Reduce massless two-point targets with one quadratic numerator.
- `s17_massless_checks.py`: Check the massless formula by gamma expressions and native Kira.
- `s18_deployment.py`: Select the learned and fixed policies for the remaining native work.

## Execution order

Use scheduled jobs for native calculations.
For a fresh study, run `s02_model.py`, then `s04_checks.py`.
Run `s06_test.py 0` and `s06_test.py 1` as the two initial workers.
Wait for both completion records.
Run `s15_formula_audit.py` and `s17_massless_checks.py --algebra-only`.
Then run `s09_extension.py` to check formulas, prepare bases, select the final policy, and freeze the corrected protocol.
Run `s11_extension_test.py 0` and `s11_extension_test.py 1` as the two corrected workers.
After both finish, run `s14_validate.py`.
This final script runs analysis, writes the documents, builds both PDFs, and checks the saved evidence.
Inspect the PDFs before publication.
Keep completed test records and frozen policies.
Use a separate study for a changed policy.
Exclusive claim files keep each paired request on one worker.
A stopped worker needs its own unfinished claims reviewed before a restart.
Do not remove claims from an active worker.

Use the existing scientific Python environment.
Training uses NumPy and scikit-learn.
Exact formulas use SymPy, and plots use Matplotlib.
Native calls use `.tools/kira-sector-wide/kira`.
Read `../portfolio_policy/README.md` and `s16_build_wide.py` there for the existing executable and build checks.
Recheck the storage plan before rebuilding.

`factorized_appendix.tex` gives the source for the mathematical derivation.
`basis_cache.json` preserves the initial alternative preference lists.
`extension/basis_cache.json` contains the corrected checked bases.
`protocol.json` defines the initial reserved grid.
`summary.json` contains both experiments and all comparison sets.
`validation.json` records final evidence checks.
`visual_review.json` records the PDF review.
`resource_plan.json` bounds combined project storage.
`jobs.json` records scheduled job identifiers.

## Limits

Keep at most two native workers active.
The wrapper reserves two slots and 8 GB total memory. The corrected tests reserve one slot and 8 GB because each worker uses one CPU thread.
The native process has a 6 GB address limit and a 32 MiB scratch limit.
The application has a 110-second reduction budget.
Each native call has a 45-second limit.
The test process has a 125-second emergency limit.
Keep this study below 32 MiB and the combined project below 10 GB.
Training and scientific outputs stay on Hoffman and GitHub.
The report and notes also stay on the local machine.
