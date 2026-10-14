"""Write the completed specialist results into the paper and archived notes."""
import json,math,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
NAMES={'sunrise':'Sunrise','double_box':'Planar box','vacuum3':'Vacuum','ladder3':'Ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box'}
LABELS={'native':'Native','sector':'Target sectors','truncate0':'Truncation','truncate1':'Stronger truncation','sector_truncate0':'Sectors and truncation','tight':'Smaller seeds','expanded':'Larger seeds','equation':'Equation tree','order5':'Ordering five',
 'constant':'Constant','tree1':'Depth-one tree','tree2':'Depth-two tree','tree3':'Depth-three tree','forest16':'Bagged trees','ridge0.1':'Ridge 0.1','ridge1.0':'Ridge 1','ridge10.0':'Ridge 10','nearest1':'One neighbour','nearest3':'Three neighbours'}
def main():
 d=json.loads((HERE/'model_test/summary.json').read_text());audit=json.loads((HERE/'evidence_validation.json').read_text())
 assert d['complete'] and d['all_exact'] and audit['complete']
 r=d['aggregate']['learned'];q=d['aggregate']['learned_to_family_fixed'];enabled=[k for k,p in d['policies'].items() if p['enabled']]
 faster=sum(v['learned']<1 for v in d['by_topology'].values())
 def value(x):return f"${x['ratio']:.4f}$ with descriptive interval $[{x['interval'][0]:.4f},{x['interval'][1]:.4f}]$"
 if r['ratio']<1:change=f"{100*(1-r['ratio']):.1f}\\% less time"
 else:change=f"{100*(r['ratio']-1):.1f}\\% more time"
 judgement='The aggregate interval includes equal time.' if q['interval'][0]<=1<=q['interval'][1] else ('The aggregate interval lies below equal time.' if q['interval'][1]<1 else 'The aggregate interval lies above equal time.')
 rows=[]
 for k,p in d['policies'].items():
  cs=[c for c in d['cases'] if c['topology']==k]
  native=math.exp(statistics.mean(math.log(c['median_seconds']['native']) for c in cs));selected=math.exp(statistics.mean(math.log(c['median_seconds']['learned']) for c in cs))
  name=LABELS[p['model']] if p['enabled'] else LABELS[p['validation_control']]
  rows.append(f"{NAMES[k]} & {name} & {native:.3f} & {selected:.3f} & {d['by_topology'][k]['learned']:.3f}"+r'\\')
 route_text=(f"Validation activates a new cost model for {len(enabled)} of the seven graphs and retains a control strategy for the others." if enabled else 'Validation retains a control strategy for every graph.')
 text=r'''\section{Choosing a policy for each integral type}
\label{sec:type-specialists}
The preceding study used one cost predictor across seven graph structures.
We now train separate predictors and enlarge the set of possible seed
strategies. This lets a target-dependent choice depend on the graph's own
measured costs. The new candidates include restricting the maximal target
sectors and reducing numerator seeding in lower sectors, using Kira's
truncation option~\cite{Kira3}. The comparison retains exact algebra,
master-basis checks, and fallback. Every method first enforces a valid
positive-index bound for its declared sectors.

We fit ten candidates for each graph, giving seventy fitted models.
They include regression trees, a bagged tree ensemble, regularized linear
models, and nearest-neighbour models. The model receives nine features of
the target indices and family and predicts complete-time ratios for nine
strategies. The response includes failed attempts and retries. We train
on 36 batches, choose settings on 18 validation batches, and reserve
36 batches at new rational parameter values for testing. The dimension
remains symbolic. The targets include denominators raised to power three,
lower sectors, and numerator indices $-2$ on auxiliary entries. Appendix~\ref{app:type-specialists}
gives the exact definitions, model fits, and selection rule.
'''+f"The final training and validation records contain {sum(d['final_label_seconds'].values()):,.1f} seconds of measured reductions, and fitting all seventy candidates takes {d['fitting_seconds']:.2f} seconds. "+r'''The label total excludes reference construction, development, and replaced measurements. These offline costs remain outside the reserved reduction times.

The route enables a new cost model only when validation shows at least
five percent less time than the fastest available control. This threshold
is fixed before testing. The controls are native choices, a deterministic
sector-and-truncation rule, and one fixed strategy per graph selected
from training. The last control can include the older equation filter.
'''+route_text+r'''
Unknown graph structures and target features outside the training range
use native choices. A chosen strategy can still fail its basis check;
the route then retries, and the comparison includes that cost.

Five repetitions of four methods give 720 reserved timing trials.
All trials pass exact coefficient checks. Giving each graph equal weight,
the selected route has geometric mean full-time ratio
'''+value(r)+', corresponding to '+change+r'''.
Its ratio to the fixed choice per graph is '''+value(q)+'. '+judgement+r'''
Table~\ref{tab:type-specialists} gives each graph's result.
'''+f'The selected route has a time ratio below one for {faster} of the seven graph groups.'+r'''
These are measurements within the tested input groups, not a speed
guarantee for every integral in those graphs.
'''+f"Across its 180 timed trials, the selected route makes {d['fallbacks'].get('learned',0)} retry attempts; native choices make {d['fallbacks'].get('native',0)} retries in the matched 180 trials. The time ratios include these retries."+r'''

'''+f"The enabled trees give {100*(1-d['by_topology']['double_box']['learned']):.1f}\\%, {100*(1-d['by_topology']['ladder3']['learned']):.1f}\\%, and {100*(1-d['by_topology']['nonplanar_box']['learned']):.1f}\\% less time for the planar box, ladder, and nonplanar box, respectively. The vacuum and virtuality box show {100*(d['by_topology']['vacuum3']['learned']-1):.1f}\\% and {100*(d['by_topology']['one_mass_box']['learned']-1):.1f}\\% more time. Both of those groups use a retained control throughout. The vacuum route selects native settings, so its measured difference includes routing overhead and timing variation."+r'''

\begin{table}[!htbp]
\centering\small
\caption{Results for each graph. Times are geometric means of the batch
median times, in seconds. A ratio below one means less complete time.
The route column names the enabled cost model or retained control.}
\label{tab:type-specialists}
\begin{tabular}{@{}llrrr@{}}\toprule
Graph & Route & Native & Selected & Ratio\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}

\begin{figure}[!htbp]
\centering\includegraphics[width=\linewidth]{paper_figures/type_specialists.pdf}
\caption{The effect of choosing a separate policy for each graph.
Left: full-time ratios to native choices. Right: the selected route
relative to one fixed strategy per graph. Bars show the range across two
reserved parameter profiles; they are not significance intervals.
Both panels retain the equal-time reference.}
\label{fig:type-specialists}
\end{figure}
\FloatBarrier

The timing trials check '''+f"{d['coefficient_entries_checked']:,}"+r''' coefficient entries.
We also complete 36 applications supplied only with the master basis and
seven further application checks, then compare their coefficients independently.
These additional applications check '''+f"{audit['application_coefficient_checks']:,}"+r''' coefficients.
The new study uses the same seven graph structures as before, at one
through three loops. Its target patterns occur in training, and it tests
new kinematic profiles. General scattering beyond three loops and new
target structures remain outside this comparison. The per-graph models
have two training parameter profiles; the fixed range guard and
reserved checks limit the claims accordingly.
'''
 (REPORT/'type_specialist_results.tex').write_text(text)
 paper=REPORT/'report.tex';s=paper.read_text()
 if '\\input{type_specialist_results}' not in s:s=s.replace('\\input{workflow_results}','\\input{workflow_results}\n\n\\input{type_specialist_results}')
 if '\\input{type_specialist_appendix}' not in s:s=s.replace('\\input{workflow_appendix}','\\input{workflow_appendix}\n\\input{type_specialist_appendix}')
 abstract=r'''We study learned choices of seeds, elimination rows and equations during exact Feynman integral reduction with Kira. We include prediction, algebra, checks and retries in the measured time. Original tests give an 8.6\% saving from seed selection with supplied equations and a 5.7\% saving from equation selection in four native graph structures. Row selection gives no reliable saving and is omitted. A later global cost predictor gives no reliable extra gain over native controls. We therefore fit seventy candidates with separate models for seven graph structures. The selected route gives '''+change+f" in 720 reserved trials, with a time ratio of ${r['ratio']:.4f}$ to native choices and ${q['ratio']:.4f}$ to a fixed strategy per graph. "+r'''Every trial passes exact checks. Combining compatible requests gives a separate 48.3\% saving through shared reduction. Exact recurrences and reuse give a 543.8-fold saving in a restricted vacuum family through twelve loops. The native studies cover known graph structures at one through three loops; the results retain their stated inputs, controls and timing conditions.'''
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,flags=re.S)
 old='requests. We compare full calculation times because fewer equations or accurate predictions alone do not show that a reduction is faster.'
 new='requests. We then test separate policies for each graph with new seed strategies. We compare full calculation times because fewer equations or accurate predictions alone do not show that a reduction is faster.'
 s=s.replace(old,new)
 old='control. This result is a direct comparison of identical paired requests.'
 addition='\nThe separate graph-specific study in Section~\\ref{sec:type-specialists}\ngives '+change+f" relative to native choices and ratio ${q['ratio']:.4f}$\nto the fixed strategy per graph. Its gains cannot be multiplied by the\njoint-request saving because the two studies use different requests."
 if addition not in s:s=s.replace(old,old+addition)
 row='Policies per graph & Higher powers and lower sectors, loops 1--3 & '+change+r'\\'
 marker='Joint integrated reduction &'
 if row not in s:s=s.replace(marker,row+'\n'+marker)
 conclusion=r'''\section{Conclusion}
The original seed and equation models save time in their stated test
domains. We omit learned row selection because its complete-time
comparisons give no reliable saving. Additional scattering training
improves equation sufficiency, and the subsequent cost studies compare
whole calculations with all retries included.

The new experiment fits seventy candidates and chooses a separate policy
for each of seven graph structures. '''+route_text+' The selected route gives '+change+r'''
relative to native choices on fresh rational profiles, with time ratio
'''+value(r)+r'''. Its comparison with a fixed strategy for each graph gives
'''+value(q)+'. '+judgement+r'''
All 720 timing trials and 43 further applications pass exact checks.
The per-graph measurements and controls show where learned selection,
fixed settings, or fallback determine the result.

Sharing compatible requests gives a separate 48.3\% saving. The
543.8-fold saving through twelve loops comes from exact recurrences and
reuse in a restricted vacuum family. These results measure different
calculations and do not define a combined product of speedups.

The native comparisons cover known structures at one through three loops.
The newest test retains the training target patterns and changes their
kinematic parameters. It does not establish a significant learned gain
for every possible integral type. General high-loop scattering and
globally optimal reduction paths remain outside the demonstrated results.
'''
 a=s.index('\\section{Conclusion}');b=s.index('\\appendix',a);s=s[:a]+conclusion+'\n'+s[b:];paper.write_text(s)
 notes=REPORT/'notes.tex';s=notes.read_text()
 if '\\input{type_specialist_results}' not in s:s=s.replace('\\input{workflow_results}','\\input{workflow_results}\n\\input{type_specialist_results}')
 if '\\input{type_specialist_appendix}' not in s:s=s.replace('\\input{workflow_appendix}','\\input{workflow_appendix}\n\\input{type_specialist_appendix}')
 added='\nThe graph-specific study in Section~\\ref{sec:type-specialists} fits\nseventy candidates and gives '+change+f" relative to native choices\non 720 reserved trials. Its ratio to a fixed strategy per graph is\n${q['ratio']:.4f}$. All trials and 43 additional applications pass exact\nchecks. The study covers the seven known graphs at one through three\nloops with new rational profiles and repeated target patterns.\n"
 if added not in s:
  marker='The earlier\nrestricted vacuum result through twelve loops remains a separate result.\n';assert marker in s;s=s.replace(marker,marker+added)
 s=s.replace('The latest complete-cost study in Section~','The complete-cost study in Section~')
 old='\\bibliography{references}';new='\\bibliography{references,type_specialist_references}'
 revision=json.loads((REPORT/'notes_revision.json').read_text())
 if old in s:s=s.replace(old,new)
 if [new,old] not in revision['reverse_replacements']:revision['reverse_replacements'].append([new,old])
 notes.write_text(s);(REPORT/'notes_revision.json').write_text(json.dumps(revision,indent=2)+'\n')
 def readme_block(path,body):
  begin='<!-- BEGIN GRAPH POLICY RESULTS -->';end='<!-- END GRAPH POLICY RESULTS -->'
  old=path.read_text();block=begin+'\n\n'+body.strip()+'\n\n'+end
  if begin in old:old=re.sub(re.escape(begin)+r'.*?'+re.escape(end),lambda m:block,old,flags=re.S)
  else:old=old.rstrip()+'\n\n'+block+'\n'
  path.write_text(old)
 result_lines=[
  '## Completed graph-policy results',
  '',
  'The final fit contains 70 candidates for seven graph types.',
  'It uses 544 training cost records and 408 separate validation records.',
  'The reserved test contains 720 timing trials and 43 further application checks.',
  'All checks pass.',
  f"The selected-to-native geometric mean time ratio is {r['ratio']:.6f}.",
  f"Its descriptive interval is [{r['interval'][0]:.6f}, {r['interval'][1]:.6f}].",
  f"The selected-to-fixed ratio is {q['ratio']:.6f}.",
  f"Its descriptive interval is [{q['interval'][0]:.6f}, {q['interval'][1]:.6f}].",
  'Each graph has equal weight in these aggregate ratios.',
  'A ratio below one means less complete reduction time.',
  f'The selected route has a ratio below one in {faster} of the seven graph groups.',
  'The inputs use known graph structures and target patterns at new rational profiles.',
  'These results give no speed guarantee for other inputs.',
  '',
  '| Graph | Selected model or control | Time / native time |',
  '| --- | --- | ---: |']
 for k,p in d['policies'].items():
  name=('Model '+p['model']) if p['enabled'] else ('Control '+p['validation_control'])
  result_lines.append(f"| {NAMES[k]} | {name} | {d['by_topology'][k]['learned']:.4f} |")
 result_lines.extend(['',
  'The model_test/summary.json file contains times, decisions, retries, and plot values.',
  'The evidence_validation.json file records the final checks.',
  f"Final training and validation records contain {sum(d['final_label_seconds'].values()):.1f} seconds of measured reductions.",
  f"Fitting the final 70 candidates takes {d['fitting_seconds']:.2f} seconds.",
  'The label total excludes development, reference construction, and replaced records.',
  'These offline costs remain outside the reserved time ratios.'])
 readme_block(HERE/'README.md','\n'.join(result_lines))
 short='\n'.join(result_lines[:result_lines.index('| Graph | Selected model or control | Time / native time |')])+'\nSee the study guide for the graph results and limits.'
 readme_block(ROOT/'README.md',short)
 readme_block(HERE.parent/'README.md',short)
 parent=HERE.parent/'README.md';parent.write_text(parent.read_text().replace('describes the next cost-model study.','describes the completed cost-model study.'))
 readme_block(HERE/'model_test/README.md',f"## Completed checks\n\nAll 720 reserved timing trials pass.\nAll 36 basis-only applications and seven public applications pass.\nThe checks cover {d['coefficient_entries_checked']:,} timing-trial coefficient entries and {audit['application_coefficient_checks']:,} application entries.\nThe s08_validate.py script writes evidence_validation.json in the study folder.\nSee summary.json and the [study guide](../README.md) for time ratios and limits.")
 print(json.dumps(dict(complete=True,faster_graph_groups=faster,enabled_models=enabled,aggregate=r,fixed_comparison=q)))
if __name__=='__main__':main()
