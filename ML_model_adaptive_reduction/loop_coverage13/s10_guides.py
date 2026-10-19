"""Write human-readable guides for the new exact domain and its tests."""
from s00_loop_common import *

def main():
 s=read(HERE/'summary.json');v=s['comparisons']['trees'];m=s['comparisons']['batches_ml_off'];g=s['coverage']['grid'];limit=read(HERE/'resource_plan.json')
 text='''# Connected bubble-tree reductions through thirteen loops

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

'''
 text+='## Measured results\n\n'
 text+=f"All 39 connected-tree requests complete. They contain 273 target entries.\nThe broad grid completes {g['methods']['integrated']['completed']} of 110 requests.\n"
 if v['pairs']:text+=f"On {v['pairs']} completed tree pairs, the summed median time changes from {v['control_seconds']:.3f} to {v['new_seconds']:.3f} seconds.\nThe measured speed factor is {v['speedup']:.2f}.\n"
 if m['pairs']:text+=f"On sixteen native box batches, retained ML has time ratio {m['ratio']:.3f} against fixed choices.\nThe request interval is {m['request_interval'][0]:.3f} to {m['request_interval'][1]:.3f}.\n"
 text+='These finite results do not establish all integral types or a global minimum runtime.\n\n'
 text+='## Resource bounds\n\nThe study has an 8 MiB output cap. Each of two native workers has a 32 MiB scratch cap.\nEach worker has a 7 GiB process memory limit inside an 8 GiB scheduled allocation.\n'
 text+=f"The combined publication peak has a conservative bound of {limit['publish_peak_upper_bytes']:,} bytes.\nThe project ceiling is 10,000,000,000 bytes.\nThe resource plan includes reports, local copies, Git storage, and temporary index files.\n"
 (HERE/'README.md').write_text(text)
 descriptions={'development':'Read the case definition, complete native coefficients, exact Gamma checks, and timeout records. These are development inputs.','trees':'Each compressed file stores one fresh-process connected-tree reduction. Names identify case, method, and repetition. Failures remain recorded.','batches':'Each compressed file stores one two-loop native batch comparison. The models are frozen. The fixed control disables both retained native learned choices.','grid':'Each compressed file stores one bounded broad-grid attempt. This grid measures coverage. A timeout is not a completed reduction.','outcomes':'Read one summary per requested case. It includes all method times, output checks, completion, and failed statuses.','requests':'This folder holds temporary inputs and outputs. Completed tests remove these temporary files. Keep generated integral data on the cluster and GitHub.','logs':'Scheduler logs remain on the cluster. Summary files record the scientific outcomes. Raw logs are excluded from publication.','provenance':'These sources preserve the verification recorder before its import correction. The original protocol is retained. Use the current root sources to run the application.'}
 for name,body in descriptions.items():
  p=HERE/name;p.mkdir(exist_ok=True);(p/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+body+'\n\nRead the parent README for the protocol, assumptions, and execution order.\n')
 for name,target in [('README.md','ML_model_adaptive_reduction/loop_coverage13/README.md'),('ML_model_adaptive_reduction/README.md','loop_coverage13/README.md'),('report/README.md','../ML_model_adaptive_reduction/loop_coverage13/README.md')]:
  p=ROOT/name;z=p.read_text();header='## Current connected bubble-tree application'
  if header not in z:
   z=z.replace('## Current fast exact and learned decomposition','## Earlier fast exact and learned decomposition').replace('[the current method guide]','[the preceding method guide]').replace('## Current exact triangle and target-batch method','## Preceding exact triangle and target-batch method').replace('## Current analytic batch application','## Preceding analytic batch application').replace('## Current analytic batch report files','## Preceding analytic batch report files')
   intro=header+'\n\nRead [the current method guide]('+target+').\nUse loop_coverage13/s02_runtime.py with --method integrated.\nThe new exact identity reduces connected massless bubble trees through thirteen loops.\nThe application keeps the preceding trained choices for other supported inputs.\nThe paper and notes give the derivation, fresh comparisons, coverage, and limits.\nEarlier methods retain their original data and claims.\n\n'
   p.write_text(intro+z)
 q=ROOT/'report/README.md';z=q.read_text();addition='''\n## Connected-tree report files

loop_coverage13_method.tex explains the physical domain and its integration with the learned workflow.
loop_coverage13_results.tex gives all new timing and coverage results.
loop_coverage13_appendix.tex derives the bubble, triangle, and rational reduction formulas.
loop_coverage13_data.json contains the report summary.
loop_coverage13_validation.json records the current checks and PDFs.
paper_figures/loop_coverage13.pdf shows completed coverage by type and loop order.
paper_figures/loop_coverage13_time.pdf shows complete times for the connected trees.
The notes_loop_coverage13 files retain the same current evidence in the notes.
Use loop_coverage13/s12_finish.py to rebuild this extension after completed tests.
Earlier document writers can replace current prose. Use the current writer for the latest paper.
'''
 if '## Connected-tree report files' not in z:q.write_text(z.rstrip()+'\n'+addition)
 print(json.dumps(dict(readmes_updated=True)),flush=True)
if __name__=='__main__':main()
