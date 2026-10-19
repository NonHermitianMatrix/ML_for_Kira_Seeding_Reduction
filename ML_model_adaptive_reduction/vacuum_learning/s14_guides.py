"""Keep the application, evidence folders, and document guides current."""
from s00_vac_common import *

def main():
 s=read(HERE/'summary.json');m=read(HERE/'trained_model/policy.json');v=s['groups']['vacuum'];ml=s['ml']
 text='''# Exact vacuum reduction and trained seed choices

Use this folder for the combined exact and learned application.
The new exact rule reduces a connected massless bubble tree with one massive vacuum root.
The new cost model chooses a sparse seed boundary for supported native box targets.
The application retains the previous exact rules and native choices for other inputs.

Run from the project root on a compute node:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/vacuum_learning/s18_fast_runtime.py --case CASE.json --output ML_model_adaptive_reduction/vacuum_learning/requests/answer.json.gz --method integrated
```

Use the family definition and target-index format in protocol.json.gz.
The definition gives loop momenta, external momenta, propagators, masses, scalar-product rules, and physical propagator count.
Each target is an integer vector with one entry for each propagator, including auxiliary coordinates.
The result contains exact coefficients, master indices, completion status, and the selected native action when applicable.
Use --method all_fixed to disable the new model and select the fixed validation choice on eligible native inputs.
This control keeps the new exact vacuum rule.
Use --method previous to call the previous application.
The benchmark launches that application directly, so its timer does not include the new wrapper.

## Exact domain

The graph must form a connected rooted tree in the recognized momentum routing.
The root has one denominator with mass squared m2, or a positive rational mass squared.
All other physical lines are massless.
Every nonroot vertex has a self denominator and a difference with its parent momentum.
The root, edge, and leaf powers must be positive integers.
An internal massless self power can be zero or negative.
All auxiliary powers must be zero.
The implementation accepts one through thirteen loops and absolute powers at most sixteen.
It rejects cuts, symbolic index powers, other masses, and other physical graphs.
The paper derives the Gamma-product ratio to the unit-power master.
This rule gives an exact reduction within that domain.
It does not solve arbitrary massive vacuum or scattering integrals.

## Learned native domain

The eligibility gate requires two loops, three independent external momenta, nine integral indices, and zero propagator masses.
It checks these counts and powers rather than a graph name.
The measured native scope consists of planar and nonplanar boxes.
All seven physical powers are one, and the two auxiliary powers are nonpositive.
The numerator rank is one through four.
The interface accepts one through six targets and rational kinematics.
Training and the reserved comparison use one through four targets in planar and nonplanar boxes.
Inputs outside the training feature ranges use the fixed validation choice.
The policy has no topology-name input and does not predict reduction coefficients.
The three candidate seed boundaries share the exact checks, master basis, and native recovery.
The policy minimizes measured complete process time, with a cost penalty for an unverified outcome.
The batch sets of numerator-power pairs differ across training, validation, and reserved inputs.
Individual pairs can occur in different batches.
No reserved outcome enters fitting or selection.

## Files and order

- s00_vac_common.py loads the preceding application, defines model features, and bounds stored output.
- s01_vacuum.py recognizes the exact vacuum domain and computes rational coefficients.
- s02_native.py applies the new seed choice through the existing native reduction interface.
- s03_runtime.py is the first frozen application entry point.
- s04_cases.py defines complete vacuum coordinates and disjoint native target batches.
- s05_measure.py bounds fresh processes and prepares independent native references.
- s06_collect.py records training and validation times for each action.
- s07_job.sh runs one bounded scheduler job with one CPU thread.
- s08_train.py fits cost trees and selects the policy on validation data.
- s09_checks.py checks Gamma values, native coefficients, and rejected inputs.
- s10_prepare.py trains, checks the exact rule, and freezes the reserved protocol.
- s11_test.py runs one of two reserved workers and checks exact results.
- s12_analyze.py separates matched timing ratios from failures.
- s13_document.py writes the new results, derivation, plot, abstract, conclusion, and matching notes.
- s14_guides.py writes these guides and updates the main folder links.
- s15_validate.py checks the study and builds both documents.
- s16_finish.py analyzes both completed tests and builds the final documentation.
- s17_output_budget.py bounds transient output files under a process lock.
- s18_fast_runtime.py is the final complete application entry point.
- s19_fast_protocol.py freezes a separate request collection with unchanged model weights.
- s20_fast_test.py measures the final application and its controls on new requests.
- s21_fast_analyze.py separates the final application change from the model effect.

Run s06_collect.py 0 and s06_collect.py 1 first, in separate scheduler jobs.
Run s10_prepare.py after both collection jobs complete.
Run s11_test.py 0 and s11_test.py 1 only after the protocol exists.
Run s19_fast_protocol.py after both reserved workers complete.
Run s20_fast_test.py 0 and s20_fast_test.py 1 after the second protocol exists.
Run s16_finish.py after both final workers complete.
Preserve the existing evidence before repeating a study.
Use at most two native workers at once.

The scheduler sets one thread and a memory bound for each job.
Permanent study evidence has a four MiB allocation bound.
The final entry point uses a separate 512 KiB allowance for flat temporary request files.
This allowance comes from the existing per-application transient reserve.
Each compressed output must be below 256 KiB, and input and uncompressed output must be below three MiB.
A file lock protects the request budget when two workers write at once.
The application scans only the request directory for this check.
It does not scan permanent study data for each short analytic output.
The benchmark removes temporary request files before publication.
resource_plan.json records the combined project bound below ten GB.
Generated training data, model weights, and scientific outputs remain on Hoffman and GitHub.
Only the report and notes are synchronized to the local machine.

## Evidence and measured limits

model_application_audit.json counts failed internal attempts and generated equation instances in the final repetition.
It uses only native requests that both methods complete and verify in all repetitions.
It counts regenerated rows again and does not claim a count of unique IBP identities.

'''
 text+=f"The vacuum rule completes {v['new_completed']}/{v['requests']} reserved requests; the preceding application completes {v['old_completed']}/{v['requests']}.\nThe matched times are {v['old_seconds']:.6f} seconds for the preceding application and {v['new_seconds']:.6f} seconds for the new rule.\nThe new native model has time ratio {ml['ratio']:.6f} against the fixed choice, with request interval {ml['interval']}.\nThe model runs on {s['model_requests']} of 32 reserved native requests.\n"
 if ml['interval'][0]<=1<=ml['interval'][1]:text+='The interval includes equal time. This sample does not establish a consistent learned gain across its requests.\n'
 text+='Each time is a sum of three-run request medians for matched completed requests.\nFailures remain in the completion counts and receive no finite speed factor.\nThe timer includes startup, prediction, native recovery, exact application work, output, and exit.\nIndependent coefficient comparisons run outside both timers.\nThe native test uses two known topology classes. It does not establish transfer to arbitrary graphs.\nThe native 31-index restriction remains for unrecognized graphs.\n'
 o=read(HERE/'output_summary.json')
 text+=f"\nThe final entry point completes {o['all']['new_completed']}/22 separate requests. Its time ratio against the first revision is {o['all']['ratio']:.6f}, with request interval {o['all']['interval']}.\nThe unchanged model has ratio {o['ml']['ratio']:.6f} against fixed choices on {o['ml']['matched_completed']} matched native requests, with interval {o['ml']['interval']}. The model completes all eight requests in every repetition; the fixed control completes {o['ml']['old_completed']} in every repetition.\nThe retained analytic rules have ratio {o['retained_exact']['ratio']:.6f} against the preceding published entry point.\nThese separate collections do not provide speed factors that can be multiplied.\n"
 (HERE/'README.md').write_text(text)
 guides={'training':'These compressed records contain training cases, features, measured action costs, exact checks, and full results. The rows file also includes validation rows for model selection.','validation':'These compressed records contain separate validation patterns. They select the model settings and the fixed comparison action.','trained_model':'policy.json contains the fitted cost trees, feature ranges, validation selection, and deployment gate. fixed.json stores the action used with the new model disabled. selection.json retains all model candidates.','references':'These are independent native reference outputs. They are used after timing to check exact coefficients. They are not model inputs.','results':'Each compressed record contains one reserved request, all times, success flags, exact checks, and the final output of each method. protocol.json.gz contains the full request definitions.','requests':'Each worker writes temporary input and output files here, then removes its own files. Save application outputs that you need before another run.','output_test':'These compressed records contain the separate final application test. output_protocol.json.gz defines 22 new requests and freezes the unchanged model and revised entry point. output_summary.json reports complete time and ML-off controls separately.','logs':'Scheduler logs remain on Hoffman. Structured measurements and this guide are published on GitHub.'}
 for name,body in guides.items():
  p=HERE/name;p.mkdir(exist_ok=True);(p/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+body+'\n')
 banner='''## Current exact vacuum and learned application

Read [the current method guide](LINK).
Use vacuum_learning/s18_fast_runtime.py with --method integrated.
This version adds exact single-mass vacuum trees and a newly trained native seed-choice model.
The paper and notes give separate exact and ML measurements, failures, and domain limits.

'''
 for name,link in [('README.md','ML_model_adaptive_reduction/vacuum_learning/README.md'),('ML_model_adaptive_reduction/README.md','vacuum_learning/README.md'),('report/README.md','../ML_model_adaptive_reduction/vacuum_learning/README.md')]:
  p=ROOT/name;z=p.read_text()
  if '## Current exact vacuum and learned application' not in z:p.write_text(banner.replace('LINK',link)+z.replace('## Current two-point and learned application','## Preceding two-point and learned application',1))
 print('Application and evidence guides updated.',flush=True)
if __name__=='__main__':main()
