"""Write the measured seed-expansion results into both research documents."""
import json,math,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
NAMES={'sunrise':'Sunrise','double_box':'Planar box','vacuum3':'Vacuum','ladder3':'Ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box'}
def main():
 d=json.loads((HERE/'model_test/summary.json').read_text());public=json.loads((HERE/'model_test/public_checks.json').read_text())
 assert d['complete'] and d['all_exact'] and public['complete'] and public['all_exact']
 def change(r):return f'{100*abs(1-r):.1f}\\% '+('less' if r<1 else 'more')+' time'
 def val(key):
  r=d['aggregate'][key];return f"${r['ratio']:.4f}$ with descriptive interval $[{r['interval'][0]:.4f},{r['interval'][1]:.4f}]$"
 nr=d['aggregate']['selected_to_native']['ratio'];pr=d['aggregate']['selected_to_previous']['ratio'];fr=d['aggregate']['selected_to_fixed']['ratio']
 enabled=[k for k,p in d['policies'].items() if p['enabled']]
 labels={'previous':'Preceding route','completion':'Restricted basis completion','completion_full':'Full-sector basis completion'}
 def label(cfg):
  if cfg in labels:return labels[cfg]
  return '$B_c+('+','.join(cfg.split('_')[1])+')$'
 config_text=', '.join(label(c) for c in d['configurations'])
 policies={'previous':'Previous','completion':'Complete basis','completion_full':'Complete basis','delta_100':'Add $r$','delta_010':'Add $s$','delta_110':'Add $r,s$','tree1':'Tree depth 1','tree2':'Tree depth 2','tree3':'Tree depth 3','forest16':'Bagged trees','nearest1':'1 neighbour','nearest3':'3 neighbours','ridge0.1':'Ridge 0.1','ridge1.0':'Ridge 1','ridge10.0':'Ridge 10','constant':'Constant'}
 rows=[]
 for k in NAMES:
  cs=[c for c in d['cases'] if c['topology']==k]
  old=math.exp(statistics.mean(math.log(c['median_seconds']['previous']) for c in cs));new=math.exp(statistics.mean(math.log(c['median_seconds']['selected']) for c in cs))
  policy=d['policies'][k];description=policies[policy['model'] if policy['enabled'] else policy['validation_control']]
  rows.append(f"{NAMES[k]} & {description} & {old:.3f} & {new:.3f} & {d['by_topology'][k]['selected_to_previous']:.3f} & {d['by_topology'][k]['selected_to_native']:.3f}"+r'\\')
 intro=r'''\section{Reducing the cost of seed expansion}
\label{sec:basis-completion}
The preceding graph-specific study records more solver time in symbolic
equation regeneration than in any other instrumented stage. Some batches
need larger seed regions to reach the prescribed masters, so generating
fewer unnecessary equations in those regions can reduce the remaining
cost. We test six ways to increase selected seed limits and two ways to
reduce first to a temporary basis. The latter methods then reduce the
remaining basis integrals and combine their exact coefficients. They
retain the same final master-basis requirement. Appendix~\ref{app:basis-completion}
defines all candidates and derives the basis conversion.

For each development batch, we retain its fastest new candidate if it
saves at least ten percent against the preceding route. The preceding
route also remains available. Let $B_c=(r_c,s_c,q_c)$ be the initial valid seed limits for target batch $c$. They bound the sum of positive indices, numerator rank, and number of extra denominator powers, respectively. The selected candidates are '''+config_text+r'''.
Development measurements guide this choice; they do not enter the
reserved comparison. We train on 36 new batches, select settings on 18
validation batches, and reserve 36 further batches. All use new rational
kinematic profiles of the same seven graphs, with symbolic $d$ and the
target patterns defined in Appendix~\ref{app:type-specialists}.

We fit ten predictors per graph using the earlier nine target features.
They predict full time relative to the preceding route. Validation
compares each predictor with that route and with a single fixed strategy
chosen from training for each graph. A new predictor must save at least
five percent against the faster control before it is enabled. Otherwise,
the selected route uses the control. These comparisons measure the effect of the new seed options and the
additional effect of the full selection procedure. A fixed candidate can itself call the preceding learned route; this control measures the extra choice among the new candidates.
'''
 intro+=f'Validation enables a new predictor for {len(enabled)} of the seven graphs. '
 intro+=f"The final training and validation records contain {sum(d['label_seconds'].values()):,.1f} seconds of measured reductions; fitting the seventy candidates takes {d['fitting_seconds']:.2f} seconds. "
 intro+=r'''These offline costs exclude reference construction and development and remain outside the reserved reduction timer.

The reserved test compares native choices, the preceding route, the new
fixed strategy, and the selected route. Five repetitions give 720 full
calculations. All pass exact coefficient checks, and all 43 further
applications pass checks when target coefficients are withheld during
reduction. The new route has time ratio '''+val('selected_to_previous')+r'''
to the preceding route, corresponding to '''+change(pr)+r'''. Its ratio to
native choices measured in the same experiment is '''+val('selected_to_native')+r''',
or '''+change(nr)+r'''. Its ratio to the new fixed strategy is
'''+val('selected_to_fixed')+'.\n\n'
 totals={m:sum(c['median_seconds'][m] for c in d['cases']) for m in ['native','previous','selected']}
 intro+=f"For one execution of each of the 36 reserved batches, the sum of median reduction times is {totals['native']:.2f} seconds for native choices, {totals['previous']:.2f} seconds for the preceding route, and {totals['selected']:.2f} seconds for the new route. This workload total weights each requested batch once; the geometric means above give each graph equal weight.\n\n"
 regen_old=d['stage_totals']['previous']['equation_regeneration'];regen_new=d['stage_totals']['selected']['equation_regeneration']
 intro+=f"Across 180 timed runs per method, symbolic equation regeneration takes {regen_old:.2f} seconds for the preceding route and {regen_new:.2f} seconds for the new route. The new route makes {d['fallbacks'].get('selected',0)} fallback attempts, compared with {d['fallbacks'].get('previous',0)} for the preceding route and {d['fallbacks'].get('native',0)} for native choices. Planned second-stage basis reductions are counted in full time and are separate from fallback attempts.\n\n"
 if enabled and d['aggregate']['selected_to_fixed']['interval'][1]<1:
  intro+='The fixed-strategy comparison supports a further saving from the selection procedure on these inputs. This procedure combines validation-based control choices with target-dependent predictions.\n'
 else:intro+='The fixed-strategy comparison does not establish a further saving from the selection procedure. This procedure combines validation-based control choices with target-dependent predictions.\n'
 intro+=r'''
\begin{table}[!htbp]
\centering\small
\caption{Full reduction times for the new reserved profiles. Times are
geometric means of batch medians in seconds. Ratios below one indicate a
faster new route. The policy is the fitted predictor or fixed control
chosen by validation. Each graph has two reserved parameter profiles.}
\label{tab:basis-completion}
\begin{tabular}{@{}llrrrr@{}}\toprule
Graph & Policy & Previous (s) & New (s) & New/previous & New/native\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}

\begin{figure}[!htbp]
\centering\includegraphics[width=\linewidth]{paper_figures/basis_completion.pdf}
\caption{Selective choices change complete reduction time. Left: the new
fixed strategy and selected route relative to the preceding route.
Right: the preceding and new routes relative to native choices in the
same test. Values below one are faster. Bars show the range over the two
reserved profiles; they are not significance intervals.}
\label{fig:basis-completion}
\end{figure}
\FloatBarrier

The result includes prediction, native IBP generation, exact algebra,
checks, cleanup, and fallback. It measures an additional change from the
preceding method and a direct comparison with native choices. It does
not multiply speedups from earlier experiments. The graphs and target
patterns are known during training; the new parameter profiles test
transfer within those inputs. General symbolic kinematics and arbitrary
high-loop graphs remain outside this new measurement.
'''
 slower=[(k,v['selected_to_previous']) for k,v in d['by_topology'].items() if v['selected_to_previous']>1]
 if slower:
  losses='; '.join(f"{NAMES[k].lower()}, {100*(r-1):.1f}\\%" for k,r in slower)
  intro=intro.replace('\nThe result includes', '\nThree graph groups take more time than the preceding route: '+losses+'.\n\nThe result includes')
 (REPORT/'basis_completion_results.tex').write_text(intro)
 (REPORT/'basis_completion_appendix.tex').write_text((HERE/'basis_completion_appendix.tex').read_text())
 p=REPORT/'report.tex';s=p.read_text()
 if '\\input{basis_completion_results}' not in s:
  s=s.replace('\\input{type_specialist_results}','\\input{type_specialist_results}\n\n\\input{basis_completion_results}')
  s=s.replace('\\input{type_specialist_appendix}','\\input{type_specialist_appendix}\n\\input{basis_completion_appendix}')
  s=s.replace('Combining compatible requests gives',f'A further study of selective seed expansion gives {change(pr)} against that route and {change(nr)} against native choices in 720 new trials. Combining compatible requests gives',1)
  s=s.replace('We then test separate policies for each graph with new seed strategies.','We then test separate policies for each graph with new seed strategies and selectively expand seed limits to reduce the remaining cost.')
  needle='joint-request saving because the two studies use different requests.'
  s=s.replace(needle,needle+f'\nSection~\\ref{{sec:basis-completion}} then measures {change(pr)} relative to the preceding route and {change(nr)} relative to native choices on new profiles.')
  needle='Joint integrated reduction &'
  s=s.replace(needle,f'Selective seed expansion & Known graphs, new profiles, loops 1--3 & {change(nr)} than native\\\\\n'+needle)
  needle='Sharing compatible requests gives a separate 48.3\\% saving.'
  s=s.replace(needle,f'The subsequent seed-expansion study gives {change(pr)} against that graph-specific route and {change(nr)} against native choices, with all 720 trials and 43 applications passing exact checks. Its comparison with the new fixed strategy has ratio ${fr:.4f}$. This separates the effect of choosing seed regions from the extra contribution of target-dependent prediction.\n\n'+needle)
 p.write_text(s)
 p=REPORT/'notes.tex';s=p.read_text()
 if '\\input{basis_completion_results}' not in s:
  s=s.replace('\\input{type_specialist_results}','\\input{type_specialist_results}\n\\input{basis_completion_results}')
  s=s.replace('\\input{type_specialist_appendix}','\\input{type_specialist_appendix}\n\\input{basis_completion_appendix}')
 p.write_text(s)
 p=REPORT/'Makefile';s=p.read_text().replace('type_specialist_appendix.tex paper_references.bib','type_specialist_appendix.tex basis_completion_results.tex basis_completion_appendix.tex paper_references.bib');p.write_text(s)
 print(json.dumps(dict(report_written=True,ratio_to_previous=pr,ratio_to_native=nr,ratio_to_fixed=fr)))
if __name__=='__main__':main()
