"""Finish conclusions and readable guides from completed preparation evidence."""
from s00_common import *
from s14_prepare import P

def main():
 s=READ(P/'summary.json');report=ROOT/'report';c=s['comparisons'];counts=s['counts']
 def sentence(key,label):
  a=c[key]
  if not a['cases']:return label+' has no matched timing ratio. '
  return f"{label} gives ratio {a['ratio']:.3f} on {a['cases']} matched requests, with repeat interval [{a['interval'][0]:.3f},{a['interval'][1]:.3f}]. "
 text=sentence('cached_native/expanded','Compact preparation without ML compared with expanded discovery')
 text+=sentence('cached_learned/cached_native','The neural model within compact preparation')
 text+=sentence('cached_risk/cached_native','The cost-and-risk model within compact preparation')
 risk=c['cached_risk/cached_native'];neural=c['cached_learned/cached_native']
 if risk['cases'] and risk['interval'][1]<1:
  interpretation='The cost-and-risk model adds a resolved time saving within this matched set. Its broader completion counts remain separate from that conditional ratio.'
 elif risk['cases'] and risk['interval'][0]>1:
  interpretation='The cost-and-risk model increases time in this broad comparison. The neural preparation result also remains consistent with equal time. We keep the failure model and its records for analysis, while the shared neural model remains the validated supplied-basis default.'
 else:
  interpretation='The cost-and-risk model supplies no resolved additional time saving on this comparison. We keep its trained parameters and failure records for analysis, while the shared neural model remains the validated supplied-basis default.'
 conclusion='\n\n'+text+interpretation+' The cache supplies only previously checked master indices, and every new target is reduced and checked at its own parameters. The preparation change and the learned choice therefore receive separate controls.\n'
 f=report/'paper_conclusion.tex';t=f.read_text();t=t.replace('\n\nThe remaining limitation is native coverage.',conclusion+'\nThe remaining limitation is native coverage.');f.write_text(t)
 f=report/'preparation_results.tex';f.write_text(f.read_text()+'\n'+text+interpretation+'\n')
 route=s['outside_scalar_formula'];v=route['comparisons']['cached_learned'];deployment=s['deployment']
 routing='The full application first checks whether the restricted scalar massless formula applies. This is a physical condition, independent of measured time. '
 if v['cases']:routing+=f"Among the remaining requests, the neural preparation model gives ratio {v['ratio']:.3f} on {v['cases']} matched completions, with repeat interval [{v['interval'][0]:.3f},{v['interval'][1]:.3f}], relative to compact preparation without ML. "
 if deployment['preparation_method']=='learned':routing+='We retain that model for preparation because its interval lies below one and it completes every request completed by the native control in this subset. '
 else:routing+='These measurements do not meet both conditions for retaining learned preparation: a time interval below one and completion of every request completed by its native control. The default therefore uses native choices for preparation and retains the shared neural model for supplied-basis reduction, where the separate test establishes a gain. '
 routing+='This deployment choice follows the candidate comparisons. The reported ratios belong to the frozen methods; they do not provide a new independent timing test of the resulting selector.'
 f=report/'preparation_results.tex';f.write_text(f.read_text()+'\n'+routing+'\n')
 f=report/'paper_conclusion.tex';t=f.read_text();t=t.replace('\nThe remaining limitation is native coverage.','\nThe final application separates physical exact formulas, preparation, and supplied-basis reduction. It enables learned choices in the stages supported by their complete-time comparisons.\n\nThe remaining limitation is native coverage.');f.write_text(t)
 f=report/'paper_abstract.tex';t=f.read_text();extra=' A separate 33-request preparation comparison trains on both completed and failed attempts and separates the cost of basis reuse from the effect of learned choices.'
 if deployment['preparation_method']=='native':extra+=' It does not support learned preparation, so that stage retains native choices.'
 t=re.sub(r'On separate known-graph workloads,.*?retained method\.', 'Local seed and equation models give measured savings, while learned row selection gives no reliable gain and is omitted.',t)
 t=t.replace(' Failed references and unsupported inputs remain explicit.',extra+' Failed references and unsupported inputs remain explicit.');f.write_text(t)
 f=report/'paper_conclusion.tex';t=f.read_text();decision=('The default keeps native preparation and uses the shared neural model when a master basis is supplied.' if deployment['preparation_method']=='native' else 'The default retains the shared neural model for preparation and supplied-basis reduction in their measured domains.')
 t=t.replace('The final application separates physical exact formulas, preparation, and supplied-basis reduction. It enables learned choices in the stages supported by their complete-time comparisons.',decision+' The exact scalar formula takes priority when its physical assumptions hold.');f.write_text(t)
 f=report/'report.tex';t=f.read_text();anchor='Learned row selection remains omitted because its measured gain is not resolved from timing variation.'
 clarification=' The current shared-model application enables learned seed bounds. The equation filter retains its separate validated application, and no combined gain is inferred from these separate tests.'
 if clarification not in t:t=t.replace(anchor,anchor+clarification)
 f.write_text(t)
 f=report/'notes.tex';t=f.read_text();marker='% END CURRENT WORKFLOW UPDATE';start=t.index('\\paragraph{Current');end=t.index(marker,start)
 t=t[:end]+'\\paragraph{Current preparation comparison.} '+text+interpretation+'\n'+t[end:];f.write_text(t)
 readme='''# Preparation with learned attempt cost

This comparison reduces repeated master discovery and measures failed work.
It keeps the earlier neural model and adds a model of attempt time and failure.
Kira computes every new coefficient. The cache stores master indices only.

## Run order

Use `.tools/seed-model/venv/bin/python` from the project root on a Hoffman compute node.
Use `../s04_job.sh` to submit scripts. Keep at most two native workers active.

1. Run `../s15_risk.py`. It trains the cost-and-failure model, checks the exported predictions, and calls `../s14_prepare.py` to freeze the cache and test protocol.
2. Run `../s16_test_preparation.py 0` and `../s16_test_preparation.py 1`. Each worker runs its declared requests. It retains failures and repeats initially successful methods twice.
3. Run `../s17_analyze_preparation.py`. It checks exact agreement, keeps matching bases, and creates the result summary and figure.
4. Run `../s18_document_preparation.py` and `../s19_finish_preparation.py` after the shared document writer. They update the paper, notes, and guides.
5. Run `../s13_finish.py` after the preparation and recovery workers finish to collect the full checks and build both PDFs.

## Use the preparation application

Prepare a JSON object with `case` and `method` keys. A case has `id`, `definition`, `targets`, and `size`, as in `protocol.json`.
Choose `cached_learned` for the neural model, `cached_risk` for the cost-and-failure model, `cached_native` to disable ML, or `expanded` for the broad discovery control.
Run `../s14_prepare.py --input REQUEST.json --output RESULT.json.gz` from this folder, using the scientific Python.
Use absolute paths when running from the project root. Use a scheduled compute job for Kira.
The application needs no reference coefficients. It compares two exact reductions internally.
The `s16` timer also includes process start and exit. The application's inner timer does not include its imports.
For an already supplied basis, the public `../s11_reduce.py` interface retains the shared neural policy and applicable exact scalar formulas.

## Training and test separation

Training uses historical training attempts and the initial shared-model profile 1201.
Historical validation requests select the forest and penalty. The fresh profile 1237 stays reserved.
The distinct-mass vacuum benchmark, nonplanar boxes, pentagons, and orders six and above supply no training or validation labels.
The 52 features describe the mathematical structure, requested powers, candidate bounds, basis state, and ordering.
The model receives no family name or stored structure key. Only the separate exact basis cache uses an ordered structure key.
The failure output is a ranking score. It is not a calibrated probability.

## Controls and exact checks

All four controls use `.tools/kira-sector-wide/kira` with bounded sector arrays.
The build procedure is in `ML_model_adaptive_reduction/portfolio_policy/s16_build_wide.py`. Read that folder's guide and source receipt before rebuilding.
The 128-bit setting stores integral-ordering labels. Exact rational coefficients use the same arithmetic in all controls.
The supplied index limit remains 31. Each request has 110 seconds; one native call has at most 60 seconds.
The native process watchdog reserves cleanup time inside that call cap.
Each worker has at most 32 MiB of scratch and a 5,200 MiB process-tree RSS limit.
The project limit remains 10 GB. Read `../resource_plan.json` before adding work.

The compact workflow reuses a previously checked index basis when available.
It recalculates coefficients at the new kinematics and compares a second reduction with a different integral ordering.
If no cache entry exists, compact discovery returns a provisional basis.
This check establishes the requested identities. It does not prove a globally minimal master basis.
Cache construction cost precedes these measurements and is reported separately.
Incomplete attempts can expand bounds. Duplicate native settings are not run again within a request.

## Read the results

`summary.json` retains every first request, failed-call cost, three-repeat completion, and matched time comparison.
Pairwise time ratios require the same master-index set and exact coefficients in all three repetitions.
Different bases and failed requests stay in the outcome counts. They do not receive a successful speedup ratio.
The ML-off compact control separates learned effects from reuse and the changed check.
`basis_cache.json` records the earlier source and check for every stored index basis.
`protocol.json` records the inputs, budgets, frozen models, and cache.
`trained_model/` contains the forest and fitting records. `model_test/` contains measured outputs.
`coverage/` contains each request's outcome. `requests/` holds only temporary running inputs.

'''
 readme+=text+interpretation+'\n';(P/'README.md').write_text(readme)
 guides={'trained_model':'The saved forest predicts log attempt time and a scaled failure label. freeze.json contains weights, sources, candidate scores, and selection. selection.json gives the short result. s15_risk.py produces both files. The exported evaluator passes comparison with the training library on all training inputs.',
 'model_test':'s16_test_preparation.py produces one compressed record per method and repetition. Each record includes complete process time and native attempt outcomes. Failed first requests remain. A successful first request gets two more repetitions. Read summary.json for exact matching and the full denominator.',
 'coverage':'s16_test_preparation.py records one outcome per physical request. The record includes all four first outcomes and initial cross-method agreement. s17_analyze_preparation.py also checks every completed repetition.',
 'requests':'s16_test_preparation.py writes temporary input files here and removes them after each call. Scientific outputs are stored in model_test.'}
 for name,body in guides.items():
  f=P/name;f.mkdir(exist_ok=True);(f/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+body+'\n\nRead [the preparation guide](../README.md) for inputs, run order, and limits.\n')
 (P/'trained_model/training_diagnostics.txt').write_text((HERE/'logs/preparation_train.log').read_text())
 recovery=READ(HERE/'recovery/summary.json')
 recovery_text='The first compact trial exposed a target-dependent basis mismatch: a basis checked for earlier targets can omit masters needed by a new batch. The revised application discards a rejected cached basis after expanded seeding also fails, rediscovers without that constraint, and checks the result. It also permits an expanded target check when smaller checks fail. All steps remain inside the same 110-second request budget. '
 recovery_text+='A focused follow-up uses six fresh requests at two through five loops and keeps the models and index cache fixed. '
 recovery_text+=f"All three repetitions complete on {recovery['completed']['cached_native']}/6 requests with ML disabled, {recovery['completed']['cached_learned']}/6 with the neural model, and {recovery['completed']['cached_risk']}/6 with the cost-and-risk model. "
 for k,label in [('cached_learned/cached_native','neural'),('cached_risk/cached_native','cost-and-risk')]:
  v=recovery['comparisons'][k]
  if v['cases']:recovery_text+=f"The {label} model gives a ratio of {v['ratio']:.3f} on {v['cases']} matched requests, with repeat interval [{v['interval'][0]:.3f},{v['interval'][1]:.3f}], relative to the revised workflow without ML. "
 recovery_text+=f"The comparison passes {recovery['coefficient_checks']:,} coefficient checks. It tests the recovery change on fresh parameters of selected structures and does not replace the broad trial."
 f=report/'preparation_results.tex';f.write_text(f.read_text()+'\n\\subsection{Recovery from an incomplete stored basis}\n'+recovery_text+'\n')
 f=report/'paper_conclusion.tex';t=f.read_text().replace('\nThe remaining limitation is native coverage.','\nThe focused follow-up adds basis refresh when a stored basis cannot reduce a new batch. Its complete outcomes and matched model comparisons appear in Section~\\ref{sec:preparation}.\n\nThe remaining limitation is native coverage.');f.write_text(t)
 f=report/'preparation_appendix.tex';f.write_text(f.read_text()+'\nThe focused recovery comparison uses profile $h=1249$ for the distinct-mass vacuums at four and five loops, the massless and massive three-loop two-point families, the three-loop box with bubbles, and the two-loop ladder. It uses dotted targets at odd orders and mixed targets at even orders. Three repetitions compare the same compact workflow with native bounds, the neural model, and the cost-and-risk model. Model weights and cache entries are unchanged. The revised recovery rule follows the basis rejection observed in the preceding experiment; this follow-up therefore tests that specific correction.\n')
 rguide='''# Recovery from an incomplete stored basis

`s20_prepare_resilient.py` in the parent folder is the revised preparation application.
Use its `--input` and `--output` arguments as described in the preparation guide.
It retains the learned seed choice and exact checks. If an earlier index basis is rejected even with expanded bounds, it discovers a basis without that constraint.
It also tries an expanded target check if smaller checks fail. The total request budget remains 110 seconds.
The original s14 application and its measurements remain unchanged.

Run `../s21_recovery.py initialize` to freeze the focused profile before measurements.
Run `../s21_recovery.py 0` and `../s21_recovery.py 1` as compute jobs after the preparation workers finish.
Run `../s21_recovery.py analyze` to check all repeated outputs and produce summary.json.
The models and basis cache come from preparation/ and refit/. No model is fitted on these six cases.
The comparison uses three methods and three repetitions for initially successful methods.
Failed requests stay in the summary. A paired ratio requires matching exact outputs and the same master-index set.

'''
 (HERE/'recovery/README.md').write_text(rguide+recovery_text.replace('~',' ')+'\n')
 for folder,description in [('model_test','Measured complete process times, native attempts, basis refresh, and exact coefficients.'),('coverage','The first and three-repeat completion status for every request.'),('requests','Temporary application inputs. The worker removes each input after storing its result.')]:
  d=HERE/'recovery'/folder;d.mkdir(exist_ok=True);(d/'README.md').write_text('# '+folder.replace('_',' ').capitalize()+'\n\n'+description+'\n\nThe producer is `../../s21_recovery.py` in the general_policy folder. Read [the recovery guide](../README.md) for run order and inputs.\n')
 f=P/'README.md';t=f.read_text();t+='\n## Revised recovery application\n\nUse `../s20_prepare_resilient.py` for the revised preparation workflow. It can discard an incomplete cached basis and discover a new one. Read [the recovery comparison](../recovery/README.md) for its fresh tests. The s14 application remains the frozen original comparison.\n';f.write_text(t)
 f.write_text(f.read_text()+'\nThe unified `../s22_reduce.py` interface accepts an optional basis. It follows deployment.json when no basis is supplied, while preserving the shared neural model for a supplied basis. The deployment file records a decision made after these candidate tests; it has no independent selector-speedup claim.\n')
 f=report/'README.md';t=f.read_text();block='''\n## Complete preparation comparison

`preparation_results.tex` reports all outcomes and matched full workflow times.
`preparation_appendix.tex` derives the cost-and-failure objective and defines the test inputs.
`preparation_data.json` contains the compact comparison evidence.
`notes_general_methods.tex` places the shared model and physical definitions in the notes.
Scripts s17 through s19 in `general_policy/` produce these files and the preparation figure.
The main `s13_finish.py` writer runs them after the shared-model writer.
'''
  # This is a distinct section of the same guide.
 if '## Complete preparation comparison' not in t:f.write_text(t+block)
 f=report/'paper_figures/README.md';t=f.read_text();block='\n`preparation_results.pdf` separates failed-call cost from the ML increment within compact preparation. Its producer is `general_policy/s17_analyze_preparation.py`. Read `preparation_data.json` for all completions and pairwise denominators.\n'
 if '`preparation_results.pdf`' not in t:f.write_text(t+block)
 f=report/'general_policy_citation_audit.json';audit=READ(f)
 audit['original_equations'].update({'eq:risk-fit':'Defined two-output squared loss, with leaf means derived by differentiation','eq:risk-score':'Defined ranking, inverse transformations and failure penalty explained','eq:risk-selection':'Defined validation objective, denominator-independent minimization explained'})
 audit['original_results_tables']+= [a for a in ['tab:preparation-coverage','tab:preparation-times','tab:preparation-loops'] if a not in audit['original_results_tables']]
 audit['primary_source_recheck']='Kira 3, arXiv:2505.20197, sections 3.1, 3.6 and 4.2: seed truncation, supplied master check, and 128-bit ordering labels.'
 write(f,audit)
 for name in ['README.md','ML_model_adaptive_reduction/README.md']:
  f=ROOT/name;t=f.read_text();prefix='''<!-- BEGIN PREPARATION COST MODEL -->
`ML_model_adaptive_reduction/general_policy/preparation/` contains the attempt-time and failure model.
Its controls separate learned choices from basis reuse and smaller exact checks.
`general_policy/recovery/` records fresh tests of recovery from an incomplete stored basis.
Use `general_policy/s20_prepare_resilient.py` for that revised preparation application.
Read the folder guides for complete-time results, failures, and supported inputs.
<!-- END PREPARATION COST MODEL -->

'''
  if '<!-- BEGIN PREPARATION COST MODEL -->' not in t:f.write_text(prefix+t)
 print('PREPARATION GUIDES COMPLETE',flush=True)

if __name__=='__main__':main()
