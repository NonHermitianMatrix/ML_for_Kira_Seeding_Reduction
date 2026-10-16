"""Maintain short folder guides and the current application links."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def block(p,title,text,marker='ADAPTIVE REDUCTION'):
    a='<!-- BEGIN '+marker+' -->';b='<!-- END '+marker+' -->'
    s=p.read_text() if p.exists() else '';new=a+'\n\n## '+title+'\n\n'+text.strip()+'\n\n'+b+'\n'
    if a in s:
        lo=s.index(a);hi=s.index(b,lo)+len(b);s=s[:lo]+new.rstrip()+s[hi:]
    else:s=s.rstrip()+'\n\n'+new
    p.write_text(s)
def main():
    guide=HERE/'README.md';s=guide.read_text()
    s=s.replace('This folder contains one model that selects a complete reduction calculation.','This folder contains models for a policy that selects a complete reduction calculation.')
    s=s.replace('The model predicts total time from the integral family and target indices.','The models predict relative calculation cost from the integral family and target indices.')
    s=s.replace('Its training labels include failed attempts and the time needed to recover.','Their training labels include failed attempts and the time needed to recover.')
    s=s.replace('Run one project science job at a time.','After preparation, the graph-control and preprocessing comparisons can run as two independent jobs.\nEach job reserves one core and 8 GB of memory. Other stages run in sequence.')
    s=s.replace('The production study reserves one slot with 8 GB of memory.','Each production job reserves one slot with 8 GB of memory.\nThe two independent comparison jobs reserve at most 16 GB together.')
    if 'The two comparison jobs use at most 64 MiB' not in s:
        s=s.replace('Each attempt uses at most 32 MiB of temporary files.','Each attempt uses at most 32 MiB of temporary files.\nThe two comparison jobs use at most 64 MiB together.')
    if 'A registered condition can add' not in s:
        s=s.replace('Profile 304 supplies test data.','Profile 304 supplies test data.\nA registered condition can add a fresh four-loop confirmation at profile 305.\nRead `conditional_reference_protocol.json` for its trigger and seed limits.\nThe original failed check remains in the results.')
    s=s.replace('6. Run `s07_report.py` to update the paper, notes, and folder guides.','6. Run `s07_report.py` to update the paper and notes.\n7. Run `s10_document.py` to update the folder guides.')
    s=s.replace('7. Build both PDFs with the report Makefile and run the report checks.','8. Build both PDFs with the report Makefile and run the report checks.')
    guide.write_text(s)
    block(guide,'Build requirements and final checks','''Use the source and dependency versions from the existing Kira build in `.tools/kira-build/`.
The builder reads its compiler commands from `compile_commands.json`.
It also reads the restricted-sector source and link command from `Kira_comparison/higher_scattering/`.
That build uses the earlier equation-filter and temporary-data changes.
The parent folder guides give their build order and dependency setup.
Run `s00_build.py` only after these parent builds exist.
`integration/build.json` records the exact compiler and linker inputs used in this study.
The new executable has a separate path, so earlier results retain their original binaries.

Training requires NumPy and scikit-learn in the existing seed-model environment.
Exact checks require SymPy. Figure generation requires Matplotlib.
The application evaluates the saved tree arrays directly.
It still uses the common Python reduction driver and its dependencies.

`s11_finalize.py` runs both study audits, writes both documents, updates the guides, and builds both PDFs.
It then runs `report/s01_check_paper.py` and writes `validation.json`.
This script does not publish files or change model weights.
`study_final.log`, `prepare.log`, `graph.log`, `integration.log`, and `finalize.log` record the scheduled stages.
`job_plan.json` records their dependencies and resource allocations.
For `s09_integration_check.py`, `ADAPTIVE_CHECK_STAGE=prepare` freezes predictors and completes any conditional reference.
It writes `prepared_checks.json` before the independent comparisons can start.
`ADAPTIVE_CHECK_STAGE=graph` runs the graph-specific controls.
`ADAPTIVE_CHECK_STAGE=integration` runs the public applications and exact-preprocessing comparison.
These two stages write separate folders and can run in parallel after preparation succeeds.
Run final checks only after both stages succeed.
Without this variable, `s09_integration_check.py` runs all three stages in sequence.
Interrupted development logs remain separate from completed measurements.
`resource_plan.json` records memory and storage allowances.
`conditional_reference_protocol.json` records the conditional four-loop check before model fitting.
`followup_cases.json` exists only when that condition is used.
`s12_graph_policy.py` selects a fixed setting for each graph from validation data.
It also fits three local regression trees for each graph with at least four training cases.
The local tree depths are one, two, and three. Each leaf needs at least two training cases.
The local trees add the largest individual propagator power and the mean number of dotted propagators to the 18 global inputs.
Validation compares the local trees with the global model and selects a prediction gate.
It permits predictions only when they save at least two percent in validation and win both repetitions.
`graph_control_protocol.json` records this rule before any reserved timing comparison.
`trained_model/graph_candidates.json` stores the local fitted trees and their training case identifiers.
`trained_model/graph_gate.json` stores the selected settings and guard decisions.
The public application uses this guard when it is present.
Repeated calls keep the model objects in memory and reload them when their files change.
Source and executable checks reuse their results while the file identity, size, and modification time remain unchanged.
Each reduction still starts a fresh Kira process and recomputes its coefficients.
`s09_integration_check.py` runs its matched comparisons before the application and preparation checks.
No failed or unfinished reference receives a speedup estimate.''','ADAPTIVE REDUCTION BUILD')
    purposes={
      'integration':'Source patches and build commands for exact file indexing and the projected zero-sector criterion. The full Kira source and earlier binaries remain unchanged.',
      'development':'Exact parity checks against earlier references. The seven-action list was set before global fitting and validation. The graph-control procedure was recorded before reserved timings. Completed compatible training records were retained.',
      'development_initial':'Partial development build with indexing before triangular reduction only. The interrupted four-loop attempt has no completed timing result.',
      'development_index_only':'Development build with file indexing in both triangular reduction and back-substitution. It does not project the zero-sector criterion.',
      'training':'Measured complete costs for the training cases. Each label includes failed attempts, recovery, and exact coefficient comparison.',
      'validation':'Separate complete-cost measurements used to select the model, decision gate, and fixed control. These records do not belong to the reserved test.',
      'references':'Expanded native reductions. Reserved cases also have an enlarged-seed coefficient check. Failed references remain part of the evidence.',
      'trained_model':'Global and graph-specific candidate models, the selected global model, and the validated deployment policy. JSON files contain tree splits and leaf cost predictions. They contain no executable serialized objects.',
      'model_test':'Reserved timing comparisons with frozen weights. Each method has three repetitions. Application records withhold target coefficients until reduction finishes.',
      'application_test':'Checks of s08_reduce.py using a prescribed basis without target coefficients. Exact reference comparisons follow execution.',
      'integration_test':'Matched timings with exact preprocessing changes enabled in sequence. A fourth method applies the validated policy. All settings use the same targets and basis.'}
    purposes['graph_control_test']='Matched tests of the best fixed setting per graph, the cost model, and the validated policy. The guard and fixed settings use validation data only. Each method has three repetitions.'
    for name,purpose in purposes.items():
        p=HERE/name
        if not p.exists():continue
        (p/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+purpose+'\n\nRead the [main guide](../README.md) for inputs, outputs, scripts, and resource limits.\nUse the documented producer scripts to reproduce these files.\nCompressed JSON records use seconds for time and bytes for storage and memory.\nKeep completed records unchanged.\n')
    text='''The current redesign uses [one complete-cost policy](ML_model_adaptive_reduction/README.md).
It selects a seed region, integral ordering, or equation filter before Kira starts the reduction.
Training includes failed attempts and recovery costs.
The original seed, row, and equation models remain available as earlier experiments.
The new tests separate exact preprocessing changes from the learned decision.
Read `ML_model_adaptive_reduction/summary.json` for the current checked results.'''
    block(ROOT/'README.md','Current adaptive reduction',text)
    # Keep the current interface visible before the earlier experiment catalog.
    p=ROOT/'README.md';s=p.read_text();a='<!-- BEGIN ADAPTIVE REDUCTION -->';b='<!-- END ADAPTIVE REDUCTION -->'
    lo=s.index(a);hi=s.index(b,lo)+len(b);current=s[lo:hi];s=(s[:lo]+s[hi:]).strip()
    first,rest=s.split('\n',1);p.write_text(first+'\n\n'+current+'\n\n'+rest.lstrip()+'\n')
    for name in ['ML_model_seed_selection','ML_model_reduction','ML_model_equation_selection','ML_model_workflow_selection']:
        block(ROOT/name/'README.md','Current complete-cost policy',text.replace('(ML_model_adaptive_reduction/','(../ML_model_adaptive_reduction/'))
    block(ROOT/'Kira_comparison/README.md','Current complete-cost comparison','''The [adaptive reduction study](../ML_model_adaptive_reduction/README.md) trains one new policy on complete native costs.
It retains exact coefficient checks and compares the learned choice with native and fixed controls.
The earlier component comparison is preserved in `higher_scattering/`.
Its remaining repetitions were paused for this redesign.''')
    block(ROOT/'report/README.md','Adaptive policy and exact preprocessing','''`adaptive_results.tex` reports the new model and its complete-cost tests.
`adaptive_appendix.tex` defines its inputs, training objective, and recovery rule.
It also derives the exact zero-sector projection.
`adaptive_reduction_data.json` contains the checked compact results.
`higher_scattering_results.tex` records the earlier component controls and bounded scattering attempts.
Both the paper and notes include these additions.
The archived notes can still be reconstructed exactly by removing their marked current-update blocks.
Run the new study's `s06_analyze.py` and `s07_report.py` before rebuilding both PDFs.
Then run `report/s01_check_paper.py`.
The current study changes the implementation, model, measurements, and report.
The earlier editorial audit remains a historical record.''')
    p=ROOT/'report/README.md';s=p.read_text()
    note='The workflow appendix now states sunrise masses `(3,7,13)` and vacuum masses `(1,1,1,13,13,53+2h)`.\nThese values match the stored workflow and specialist case definitions.\nThis correction changes the description only; the saved calculations and timings remain unchanged.\n'
    if 'The workflow appendix now states sunrise masses' not in s:p.write_text(s+'\n'+note)
    block(ROOT/'report/paper_figures/README.md','Adaptive reduction figures','''`adaptive_reduction.pdf` compares learned time with native and fixed controls after the same exact improvements.
It divides sums of batch median times within each graph structure.
`adaptive_integration.pdf` separates file indexing, zero-sector projection, and the validated policy.
`adaptive_graph_controls.pdf` compares predictions and the validated policy with the best fixed setting for each graph.
Both figures use matched three-run medians.
Only `adaptive_integration.pdf` uses a logarithmic time axis. The control figure uses linear time ratios.
The producer is `ML_model_adaptive_reduction/s06_analyze.py`.
The figure data are in `report/adaptive_reduction_data.json`.''')
    if (HERE/'summary.json').exists():
        d=json.loads((HERE/'summary.json').read_text())
        block(HERE/'README.md','Checked results',f'''The selected model is `{d['model']}` with {d['trees']} tree(s).
It uses {d['training_cases']} training cases and {d['validation_cases']} validation cases.
The reserved test completes {d['test_cases']} batches and {d['workflows']} timed workflows.
All completed outputs pass exact coefficient comparisons.
The sums of batch median times are {d['totals']['native']:.6f} seconds for native choices, {d['totals']['fixed']:.6f} seconds for the fixed control, and {d['totals']['learned']:.6f} seconds for the learned policy.
The learned/native ratio is {d['learned_to_native']:.6f}.
The learned/fixed ratio is {d['learned_to_fixed']:.6f}.
The public interface passes {len(d['public_applications'])} additional batch checks.
The stronger graph-specific comparison contains {d['graph_controls']['workflows']} exact reductions.
Its validated-policy/fixed ratio is {d['graph_controls']['guarded_to_fixed']:.6f}.
The validated policy enables predictions in {len(d['graph_controls']['enabled_graphs'])} graph structures.
Read the summary for individual graphs, unsuccessful references, and exact preprocessing comparisons.''')
    print(json.dumps(dict(documented=True,folders=sum((HERE/n).exists() for n in purposes))),flush=True)
if __name__=='__main__':main()
