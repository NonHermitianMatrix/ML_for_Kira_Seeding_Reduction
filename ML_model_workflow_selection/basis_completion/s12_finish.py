"""Validate the completed study, update guides, and render both documents."""
import json,subprocess,sys
import s11_validate as audit
import s10_write_report as paper
w=audit.w
def append(path,heading,text):
 s=path.read_text()
 if heading not in s:path.write_text(s.rstrip()+'\n\n'+heading+'\n\n'+text.rstrip()+'\n')
def main():
 audit.main();paper.main()
 summary=json.loads((w.HERE/'model_test/summary.json').read_text());a=summary['aggregate']
 def change(key):
  r=a[key]['ratio'];return f"{100*abs(1-r):.1f} percent "+('less' if r<1 else 'more')
 append(w.ROOT/'README.md','## Selective seed expansion',
  'Use [the selective-seeding route](ML_model_workflow_selection/basis_completion/README.md) for the latest checked application on the stated target domain. '
  f"The reserved test gives {change('selected_to_previous')} complete reduction time than the preceding route and {change('selected_to_native')} than native choices in the same test. "
  'It contains 720 timing trials and 43 further applications. All pass exact checks. The study uses seven known graphs at one through three loops, new rational parameter profiles, and symbolic dimension. The caller and model are loaded before timing. The report gives per-graph results and descriptive intervals. These gains are not multiplied by earlier results.')
 append(w.ROOT/'ML_model_workflow_selection/README.md','## Selective seed expansion',
  'The [basis-completion study](basis_completion/README.md) adds selective seed limits and tests exact conversion of a temporary basis. Its public entry point is `basis_completion/s07_reduce.py`. It uses the previous frozen route when a new strategy fails or the input is outside its trained domain. The earlier routes remain available for comparison. The new comparison includes complete reduction and exact checks.')
 append(w.ROOT/'report/README.md','## Selective seed expansion',
  '`basis_completion_results.tex` gives the new methods and measured results. `basis_completion_appendix.tex` defines the inputs, candidates, exact basis conversion, model selection, and comparison. `basis_completion_figure_data.json` contains the compact plot and table values. `basis_completion_validation.json` records the completed evidence checks. The [study guide](../ML_model_workflow_selection/basis_completion/README.md) explains all code and data. `s01_check_paper.py` also checks the new summaries against their scientific sources on Hoffman.')
 append(w.ROOT/'report/notes_README.md','## Selective seed expansion',
  'The current-update blocks also include the new seed-expansion results and derivation. The preservation check still reconstructs the original notes and verifies all 91 earlier supporting files.')
 append(w.ROOT/'report/paper_figures/README.md','## Selective seed expansion',
  '`basis_completion.pdf` compares the new route with the previous route and native choices. Ratios below one mean less time. Bars show the range over two reserved parameter profiles. The study script `../../ML_model_workflow_selection/basis_completion/s06_analyze.py` makes the plot from checked full-time records. The axes use the observed ratio ranges and include equal time at one.')
 subprocess.run(['make','-C','report'],cwd=w.ROOT,check=True,timeout=480)
 subprocess.run([sys.executable,'report/s01_check_paper.py'],cwd=w.ROOT,check=True,timeout=180)
 w.emit(stage='documents_complete')
if __name__=='__main__':main()
