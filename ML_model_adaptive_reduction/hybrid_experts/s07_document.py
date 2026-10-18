"""Describe complete-time selection with a validated sparse-seed expert."""
from s00_cost_common import *

def main():
 report=ROOT/'report';s=READ(HERE/'summary.json');f=READ(HERE/'trained_model/freeze.json');expert=READ(HERE/'trained_model/expert.json');b=READ(BASE/'summary.json')
 totals=s['totals'];comp=s['comparisons'];has_ml=totals['learned']['model_requests']>0
 names={'native':'native seed bounds','fixed':'the validation-selected ML-free control','previous':'the preceding complete-time application'}
 actions={'base':'the preceding basis-compatible setting','sparse_fixed':'a fixed sparse-seed boundary','sparse_learned':'the trained sparse-seed expert','raw_native':'the original native bounds'}
 def result(group,control):
  v=comp[group][control]
  if not v['cases']:return 'No matched completed request supports this comparison.'
  direction='less' if v['ratio']<1 else 'more';lo,hi=v['repeat_interval']
  return f"For {v['cases']} matched requests, the integrated method takes {v['learned_seconds']:.3f} seconds and {names[control]} takes {v['control_seconds']:.3f} seconds. This gives {abs(v['reduction_percent']):.1f}\\% {direction} time, with ratio {v['ratio']:.3f} and repetition interval $[{lo:.3f},{hi:.3f}]$."
 v=comp['expert_domain']['fixed']
 if not has_ml:interpretation='Validation retains ML-free choices, and this test establishes no runtime gain from learned prediction.'
 elif v['cases'] and v['repeat_interval'][1]<1:interpretation='The comparison with the selected ML-free control resolves an added saving from learned decisions beyond the measured repetition variation.'
 elif v['cases'] and v['repeat_interval'][0]>1:interpretation='The learned method takes more time than the selected ML-free control on the reserved expert-domain requests.'
 else:interpretation='The comparison with the selected ML-free control does not resolve an added learned saving beyond repetition variation.'
 text=r'''\section{Combining learned and exact reduction methods}
\label{sec:hybrid-experts}
The complete-time comparison above retains a fixed setting for the broad request collection. The earlier sparse-seed model has a separate tested use for nonplanar two-loop integrals with higher numerator powers. We therefore combine these methods and measure their complete costs on fresh inputs. Exact formulas handle their supported families first, and independent loop blocks are reduced separately. For the remaining work, the application can use the preceding setting, a fixed sparse boundary, the trained sparse-seed expert, or the original native bounds. Every route retains exact Kira algebra, the supplied master-basis check, and recovery after an unsuccessful attempt.

\subsection{The sparse expert and the complete-time selector}
The sparse expert acts before Kira generates equations. It uses the target numerator powers to select the boundary of a seed region, as defined in Section~\ref{sec:seed-row} and Appendix~\ref{app:sparse}. Its validated input domain contains one target in the specified nonplanar massless two-loop box, with seven unit physical powers and numerator rank two, three, or four. We check the ordered denominator and momentum structure before using this expert. Other blocks use the preceding fixed setting within its training ranges and return to original native bounds outside those ranges. The range check also covers numerator ranks above the broad training collection. This domain restriction permits a useful local model without assigning it an unsupported task.

''' + f"The expert retains its previously trained {len(expert['model']['trees'])}-tree model with maximum depth {expert['depth']}. Its {len(expert['training_cases'])} original training requests and {len(expert['validation_cases'])} model-selection requests precede this experiment. The model predicts log-time ratios for candidate sparse boundaries from 68 inputs: 27 family and target summaries, 40 positive- and negative-power coordinates, and the largest number of negative entries. Tree evaluation uses the saved thresholds and mean leaf values, following the earlier extremely randomized forest construction~\\cite{{Geurts2006ExtraTrees}}. Appendix~\\ref{{app:hybrid-experts}} gives the candidate boundaries and the fresh target batches. The current comparison includes feature calculation, prediction, seed enumeration, input preparation, and every recovery attempt.\n\n" + r'''We then fit an outer cost model from new complete reduction times. It receives the 51 structural and master-basis inputs of Appendix~\ref{app:total-time}, together with the two auxiliary numerator powers for this ordered family. Its four actions are the four routes listed above. The training cost includes the inner expert's prediction when that route uses it. We use the direct cost split of Eq.~\eqref{eq:total-split}, so the outer model learns which complete route takes less time.

''' + f"The new collection has {f['training_requests']} training requests and {f['validation_requests']} validation requests with separate rational kinematics. Each training action is measured once and each validation action twice. We compare one tree or sixteen trees, maximum depths one through five, and minimum leaf sizes two, four, or seven. Validation first compares the outer prediction with the best constant route. It then compares the resulting application with the best ML-free candidate. Each deployment comparison requires at least 1.5\\% less validation cost and no increase in unverified requests. The fixed sparse candidate retains the boundary selected in the earlier expert study. Current validation compares that candidate with the preceding setting and original native bounds to select the ML-free control. The selected control is {actions[f['fixed_action']]}. "
 if f['outer_enabled']:text+=f"Validation enables the outer {len(f['trees'])}-tree model, with maximum depth {f['selection']['depth']} and minimum leaf size {f['selection']['minimum']}. "
 else:text+=f"Validation retains {actions[f['default_action']]} as the constant route within this domain. "
 if f['default_action']=='sparse_learned' and not f['outer_enabled']:text+='The selected expert still predicts a sparse boundary for each target. '
 text+=f"The selected validation cost is {f['validation_selected_seconds']:.3f} seconds, compared with {f['validation_fixed_seconds']:.3f} seconds for the ML-free control. These model-selection results precede the reserved test.\n\n"
 text+=r'''\subsection{Fresh complete-workflow comparison}
The reserved comparison contains twenty-four nonplanar target requests and ten compatibility requests. The nonplanar requests cover every distribution of numerator ranks two through four across the two auxiliary coordinates at two new kinematic profiles. Eight of these requests use index vectors absent from the new outer-model training and validation collection. The earlier inner expert has a separate training history, which includes some of these added shapes. The ten compatibility requests include native coupled families through three loops, independent products through thirteen loops, and a thirteen-loop analytic case. We freeze the expert weights, outer model, domain checks, and decisions before testing. Each request uses three repetitions with rotated method order on one worker. The preceding application runs through its actual entry point. The fixed control disables both learned predictions, while all routes retain exact coefficient checks and the same native resource limits.

''' + f"The integrated application verifies {totals['learned']['verified_requests']} of {s['requested']} requests in all three repetitions, and invokes learned prediction on {totals['learned']['model_requests']}. "+result('all','previous')+' '+result('expert_domain','native')+' '+result('expert_domain','fixed')+' '+interpretation+' '+result('new_patterns','fixed')+' '+result('new_patterns','previous')+' These added index patterns expose a remaining transfer limit for the outer selector.\n\n'
 text+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete hybrid comparison. The first-pass time includes one attempt at every requested calculation. Ratios use sums of request medians on matched exact completions. The fixed setting is selected from the three declared ML-free candidates on validation data.}
\label{tab:hybrid-experts}
\begin{tabular}{@{}lrrrr@{}}\toprule
Method & Verified & First pass (s) & Integrated/method & Failed calls\\\midrule
'''
 for m,label_ in [('previous','Preceding application'),('native','Native bounds'),('fixed','Selected ML-free control'),('learned','Integrated method')]:
  t=totals[m];ratio=comp['all'][m].get('ratio',0) if m!='learned' else 1.
  text+=f"{label_} & {t['verified_requests']}/{s['requested']} & {t['first_pass_seconds']:.3f} & {ratio:.3f} & {t['failed_native_attempts']}\\\\\n"
 text+=r'''\bottomrule\end{tabular}\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/hybrid_expert_selection.pdf}
\caption{The left panel gives complete-time ratios for all matched requests, the sparse-expert domain, and the additional index patterns absent from outer-model training. The fixed control isolates the added learned decision. The line at one marks equal time, and horizontal bars show paired repetition variation. The right panel includes one attempt for every request and labels verified coverage. Prior and Hybrid denote the preceding and integrated applications.}
\label{fig:hybrid-experts}
\end{figure}
'''
 count=sum(q['measurements'] for q in s['collection'].values());seconds=sum(q['timed_seconds'] for q in s['collection'].values())
 text+=f"Across all recorded attempts and repetitions, the integrated method takes {totals['learned']['all_attempt_seconds']:.3f} seconds, compared with {totals['fixed']['all_attempt_seconds']:.3f} seconds for the ML-free setting and {totals['previous']['all_attempt_seconds']:.3f} seconds for the preceding application. The {count} new training and validation measurements take {seconds:.3f} timed seconds; outer-model fitting takes {f['fit_seconds']:.3f} seconds. Independent reference preparation for the reserved requests takes {s['reference_preparation_seconds']:.3f} seconds outside the application timers. The earlier expert training and checked master-basis preparation are additional prior costs.\n\n"
 text+=r'''The comparison measures use with an existing checked basis and includes model loading, prediction, equation generation, algebra, exact checks, and recovery. The direct learned result applies to the specified nonplanar family and numerator range. The compatibility checks verify the retained routes on their stated families; the broader baseline comparison above remains a separate experiment. The application keeps native row and equation choices. These finite tests establish no globally fastest reduction or coverage of arbitrary high-loop scattering.
'''
 (report/'hybrid_expert_results.tex').write_text(text)
 (report/'notes_hybrid_expert_results.tex').write_text(text.replace(r'Section~\ref{sec:seed-row} and Appendix~\ref{app:sparse}',r'Appendix~\ref{app:seed-geometry}'))
 # Keep the full preceding experiment in the notes, with a concise baseline in the paper.
 v=b['comparisons']['all']['native'];old=b['comparisons']['all']['previous'];bt=b['totals']
 baseline=r'''\section{Choosing baseline seed bounds by complete time}
\label{sec:refined-time}\label{sec:total-time}
The exact routes in Section~\ref{sec:blocks13} leave a native Kira problem whenever no supported formula applies. We compare nine seed settings for this remaining work. The candidates include native bounds, bounds enlarged to contain the supplied masters, and subsector truncations. Two candidates use the least enlargement that admits the required masters under Kira's additional cutoff~\cite{Kira3}; Appendix~\ref{app:refined-time} derives this condition. We fit cost-sensitive trees from 31 training requests and use 20 separate requests for model selection, with all failed attempts and recovery included in the cost.

Validation retains a fixed truncation with an increased numerator-rank bound because the forest's added saving does not reach the declared deployment threshold. Thus this stage supplies an ML-free baseline for the combined method below. The notes preserve its complete model search, measurements, and earlier conservative comparison.

'''+f"The reserved baseline test requests {b['requested']} reductions and verifies {bt['learned']['verified_requests']} in all three repetitions. On matched completions, the selected application takes {v['learned_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for original native bounds, giving a ratio of {v['ratio']:.3f}. Its ratio to the preceding application is {old['ratio']:.3f}; that comparison also includes the revised output handling. The first pass across all requests, including unfinished work, takes {bt['learned']['first_pass_seconds']:.3f} seconds. The grid spans loop orders one through thirteen through specified formulas and independent products, while coupled native requests reach three loops. The three-loop ladder remains unverified within the resource limits. These are fixed-workflow results and do not establish an added gain from the fitted forest.\n"
 (report/'hybrid_baseline_summary.tex').write_text(baseline)
 appendix=r'''\section{Definition of the hybrid expert comparison}
\label{app:hybrid-experts}
The sparse expert uses the nonplanar denominators in Eq.~\eqref{eq:nonplanar-new}. Its targets have seven unit physical powers. For numerator rank $R=2,3,4$, we include
\begin{equation}
 \boldsymbol a^{(1)}_R=(1,1,1,1,1,1,1,-R,0),\qquad
 \boldsymbol a^{(2)}_R=(1,1,1,1,1,1,1,0,-R).
\end{equation}
For $R=3,4$, we also include
\begin{equation}
 \boldsymbol a^{(12)}_R=(1,1,1,1,1,1,1,-\lceil R/2\rceil,-\lfloor R/2\rfloor).
\end{equation}
These definitions give eight training and validation targets per kinematic profile. The reserved collection additionally includes every vector $(1,1,1,1,1,1,1,-j,-(R-j))$ for $j=0,\ldots,R$ and $R=2,3,4$, giving twelve targets per profile. We use $s=-113-18h$ and $t=-127-10h$, with $h=2301,2303$ for training, $2309$ for validation, and $2311,2317$ for reserved tests. The additional two outer-model inputs are $\max(0,-a_8)$ and $\max(0,-a_9)$, appended to the 51 inputs in Appendix~\ref{app:total-time}. Their coordinate meanings remain fixed within this ordered family.

The outer actions are the preceding basis-compatible setting, the expert's fixed sparse boundary, its learned boundary, and original native bounds. The best ML-free control minimizes validation cost over all but the learned boundary. The cost-sensitive tree objective follows Eqs.~\eqref{eq:total-cost}--\eqref{eq:total-gate}, with complete costs for these four actions. The outer prediction is retained only if it improves on the best constant action by at least 1.5\%. The resulting application must also improve on the best ML-free candidate by at least 1.5\%, with no increase in unverified requests. A constant choice of the learned expert still performs that expert's target-dependent boundary prediction.

For the inner expert, the boundary coefficients $\theta_0,\ldots,\theta_6$ have the definitions in Appendix~\ref{app:sparse}. The saved forest predicts log-time ratios for these candidates. It changes the fixed candidate only when the predicted decrease exceeds its frozen margin. Table~\ref{tab:hybrid-boundaries} records the candidate coefficients; the native row applies no sparse boundary. Target and master seeds that satisfy the outer native bounds remain explicitly included. The native master-basis and coefficient checks determine acceptance, and a failed sparse attempt returns to less restrictive native work.

\begin{table}[!htbp]\centering\small
\caption{Frozen sparse-boundary candidates used by the inner expert. Coefficients define the seed region of Eq.~\eqref{eq:sparse-new}.}
\label{tab:hybrid-boundaries}
\begin{tabular}{@{}lrrrrrrr@{}}\toprule
Candidate & $\theta_0$ & $\theta_1$ & $\theta_2$ & $\theta_3$ & $\theta_4$ & $\theta_5$ & $\theta_6$\\\midrule
'''
 for i,theta in enumerate(expert['candidates']):
  if theta is None:appendix+=f"{i}: native & -- & -- & -- & -- & -- & -- & --\\\\\n"
  else:appendix+=str(i)+' & '+' & '.join(format(x,'.8g') for x in list(theta)+[0]*(7-len(theta)))+chr(92)*2+'\n'
 appendix+=r'\bottomrule\end{tabular}\end{table}'+'\n\n'+f"The fixed boundary index is {expert['fixed_index']} and the inner decision margin is {expert['margin']}. The ten compatibility requests use profile 2321 for the three original coupled native families, a pentagon, a rank-three massive two-point target, and the one-mass analytic family, and profiles $2327+4L$ for four independent products. Their denominators and target rules remain those in Appendices~\\ref{{app:families-new}} and~\\ref{{app:total-targets}}. They provide checks at loop orders one, two, three, four, eight, twelve, and thirteen.\n"
 if f['outer_enabled'] and f['selection']['name']=='d2_n4_t1_a0_m0.0':
  tree=f['trees'][0]
  assert f['features'][tree['feature']]=='first_auxiliary_rank' and tree['cut']==2.5
  assert f['features'][tree['left']['feature']]=='max_rank' and tree['left']['cut']==3.5
  for leaf,expected in [(tree['left']['left'],'sparse_learned'),(tree['left']['right'],'sparse_fixed'),(tree['right'],'base')]:
   j=min(range(4),key=lambda i:leaf['cost'][i]);anchor=f['anchor']
   if leaf['cost'][j]+f['decision_allowance_seconds']>=leaf['cost'][anchor]*(1-f['margin']):j=anchor
   assert ACTIONS[j]==expected
  appendix+=r"""
For the selected tree, let $u=\max(0,-a_8)$ be the first auxiliary numerator power and let $R=\max(0,-a_8)+\max(0,-a_9)$ be the total numerator rank. The first split tests $u\leq2.5$, and its lower branch tests $R\leq3.5$. Since both quantities are integers, the deployed choice within the expert domain is
\begin{equation}
 \pi(u,R)=\begin{cases}
  \text{learned sparse boundary},&u\leq2,\ R\leq3,\\
  \text{fixed sparse boundary},&u\leq2,\ R=4,\\
  \text{preceding basis-compatible setting},&u\geq3.
 \end{cases}
 \label{eq:hybrid-tree}
\end{equation}
Here $\pi(u,R)$ is the selected reduction route. Each leaf selects the route with its lowest predicted complete cost, subject to the decision allowance of Eq.~\eqref{eq:total-gate}. For the first two leaves, the predicted saving relative to the anchor exceeds the 0.002-second allowance. The third leaf already selects the anchor, so the allowance leaves its choice unchanged. These comparisons give Eq.~\eqref{eq:hybrid-tree}. Thus the outer tree can select a fixed or native setting even within the sparse expert's supported family. The exact checks and recovery rules still apply to each selected route.
"""
 (report/'hybrid_expert_appendix.tex').write_text(appendix)
 (report/'notes_hybrid_expert_appendix.tex').write_text(appendix.replace('app:sparse','app:seed-geometry').replace('eq:sparse-new','eq:geometry-boundaries'))
 for name in ['paper_abstract.tex','paper_conclusion.tex']:
  saved=report/('before_hybrid_expert_'+name)
  if not saved.exists():saved.write_text((report/name).read_text())
 v=comp['expert_domain']['fixed'];previous=comp['all']['previous'];novel=comp['new_patterns']['previous']
 transfer_limit=(f"On the {novel['cases']} requests with index vectors absent from outer-model training, the method takes {abs(novel['reduction_percent']):.1f}\\% more time than the preceding application. " if novel['cases'] and novel['ratio']>1 else '')
 abstract=r'''\begin{abstract}
Integration-by-parts reduction expresses Feynman integrals in a master basis~\cite{KiraOriginal}. We combine exact formulas, independent-loop factorization, basis-compatible native settings, and a trained sparse-seed expert. An outer model learns complete route costs, including prediction, equation generation, algebra, exact checks, and recovery. Separate validation compares the resulting method with the selected ML-free control before enabling learned decisions. '''+f"The hybrid test contains {s['requested']} requests, of which {totals['learned']['verified_requests']} pass three exact checks. "+result('expert_domain','fixed')+' '+interpretation+' '+transfer_limit+r'''A separate 65-request baseline test covers specified analytic families and independent products through thirteen loops, while coupled native calculations reach three loops. The sparse-expert comparison uses a nonplanar two-loop family with numerator ranks two through four. We keep the dimension symbolic and use rational values for other invariants. These timings assume a prepared master basis; training and independent reference preparation remain separate costs. General high-loop scattering and globally minimum reduction paths remain unverified.
\end{abstract}
'''
 (report/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
The integrated method applies exact formulas when their assumptions hold and reduces each distinct independent block once. It then selects a native setting or a trained sparse-seed expert for the remaining algebra. We train the outer choice from complete elapsed costs and compare it with ML-free controls. Validation retains a fixed basis-compatible setting for the broad collection and separately decides whether the sparse expert helps on its supported numerator domain.

'''+result('all','previous')+' '+result('expert_domain','fixed')+' '+interpretation+' '+transfer_limit+'\n\n'+f"The integrated test completes {totals['learned']['verified_requests']} of {s['requested']} requests in all three repetitions. Its first pass, including every requested outcome, takes {totals['learned']['first_pass_seconds']:.3f} seconds. The broader baseline study completes {bt['learned']['verified_requests']} of {b['requested']} requests and retains the unfinished three-loop ladder in its cost and coverage records.\n\n"+r'''The learned result remains specific to the stated nonplanar family and numerator powers. Exact formulas and independent products extend the checked loop range under their mathematical assumptions. The workflow retains native row and equation choices, while the earlier equation-selection gain remains a separate measured result. Master-basis preparation and model training precede the supplied-basis timers. These measurements establish the supported benefits and remaining failures without asserting a globally fastest reduction for every integral.
'''
 (report/'paper_conclusion.tex').write_text(conclusion)
 p=report/'report.tex';t=p.read_text()
 if r'\input{hybrid_expert_results}' not in t:t=t.replace(r'\input{refined_time_results}\label{sec:total-time}',r'\input{hybrid_baseline_summary}'+'\n'+r'\input{hybrid_expert_results}')
 if r'\input{hybrid_expert_appendix}' not in t:t=t.replace(r'\input{refined_time_appendix}',r'\input{refined_time_appendix}'+'\n'+r'\input{hybrid_expert_appendix}')
 t=t.replace(r'The current complete-time comparison in Section~\ref{sec:refined-time}',r'The current hybrid comparison in Section~\ref{sec:hybrid-experts}')
 t=t.replace(r'The shared-model application enables learned seed bounds; the block extension also applies the exact reductions in Section~\ref{sec:blocks13}. The equation filter retains its separate validated application, and no combined gain is inferred from these separate tests.',r'The current hybrid uses its validated sparse expert and the exact reductions in Section~\ref{sec:blocks13}. The shared model and equation filter retain their separately tested applications, and their gains are not added to the hybrid result.')
 p.write_text(t)
 p=report/'notes.tex';t=p.read_text();marker='% HYBRID EXPERT COMPARISON'
 if marker not in t:
  addition='% BEGIN CURRENT WORKFLOW UPDATE\n'+marker+'\n\\input{notes_hybrid_expert_results}\n\\input{notes_hybrid_expert_appendix}\n% END CURRENT WORKFLOW UPDATE\n'
  t=t.replace(r'\bibliographystyle{unsrt}',addition+r'\bibliographystyle{unsrt}')
 p.write_text(t)
 p=report/'Makefile';lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if line.startswith('report.pdf:'):
   lines[i]=line+' '+' '.join(n for n in ['hybrid_baseline_summary.tex','hybrid_expert_results.tex','hybrid_expert_appendix.tex'] if n not in line.split());break
 p.write_text('\n'.join(lines)+'\n')
 (report/'hybrid_expert_data.json').write_text(json.dumps(s,indent=2)+'\n')

if __name__=='__main__':main()
