"""Write measured ordering results and their derivation into both documents."""
import json,math,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
NAMES={'sunrise':'Sunrise','double_box':'Planar box','vacuum3':'Vacuum','ladder3':'Ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box'}
def change(r):return f'{100*abs(1-r):.1f}\\% '+('less' if r<1 else 'more')+' time'
def main():
 d=json.loads((HERE/'model_test/summary.json').read_text());pub=json.loads((HERE/'model_test/public_checks.json').read_text())
 assert d['all_exact'] and pub['all_exact']
 def ratio(key):
  a=d['aggregate'][key];return f"${a['ratio']:.4f}$ (descriptive interval $[{a['interval'][0]:.4f},{a['interval'][1]:.4f}]$)"
 pr=d['aggregate']['selected_to_previous']['ratio'];nr=d['aggregate']['selected_to_native']['ratio'];fr=d['aggregate']['selected_to_fixed']['ratio']
 enabled=[k for k,v in d['policies'].items() if v['enabled']]
 totals={m:sum(c['median_seconds'][m] for c in d['cases']) for m in ['native','previous','family_fixed','selected']}
 rows=[]
 for k in NAMES:
  cs=[c for c in d['cases'] if c['topology']==k]
  times={m:math.exp(statistics.mean(math.log(c['median_seconds'][m]) for c in cs)) for m in ['previous','selected']}
  policy=d['policies'][k]
  labels={'tree1':'Tree depth 1','tree2':'Tree depth 2','tree3':'Tree depth 3','forest16':'Bagged trees','nearest1':'1 neighbour','nearest3':'3 neighbours','ridge0.1':'Ridge 0.1','ridge1.0':'Ridge 1','ridge10.0':'Ridge 10','constant':'Constant','previous':'Previous'}
  setting=policy['model'] if policy['enabled'] else policy['validation_control']
  choice=labels.get(setting,('$('+','.join(setting[1:].split('p'))+')$') if setting.startswith('o') else setting)
  rows.append(f"{NAMES[k]} & {choice} & {times['previous']:.3f} & {times['selected']:.3f} & {d['by_topology'][k]['selected_to_previous']:.3f} & {d['by_topology'][k]['selected_to_native']:.3f}"+r'\\')
 text=r'''\section{Choosing integral order before equation generation}
\label{sec:ordering-policy}
Selective seed limits reduce the number of equations, but the order in
which Kira treats their integrals can also change the remaining work.
Kira provides eight integral priority rules and four automatic propagator
ordering schemes~\cite{Kira12,Kira3}. We test whether a model can choose
between these settings from the requested target indices before Kira
generates equations. The earlier learned seed strategy stays active.
The new model makes one choice per target batch; Kira then carries out
the exact reduction with those settings. If the result does not reach
the prescribed basis, the calculation repeats the preceding route.
Appendix~\ref{app:ordering-policy} defines the choices and derives the
invariance under relabelling.

We compare eleven initial candidates on a separate development profile,
then test the pair of best nondefault orderings for each batch. We keep
the preceding route plus each batch winner with at least ten percent less
full time. Write $\omega$ for the integral-order number and $\chi$ for the propagator-scheme number. The retained settings are '''+', '.join(('the preceding route' if x=='previous' else '$ (\\omega,\\chi)=('+','.join(x[1:].split('p'))+') $') for x in d['configurations'])+r'''.
The preceding route retains its settings. We then fit ten models
per graph on 36 training batches, select policies on 18 validation
batches, and reserve 36 further batches. The nine target features,
complete-cost labels, predictor types, and validation gate are the same
as in the seed-expansion study. The final choice can be a fitted model
or a fixed setting, according to validation cost. A fixed setting still
uses the preceding learned seed policy, so the fixed comparison isolates
the additional selection procedure. This includes both validation-based
control choices and target-dependent predictions.

'''
 text+=f"Validation enables a new predictor for {len(enabled)} of seven graph types. The training and validation measurements contain {sum(d['label_seconds'].values()):,.1f} seconds of reductions, and fitting seventy predictors takes {d['fitting_seconds']:.2f} seconds. These offline costs exclude development and reference construction and remain outside application time.\n\n"
 if not enabled:text+='None of the new ordering predictors passes the five-percent validation gate. The selected method therefore uses fixed ordering settings chosen by validation while retaining the preceding learned seed policies. Any measured change in this stage comes from those settings and their interaction with the preceding method. It does not establish an added gain from an ordering predictor.\n\n'
 text+=f"All {d['workflows']} timed reductions pass exact checks. All 43 additional applications also pass when no target coefficients are supplied to the reduction. The new-to-previous time ratio is {ratio('selected_to_previous')}, giving {change(pr)}. The new-to-native ratio is {ratio('selected_to_native')}, giving {change(nr)}. The ratio to the new fixed strategy is {ratio('selected_to_fixed')}. These ratios give each graph equal weight.\n\n"
 text+=f"The sum of median full times over the 36 reserved batches is {totals['native']:.2f} seconds for native choices, {totals['previous']:.2f} seconds for the preceding method, {totals['family_fixed']:.2f} seconds for the new fixed settings, and {totals['selected']:.2f} seconds for the selected method. This gives {change(totals['selected']/totals['previous'])} than the preceding method for that workload.\n\n"
 text+=f"The additional ordering decision takes a median of {1e6*d['ordering_prediction_seconds']['median']:.1f} microseconds per timed application. This is part of the full time above; the preceding seed-policy cost is also included in full time.\n\n"
 text+=r'''\begin{table}[!htbp]
\centering\small
\caption{Complete times for the ordering study. Times are geometric
means of batch medians in seconds. Each graph uses two reserved
kinematic profiles. The choice is a fitted predictor, the previous route,
or a fixed $(\omega,\chi)$ setting. A ratio below one indicates less time.}
\label{tab:ordering-policy}
\begin{tabular}{@{}llrrrr@{}}\toprule
Graph & Choice & Previous (s) & New (s) & New/previous & New/native\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}
\begin{figure}[!htbp]
\centering\includegraphics[width=\linewidth]{paper_figures/ordering_policy.pdf}
\caption{The effect of choosing Kira settings before reduction. Left:
new fixed settings and selected settings relative to the preceding method.
Right: preceding and selected methods relative to native choices.
Values below one indicate less full time. Bars give the range across
two parameter profiles; they are not significance intervals.}
\label{fig:ordering-policy}
\end{figure}
\FloatBarrier
'''
 slow=[f"{NAMES[k].lower()} ({100*(v['selected_to_previous']-1):.1f}\\%)" for k,v in d['by_topology'].items() if v['selected_to_previous']>1]
 if slow:text+='The following graph groups take more time than the preceding method: '+', '.join(slow)+'.\n\n'
 text+=f"The selected method makes {d['fallbacks'].get('selected',0)} fallback attempts in the timed comparison. "
 for stage,label in [('equation_regeneration','symbolic equation regeneration'),('back_substitution','back-substitution')]:
  a=d['stage_totals']['previous'].get(stage,0);b=d['stage_totals']['selected'].get(stage,0)
  text+=f"Across 180 runs per method, {label} takes {a:.2f} seconds with the preceding method and {b:.2f} seconds with the selected method. "
 text+='The total time also includes prediction, preparation, native generation, exact checks, basis conversion, retries, and cleanup. The measurements use loaded caller and model code, with a new Kira process for each attempt. They establish the measured choice among the tested strategies for known graphs at one through three loops and new rational parameter profiles. They do not establish a globally fastest ordering or a gain for arbitrary integral families.\n'
 (REPORT/'ordering_policy_results.tex').write_text(text)
 (REPORT/'ordering_policy_appendix.tex').write_text((HERE/'ordering_policy_appendix.tex').read_text())
 for name in ['report.tex','notes.tex']:
  p=REPORT/name;s=p.read_text()
  if '\\input{ordering_policy_results}' not in s:
   s=s.replace('\\input{basis_completion_results}','\\input{basis_completion_results}\n\\input{ordering_policy_results}')
   s=s.replace('\\input{basis_completion_appendix}','\\input{basis_completion_appendix}\n\\input{ordering_policy_appendix}')
  if name=='report.tex' and 'Choosing Kira settings & ' not in s:
   abstract=r'''We study learned choices that reduce the time needed for exact Feynman integral reduction with Kira. The measurements include prediction, algebra, checks, and retries. Seed and equation selection save time on their stated inputs; learned row selection gives no reliable saving and is omitted. We then train models to choose complete reduction strategies, selective seed limits, and integral orderings for seven known graph structures at one through three loops. In the latest comparison, the selected ordering method gives '''+change(pr)+' against the preceding method and '+change(nr)+r''' against native choices, with time ratios $'''+f'{pr:.4f}'+r'''$ and $'''+f'{nr:.4f}'+r'''$. All 720 timed reductions and 43 additional applications pass exact checks. The test uses new rational kinematic profiles and symbolic dimension, with target patterns known during training. Separate tests give a 48.3\% saving from sharing compatible requests and a 543.8-fold saving from exact recurrences and reuse in a restricted vacuum family through twelve loops. These results use different inputs and controls and do not define a product of speedups.'''
   if not enabled:abstract=abstract.replace('In the latest comparison,', 'Validation retains fixed ordering settings and the preceding learned seed policies; the new ordering predictors give no accepted additional gain. In the latest comparison,')
   s=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+abstract+'\n'+m[2],s,flags=re.S)
   s=s.replace('selectively expand seed limits to reduce the remaining cost.','selectively expand seed limits to reduce the remaining cost. We then test whether different integral orderings reduce that cost further.')
   needle='Section~\\ref{sec:basis-completion} then measures 8.8\\% less time relative to the preceding route and 14.8\\% less time relative to native choices on new profiles.'
   s=s.replace(needle,needle+f"\nThe ordering study in Section~\\ref{{sec:ordering-policy}} gives {change(pr)} against that preceding method and {change(nr)} against native choices on another reserved set.")
   s=s.replace('Joint integrated reduction &',f'Choosing Kira settings & Known graphs, new profiles, loops 1--3 & {change(nr)} than native\\\\\nJoint integrated reduction &')
   s=s.replace('Sharing compatible requests gives a separate 48.3\\% saving.',f'The final ordering study gives {change(pr)} relative to the preceding method and {change(nr)} relative to native choices. Its ratio to new fixed settings is ${fr:.4f}$. All 720 timed reductions and 43 additional applications pass exact checks. The choice is made before equation generation, so its cost is paid once per batch. Per-graph results retain all observed regressions.\n\nSharing compatible requests gives a separate 48.3\\% saving.')
  if name=='report.tex' and not enabled and 'The added ordering predictors remain disabled.' not in s:
   s=s.replace('Per-graph results retain all observed regressions.', 'Per-graph results retain all observed regressions. The added ordering predictors remain disabled. The tested settings give no further improvement, so the preceding route remains the retained method.')
  p.write_text(s)
 p=REPORT/'Makefile';s=p.read_text();needle='basis_completion_appendix.tex paper_references.bib'
 s=s.replace(needle,'basis_completion_appendix.tex ordering_policy_results.tex ordering_policy_appendix.tex paper_references.bib');p.write_text(s)
 print(json.dumps(dict(report_written=True,ratio_to_previous=pr,ratio_to_native=nr,workload_seconds=totals)))
if __name__=='__main__':main()
