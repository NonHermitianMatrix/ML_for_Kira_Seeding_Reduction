"""Validate the completed study, update guides, and render both documents."""
import json,subprocess,sys,importlib.util
from pathlib import Path
audit_spec=importlib.util.spec_from_file_location('thread_audit',Path(__file__).with_name('s11_validate.py'))
audit=importlib.util.module_from_spec(audit_spec);audit_spec.loader.exec_module(audit)
spec=importlib.util.spec_from_file_location('thread_paper',Path(__file__).with_name('s12_write_report.py'))
paper=importlib.util.module_from_spec(spec);spec.loader.exec_module(paper)
w=audit.w
def append(path,heading,text):
 s=path.read_text()
 if heading not in s:path.write_text(s.rstrip()+'\n\n'+heading+'\n\n'+text.rstrip()+'\n')
def main():
 spec=importlib.util.spec_from_file_location('persistent_worker_checks',Path(__file__).with_name('s16_worker_checks.py'));checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
 path=w.HERE/'model_test/worker_checks.json';valid=False
 if path.exists():
  previous=json.loads(path.read_text())
  valid=previous.get('complete') and previous.get('all_exact') and previous.get('allocated_cores')==2 and previous.get('source_sha256')==audit.model.sha(w.HERE/'s15_worker.py') and previous.get('checker_sha256')==audit.model.sha(w.HERE/'s16_worker_checks.py') and previous.get('freeze_sha256')==audit.model.sha(w.HERE/'trained_model/freeze.json')
 if not valid:checks.main()
 audit.main();paper.main()
 summary=json.loads((w.HERE/'model_test/summary.json').read_text());a=summary['aggregate']
 total={m:sum(c['median_seconds'][m] for c in summary['cases']) for m in ['previous','selected','native','family_fixed','previous_four']}
 workload=total['selected']/total['previous']
 measured_route=('Use this route for the tested workload when two cores are available.' if workload<1 else 'Keep the preceding one-worker route as the default because the new stage does not reduce summed workload time.')
 def change(key):
  r=a[key]['ratio'];return f"{100*abs(1-r):.1f} percent "+('less' if r<1 else 'more')
 append(w.HERE/'README.md','## Completed comparison',f"All 900 timed reductions and 50 further applications pass exact checks. The selected method gives {change('selected_to_previous')} full time than the preceding method and {change('selected_to_native')} than native choices. These are geometric means with equal graph weights. See `model_test/summary.json` and the paper for each graph, all regressions, timings, and limits. The test covers known graphs and target patterns with new parameter profiles.")
 append(w.ROOT/'README.md','## Worker-count comparison',
  'The [worker-count study](ML_model_workflow_selection/thread_policy/README.md) compares one, two, and four Kira workers in the same four-core allocation. '
  f"The reserved comparison gives {change('selected_to_previous')} graph-weighted complete time than the preceding route and {change('selected_to_native')} than native choices. "
  f"Summed batch medians change from {total['previous']:.2f} to {total['selected']:.2f} seconds. "
  'It includes 900 timed reductions and 50 additional applications. All pass exact checks. The report separates summed workload time, per-graph effects, and CPU cost. The earlier ordering study remains available and is not the default. '+measured_route)
 if workload<1:
  path=w.ROOT/'README.md';guide=path.read_text()
  marker='For the latest measured single-batch route'
  if marker not in guide:
   text=(marker+', use [worker-count selection](ML_model_workflow_selection/thread_policy/README.md).\n'
    'It retains the preceding learned seed strategy and chooses the Kira worker count once per batch.\n'
    'The measured scope is seven known graphs at one through three loops, with new rational parameter values.\n'
    f"Summed median time changes from {total['previous']:.2f} to {total['selected']:.2f} seconds in the reserved comparison.\n"
    'The retained frozen policy uses at most two Kira workers. Use the two-core application wrapper.\n'
    'Use [the preceding route](ML_model_workflow_selection/basis_completion/README.md) when one core is available.\n\n')
   guide=guide.replace('Read [the paper]',text+'Read [the paper]',1);path.write_text(guide)
 append(w.ROOT/'ML_model_workflow_selection/README.md','## Worker-count comparison',
  'The [worker-count study](thread_policy/README.md) chooses one, two, or four Kira workers before reduction. Its public entry point is `thread_policy/s07_reduce.py`. The experiment uses four slots for its controls. The retained policy needs at most two slots; use `thread_policy/s17_application.sh`. The previous learned seed strategy stays active. Unknown input structures use the previous one-worker route. This interface handles one application at a time because it scopes native settings for the duration of each application.')
 append(w.ROOT/'report/README.md','## Worker-count comparison',
  '`thread_policy_results.tex` gives the new methods and measured results. `thread_policy_appendix.tex` defines the inputs, candidates, worker-count invariance, model selection, and comparison. `thread_policy_figure_data.json` contains the compact plot and table values. `thread_policy_validation.json` records the completed evidence checks. The [study guide](../ML_model_workflow_selection/thread_policy/README.md) explains all code and data. `s01_check_paper.py` also checks the new summaries against their scientific sources on Hoffman.')
 append(w.ROOT/'report/notes_README.md','## Worker-count comparison',
  'The current-update blocks also include the new thread results and derivation. The preservation check still reconstructs the original notes and verifies all 91 earlier supporting files.')
 append(w.ROOT/'report/paper_figures/README.md','## Worker-count comparison',
  '`thread_policy.pdf` compares selected and fixed counts with the previous route. A second panel shows the always-four-worker control. Ratios below one mean less time. Bars show the range over two reserved parameter profiles. The study script `../../ML_model_workflow_selection/thread_policy/s08_analyze.py` makes the plot from checked full-time records. The axes use the observed ratio ranges and include equal time at one. The always-four-worker control separates the choice of worker count from extra-core effects.')
 subprocess.run(['make','-C','report'],cwd=w.ROOT,check=True,timeout=480)
 subprocess.run([sys.executable,'report/s01_check_paper.py'],cwd=w.ROOT,check=True,timeout=180)
 w.emit(stage='documents_complete')
if __name__=='__main__':main()
