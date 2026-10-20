"""Maintain human-readable instructions for the exact and learned extension."""
from s00_light_common import *
def main():
 s=read(HERE/'summary.json');m=read(HERE/'trained_model/policy.json');q=s['all'];n=s['native_ml']
 intro=f'''# Exact reductions and learned Kira seed choices

This folder extends the preceding tensor reduction method.
The new exact rule reduces a two-point sector when its external momentum has square zero.
It accepts unequal masses, equal masses, and zero masses.
It also accepts polynomial numerators within the stated bounds.
The runtime applies this rule to intermediate two-line sectors of a larger one-loop reduction.
A separate scalar rule keeps masses symbolic.
Independent loop factors share repeated calculations.

The native model chooses one of three seed regions from complete measured costs.
Training has 34 requests. Validation has 16 requests. The reserved test has 24 native requests.
The whole target batch defines a split member. An individual target can occur in more than one split.
The complete reserved comparison has 68 requests, including exact cases through 13 loops.
This coverage does not represent every coupled high-loop integral.

The new application completes {q['new_completed']} requests; the preceding one completes {q['old_completed']}.
On {q['matched_completed']} matched requests, summed median time changes from {q['old_seconds']:.6f} to {q['new_seconds']:.6f} seconds.
Against fixed native seed choices, the new ratio is {n['ratio']:.6f} on {n['matched_completed']} matched requests.
The new model is {'enabled' if m['enabled'] else 'disabled'} by validation.
Read `summary.json` for failures, slower requests, and uncertainty.

## Run a reduction

Use the project Python environment on a compute node.
The request follows the existing family, target, and basis format.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/lightlike_reduction/s05_runtime.py --case request.json --output ML_model_adaptive_reduction/lightlike_reduction/requests/result.json --method integrated
```

`all_fixed` disables the new learned native choice. It uses the selected fixed seed region.
`previous` runs the preceding published application.
The exact stage uses the same formulas for both `integrated` and `all_fixed`.
The new model uses feature ranges from training.
Outside those ranges, the integrated method uses a fixed region verified on every training and validation request.
A separate failure classifier rejects choices with a risk score above the selected threshold.
This score does not guarantee success on unseen requests.
No model predicts a reduction coefficient.
Keep the output path inside this study folder. The writer enforces its 8 MiB record limit.

## Reproduce the study

Run these steps on Hoffman. Use at most two native workers.
Keep the source and model files fixed after step 5.

1. Run `s03_checks.py` for the direct-formula and IBP checks.
2. Run `s08_collect.py 0` and `s08_collect.py 1` for training and validation costs.
3. Read both collection markers. They must report completion.
4. Run `s13_extended_checks.py` for symbolic masses and embedded sectors.
5. Run `s14_prepare.py` to repeat those checks, train, and freeze the test.
6. Run `s15_test.py 0` and `s15_test.py 1` for the reserved test.
7. Run `s20_finish.py` to analyze, write both documents, build, and validate.

Use `s04_job.sh` with `qsub` to run a numbered Python step.
After collection finishes, `s22_study.sh` runs preparation, two test workers, and the document steps in one allocation.
The wrapper requests one core and 8 GiB. Native child processes have a 6 GiB virtual-memory cap.
A lower hard parent limit prevents the native child from starting.
The test uses 20 seconds per application and three repetitions.
Each pair runs on the same worker with method order rotated.
Reference preparation and final independent comparisons are outside application timers.
Native applications receive the prepared master indices; reference coefficients are not policy inputs.

## Files

- `s00_light_common.py`: exact arithmetic imports, bounded records, and resource checks.
- `s01_lightlike.py`: finite exact tensor formula at zero two-point invariant.
- `s02_cases.py`: one-loop and independent-product inputs.
- `s03_checks.py`: native pilot and signed IBP residual checks.
- `s04_job.sh`: bounded scheduler wrapper.
- `s05_runtime.py`: exact formulas, component reuse, learned native choices, and fallback.
- `s06_native_cases.py`: disjoint native target batches and kinematic profiles.
- `s07_measure.py`: complete-process timing and termination.
- `s08_collect.py`: training and validation costs.
- `s09_symbolic.py`: symbolic scalar mass derivatives and limits.
- `s10_train.py`: cost trees, candidate selection, and deployment check.
- `s11_coefficients.py`: restricted parser for exact dimension coefficients.
- `s12_complete_tensor.py`: generic tensor recurrence with the new sub-sector identity.
- `s13_extended_checks.py`: symbolic substitutions and larger-sector native comparisons.
- `s14_prepare.py`: model training and frozen protocol.
- `s15_test.py`: held-out timing and independent exact comparisons.
- `s16_analyze.py`: completion, paired times, and resampling intervals.
- `s17_document.py`: focused paper, notes update, and plots.
- `s18_guides.py`: these folder instructions.
- `s19_validate.py`: scientific, preservation, resource, and document checks.
- `s20_finish.py`: analysis and document sequence.
- `s21_failure_guard.py`: learned failure scores and pre-launch admission checks.
- `s22_study.sh`: bounded two-worker test and document sequence.
- `focused_*.tex`: paper source templates and derivations.
- `lightlike_appendix.tex`: complete derivation of the new identity.
- `protocol.json.gz`: frozen cases and source/model identifiers.
- `summary.json`: all measured results, including incomplete requests.
- `resource_plan.json`: the combined local and remote storage bound.
- `validation.json`: final checks and document identifiers.

## Limits and preserved evidence

The tensor rule accepts at most five coordinates, numerator rank four, and four excess positive powers.
The symbolic scalar rule accepts powers at most six and total positive power at most eight.
The native model covers the measured planar and nonplanar two-loop box domain.
The test retains the same graph types as training and uses new whole batches and kinematic points.
A finite test does not prove the fastest possible reduction or coverage of every topology.
The earlier native model and exact methods remain unchanged in their original folders.

`preliminary_startup_failures` contains excluded runs with an insufficient parent memory limit.
Those records are not training data and do not contribute to a speed claim.
All generated research data remain on Hoffman and GitHub.
The local machine receives the complete report folder only.
The combined project storage ceiling is 10,000,000,000 bytes.
The study record limit is 8 MiB. Do not exceed two native workers.
'''
 (HERE/'README.md').write_text(intro)
 descriptions={'development':'Direct and embedded-sector exact checks. Each record contains the input, returned coefficients, native reference, and check count.','training':'Measured native training requests and compact fitted cost rows. Unverified actions receive a training penalty.','validation':'Separate native requests for model and fixed-choice selection. These are not reserved test requests.','trained_model':'Frozen cost-tree model, selected fixed choice, and all validation candidates. Do not refit these files during testing.','model_test':'Reserved complete-process times, returned coefficients, references, failures, and completion flags. Each request has three repetitions per method.','requests':'Temporary bounded application inputs. Successful measurement cleanup leaves this folder empty except for this guide.','logs':'Scheduler and process logs on Hoffman. GitHub stores this guide and the compact result records. Logs are not training labels.','preliminary_startup_failures':'Excluded startup failures from a parent virtual-memory limit below the native child requirement. The corrected run replaces their measurements. These files do not enter model fitting or test totals.'}
 for folder in [p for p in HERE.rglob('*') if p.is_dir() and '__pycache__' not in p.parts]:
  relative=folder.relative_to(HERE);purpose=descriptions.get(relative.parts[0],'Supporting records for this exact-reduction study.')
  (folder/'README.md').write_text(f'# {folder.name.replace("_"," ")}\n\n{purpose}\n\nRead the main [study guide]('+('../'*len(relative.parts))+'README.md) for producers, readers, commands, and limits.\n')
 for path in [ROOT/'README.md',ROOT/'ML_model_adaptive_reduction/README.md',ROOT/'report/README.md']:
  text=path.read_text();start='<!-- LIGHTLIKE STUDY BEGIN -->';end='<!-- LIGHTLIKE STUDY END -->'
  if start in text:text=text[:text.index(start)]+text[text.index(end)+len(end):]
  link='ML_model_adaptive_reduction/lightlike_reduction/README.md' if path==ROOT/'README.md' else ('lightlike_reduction/README.md' if path.parent.name=='ML_model_adaptive_reduction' else '../ML_model_adaptive_reduction/lightlike_reduction/README.md')
  addition=f'\n{start}\nThe latest application is `ML_model_adaptive_reduction/lightlike_reduction/s05_runtime.py`.\nRead the [exact and learned reduction guide]({link}).\nThe paper now focuses on exact identities, learned Kira decisions, and complete time.\nThe notes retain the earlier experiments. Both PDFs include the new measured comparison.\n`paper_before_lightlike.tex` preserves the preceding main-paper narrative in the report folder.\nThe historical numerical audits remain active; old labels are checked in retained sources.\nCurrent-paper references and citations are checked in the current paper itself.\n{end}\n'
  first,rest=text.split('\n',1);path.write_text(first+'\n'+addition+'\n'+rest.lstrip('\n').rstrip()+'\n')
 print('Updated study and parent guides.',flush=True)
if __name__=='__main__':main()
