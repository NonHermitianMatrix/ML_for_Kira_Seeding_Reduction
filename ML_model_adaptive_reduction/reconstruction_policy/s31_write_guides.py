"""Document the executable, measured evidence, and reproducible study sequence."""
from s00_reconstruction_common import *

def save(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')

def main():
 s=read(HERE/'summary.json');t=read(HERE/'training_summary.json');retained=read(HERE/'retained_summary.json');assert s['complete'] and retained['complete']
 ratio=s['all']['ratio'];m=s['new_ml'];c=s['cumulative']
 text=f"""# Exact formulas, reconstruction, and measured-cost selection

Use `s15_deploy.py` for the current application.
It retains the preceding exact formulas, recurrences, and seed model.
It adds a separately built Kira 3.1 executable with FireFly 2.0.3 and FLINT.
The standard reconstruction algorithm supplies the algebra improvement.
A new cost model selects among six algebra settings only if validation admits it.
The current validation decision is `enabled={s['model_enabled']}`.

The comparison contains 22 fresh native requests and 53 analytic regression requests.
The integrated application completes {s['all']['new_completed']} of {s['all']['requests']} requests.
On {s['all']['matched_completed']} matched requests, summed median time changes from
{s['all']['old_seconds']:.6f} to {s['all']['new_seconds']:.6f} seconds.
The ratio is {ratio:.6f}.
The added-model comparison against validated fixed settings gives ratio {m['ratio']:.6f}.
The separate inherited-ML ablation gives ratio {retained['all']['ratio']:.6f} against its existing fixed procedure.
The cumulative comparison across the two latest extensions gives ratio {c['ratio']:.6f}.
Read `summary.json` for intervals, failed attempts, slower requests, and individual times.
These results do not establish a fastest method for every integral.

## Run a request

Run the application on an allocated Intel Gold compute node with the documented modules.
The existing resource limits still apply.

```bash
module load gcc/9.5.0 python/3.9.6 gmp/6.2.1 flint/2.8.0
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/reconstruction_policy/s15_deploy.py --case /absolute/request.json --output ML_model_adaptive_reduction/reconstruction_policy/requests/result.json --method integrated
```

The case schema is the existing complete physical request schema.
It includes propagator momenta, squared masses, scalar products, and target indices.
Use `s10_cases.py` and `test_protocol.json.gz` for concrete input definitions.
Scientific request data remain on Hoffman and GitHub.
The application checks the processor before using the verified reconstruction build.
Other processors retain the preceding application.
Loop orders outside the new native training range also retain that dispatch.
The exact formulas still cover their specified domains through thirteen loops.

`integrated` uses the admitted configuration.
`fixed` uses the validated setting for each propagator structure without loading new model weights.
`previous` calls the preceding direct analytic application.
`before_formulas` calls its predecessor.
The last control measures the cumulative change across these two extensions.
It is not unmodified Kira.
Both new controls retain the preceding seed model.
Learned row selection and the separate equation filter remain off.

## Data and model

The input generator defines 48 training, 22 validation, and 22 reserved native requests.
There are four propagator structures at two and three loops.
Whole physical requests are disjoint between splits.
Some target indices and all four graph structures recur.
The kinematic numbers are rational; the dimension remains symbolic.
This is not general symbolic scattering kinematics.

The six actions are preceding symbolic reduction and FireFly with batch sizes 1, 2, 4, 8, and 16.
These are probe batch sizes, not target counts.
The model uses 29 mathematical input features.
It predicts relative complete cost and observed failure fraction.
Training measures one complete application per action; validation measures three.
Each candidate has 32 extremely randomized trees.
Validation selects depth, leaf size, and saving margin.
Deployment requires at least three percent less validation cost and no failed selected attempt.
The fixed control separately selects its setting for each propagator structure.
Inputs outside the training feature ranges use the preceding application.
Failed reconstruction retains its cost and invokes symbolic recovery.
A failure score cannot guarantee completion.

The model was fitted from {t['training']} training requests and {t['validation']} validation requests.
Read `training_summary.json` for all candidate settings and the deployment decision.
Read `trained_model/README.md` for saved weights and configurations.
`entry_checks.json` compares the exported predictor with the fitted estimator.
It also checks complete applications before the reserved test.
`training_source/` preserves the exact fitting script.
The current script changes only the numerical tolerance in its feature-consistency audit.
The exported predictions agree with the fitted estimator within 1e-12.

## Build and reproduction

The separate binary is `.tools/kira-reconstruction/kira`.
The preceding binary remains `.tools/kira-sector-wide/kira`.
The build uses the published patched Kira sources and a pinned compatible FireFly revision.
`dependency.json` records that upstream source and archive digest.
`gmp_cpp_dependency.json` records the official matching GMP 6.2.1 header.
The cluster supplies GMP and FLINT.
The system C++ stream library supplies GMP stream operations.
The compiled FireFly objects use the C++ ABI of the preceding Kira build.
`build.json` contains every compilation and link command, source digest, and module version.
Tool binaries and compilation objects are not published to Git.
The Git repository contains the reproduction records and research data.

Run `s01_fetch_firefly.py`, then `s09_fetch_gmp_header.py`.
Submit `s03_build.sh` to build with two compiler workers.
Do not run native tests during the build.
Submit the development wrappers only after the build succeeds.
Submit `s22_learn.sh` to collect the training and validation costs and fit the model.
Submit `s25_model_test.sh` after training finishes.
It checks the entry point, freezes the protocol, and runs two bounded test workers.
Prepare the inherited-ML ablation with `s34_retained_test.py prepare`.
Submit `s35_retained_test.sh` after the main test.
It uses the same reserved inputs and fixed algebra settings, without fitting a new model.
Run `s36_analyze_retained.py` after both workers finish.
Then run `s26_analyze.py`, `s27_plot.py`, `s29_write_results.py`,
`s28_write_paper.py`, `s31_write_guides.py`, and `s32_validate.py`.
The numbering records script development; this paragraph specifies the final execution order.

## Script guide

- `s00_reconstruction_common.py` defines paths, bounded storage, unique module loading, and atomic records.
- `s01_fetch_firefly.py` fetches the pinned compatible source and verifies its archive.
- `s02_build.py` builds the separate native executable and removes its new temporary objects.
- `s03_build.sh` allocates a bounded build job on an Intel Gold node.
- `s04_native.py` changes native algebra options while preserving the bounded runner and basis checks.
- `s05_runtime.py` exposes the experimental algebra actions through the preceding exact application.
- `s06_measure.py` measures a complete fresh process, including failure and cleanup.
- `s07_pilot.py` compares the initial four development requests.
- `s08_pilot.sh` submits that development comparison.
- `s09_fetch_gmp_header.py` fetches the matching official C++ header and licenses.
- `s10_cases.py` defines the separate physical requests and features.
- `s11_collect.py` measures training or validation actions against symbolic coefficients.
- `s12_collect.sh` provides the two-worker collection wrapper.
- `s13_cost_decision.py` evaluates the compact exported forest and applies its admission rules.
- `s14_train.py` fits candidate models and selects them with validation only.
- `s15_deploy.py` provides the retained complete application with bounded symbolic recovery.
- `s16_bunch_pilot.py` tests probe batch sizes and simple box requests.
- `s17_bunch_pilot.sh` submits that pilot.
- `s18_structure_pilot.py` adds massive sunrise and three-loop vacuum development requests.
- `s19_structure_pilot.sh` submits that pilot.
- `s20_reference.py` prepares separate symbolic reference coefficients in the protected basis.
- `s21_prepare_learning.py` checks split separation and massless external kinematics.
- `s22_learn.sh` collects the two splits and fits the model.
- `s23_prepare_test.py` freezes inputs, code, weights, and executable records before the final test.
- `s24_model_test.py` compares four applications on its assigned frozen requests.
- `s25_model_test.sh` checks the entry point and submits the paired final comparison.
- `s26_analyze.py` computes paired ratios, completion counts, uncertainty, and the separate ML effect.
- `s27_plot.py` draws the four report figures from the saved results.
- `s28_write_paper.py` updates the methods and preserves the earlier evidence in the notes.
- `s29_write_results.py` writes the measured results and physical input appendix.
- `s30_check_model.py` checks prediction export and complete development applications.
- `s31_write_guides.py` updates this guide, folder guides, and current entry pointers.
- `s32_validate.py` checks frozen evidence, preserved methods, documents, and resource bounds.
- `s33_retained_ml.py` switches inherited learned choices off while sharing the validated algebra setting.
- `s34_retained_test.py` freezes and measures that separate paired ablation.
- `s35_retained_test.sh` runs its two bounded workers after the main comparison.
- `s36_analyze_retained.py` reports its elapsed time, completion, and recorded seed sequences.

## Exact checks and interrupted trials

Every final coefficient is compared with a separate exact reference.
For native reconstruction, that reference is a symbolic Kira calculation.
Some larger complete-region confirmations exceeded the reference bound.
The published symbolic application still supplies their independent symbolic coefficients.
`expanded_reference_attempt/`, `ordering_reference_attempt/`, and
`complete_region_reference_attempt/` preserve those preparation trials.
They do not represent failed model-selected applications.

`kinematic_convention_attempt/` preserves an early nonplanar input error.
Its scalar-product signs did not match the intended outgoing-momentum convention.
Those records were removed from training before model fitting.
`kinematic_checks.json` verifies the corrected on-shell conditions and invariant metadata.
`pilot_basis_checks.json` resolves two pilot comparisons made in different master bases.
The original pilot output remains preserved.
No reserved outcomes select the model or its settings.

## Resource bounds

The combined project ceiling is 10,000,000,000 bytes.
The conservative preceding persistent bound is 9,778,738,176 bytes.
Retained new tools use at most 32 MiB; study files use at most 20 MiB.
Stage files and logs reserve 4 MiB.
Two native workers reserve 96 MiB for scratch and transient application files.
Publication reserves 140 MiB for report copies, Git, and temporary document files.
Native tests stop before publication.
The larger bound is 9,984,258,? bytes; `resource_plan.json` gives the exact computed value.
Each native calculation uses one computational thread.
The wrappers limit address space and output files.
Keep other user jobs unchanged.
"""
 # Keep the numerical bound computed from the same constants used by validation.
 peak=PERSISTENT_UPPER+(32+20+4+140)*1024**2
 text=text.replace('9,984,258,? bytes',f'{peak:,} bytes')
 save(HERE/'README.md',text)
 descriptions={
 'retained_ml_test':"""# Inherited learned choices

These paired runs hold the validated reconstruction settings fixed.
They compare the inherited learned application with its existing all-fixed procedure.
Both use the same reserved physical inputs and exact references as the main test.
No additional model fitting uses these outcomes.
The times are measured together and are separate from the main four-method experiment.
Do not multiply this ratio into the cumulative ratio.""",
 'trained_model':"""# Trained algebra-cost selector

`policy.json` contains the fitted forest, feature ranges, settings, training lineage, and validation result.
`fixed.json` contains the matched fixed settings and no new model weights.
`deployment.json` selects which configuration the complete application loads.
The preceding seed model is shared by both configurations.
Do not change these files during a reserved comparison.""",
 'training':"""# Training action measurements

Each compressed JSON file records one physical request and one candidate action.
The record contains features, complete elapsed time, exact checks, and failed attempts.
Training uses one timed repetition per action.
The six records for a request use the same worker and input.
Reference coefficients remain outside the timed application.
Read the root study guide for the split and cost definition.""",
 'validation':"""# Validation action measurements

Each compressed JSON file records three complete runs of one action on one request.
The mean elapsed time selects model settings and the fixed controls.
The records preserve each repetition and failed attempt.
Validation requests do not enter estimator fitting.
No reserved test time enters this selection.""",
 'references':"""# Symbolic training and validation references

These files contain separate symbolic reductions in the application's protected master basis.
They are independent of the new finite-field reconstruction.
Additional complete-region confirmation attempts can reach their bound.
The preceding symbolic application supplies the exact coefficients for those cases.
Reference preparation is outside the application timer.""",
 'test_references':"""# Reserved-test references

These exact coefficients check the complete timed outputs.
Native references come from separate symbolic Kira reductions.
Analytic references use the previously verified formulas or independent partial fractions.
The reference coefficients never enter the model or timed algebra.""",
 'model_test':"""# Complete application comparison

Each compressed JSON file records one frozen physical request.
The four methods run three times in rotating order on the same worker.
Times include imports, model use, equation generation, exact algebra, recovery, output, and exit.
The external coefficient comparison occurs after that timer.
Records contain completions, failed attempts, chosen actions, and exact results.
The root summary uses summed per-request medians on matched completed requests.
All failures remain in the separate completion counts.""",
 'development':"""# Development comparisons

These records test algebra modes, probe batch sizes, and simple physical structures.
They precede model fitting and the reserved comparison.
Some separate batch-size pilot jobs used different nodes.
Their single times do not establish a precise cross-node batch-size speed ratio.
Two apparent coefficient mismatches used different master bases.
The root pilot basis-check record gives the corrected exact comparisons.
The original records remain unchanged.""",
 'requests':"""# Transient application inputs

The timer writes one small request and result here for each active worker.
It removes those files after collecting the bounded record.
This folder must be empty apart from this guide before publication.""",
 }
 for folder,guide in descriptions.items():save(HERE/folder/'README.md',guide)
 plan=dict(persistent_preceding_upper_bytes=PERSISTENT_UPPER,tools_limit_bytes=32*1024**2,study_limit_bytes=20*1024**2,stage_and_logs_limit_bytes=4*1024**2,native_transient_limit_bytes=96*1024**2,publication_reserve_bytes=140*1024**2,native_peak_upper_bytes=PERSISTENT_UPPER+(32+20+4+96)*1024**2,publish_peak_upper_bytes=peak,ceiling_bytes=10_000_000_000)
 assert max(plan['native_peak_upper_bytes'],plan['publish_peak_upper_bytes'])<plan['ceiling_bytes']
 write(HERE/'resource_plan.json',plan)
 for name in ['README.md','ML_model_adaptive_reduction/README.md']:
  path=ROOT/name;old=path.read_text()
  guide='ML_model_adaptive_reduction/reconstruction_policy/README.md' if name=='README.md' else 'reconstruction_policy/README.md'
  begin='<!-- RECONSTRUCTION APPLICATION BEGIN -->';end='<!-- RECONSTRUCTION APPLICATION END -->'
  import re
  old=re.sub(re.escape(begin)+r'.*?'+re.escape(end)+r'\n*','',old,flags=re.S)
  addition=f"""{begin}
Use `ML_model_adaptive_reduction/reconstruction_policy/s15_deploy.py` for the current application.
Read [the reconstruction application guide]({guide}).
The integrated-to-preceding complete-time ratio is {ratio:.4f} on {s['all']['matched_completed']} matched requests.
The separate added-model ratio is {m['ratio']:.4f}; new-model deployment is `{s['model_enabled']}`.
The separate inherited-ML ratio is {retained['all']['ratio']:.4f}.
The matched cumulative ratio across the two latest extensions is {c['ratio']:.4f}.
The study retains exact formulas through thirteen loops in their stated domains.
It tests new native requests at two and three loops.
Read the paper for the physics, derivations, measured results, and coverage limits.
{end}
"""
  old=old.replace('Use `ML_model_adaptive_reduction/direct_analytic/s23_deploy.py`.','The preceding application is `ML_model_adaptive_reduction/direct_analytic/s23_deploy.py`.')
  save(path,old.split('\n',1)[0]+'\n\n'+addition+'\n'+old.split('\n',1)[1].lstrip())
 print('Study guides and current entry pointers updated',flush=True)
if __name__=='__main__':main()
