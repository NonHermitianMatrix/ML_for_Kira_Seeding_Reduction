"""Write the worker-count method, measured costs, and exact checks into both documents."""
import json,math,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
NAMES={'sunrise':'Sunrise','double_box':'Planar box','vacuum3':'Vacuum','ladder3':'Ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box'}
def change(r):return f'{100*abs(1-r):.1f}\\% '+('less' if r<1 else 'more')+' time'
def main():
 d=json.loads((HERE/'model_test/summary.json').read_text());pub=json.loads((HERE/'model_test/public_checks.json').read_text())
 assert d['all_exact'] and pub['all_exact']
 methods=['native','previous','previous_four','family_fixed','selected']
 total={m:sum(c['median_seconds'][m] for c in d['cases']) for m in methods}
 cr=d['cpu_totals']['selected']/d['cpu_totals']['previous']
 pr=d['aggregate']['selected_to_previous']['ratio'];nr=d['aggregate']['selected_to_native']['ratio'];wr=total['selected']/total['previous'];fixed=total['selected']/total['family_fixed']
 enabled=[NAMES[k].lower() for k,v in d['policies'].items() if v['enabled']]
 rows=[]
 for k in NAMES:
  cs=[c for c in d['cases'] if c['topology']==k];times={m:sum(c['median_seconds'][m] for c in cs) for m in methods}
  policy=d['policies'][k];labels={'previous':'1 worker','threads2':'2 workers','threads4':'4 workers','tree1':'Tree depth 1','tree2':'Tree depth 2','tree3':'Tree depth 3','forest16':'Bagged trees','nearest1':'1 neighbour','nearest3':'3 neighbours','ridge0.1':'Ridge 0.1','ridge1.0':'Ridge 1','ridge10.0':'Ridge 10','constant':'Constant'}
  setting=policy['model'] if policy['enabled'] else policy['validation_control']
  rows.append(f"{NAMES[k]} & {labels[setting]} & {times['previous']:.3f} & {times['selected']:.3f} & {times['selected']/times['previous']:.3f}"+r'\\')
 text=r'''\section{Selecting the number of Kira workers}
\label{sec:thread-policy}
The preceding study found no further gain from changing integral order.
We therefore retain the preceding learned seed strategy and test whether
the number of Kira workers should depend on the requested integrals.
Kira supports parallel symbolic reduction~\cite{KiraOriginal}, but the
cost of extra workers can outweigh their benefit on small batches. Our
development measurements show this effect, while larger box batches can
use extra workers to finish sooner. A model can make this choice before
equation generation, using one prediction for the complete batch.

We compare one, two, and four workers in the same integrated executable.
The native control uses Kira's own seed and reduction choices with the
common earlier implementation changes. The model receives the nine target
features used in the preceding cost studies and predicts the full time
of each choice relative to one worker. We train ten predictor types per
graph on 36 batches, select policies on 18 validation batches, and reserve
36 further batches for testing. Validation minimizes the sum of batch
costs. A new predictor must save at least two percent against the faster
control and win in at least two of three validation repetitions.
Otherwise the control remains active. Appendix~\ref{app:thread-policy}
derives the labels, explains exactness, and defines the comparisons.

'''
 text+=f"Validation enables additional predictors for {len(enabled)} graph types"
 text+=(' ('+', '.join(enabled)+')' if enabled else '')+'. The other graph types retain the preceding one-worker strategy. Their measured time differences include run-to-run variation and the additional decision cost. '
 text+=f"Training and validation contain {sum(d['label_seconds'].values()):,.1f} seconds of reduction measurements. Fitting all seventy candidates takes {d['fitting_seconds']:.2f} seconds. These offline costs exclude reference construction and development and remain outside application time.\n\n"
 frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
 cuts=[n['feature'] for v in frozen['policies'].values() if v['enabled'] and v['model']['type']=='tree' for n in v['model']['nodes'] if n['feature']>=0]
 if cuts and set(cuts)=={0}:text+='Both selected trees split only on the number of targets in a batch. This feature separates the tested target patterns. Because those patterns repeat across the parameter splits, this result does not establish that target count alone selects a suitable worker count for new integral structures.\n\n'
 text+=f"All {d['workflows']} timed reductions and 50 further applications pass exact checks. The extra applications receive targets and their prescribed basis without reference coefficients. Seven use a persistent caller in a separate two-core allocation. It keeps the models loaded across consecutive requests while each native attempt starts a fresh Kira process. The retained trees choose at most two workers; the timing comparison reserves four cores to accommodate its four-worker control. For the 36 reserved batches, the sum of median full times is {total['previous']:.2f} seconds for the preceding one-worker method and {total['selected']:.2f} seconds for the selected method, giving {change(wr)}. The native one-worker control takes {total['native']:.2f} seconds, the always-four-worker control takes {total['previous_four']:.2f} seconds, and the fixed-per-graph control takes {total['family_fixed']:.2f} seconds. The selected route gives {change(fixed)} relative to the fixed-per-graph control.\n\n"
 text+=r'''\begin{table}[!htbp]
\centering\small
\caption{Worker-count selection on reserved batches. Times sum batch
medians within each graph, in seconds. The choice names an enabled model
or the validation-selected worker count. A ratio below one indicates
less complete time.}
\label{tab:thread-policy}
\begin{tabular}{@{}llrrr@{}}\toprule
Graph & Choice & Previous (s) & Selected (s) & Selected/previous\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}
'''
 def ratio(key):
  r=d['aggregate'][key];return f"${r['ratio']:.4f}$ with descriptive interval $[{r['interval'][0]:.4f},{r['interval'][1]:.4f}]$"
 text+=f"Giving each graph equal weight instead yields a selected-to-previous time ratio of {ratio('selected_to_previous')}, or {change(pr)}. The selected-to-native ratio is {ratio('selected_to_native')}, or {change(nr)}. These measures answer different questions: the summed time measures this workload, while the geometric ratio gives every graph equal weight.\n\n"
 text+=r'''\begin{figure}[!htbp]
\centering\includegraphics[width=\linewidth]{paper_figures/thread_policy.pdf}
\caption{The effect of selecting the worker count. Left: selected and fixed worker counts compared with the preceding
one-worker route. Right: always using four workers adds overhead on
many small cases. Each panel has its own horizontal scale.
Each point is the geometric mean of batch time ratios for one graph. Bars show the
range across two parameter profiles and are not significance intervals.}
\label{fig:thread-policy}
\end{figure}
\FloatBarrier
'''
 repeated=[x/y for x,y in zip(d['repetition_totals']['selected'],d['repetition_totals']['previous'])]
 pooled={m:sum(v) for m,v in d['repetition_totals'].items()}
 wins=sum(x<y for x,y in zip(d['repetition_totals']['selected'],d['repetition_totals']['previous']))
 text+=f"Across all five repetitions, the selected route consumes {pooled['selected']:.2f} seconds and the preceding route consumes {pooled['previous']:.2f} seconds, giving {change(pooled['selected']/pooled['previous'])}. The selected route has lower summed time in {wins} of five repetitions.\n\n"
 text+=f"The selected-to-previous summed time ratio ranges from ${min(repeated):.4f}$ to ${max(repeated):.4f}$ across the five complete repetitions. This range describes repeat variation and is not a confidence interval.\n\n"
 text+=f"The extra worker-count prediction takes a median of {1e6*d['worker_prediction_seconds']['median']:.1f} microseconds; this cost is included in full time. Across 180 reductions per method, the preceding, always-four-worker, and selected routes consume {d['cpu_totals']['previous']:.1f}, {d['cpu_totals']['previous_four']:.1f}, and {d['cpu_totals']['selected']:.1f} CPU-seconds, respectively. The selected route uses {100*(cr-1):.1f}\\% more CPU time. Every method has the same four-core allocation. These figures measure used CPU time and do not imply that fewer cores were reserved. The selected route makes {d['fallbacks'].get('selected',0)} fallback attempts.\n\n"
 slow=[]
 for k in NAMES:
  cs=[c for c in d['cases'] if c['topology']==k];r=sum(c['median_seconds']['selected'] for c in cs)/sum(c['median_seconds']['previous'] for c in cs)
  if r>1:slow.append(f"{NAMES[k].lower()} ({100*(r-1):.1f}\\%)")
 if slow:text+='Summed time increases for '+', '.join(slow)+'.\n\n'
 failed={m:sum(v.values()) for m,v in d['failed_attempts'].items()}
 if any(failed.values()):text+=f"The selected and always-four-worker routes contain {failed['selected']} and {failed['previous_four']} unsuccessful native attempts, respectively. Their subsequent retries succeed, and all attempt costs enter the reported full time. Some native attempts report allocation failures under the imposed per-process limits.\n\n"
 text+='The measurements include prediction, preparation, exact algebra, basis conversion, checks, retries, and cleanup. The caller and models are loaded before timing, and each attempt starts a new Kira process. The results cover seven known graph structures at one through three loops, known target patterns, and new rational kinematics with symbolic dimension. They measure the tested model and worker choices; they do not establish a globally fastest reduction or a gain for arbitrary integral families.\n'
 if wr>=1:text+='The worker-count stage does not improve the summed workload time, so the preceding one-worker route remains the retained method.\n'
 else:text+='The selected worker policy is available for this measured workload in a four-core allocation. The preceding one-worker route remains available for other resource limits and inputs.\n'
 (REPORT/'thread_policy_results.tex').write_text(text)
 (REPORT/'thread_policy_appendix.tex').write_text((HERE/'thread_policy_appendix.tex').read_text())
 for name in ['report.tex','notes.tex']:
  p=REPORT/name;s=p.read_text()
  if '\\input{thread_policy_results}' not in s:
   s=s.replace('\\input{ordering_policy_results}','\\input{ordering_policy_results}\n\\input{thread_policy_results}')
   s=s.replace('\\input{ordering_policy_appendix}','\\input{ordering_policy_appendix}\n\\input{thread_policy_appendix}')
  if name=='report.tex':
   abstract=r'''We study learned choices that reduce the time needed for exact Feynman integral reduction with Kira. The measurements include prediction, algebra, checks, and retries. Seed and equation selection save time on their stated inputs; learned row selection gives no reliable saving and is omitted. We train models to choose complete reduction strategies and seed limits for seven known graph structures at one through three loops. Additional ordering predictors give no accepted gain. In the final study, a policy chooses one, two, or four Kira workers. It gives '''+change(wr)+r''' in the sum of median full times than the preceding one-worker route and '''+change(total['selected']/total['native'])+r''' than native one-worker choices on the reserved workload. All methods receive four allocated cores. Giving each graph equal weight yields a time ratio of $'''+f'{pr:.4f}'+r'''$ against the preceding route. All 900 timed reductions and 50 further applications pass exact checks. Tests use new rational kinematics and symbolic dimension, with known graphs and target patterns. Separate tests give a 48.3\% saving from sharing compatible requests and a 543.8-fold saving from exact recurrences and reuse in a restricted vacuum family through twelve loops. These results use different inputs and controls and do not define a product of speedups.'''
   abstract=abstract.replace('All methods receive four allocated cores.',f'All methods receive four allocated cores, while the selected route uses at most two workers. Its measured CPU use is {100*(cr-1):.1f}\\% higher than the preceding route.')
   s=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+abstract+'\n'+m[2],s,flags=re.S)
   s=s.replace('We then test whether different integral orderings reduce that cost further.','We then test integral orderings and select the number of Kira workers from the requested targets.')
   if 'Selecting Kira workers & ' not in s:
    s=s.replace('Choosing Kira settings & ',f"Selecting Kira workers & Known graphs, new profiles, loops 1--3 & {change(wr)} than previous, sum of medians\\\\\nChoosing Kira settings & ")
  if name=='report.tex':
   s=s.replace('The final ordering study','The ordering study')
   s=re.sub(r'Choosing Kira settings & [^\n]+',lambda m:r'Choosing Kira settings & Known graphs, new profiles, loops 1--3 & No added gain over preceding route\\',s)
   conclusion=r"""\section{Conclusion}
Learned seed and equation selection reduce full time in their stated test
domains. We omit learned row selection because its complete-time tests
give no reliable saving. The later models select a complete reduction
strategy before equation generation, using measured cost and exact
fallback. This lets the model avoid expensive algebra before it starts.
The ordering comparison adds no accepted predictive gain, so it does
not replace the preceding seed strategy.

"""+f"The final worker-count study changes summed median time from {total['previous']:.2f} to {total['selected']:.2f} seconds on 36 reserved batches, giving {change(wr)} against the preceding one-worker route. Native one-worker choices take {total['native']:.2f} seconds. All methods receive four allocated cores, while the selected route uses at most two workers. CPU use rises by {100*(cr-1):.1f}\\%. The graph-weighted ratio to the preceding method is ${pr:.4f}$, and the comparison with fixed counts is reported separately. All 900 timed reductions and 50 further applications pass exact checks. The selector uses one decision per batch, while Kira retains exact algebra.\n\n"+r"""Sharing compatible requests gives a separate 48.3\% saving. Exact
recurrences and reuse give a 543.8-fold saving in the restricted vacuum
family through twelve loops. These comparisons use different inputs and
controls, so their speedups cannot be multiplied.

The final native tests cover seven known graph structures at one through
three loops. They retain the training target patterns and use new rational
kinematics with symbolic dimension. The report retains slower cases,
retry costs, and CPU use. These results establish the measured choices
within this domain. General high-loop scattering and globally optimal
reduction paths remain outside the demonstrated results.

\appendix"""
   s=re.sub(r'\\section\{Conclusion\}.*?\\appendix',lambda m:conclusion,s,flags=re.S)
  p.write_text(s)
 p=REPORT/'Makefile';s=p.read_text();s=s.replace('ordering_policy_appendix.tex paper_references.bib','ordering_policy_appendix.tex thread_policy_results.tex thread_policy_appendix.tex paper_references.bib');p.write_text(s)
 print(json.dumps(dict(report_written=True,workload_seconds=total,ratio_to_previous=wr,enabled=enabled)))
if __name__=='__main__':main()
