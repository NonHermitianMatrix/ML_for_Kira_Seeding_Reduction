"""Validate the completed study, update guides, and render both documents."""
import json,subprocess,sys,importlib.util
from pathlib import Path
audit_spec=importlib.util.spec_from_file_location('ordering_audit',Path(__file__).with_name('s11_validate.py'))
audit=importlib.util.module_from_spec(audit_spec);audit_spec.loader.exec_module(audit)
spec=importlib.util.spec_from_file_location('ordering_paper',Path(__file__).with_name('s12_write_report.py'))
paper=importlib.util.module_from_spec(spec);spec.loader.exec_module(paper)
w=audit.w
def append(path,heading,text):
 s=path.read_text()
 if heading not in s:path.write_text(s.rstrip()+'\n\n'+heading+'\n\n'+text.rstrip()+'\n')
def main():
 audit.main();paper.main()
 summary=json.loads((w.HERE/'model_test/summary.json').read_text());a=summary['aggregate']
 def change(key):
  r=a[key]['ratio'];return f"{100*abs(1-r):.1f} percent "+('less' if r<1 else 'more')
 append(w.HERE/'README.md','## Completed comparison',f"All 720 timed reductions and 43 further applications pass exact checks. The selected method gives {change('selected_to_previous')} full time than the preceding method and {change('selected_to_native')} than native choices. These are geometric means with equal graph weights. See `model_test/summary.json` and the paper for each graph, all regressions, timings, and limits. The test covers known graphs and target patterns with new parameter profiles.")
 append(w.ROOT/'README.md','## Ordering comparison',
  'The [ordering comparison](ML_model_workflow_selection/ordering_policy/README.md) does not improve the preceding route. Keep the preceding route as the default. '
  f"The reserved test gives {change('selected_to_previous')} complete reduction time than the preceding route and {change('selected_to_native')} than native choices in the same test. "
  'It contains 720 timing trials and 43 further applications. All pass exact checks. The study uses seven known graphs at one through three loops, new rational parameter profiles, and symbolic dimension. The caller and model are loaded before timing. The report gives per-graph results and descriptive intervals. These gains are not multiplied by earlier results.')
 append(w.ROOT/'ML_model_workflow_selection/README.md','## Ordering comparison',
  'The [ordering study](ordering_policy/README.md) selects native integral ordering and propagator permutation before equation generation. Its public entry point is `ordering_policy/s07_reduce.py`. It uses the previous frozen route when a new strategy fails or the input is outside its trained domain. The earlier routes remain available for comparison. The new comparison includes complete reduction and exact checks.')
 append(w.ROOT/'report/README.md','## Ordering comparison',
  '`ordering_policy_results.tex` gives the new methods and measured results. `ordering_policy_appendix.tex` defines the inputs, candidates, relabelling invariance, model selection, and comparison. `ordering_policy_figure_data.json` contains the compact plot and table values. `ordering_policy_validation.json` records the completed evidence checks. The [study guide](../ML_model_workflow_selection/ordering_policy/README.md) explains all code and data. `s01_check_paper.py` also checks the new summaries against their scientific sources on Hoffman.')
 append(w.ROOT/'report/notes_README.md','## Ordering comparison',
  'The current-update blocks also include the new ordering results and derivation. The preservation check still reconstructs the original notes and verifies all 91 earlier supporting files.')
 append(w.ROOT/'report/paper_figures/README.md','## Ordering comparison',
  '`ordering_policy.pdf` compares the new route with the previous route and native choices. Ratios below one mean less time. Bars show the range over two reserved parameter profiles. The study script `../../ML_model_workflow_selection/ordering_policy/s08_analyze.py` makes the plot from checked full-time records. The axes use the observed ratio ranges and include equal time at one.')
 subprocess.run(['make','-C','report'],cwd=w.ROOT,check=True,timeout=480)
 subprocess.run([sys.executable,'report/s01_check_paper.py'],cwd=w.ROOT,check=True,timeout=180)
 w.emit(stage='documents_complete')
if __name__=='__main__':main()
