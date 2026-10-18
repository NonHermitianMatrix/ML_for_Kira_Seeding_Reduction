"""Validate frozen hybrid evidence, maintain guides, and build the paper and notes."""
from s00_cost_common import *
import subprocess,ast,struct

def guides(s):
 f=READ(HERE/'trained_model/freeze.json')
 text='''# Integrated sparse-seed expert

This application combines exact block formulas, native seed settings, and a trained sparse-seed expert.
The expert supports one target in the stated massless nonplanar two-loop family, with numerator ranks two through four.
Other requests use the preceding fixed setting within its training ranges. They use original native bounds outside those ranges. Exact formulas run before model prediction.
Every native result keeps the master-basis check and bounded recovery.

## Use

Run the application in a scheduled Hoffman job from the repository root:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/hybrid_experts/s01_runtime.py --case CASE.json --output ML_model_adaptive_reduction/hybrid_experts/requests/RESULT.json.gz --method learned
```

The case contains definition, targets, size, split, and topology_group fields.
The output contains factored master expansions, decisions, native attempts, checks, and elapsed time.
No coefficient result is reused between separate requests.
The supplied basis cache contains master indices. It contains no reduction coefficients.

Use `fixed` for the best validation-selected ML-free route.
Use `base` for the preceding fixed basis-compatible setting.
Use `raw_native` for original native seed bounds.
Use `sparse_fixed` or `sparse_learned` to measure an expert action inside its domain.
Unsupported expert inputs return to the base route.
The test label `previous` runs the actual refined_time_policy application in a fresh process.

## Training and code order

1. s00_cost_common.py defines limits, exact routes, features, the supported family, and the saved inner forest reader.
2. s01_runtime.py integrates the sparse seed list with native Kira and handles exact recovery.
3. s02_collect.py defines the disjoint physical profiles and records four complete action costs.
4. s03_train.py fits the outer cost model and selects its deployment rules from validation only.
5. s04_job.sh starts one scheduled worker with bounded memory and time.
6. s05_test.py freezes all tested sources and measures reserved requests with three rotated repetitions.
7. s06_analyze.py computes complete-time ratios, repetition variation, failures, coverage, and the plot.
8. s07_document.py writes the current method, results, derivations, and notes from measured evidence.
9. s08_validate.py checks the evidence, model conversion, source freeze, guides, and both documents.

Submit `s04_job.sh s02_collect.py pilot` first. The pilot uses one training input. Its diagnostic timings do not enter training.
It checks exact coefficients for every action and observes Kira's native seed gate.
After the pilot passes, submit collection workers with arguments 0 and 1.
Then submit s03_train.py, followed by two s05_test.py workers with arguments 0 and 1.
Run s08_validate.py after both test receipts exist.
jobs.json records the actual dependency chain. Existing measurements remain in place.
Never change a frozen decision source or model during reserved tests.

The inner expert retains the earlier cost_geometry model and its original training history.
The outer selector learns from 16 fresh training requests and 8 validation requests.
Its labels include inner prediction, seed enumeration, exact algebra, checks, and recovery.
One training repetition and two validation repetitions measure each action.
The outer selector must improve on the best constant route by at least 1.5 percent.
The combined method must also improve on the best ML-free candidate by at least 1.5 percent.
A constant choice of a learned expert still invokes that expert's target-dependent prediction.
Unverified training outcomes receive max(220 seconds, elapsed time). Reported times never substitute this penalty.

## Data

protocol.json defines training and validation. test_protocol.json freezes sources, models, and reserved requests.
trained_model/expert.json preserves the earlier trained sparse forest.
trained_model/freeze.json contains the outer policy and deployment decision.
trained_model/fixed.json contains the ML-free control; sparse_fixed.json gives the inner fixed boundary.
training/ and validation/ contain action costs. references/ holds independent exact comparisons.
model_test/ retains each reserved attempt. coverage/ retains every requested outcome.
claims/ prevents duplicate work. requests/ holds temporary inputs and outputs.
summary.json and validation.json connect the results to the documents.

Each timed record stores complete_process_and_check_seconds for the process, cleanup, and independent exact check.
application_seconds measures the process and cleanup before that check.
independently_verified records agreement with the separate reference. coefficient_checks counts compared coefficients.
blocks stores each component reduction. attempts stores every native call and its result.
model_used records whether the outer tree or inner expert made a prediction.
The stored first action can differ from the final successful action after recovery.
Logs remain on Hoffman; structured measurements and a log-folder guide are published.

## Resources and dependencies

Run at most two native workers. Each job reserves one core and 8 GiB.
Each native call has a 45-second limit, 6 GiB address limit, 5200 MiB process-tree RSS guard, and 32 MiB scratch cap.
Each sparse seed input is limited to 4 MiB. The pilot audit has an 8 MiB per-file limit.
Production measurements disable that diagnostic audit. Each request has a 110-second reduction budget and 125-second process limit.
The persistent study cap is 8 MiB. Two workers share a separate 16 MiB application-output reserve.
Inputs are limited to 256 KiB and compressed outputs to 3 MiB. The allocation counter reserves 2 MiB for guides and logs.
The counter and lock are local state and are not published. A fresh copy creates its own counter.
resource_plan.json bounds the combined project, temporary work, and publication below 10 GB.

Use the existing scientific Python environment, bounded Kira executable, Fermat, and report build tools.
NumPy and Matplotlib are needed for fitting and plots. SymPy supplies exact checks.
The runtime evaluates exported trees without importing the training library.
Scientific data and weights stay on Hoffman and GitHub. The report and notes also have a local copy.

## Results and limits

'''
 text+=f"The reserved test requests {s['requested']} calculations and verifies {s['totals']['learned']['verified_requests']} in all three repetitions.\n"
 text+=f"The integrated method invokes learned prediction on {s['totals']['learned']['model_requests']} requests.\n"
 if f['outer_enabled'] and f['selection']['name']=='d2_n4_t1_a0_m0.0':
  text+='The selected tree uses the first auxiliary numerator power u and total numerator rank R.\n'
  text+='For u <= 2 and R <= 3, it uses the learned sparse boundary.\n'
  text+='For u <= 2 and R = 4, it uses the fixed sparse boundary.\n'
  text+='For u >= 3, it uses the preceding basis-compatible setting.\n'
  text+='These rules apply only inside the declared expert domain.\n'
 for group in ['all','expert_domain','new_patterns']:
  for control in ['native','fixed','previous']:
   v=s['comparisons'][group][control]
   if v['cases']:text+=f"For {group}, the integrated/{control} ratio is {v['ratio']:.6f} on {v['cases']} matched exact completions.\n"
 text+='''
Read summary.json for first-pass costs, every failure, all-attempt totals, and repetition intervals.
The native comparison uses the same bounded modified executable and native choices.
Master-basis preparation, independent reference preparation, and training are separate prior costs.
This test does not establish a speedup for arbitrary families or general high-loop scattering.
The earlier broader test remains in refined_time_policy/. Its unfinished ladder remains recorded.
The original seven-candidate study remains in total_time_policy/.
Do not multiply speedups from these different workloads.
'''
 (HERE/'README.md').write_text(text)
 descriptions={'training':'Complete action costs for fitting the outer policy.','validation':'Separate complete costs for selecting the deployment rules.','trained_model':'Frozen expert weights, outer policy, and ML-free controls.','model_test':'Reserved full application attempts and exact coefficient checks.','references':'Independent coefficients used only for verification.','coverage':'Requested outcomes, including incomplete attempts.','claims':'Exclusive worker claims. Do not remove an active claim.','requests':'Temporary requests and results. Completed workers remove their files.','logs':'Scheduler logs remain on Hoffman. Structured measurements are published in the study folders.'}
 for p in [q for q in HERE.rglob('*') if q.is_dir() and '__pycache__' not in q.parts]:
  branch=p.relative_to(HERE).parts[0];(p/'README.md').write_text(descriptions.get(branch,'Supporting study records.')+'\n\nRead the parent README for commands, data fields, dependencies, and limits.\nKeep scientific data on Hoffman and GitHub.\n')
 for p in [ROOT/'README.md',ROOT/'ML_model_adaptive_reduction/README.md',ROOT/'report/README.md']:
  t=p.read_text();start='<!-- BEGIN COMPLETE TIME SELECTION -->';end='<!-- END COMPLETE TIME SELECTION -->'
  if start in t:t=t[:t.index(start)]+t[t.index(end)+len(end):]
  block=start+'\nThe current combined application is ML_model_adaptive_reduction/hybrid_experts/s01_runtime.py.\nRead its README for exact routes, the sparse expert, complete-time controls, and measured limits.\nThe preceding broad comparison remains in refined_time_policy/.\nThe current paper and detailed notes retain all three new comparisons.\n'+end
  t=t.replace('Use `../ML_model_adaptive_reduction/refined_time_policy/s08_validate.py` for the current paper and notes.','Use `../ML_model_adaptive_reduction/hybrid_experts/s08_validate.py` for the current paper and notes.')
  p.write_text(block+'\n\n'+t.lstrip())
 p=BASE/'README.md';t=p.read_text()
 if '## Integrated sparse expert' not in t:t+='\n## Integrated sparse expert\n\nThe later combined application is in ../hybrid_experts/.\nIt tests a sparse-seed expert on fresh higher-rank nonplanar targets and retains this application for other requests.\nThis folder preserves its frozen broad comparison. Its PDF checks precede the later document update.\nUse ../hybrid_experts/validation.json for the current PDF checks.\n'
 p.write_text(t)
 p=ROOT/'ML_model_adaptive_reduction/total_time_policy/README.md';t=p.read_text()
 t=t.replace('Use ../refined_time_policy/ for the current application and its fresh comparison.','Use ../hybrid_experts/ for the current application and its fresh comparison.\nThe intermediate broad comparison remains in ../refined_time_policy/.')
 t=t.replace('Use ../refined_time_policy/validation.json to check the current PDFs.','Use ../hybrid_experts/validation.json to check the current PDFs.')
 p.write_text(t)
 p=ROOT/'report/README.md';t=p.read_text()
 if '## Integrated expert report' not in t:t+='\n## Integrated expert report\n\nhybrid_expert_results.tex gives the combined method and direct comparisons.\nhybrid_baseline_summary.tex summarizes the preceding broad baseline in the main paper.\nhybrid_expert_appendix.tex defines fresh targets, candidate boundaries, and deployment rules.\nThe notes use matching copies with references to the historical derivations.\nhybrid_expert_data.json and hybrid_expert_validation.json contain the compact evidence and current PDF checks.\n'
 p.write_text(t)
 p=ROOT/'report/paper_figures/README.md';t=p.read_text()
 if '`hybrid_expert_selection.pdf`' not in t:t+='\n`hybrid_expert_selection.pdf` compares the integrated method with native, ML-free, and preceding choices.\nIt separates all matched completions, the expert domain, and new index patterns, and shows first-pass time with verified coverage.\n'
 p.write_text(t)

def main():
 inputs.module('hybrid_analysis',HERE/'s06_analyze.py').main()
 s=READ(HERE/'summary.json');p=READ(HERE/'test_protocol.json');train=READ(HERE/'protocol.json')
 assert sha(HERE/'trained_model/freeze.json')==p['model_sha256']
 assert sha(ROOT/'.tools/kira-sector-wide/kira')==p['binary_sha256']
 assert sha(HERE/'trained_model/expert.json')==p['expert_sha256']
 assert sha(BLOCK/'extension/basis_cache.json')==p['basis_sha256']
 assert all(sha(HERE/n)==h for n,h in p['sources'].items())
 assert all(sha(BASE/n)==h for n,h in p['previous_sources'].items())
 assert all(sha(SPARSE/n)==h for n,h in p['expert_sources'].items())
 assert READ(HERE/'pilot_validation.json')['complete']
 sets=[{c['id'] for c in train[phase]} for phase in ['training','validation']]+[{c['id'] for c in p['cases']}]
 assert all(not sets[i]&sets[j] for i in range(3) for j in range(i))
 trained_vectors={tuple(c['targets'][0]) for phase in ['training','validation'] for c in train[phase]}
 novel=[c for c in p['cases'] if '_unseen_' in c['id']];assert len(novel)==8
 assert all(tuple(c['targets'][0]) not in trained_vectors for c in novel)
 for group in s['comparisons'].values():
  for m,v in group.items():
   if v['cases']:
    assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    assert all(r['complete']['learned'] and r['complete'][m] for r in s['rows'] if r['case'] in v['case_ids'])
 # Compare the ported expert against its original pure feature and tree functions.
 source=ast.parse((SPARSE/'s05_reduce.py').read_text());nodes=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['feature','predict']]
 namespace=dict(inputs=inputs,struct=struct);exec(compile(ast.Module(body=nodes,type_ignores=[]),'original_sparse_predictor','exec'),namespace)
 expert=READ(HERE/'trained_model/expert.json')
 for c in train['training']+train['validation']:
  assert eligible(c) and expert_feature(c)==namespace['feature'](c)
  theta,scores=expert_theta(c);old=namespace['predict'](expert['model'],namespace['feature'](c));assert max(abs(a-b) for a,b in zip(scores,old))<1e-12
 import numpy as np
 model=inputs.module('hybrid_model_fixture',HERE/'s03_train.py');x=np.array([[0.],[0.],[1.],[1.]]);cost=np.array([[1.,8.],[1.,8.],[8.,1.],[8.,1.]])
 tree=model.fit_tree(x,cost,np.arange(4),1,2,np.random.RandomState(0));assert np.argmin(model.leaf(tree,[0.])['cost'])==0 and np.argmin(model.leaf(tree,[1.])['cost'])==1
 inputs.module('hybrid_document',HERE/'s07_document.py').main();guides(s)
 report=ROOT/'report';checker=report/'s01_check_paper.py';t=checker.read_text();marker='    result=dict(general_model_test_complete=True'
 if 'hybrid_expert=json.loads' not in t:
  addition="""    hybrid_expert=json.loads((HERE/'hybrid_expert_data.json').read_text())
    assert hybrid_expert['complete'] and hybrid_expert['requested']==len(hybrid_expert['rows'])==34
    assert 'sec:hybrid-experts' in labels and 'app:hybrid-experts' in labels
    for group in hybrid_expert['comparisons'].values():
        for v in group.values():
            if v['cases']:assert abs(v['ratio']-v['learned_seconds']/v['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/hybrid_experts/summary.json'
    if p.exists():assert json.loads(p.read_text())==hybrid_expert
"""
  assert marker in t;t=t.replace(marker,addition+marker);checker.write_text(t)
 subprocess.run(['make','-C',str(report),'all'],check=True,timeout=600)
 subprocess.run([sys.executable,str(checker)],check=True,timeout=180)
 allocated=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file());assert allocated<CAP
 v=dict(complete=True,all_matched_results_exact=True,expert_prediction_conversion_checked=True,summary_sha256=sha(HERE/'summary.json'),model_sha256=sha(HERE/'trained_model/freeze.json'),protocol_sha256=sha(HERE/'test_protocol.json'),source_sha256={p.name:sha(p) for p in HERE.glob('s*.py')},pdf_sha256={n:sha(report/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=allocated)
 write(HERE/'validation.json',v);(report/'hybrid_expert_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)

if __name__=='__main__':main()
