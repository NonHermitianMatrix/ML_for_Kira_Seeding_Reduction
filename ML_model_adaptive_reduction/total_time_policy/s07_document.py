"""Write the current physics result and preserve earlier measured evidence."""
from s00_cost_common import *

def main():
 s=READ(HERE/'summary.json');f=READ(HERE/'trained_model/freeze.json');report=ROOT/'report';tot=s['totals'];comp=s['comparisons'];n=s['requested']
 def desc(g,m):
  v=comp[g][m]
  if not v['cases']:return 'No completed matched requests support this comparison.'
  lo,hi=v['repeat_interval'];direction='less' if v['ratio']<1 else 'more'
  return f"On {v['cases']} matched requests, the application uses {v['learned_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for {m} choices, or {abs(v['reduction_percent']):.1f}\\% {direction} time. The time ratio is {v['ratio']:.3f}, with repetition interval $[{lo:.3f},{hi:.3f}]$."
 def inference(m):
  v=comp['ml'][m]
  if not v['cases']:return 'Validation disables learned choices in the deployed application.'
  lo,hi=v['repeat_interval']
  if hi<1:return ('The comparison with the best fixed choice resolves an added ML saving beyond repetition variation.' if m=='fixed' else 'The complete application resolves a saving over the native-bound control beyond repetition variation.')
  if lo>1:return f'The matched comparison with {m} choices resolves an increase in time.'
  return f'The matched comparison with {m} choices does not resolve a difference beyond repetition variation.'
 action_names={'native':'basis-compatible native bounds','raw_native':'the original native bounds','rank_plus':'an increased numerator-rank bound','expanded':'an enlarged region','truncate':'a truncated region','truncate_rank_plus':'a truncated region with increased numerator rank','truncate_relaxed':'a relaxed truncation'}
 model=f"a cost-sensitive {'tree' if len(f['trees'])==1 else 'forest of '+str(len(f['trees']))+' trees'}"
 text=r'''\section{Selecting the method by complete reduction time}
\label{sec:total-time}
The preceding comparison exposed a mismatch between the historical training labels and the deployed master-basis checks. Restricted choices could appear inexpensive in training and then require recovery in the application. We therefore collect new timings with the current exact checks and train a selector to minimize the measured total cost. Exact formulas and independent-loop factorization remain the first steps. For each remaining loop block, the selector can retain native Kira settings or choose a different seed region. Kira performs the algebra and verifies the required master basis in every case.

\subsection{Training and integration}
We measure seven settings: the original native bounds, basis-compatible native bounds, an increased numerator-rank bound, an enlarged region, and three subsector-truncation choices. The six adjusted candidates contain the supplied master indices. The original bounds remain available when enlarging the region would add unnecessary work. The learned and fixed controls share all seven candidates. Appendix~\ref{app:total-time} derives the adjustment and the learning objective. The exact formulas retain their assumptions from Appendix~\ref{app:blocks13}; the new selector does not extend their mathematical domain.

The model receives the 44 structural inputs used above and seven summaries of the supplied master basis. These additional inputs describe its size, positive-power bounds, numerator ranks, dots, truncation limit, and differences from the target bounds. No family name or parameter-profile identifier enters the features. Each candidate action is timed through process completion and an independent exact coefficient check, including failed attempts and recovery. We use one repetition for each training action and two for each validation action. Unverified outcomes receive a declared training penalty and remain in the evidence.

''' + f"The collection contains {f['training_requests']} training requests and {f['validation_requests']} validation requests, with separate rational parameter profiles and symbolic dimension. It covers vacuum, two-point, and scattering structures through three loops. Pentagon requests are absent from both sets. We fit trees with maximum depths one through five and minimum leaf sizes two, four, or seven, using either one tree or sixteen trees. The split objective minimizes elapsed reduction cost. Validation selects {model} with maximum depth {f['selection']['depth']} and minimum leaf size {f['selection']['minimum']}. It also selects the anchor action and decision margin. It compares the selected method with the fastest fixed candidate before enabling prediction. The selected fixed action is "+action_names[f['fixed_action']]+'. ' + f"The validation totals are {f['validation_selected_seconds']:.3f} seconds for the selected application, {f['validation_native_seconds']:.3f} for native choices, and {f['validation_fixed_seconds']:.3f} for the fixed candidate. The model changes the best fixed action on {f['selection']['changed']} of the {f['validation_requests']} validation requests. These are model-selection measurements.\n\n" + r'''The application loads model weights and computes predictions only for a block that needs native algebra. An exact formula therefore incurs no model prediction. Identical independent blocks share one reduction within the request, and the resulting product remains factored. A structural-range check sends inputs outside the training ranges to native settings. The selector also retains native settings when no checked master basis is available. These rules avoid unsupported learned choices; they do not establish that an unseen integral will reduce quickly.

\subsection{Reserved comparison}
We freeze the weights and decision rules before using the new test profiles. Every request compares the learned application, native choices, a validation-selected fixed choice, and the previously published application. The first three methods use identical exact formulas, basis checks, and recovery code. The native control uses the original seed bounds; the learned and fixed methods choose from the same seven candidates. The comparison with the best fixed choice therefore measures the added request-dependent decision. The previous application also differs in basis-aware seeding and model implementation, so that comparison measures the complete update.

''' + f"The test contains {n} requests. It includes new target shapes and parameter values, the held-out pentagon structure, independent products through thirteen loops, the specified analytic families at every order, and the previously difficult three-loop ladder. Each method runs three times in rotated order on the same worker. A method that fails its first exact check receives no further repetitions for that request. The learned application completes all three checks on {tot['learned']['verified_requests']} requests; Table~\\ref{{tab:total-time}} retains the other outcomes.\n\n" + desc('all','previous')+' '+desc('ml','native')+' '+desc('ml','fixed')+' '+inference('native')+' '+inference('fixed')+'\n\n'
 text+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete-time comparison on the same requested workload. The first-pass column includes one timed attempt for every request, including unverified outcomes. Each ratio divides the summed request medians for the learned method by those for the listed method, using only their matched exact completions.}
\label{tab:total-time}
\begin{tabular}{@{}lrrrr@{}}\toprule
Method & Verified requests & First pass (s) & Learned/method & Failed calls\\\midrule
'''
 for m,name in [('previous','Previous application'),('native','Native choices'),('fixed','Fixed choice'),('learned','Learned selector')]:
  v=comp['all'][m] if m!='learned' else comp['all']['native'];t=tot[m];matched=v.get('ratio',0) if m!='learned' else 1.
  text+=f"{name} & {t['verified_requests']}/{n} & {t['first_pass_seconds']:.3f} & {matched:.3f} & {t['failed_native_attempts']}\\\\\n"
 text+=r'''\bottomrule\end{tabular}
\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/total_time_selection.pdf}
\caption{The left panel separates the complete application change from the added learned choice. Each point uses completed matched requests; bars show variation from resampling the three repetitions, and the dashed line marks equal time. The right panel includes one attempt for every requested calculation. Its labels give elapsed seconds and verified coverage, so an unfinished request cannot appear as a successful speedup.}
\label{fig:total-time}
\end{figure}
'''
 text+=r"""\begin{table}[!htbp]\centering\small
\caption{Use of the selector in each physical domain. The pentagon row is a subset of coupled requests. The ratio uses only matched requests that invoke the model, with the best fixed candidate as control. A dash means that no such comparison exists.}
\label{tab:total-domains}
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
 (report/'total_time_results.tex').write_text(text)
 (report/'total_time_appendix.tex').write_text((HERE/'total_time_appendix.tex').read_text())
 # Preserve current document fragments before replacing the current summary.
 for name in ['paper_abstract.tex','paper_conclusion.tex']:
  saved=report/('before_total_time_'+name)
  if not saved.exists():saved.write_text((report/name).read_text())
 brief=desc('all','previous')+' '+desc('ml','native')+' '+desc('ml','fixed')
 abstract=r'''\begin{abstract}
Integration-by-parts reduction expresses Feynman integrals in a master basis~\cite{KiraOriginal}. We combine exact reductions with a learned choice of Kira seed settings and train that choice on complete elapsed time. The model uses integral structure and the required master basis; its training cost includes unsuccessful attempts and recovery. Exact formulas handle their supported families before any prediction, while native Kira settings remain available for other inputs. '''+f"The new test contains {n} requests, and the learned application completes three exact checks on {tot['learned']['verified_requests']}. "+brief+' '+inference('fixed')+r''' The comparison includes model use, equation generation, algebra, exact checks, and recovery; master-basis and reference preparation precede these timers. We keep the dimension symbolic and use rational values for other kinematic variables. Specified formulas and independent products extend the checked range through thirteen loops, while coupled native tests reach three loops. General high-loop scattering and globally minimum reduction paths remain unverified. Earlier local seed and equation models give separate measured savings; the application retains native row selection because the tested row models give no reliable complete-time gain.
\end{abstract}
'''
 (report/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
The integrated method uses an exact formula when its assumptions hold, reduces each distinct independent loop block once, and chooses a seed setting for the remaining Kira work. We retrain this choice from complete application timings with the current master-basis checks. The basis summaries and compatible seed bounds address a concrete source of recovery cost in the previous model. The cost-sensitive training objective rewards completed reductions that take less time, and validation can leave the fixed or native method active.

'''+brief+' '+inference('native')+' '+inference('fixed')+'\n\n'+f"The first pass over every request takes {tot['learned']['first_pass_seconds']:.3f} seconds with the learned application and {tot['native']['first_pass_seconds']:.3f} seconds with native choices. Both the completion counts and unfinished work enter the reported comparison. Reference preparation and model training remain separate costs, so the result describes use with an existing checked basis.\n\n"+r'''The analytic reductions and independent products reach thirteen loops within their stated assumptions. They do not demonstrate a general high-loop scattering reduction. The native comparison keeps exact algebra responsible for the coefficients and preserves less restrictive recovery settings when a selected region fails. Earlier seed and equation-selection gains remain separate results, and the present workflow retains native row and equation choices. The measurements identify which parts of this application benefit from selection and which costs remain; they establish no globally fastest method for every integral accepted by Kira.
'''
 (report/'paper_conclusion.tex').write_text(conclusion)
 p=report/'report.tex';t=p.read_text().replace(r'\date{October 17, 2026}',r'\date{October 18, 2026}')
 if r'\input{total_time_results}' not in t:t=t.replace(r'\input{factorized_results}',r'\input{factorized_results}'+'\n\\input{total_time_results}')
 if r'\input{total_time_appendix}' not in t:t=t.replace(r'\input{factorized_appendix}',r'\input{factorized_appendix}'+'\n\\input{total_time_appendix}')
 t=t.replace('We then extend the application through thirteen loops for specified coupled, factorable, and analytic families.','We then extend the application through thirteen loops for specified factorable and analytic families, and retrain the final selector on complete timings with the current master-basis checks.')
 p.write_text(t)
 selection_label=f['selection']['name'].replace('_',r'\_')
 notes=r'''\section{Details of complete-time selection}
\label{app:total-time-details}
The training parameter profile is 1901 and the validation profile is 1907. Training targets use dots, a dot with one numerator power, and numerator rank two; exact formulas remove some requests before native collection. Validation uses the first two shapes. Reserved native requests use profile 2011 and additionally include pinched targets; products use $2027+4L$, analytic requests use 2039, and the three-loop ladder uses 2053. No reserved measurement changes the trained selector. We collected the unadjusted native-bound candidate after the six adjusted candidates, before model fitting. The reserved comparison then times all four methods in rotated order on the same worker for each request.

The candidates use seven seed settings, thirty tree or forest structures, two possible anchor settings where distinct, and margins $0$, $0.03$, $0.08$, or $0.15$. A forest draws sixteen bootstrap samples, each the size of the training collection, and samples fourteen features at each node. Leaves store mean complete costs. A single tree examines all features. Threshold searches use at most seventeen feature values. The split must save more than $0.002$ seconds per request in its training node. The feature-range guard checks loop and external-momentum counts, index counts, symbolic-invariant counts, maximum dots and rank, positive-index counts, massive and coupled denominators, loop incidence and degree, maximum positive-power sum, target-sector deficit, and the basis dot gap.

'''+f"Validation chooses {selection_label}. Model fitting takes {f['fit_seconds']:.3f} seconds; the timed collection of native training labels is a separate cost. The deployment flag is "+('enabled' if f['enabled'] else 'disabled')+r'''. The table below preserves coverage at every loop order.
\begin{center}\small
\begin{tabular}{@{}rrrrr@{}}\toprule
Loops & Requested & Learned verified & Native verified & Fixed verified\\\midrule
'''
 for L,v in s['by_loop'].items():notes+=f"{L} & {v['requested']} & {v['verified']['learned']} & {v['verified']['native']} & {v['verified']['fixed']}\\\\\n"
 notes+=r'\bottomrule\end{tabular}\end{center}'+'\n'
 (report/'notes_total_time.tex').write_text(notes)
 p=report/'notes.tex';t=p.read_text()
 addition='\\input{total_time_results}\n\\input{total_time_appendix}\n\\input{notes_total_time}\n'
 marked='% BEGIN CURRENT WORKFLOW UPDATE\n% TOTAL TIME SELECTION\n'+addition+'% END CURRENT WORKFLOW UPDATE\n'
 if '% TOTAL TIME SELECTION' not in t:
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
 p=report/'Makefile';t=p.read_text();t=t.replace('report.pdf: factorized_results.tex','report.pdf: total_time_results.tex total_time_appendix.tex factorized_results.tex');p.write_text(t)
 (report/'total_time_data.json').write_text(json.dumps(s,indent=2)+'\n')
 print(json.dumps(dict(report_written=True,requested=n,model_enabled=f['enabled'])),flush=True)
if __name__=='__main__':main()
