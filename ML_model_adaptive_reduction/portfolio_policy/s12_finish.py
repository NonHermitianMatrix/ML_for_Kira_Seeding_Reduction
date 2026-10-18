"""Verify results, document each folder, and rebuild both research documents."""
from s00_common import *
import subprocess

def main():
 for n in ['test_0_complete.json','test_1_complete.json','integration/completion.json','integration/extended_checks_complete.json','wide_integration/completion.json','integration/application_completion.json','scalar_test/summary.json','combined_0_complete.json','combined_1_complete.json']:assert read(HERE/n)['complete'],n
 for folder in ['kira-sector-storage','kira-sector-wide']:
  for obj in (ROOT/'.tools'/folder).glob('*.o'):obj.unlink()
 for n in ['s10_analyze.py','s11_document.py']:subprocess.run([sys.executable,str(HERE/n)],check=True)
 assert read(HERE/'integration/ordering_validation.json')['passed']
 s=read(HERE/'summary.json');f=read(HERE/'trained_model/freeze.json')
 for n,h in f['model_sha256'].items():assert inputs.sha(HERE/'trained_model'/n)==h
 assert f['application_sha256']==inputs.sha(HERE/'s01_application.py') and f['production_sha256']==inputs.sha(HERE/'s08_reduce.py')
 sources={
  'training':'s02_collect.py creates the new measured training costs. Each action record contains its complete time, exact coefficients, checks, and all retries. Duplicate configurations link to their measured record through identical_configuration_from.',
  'validation':'s02_collect.py creates the separate validation costs. s04_train.py uses these costs to select fixed settings, tree models, decision margins, and deployment gates. selection.json records every candidate score.',
  'confirmation':'s15_confirm.py checks proposed learned gains on profile 1113. This profile is separate from training, initial validation, and testing. selection.json records which model gates remain enabled.',
  'trained_model':'s04_train.py fits the saved tree models. fixed.json gives the fixed action, domain bounds, selected model, and deployment decision for each family. freeze.json records the training sources and fixed model contents. Live prediction does not load scikit-learn.',
  'references':'s02_collect.py creates independent native references. Each check increases the numerator bound and changes the integral ordering. Failed references stay here. The application receives a master basis but receives no reference coefficients as model inputs.',
  'coverage':'s05_test.py writes one outcome per reserved request. Read these records before interpreting matched timing results. Missing checked references remain explicit.',
  'model_test':'s05_test.py compares native, fixed, learned, previous, and combined applications. Each matched request has five rotated repetitions. All times include the fresh process and exact checks.',
  'requests':'s02_collect.py writes temporary request files here. It removes each file after its measured process finishes. A completed study leaves only this guide.',
  'logs':'These files contain scheduler output. Logs stay on Hoffman and outside Git. Scientific records retain failures and error tails.',
  'integration':'s06_build_sector_storage.py creates sector_storage.patch and sector_weights.patch, plus the exact build recipe. These patches bound sector arrays, retain the order of admitted sectors, and count trivial sectors without an exhaustive scan. s07_sector_checks.py compares it with native allocation. The compiled executable stays under .tools/kira-sector-storage. The patch retains native allocation unless KIRA_BOUNDED_SECTOR_ARRAYS and the existing sector restriction are active.',
  'integration/initial_check_failures':'These are the initial 60-second enlarged-check failures. s23_retry_enlarged_checks.py retains the original criterion and retries only time limits with 180 seconds. Final records state the extended budget.',
  'integration/references':'s07_sector_checks.py discovers bases with the bounded allocation. A second run increases numerator bounds and changes ordering. Failed attempts remain available.',
  'integration/model_test':'s07_sector_checks.py records repeated old and bounded allocation reductions in a common basis. A failed old allocation has no finite completion-time ratio. These tests use no learned choices.',
  'integration/application_checks':'s22_select_storage.py checks the complete application for each proposed exact storage route against its independent reference. Routes that fail these checks remain disabled.',
  'uncached_storage':'These validation records precede the bounded cache of exactly zero coefficients. They measure its original overhead. Final deployment uses only the cached implementation and separate later tests.',
  'uncached_storage/references':'These are the original exact storage reference calculations. They remain separate from the final version.',
  'uncached_storage/results':'These outcomes belong to the uncached exact zero-coefficient check.',
  'uncached_storage/model_test':'These repetitions measure the uncached zero-coefficient check, which is retained only for diagnosis.',
  'integration/results':'s07_sector_checks.py writes one final outcome for each predefined storage request. Read times, failed_methods, and status together.',
  'combined_coverage':'s14_combined_test.py records all final reserved requests at profile 1151. Read these outcomes before using the matched timing table.',
  'wide_integration':'s16_build_wide.py rebuilds the same exact implementation with 128-bit Kira weights. s17_wide_checks.py repeats the predefined storage grid. This width changes an internal ordering representation and leaves the algebra exact.',
  'wide_integration/references':'These files retain the wider executable reference calculations and independent enlarged checks, including failures.',
  'wide_integration/results':'Each record gives the final outcome of one predefined storage request with 128-bit weights.',
  'wide_integration/model_test':'These matched tests compare native and bounded allocation within the same 128-bit executable. Read the references and outcomes with the times.',
  'combined_test':'s14_combined_test.py compares the final exact and learned implementation with matched native, previous, and fixed controls. Five rotated repetitions retain every exact check and failure. combined_protocol.json freezes the sources, models, and executable.',
  'scalar_test':'s09_scalar_checks.py tests full-coordinate scalar massless two-point inputs through the final application at loops one through twelve. It uses a separate raising recurrence for exact coefficient checks. These checks test the analytic formula and use no ML.'}
 for name,text in sources.items():
  p=HERE/name;p.mkdir(parents=True,exist_ok=True);(p/'README.md').write_text('# '+name.rsplit('/',1)[-1].replace('_',' ').capitalize()+'\n\n'+text+'\n\nRead the main folder guide for execution order and limits.\n')
 for archive in ['initial_fit','integration_repairs','uncached_storage']:
  base=HERE/archive
  if base.exists():
   for folder in [base]+[q for q in base.rglob('*') if q.is_dir() and '__pycache__' not in q.parts]:
    q=folder/'README.md'
    if not q.exists():q.write_text('# Archived '+folder.name.replace('_',' ')+'\n\nThese files belong to '+archive.replace('_',' ')+'. Read the archive parent guide for their status. They do not enter the current timing summary. Original model, case, coefficient, and failure records remain unchanged.\n')
 (ROOT/'.tools/kira-sector-storage/README.md').write_text('# Bounded sector storage\n\nThis folder contains the compiled exact Kira implementation. Read ML_model_adaptive_reduction/portfolio_policy/integration/README.md for the source patches, build recipe, exact checks, and conditions. Rebuild with s06_build_sector_storage.py in a compute job. No fitted model is stored here.\n')
 assert not list((HERE/'requests').glob('*.json'))
 assert not s['combined']['failures'],'Inspect combined failures before deployment'
 o=s['combined']['overall'];r=o['summed_median_seconds']
 text=f'''# Family-aware seed-cost model

This study chooses seed bounds before Kira generates IBP equations.
IBP means integration by parts.
Kira performs the exact algebra. Failed choices trigger bounded recovery.
The model predicts the full cost of ten settings.
It receives integral features and no answer coefficients.

The final reserved grid contains {s['combined']['requested']} batches. The matched set contains {o['cases']} nontrivial batches.
The learned-to-fixed time ratio is {o['learned_over_fixed']:.6f}.
The combined-to-previous ratio is {o['production_over_previous']:.6f}.
The new target-pattern model deploys on {s['combined']['deployed'].get('cases',0)} matched batch.
Its learned-to-fixed time ratio is {s['combined']['deployed']['learned_over_fixed']:.6f}.
Its learned-to-native time ratio is {s['combined']['deployed']['ratios_to_native']['learned']:.6f}.
The new model reduces time against the fixed control and gives no clear gain against native bounds in this batch.
The final application's time ratio against native is {o['ratios_to_native']['production']:.6f} over all matched batches with a supplied basis.
The final-to-previous interval is {o['intervals']['production_over_previous']}. It includes one, so the added aggregate gain remains uncertain.
Read the deployed subset in summary.json for its isolated model effect.
Inactive learned and fixed conditions use identical choices. Their time differences measure run variation.
A ratio below one means less time.
Read summary.json for intervals, each family, failed references, and active learned decisions.
A combined gain includes exact formula selection and fixed choices.
Do not describe the full combined gain as an ML gain.

## Use

Run from the project root in a Hoffman compute job.
Use the case and basis schema from protocol.json and references/.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/portfolio_policy/s13_optimized.py --case CASE.json --basis BASIS.json --output RESULT.json.gz
```

The combined application keeps the exact scalar formula where valid.
It uses the new choice only when validation improves on the previous application.
A target-shape gate deploys the learned choice where confirmation improves on both fixed and previous controls.
Other inputs use the previous application and its domain guards.
The native index limit still applies to general IBP calculations.
Scalar formula inputs can use the full coordinate representation through twelve tested loops.
The sector-storage executable supplies a separate exact optimization.
The final application uses it only in domains selected by the separate exact validation.
Other inputs retain the previous executable.
A separate wider executable supports the tested 128-bit integral-weight route.
Its matched controls separate the learned gain from the exact gain.
Use KIRA_BOUNDED_SECTOR_ARRAYS=1 with KIRA_RESTRICT_SECTOR_INIT=1 when calling that executable.
Its tests cover cold single-family runs without cuts or symbolic IBP.
The main learned comparison uses the preceding exact executable for all controls.

## Reproduce

1. Read resource_plan.json and protocol.json.
2. Run s02_collect.py training 0 and training 1 through s03_job.sh.
3. Run s02_collect.py validation 0 and validation 1.
4. Run s04_train.py to fit and freeze the models.
5. Run s05_test.py 0 and s05_test.py 1.
6. Run s06_build_sector_storage.py to build the bounded sector arrays.
7. Run s20_check_sector_order.py and s07_sector_checks.py for the separate exact comparison.
Run s23_retry_enlarged_checks.py for the one longer attempt on timed-out enlarged checks.
8. Run s09_scalar_checks.py for the full-coordinate scalar checks.
9. Run s16_build_wide.py and s17_wide_checks.py for the separate 128-bit checks.
10. Run s19_freeze_deployment.py to freeze target-shape gates from confirmation.
11. Run s22_select_storage.py to select and verify exact routes.
12. Run s14_combined_test.py 0 and s14_combined_test.py 1 on fresh profile 1151.
13. Run s12_finish.py to analyze, write, build, and check both documents.

Use at most two project compute jobs at once.
The study uses the existing NumPy, scikit-learn, SymPy, and Matplotlib environment.
C++ compilation uses the existing GCC and Kira build recipes.
The report uses the existing Tectonic installation.

## Files and limits

s00_common.py defines the physical inputs, feature extraction, file format, and storage guard.
s01_application.py runs a fresh measured application or one cost action.
s02_collect.py records full process time and creates independent references.
s03_job.sh sets the scheduler, thread, and memory limits.
s04_train.py compares nine shared models, separate family cost trees, and three decision margins.
It then calls s15_confirm.py on another validation profile.
s05_test.py checks the frozen reserved inputs.
s06_build_sector_storage.py builds the exact storage change and records the patch.
s07_sector_checks.py checks that change on low- and higher-loop inputs.
s08_reduce.py combines the learned policy with the preceding exact implementation.
s13_optimized.py adds bounded sector storage.
s14_combined_test.py tests the final combined implementation.
s09_scalar_checks.py checks the scalar formula through twelve loops.
s16_build_wide.py and s17_wide_checks.py build and check wider integral weights.
s19_freeze_deployment.py selects target-shape deployment from confirmation costs.
s18_debug_storage.py traces the discarded initial storage error and is not part of production.
s20_check_sector_order.py compares the sector ordering and minimum-line count against exhaustive small controls.
s21_cached_storage_checks.py preserves the uncached comparison and checks the exact cache.
s22_select_storage.py selects exact routes from validation and checks the complete application.
s23_retry_enlarged_checks.py retries timed-out enlarged checks once with a longer time budget.
It preserves the original independent check and the initial failures.
s10_analyze.py creates the summaries and timing figure.
s11_document.py writes the method and results in the report and notes.
s12_finish.py writes folder guides, rebuilds both PDFs, and validates publication inputs.

The training profiles differ from validation and test profiles.
The graph structures and target patterns overlap between these sets.
Historical training records use their earlier internal application timer.
New training, validation, and tests include fresh-process cost.
The native, fixed, and learned test controls use the same exact executable.
Reference discovery remains separate from the primary application time.
The repeated timer includes model loads, prediction, algebra, checks, and retries.

Each native attempt uses one worker, a 6 GiB address limit, a 5,200 MiB process-tree limit, and 32 MiB of temporary storage.
Application attempts have 60 seconds. Reference attempts have 90 seconds.
The driver reserves ten seconds for completion and cleanup.
The study retains at most 24 MiB of records. The completed build objects are removed. Recheck the global storage budget before starting a new compilation.
Keep the whole project below 10,000,000,000 bytes.
Keep generated models and data on Hoffman and GitHub.
Keep both reports locally as well.

These tests do not establish a speedup for every integral type or arbitrary loop order.
The twelve-loop scalar checks verify a stated exact identity and use no learned prediction.
'''
 (HERE/'README.md').write_text(text)
 p=ROOT/'ML_model_adaptive_reduction/README.md';t=p.read_text();line='portfolio_policy/ adds family-aware seed-cost models, exact sector-storage checks, and full-coordinate scalar checks. Read its README for the tested scope.'
 if line not in t:p.write_text(t+'\n'+line+'\n')
 p=ROOT/'README.md';t=p.read_text()
 import re
 current='''<!-- BEGIN ADAPTIVE REDUCTION -->
## Current reduction interface

Use [the family-aware application](ML_model_adaptive_reduction/portfolio_policy/README.md) for individual target batches.
It retains exact scalar formulae and uses validation-selected learned or fixed seed choices.
Other inputs retain the preceding sparse-seed, equation-filter, and native paths.
Use [the joint-configuration application](ML_model_seed_selection/joint_policy/README.md) for its supported scale-reuse sequences.
The new folder also contains a separate exact sector-storage executable and its checks.
Kira keeps native row choices and exact algebra.
Read each guide for the measured physical domain and timing controls.
Earlier studies remain available. Their speedup factors cannot be multiplied.
<!-- END ADAPTIVE REDUCTION -->'''
 t=re.sub(r'<!-- BEGIN ADAPTIVE REDUCTION -->.*?<!-- END ADAPTIVE REDUCTION -->',lambda _:current,t,flags=re.S);p.write_text(t)
 subprocess.run(['make','all'],cwd=ROOT/'report',check=True)
 subprocess.run([sys.executable,str(ROOT/'report/s01_check_paper.py')],cwd=ROOT/'report',check=True)
 v=dict(complete=True,all_matched_results_exact=True,summary_sha256=inputs.sha(HERE/'summary.json'),storage_policy_sha256=inputs.sha(HERE/'integration/deployment.json'),model_sha256=dict(f['model_sha256'],**{'deployment.json':inputs.sha(HERE/'trained_model/deployment.json')}),source_sha256={p.name:inputs.sha(p) for p in HERE.glob('s*.py')},pdf_sha256={n:inputs.sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file()))
 assert v['study_allocated_bytes']<24*1024**2
 write(HERE/'validation.json',v);write(ROOT/'report/family_cost_validation.json',v);print(json.dumps(v),flush=True)
if __name__=='__main__':main()
