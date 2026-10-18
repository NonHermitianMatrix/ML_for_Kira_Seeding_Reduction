"""Write the current physics result and preserve earlier measured evidence."""
from s00_cost_common import *

def main():
 s=READ(HERE/'summary.json');f=READ(HERE/'trained_model/freeze.json');report=ROOT/'report';tot=s['totals'];comp=s['comparisons'];n=s['requested']
 def desc(g,m):
  v=comp[g][m]
  if not v['cases']:return 'No completed matched requests support this comparison.'
  lo,hi=v['repeat_interval'];direction='less' if v['ratio']<1 else 'more'
  method_name={'previous':'the previous application','native':'native bounds','fixed':'the best fixed setting'}[m]
  return f"On {v['cases']} matched requests, the application uses {v['learned_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for {method_name}, or {abs(v['reduction_percent']):.1f}\\% {direction} time. The time ratio is {v['ratio']:.3f}, with repetition interval $[{lo:.3f},{hi:.3f}]$."
 def inference(m):
  v=comp['ml'][m]
  if not v['cases']:return 'No matched completed request invokes the model, so this comparison does not measure an added learned choice.'
  lo,hi=v['repeat_interval']
  if hi<1:return ('The comparison with the best fixed choice resolves an added ML saving beyond repetition variation.' if m=='fixed' else 'The complete application resolves a saving over the native-bound control beyond repetition variation.')
  if lo>1:return f'The matched comparison with {m} choices resolves an increase in time.'
  return f'The matched comparison with {m} choices does not resolve a difference beyond repetition variation.'
 comparison_group='ml' if comp['ml']['fixed']['cases'] else 'all'
 evidence=desc('all','previous')+' '+desc(comparison_group,'native')+' '+desc(comparison_group,'fixed')
 interpretation=(inference('native')+' '+inference('fixed') if f['enabled'] else 'Validation leaves prediction off. These measurements describe the fixed workflow and do not establish an added gain from the fitted forest.')
 action_names={'checked_truncate':'a truncation with the tighter basis condition','checked_truncate_rank':'a truncation with the tighter basis condition and increased rank','native':'basis-compatible native bounds','raw_native':'the original native bounds','rank_plus':'an increased numerator-rank bound','expanded':'an enlarged region','truncate':'a truncated region','truncate_rank_plus':'a truncated region with increased numerator rank','truncate_relaxed':'a relaxed truncation'}
 model=f"a cost-sensitive {'tree' if len(f['trees'])==1 else 'forest of '+str(len(f['trees']))+' trees'}"
 model_sentence=(f"Validation selects {model} with maximum depth {f['selection']['depth']} and minimum leaf size {f['selection']['minimum']}. It also selects the anchor action and decision margin." if f['enabled'] else "Validation retains the fixed setting because the fitted candidates do not meet the declared improvement threshold. The deployed application therefore performs no tree prediction.")
 text=r'''\section{Selecting the method by complete reduction time}\label{sec:total-time}
\label{sec:refined-time}
The target integrals and required master basis determine which seed regions can support a reduction. A region that excludes a required master can cause an unsuccessful attempt and a repeat calculation. We therefore include basis information in both the model inputs and the candidate settings, and train the model to minimize the complete time after recovery. Kira's subsector cutoff admits numerator ranks zero and one, and can also admit a master through an explicitly assigned sector limit~\cite{Kira3}. Two candidates use this condition to retain the required masters with the least enlargement of that cutoff. The selector compares their measured cost with seven other settings. Exact formulas and independent-loop factorization precede prediction, and Kira computes the coefficients for each remaining native block.

\subsection{Training and integration}
The nine settings include the original native bounds, six conservative basis-compatible candidates, and two candidates with the tighter cutoff condition. The new pair uses the ordinary or increased numerator-rank bound. Appendix~\ref{app:refined-time} derives the new condition from Kira's cutoff, while Appendix~\ref{app:total-time} gives the shared timing objective and structural inputs. Every candidate retains the exact basis check and recovery code. The exact formulas retain their assumptions from Appendix~\ref{app:blocks13}.

The model receives the 44 structural inputs used above and seven summaries of the supplied master basis. These additional inputs describe its size, positive-power bounds, numerator ranks, dots, truncation limit, and differences from the target bounds. No family name or parameter-profile identifier enters the features. Each candidate action is timed through process completion and an independent exact coefficient check, including failed attempts and recovery. We use one repetition for each training action and two for each validation action. Unverified outcomes receive a declared training penalty and remain in the evidence.

''' + f"The collection contains {f['training_requests']} training requests and {f['validation_requests']} validation requests, with separate rational parameter profiles and symbolic dimension. It covers vacuum, two-point, and scattering structures through three loops. Pentagon requests are absent from both sets. We fit trees with maximum depths one through five and minimum leaf sizes two, four, or seven, using either one tree or sixteen trees. The split objective minimizes elapsed reduction cost. {model_sentence} It compares the selected method with the fastest fixed candidate before enabling prediction. The selected fixed action is "+action_names[f['fixed_action']]+'. ' + f"The validation totals are {f['validation_selected_seconds']:.3f} seconds for the selected application, {f['validation_native_seconds']:.3f} for native choices, and {f['validation_fixed_seconds']:.3f} for the fixed candidate. The model changes the best fixed action on {f['selection']['changed'] if f['enabled'] else 0} of the {f['validation_requests']} validation requests. These are model-selection measurements.\n\n" + r'''The application loads model weights and computes predictions only for a block that needs native algebra. An exact formula therefore incurs no model prediction. Identical independent blocks share one reduction within the request, and the resulting product remains factored. When prediction is enabled, a structural-range check sends inputs outside the training ranges to native settings. The selector also retains native settings when no checked master basis is available. These rules avoid unsupported learned choices; they do not establish that an unseen integral will reduce quickly.

\subsection{Reserved comparison}
We freeze the weights and decision rules before using the new test profiles. Every request compares the learned application, native choices, a validation-selected fixed choice, and the previously published application. The first three methods use identical exact formulas, basis checks, and recovery code. The native control uses the original seed bounds; the learned and fixed methods choose from the same nine candidates. The comparison with the best fixed choice therefore measures the added request-dependent decision. The previous application also differs in basis-aware seeding, model implementation, and output handling, so that comparison measures the complete update.

''' + f"The test contains {n} requests. It includes new target shapes and parameter values, the held-out pentagon structure, independent products through thirteen loops, the two specified analytic families at thirteen loops, and the previously difficult three-loop ladder. Each method runs three times in rotated order on the same worker. A method that fails its first exact check receives no further repetitions for that request. The learned application completes all three checks on {tot['learned']['verified_requests']} requests; Table~\\ref{{tab:refined-time}} retains the other outcomes.\n\n" + evidence+' '+interpretation+'\n\n'
 text+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete-time comparison on the same requested workload. The first-pass column includes one timed attempt for every request, including unverified outcomes. Each ratio divides the summed request medians for the learned method by those for the listed method, using only their matched exact completions.}
\label{tab:refined-time}
\begin{tabular}{@{}lrrrr@{}}\toprule
Method & Verified requests & First pass (s) & Learned/method & Failed calls\\\midrule
'''
 for m,name in [('previous','Previous application'),('native','Native choices'),('fixed','Fixed choice'),('learned','Learned selector')]:
  v=comp['all'][m] if m!='learned' else comp['all']['native'];t=tot[m];matched=v.get('ratio',0) if m!='learned' else 1.
  text+=f"{name} & {t['verified_requests']}/{n} & {t['first_pass_seconds']:.3f} & {matched:.3f} & {t['failed_native_attempts']}\\\\\n"
 text+=r'''\bottomrule\end{tabular}
\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/refined_time_selection.pdf}
\caption{The left panel separates the complete application change from the added learned choice. Each point uses completed matched requests; bars show variation from resampling the three repetitions, and the dashed line marks equal time. The right panel includes one attempt for every requested calculation. Its labels give elapsed seconds and verified coverage, so an unfinished request cannot appear as a successful speedup.}
\label{fig:refined-time}
\end{figure}
'''
 text+=r"""\begin{table}[!htbp]\centering\small
\caption{Use of the selector in each physical domain. The pentagon row is a subset of coupled requests. The ratio uses only matched requests that invoke the model, with the best fixed candidate as control. A dash means that no such comparison exists.}
\label{tab:refined-domains}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Domain & Requested & Verified & Use ML & ML/fixed\\\midrule
"""
 for group,name,mlgroup in [('coupled','Coupled families','coupled_ml'),('products','Independent products','products_ml'),('formula','Analytic formulas',None),('pentagon','Pentagon subset','pentagon_ml')]:
  scope={'coupled':'coupled_family','products':'independent_loop_blocks','formula':'analytic_formula'}
  rows=[r for r in s['rows'] if ('pentagon' in r['family'] if group=='pentagon' else r['scope']==scope[group])]
  v=comp[mlgroup]['fixed'] if mlgroup else {'cases':0};ratio=f"{v['ratio']:.3f}" if v['cases'] else '--'
  text+=f"{name} & {len(rows)} & {sum(r['complete']['learned'] for r in rows)} & {sum(r['model_used']['learned'] for r in rows)} & {ratio}\\\\\n"
 text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 text+=f"Across every timed attempt, the learned application uses {tot['learned']['all_attempt_seconds']:.3f} seconds, native choices use {tot['native']['all_attempt_seconds']:.3f}, the fixed choice uses {tot['fixed']['all_attempt_seconds']:.3f}, and the previous application uses {tot['previous']['all_attempt_seconds']:.3f}. These totals include all recorded repetitions and failures. Independent reference preparation takes {s['reference_preparation_seconds']:.3f} seconds outside the application timers. The existing checked master-basis preparation and training-label collection also precede deployment. The {s['collection']['training']['measurements']+s['collection']['validation']['measurements']} training and validation action measurements use {s['collection']['training']['timed_seconds']+s['collection']['validation']['timed_seconds']:.3f} seconds in total, before independent reference preparation and {f['fit_seconds']:.3f} seconds of model fitting. The supplied-basis comparison therefore measures subsequent reductions, rather than a complete first-use calculation with unknown masters.\n\n"
 text+=r'''The high-loop results remain specific to the defined analytic families and products of small independent blocks. The coupled native tests reach three loops. No result establishes a globally minimum reduction time or complete coverage of arbitrary thirteen-loop scattering. The earlier seed and equation models retain their separate measured domains; the present selector keeps native equation and row choices, and we do not multiply savings from separate experiments.
'''
 (report/'refined_time_results.tex').write_text(text.replace(r'\label{sec:total-time}',''))
 (report/'refined_time_appendix.tex').write_text((HERE/'refined_time_appendix.tex').read_text())
 # Preserve current document fragments before replacing the current summary.
 for name in ['paper_abstract.tex','paper_conclusion.tex']:
  saved=report/('before_refined_time_'+name)
  if not saved.exists():saved.write_text((report/name).read_text())
 brief=evidence
 previous_result=comp['all']['previous'];ml_result=comp['ml']['fixed']
 abstract=r'''\begin{abstract}
Integration-by-parts reduction expresses Feynman integrals in a master basis~\cite{KiraOriginal}. We train a cost-sensitive selector to choose among nine Kira seed settings from the integral structure and required master basis. Training minimizes measured application time, including unsuccessful attempts and recovery. Exact formulas and independent-loop factorization precede prediction, while native settings remain available. '''+f"The reserved comparison contains {n} requests, of which {tot['learned']['verified_requests']} complete three exact checks. "
 if previous_result['cases']:
  direction='less' if previous_result['ratio']<1 else 'more'
  abstract+=f"On matched completions, the updated application uses {abs(previous_result['reduction_percent']):.1f}\\% {direction} time than the previous application. "
 if ml_result['cases']:
  direction='less' if ml_result['ratio']<1 else 'more'
  abstract+=f"On {ml_result['cases']} matched requests that invoke the model, the learned choice uses {ml_result['learned_seconds']:.3f} seconds against {ml_result['control_seconds']:.3f} seconds for the best fixed setting, or {abs(ml_result['reduction_percent']):.1f}\\% {direction} time. "+inference('fixed')+' '
 else:abstract+='Validation retains a fixed setting for deployment. '
 abstract+=r'''The timers include model use, equation generation, algebra, exact checks, and recovery; master-basis preparation and model training precede these measurements. We keep the dimension symbolic and use rational values for the other kinematic variables. The tests cover coupled native families through three loops and specified formulas and independent products through thirteen loops. General high-loop scattering and globally minimum reduction paths remain unverified.
\end{abstract}
'''
 (report/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
The integrated method uses an exact formula when its assumptions hold, reduces each distinct independent loop block once, and chooses a seed setting for the remaining Kira work. We retrain this choice from complete application timings with the current master-basis checks. The basis summaries and compatible seed bounds address a concrete source of recovery cost in the previous model. The cost-sensitive training objective rewards completed reductions that take less time, and validation can leave the fixed or native method active.

'''+brief+' '+interpretation+'\n\n'+f"The first pass over every request takes {tot['learned']['first_pass_seconds']:.3f} seconds with the learned application and {tot['native']['first_pass_seconds']:.3f} seconds with native choices. Both the completion counts and unfinished work enter the reported comparison. Reference preparation and model training remain separate costs, so the result describes use with an existing checked basis.\n\n"+r'''The analytic reductions and independent products reach thirteen loops within their stated assumptions. They do not demonstrate a general high-loop scattering reduction. The native comparison keeps exact algebra responsible for the coefficients and preserves less restrictive recovery settings when a selected region fails. Earlier seed and equation-selection gains remain separate results, and the present workflow retains native row and equation choices. The measurements identify which parts of this application benefit from selection and which costs remain; they establish no globally fastest method for every integral accepted by Kira.
'''
 (report/'paper_conclusion.tex').write_text(conclusion)
 p=report/'report.tex';t=p.read_text().replace(r'\date{October 17, 2026}',r'\date{October 18, 2026}')
 if r'\input{refined_time_results}' not in t:t=t.replace(r'\input{factorized_results}',r'\input{factorized_results}'+'\n\\input{refined_time_results}')
 if r'\input{refined_time_appendix}' not in t:t=t.replace(r'\input{total_time_appendix}',r'\input{total_time_appendix}'+'\n\\input{refined_time_appendix}')
 t=t.replace('We then extend the application through thirteen loops for specified coupled, factorable, and analytic families.','We then extend the application through thirteen loops for specified factorable and analytic families, and retrain the final selector on complete timings with the current master-basis checks.')
 if 'The current complete-time comparison in Section' not in t:
  t=t.replace('The direct local comparisons establish savings',r'The current complete-time comparison in Section~\ref{sec:refined-time} tests seed settings after exact formula and independent-block reduction. Its fixed control isolates the added learned choice under the same exact checks and recovery rules.'+'\n\nThe direct local comparisons establish savings')
 t=t.replace(r'\input{total_time_results}', '')
 t=t.replace(r'\input{refined_time_results}\label{sec:total-time}',r'\input{refined_time_results}')
 t=t.replace(r'\input{refined_time_results}',r'\input{refined_time_results}\label{sec:total-time}')
 p.write_text(t)
 selection_label=f['selection']['name'].replace('_',r'\_')
 notes=r'''\section{Details of complete-time selection}
\label{app:refined-time-details}
The training parameter profile is 2101 and the validation profile is 2107. Training targets use dots, a dot with one numerator power, and numerator rank two; exact formulas remove some requests before native collection. Validation uses the first two shapes. Reserved native requests use profile 2203, with rank-two and pinched targets added for three structures; products use $2213+4L$, the thirteen-loop analytic requests use 2221, and the three-loop ladder uses 2227. The product grid includes all four structures at odd loop orders and one rotating structure at each even order. No reserved measurement changes the trained selector. We time all nine training candidates together in rotated order on the same worker for each request. The reserved comparison also uses rotated method order.

The candidates use nine seed settings, thirty tree or forest structures, two possible anchor settings where distinct, and margins $0$, $0.03$, $0.08$, or $0.15$. A forest draws sixteen bootstrap samples, each the size of the training collection, and samples fourteen features at each node. Leaves store mean complete costs. A single tree examines all features. Threshold searches use at most seventeen feature values. The split must save more than $0.002$ seconds per request in its training node. The feature-range guard checks loop and external-momentum counts, index counts, symbolic-invariant counts, maximum dots and rank, positive-index counts, massive and coupled denominators, loop incidence and degree, maximum positive-power sum, target-sector deficit, and the basis dot gap.

'''+f"Validation chooses {selection_label}. Model fitting takes {f['fit_seconds']:.3f} seconds; the timed collection of native training labels is a separate cost. The deployment flag is "+('enabled' if f['enabled'] else 'disabled')+r'''. The table below preserves coverage at every loop order.
\begin{center}\small
\begin{tabular}{@{}rrrrr@{}}\toprule
Loops & Requested & Learned verified & Native verified & Fixed verified\\\midrule
'''
 for L,v in s['by_loop'].items():notes+=f"{L} & {v['requested']} & {v['verified']['learned']} & {v['verified']['native']} & {v['verified']['fixed']}\\\\\n"
 notes+=r'\bottomrule\end{tabular}\end{center}'+'\n'
 (report/'notes_refined_time.tex').write_text(notes)
 p=report/'notes.tex';t=p.read_text()
 addition='\\input{refined_time_results}\n\\input{refined_time_appendix}\n\\input{notes_refined_time}\n'
 marked='% BEGIN CURRENT WORKFLOW UPDATE\n% REFINED TIME SELECTION\n'+addition+'% END CURRENT WORKFLOW UPDATE\n'
 if '% REFINED TIME SELECTION' not in t:
  t=t.replace(addition,marked) if addition in t else t.replace(r'\bibliographystyle{unsrt}',marked+r'\bibliographystyle{unsrt}')
 p.write_text(t)
 bib=r'''@inproceedings{Xu2011HydraMIP,
 author={Xu, Lin and Hutter, Frank and Hoos, Holger H. and Leyton-Brown, Kevin},
 title={Hydra-MIP: Automated Algorithm Configuration and Selection for Mixed Integer Programming},
 booktitle={Proceedings of the 18th RCRA Workshop},
 year={2011},
 url={https://www.cs.ubc.ca/~kevinlb/papers/2011-HYDRA-MIP.pdf}
}
'''
 for n in ['paper_references.bib','notes_additional_references.bib']:
  p=report/n;t=p.read_text()
  if 'Xu2011HydraMIP' not in t:p.write_text(t+'\n'+bib)
 p=report/'Makefile';t=p.read_text();lines=t.splitlines()
 for i,line in enumerate(lines):
  if line.startswith('report.pdf:'):
   required=[n for n in ['refined_time_results.tex','refined_time_appendix.tex'] if n not in line.split()]
   lines[i]=line+' '+ ' '.join(required);break
 p.write_text('\n'.join(lines)+'\n')
 (report/'refined_time_data.json').write_text(json.dumps(s,indent=2)+'\n')
 print(json.dumps(dict(report_written=True,requested=n,model_enabled=f['enabled'])),flush=True)
if __name__=='__main__':main()
