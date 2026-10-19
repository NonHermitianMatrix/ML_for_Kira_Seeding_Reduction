"""Explain the integral identity, complete-time comparisons, and remaining domains."""
from s00_loop_common import *
REPORT=ROOT/'report'

def main():
 s=read(HERE/'summary.json');assert s['complete'];c=s['comparisons'];tc=s['coverage']['trees'];gc=s['coverage']['grid'];mc=c['batches_ml_off'];dev=s['development']
 method=r'''\section{Reducing connected higher-loop subintegrals exactly}
\label{sec:loop-tree-method}
The previous triangle formula reduces independent products through thirteen loops. Connected integrals require identities that account for their shared loop momenta. We therefore integrate a massless two-line subgraph whenever it belongs to a supported connected tree attached to a one-scale triangle. Analytic integration of massless insertions is an established part of parametric reduction~\cite{Ruijl2017Forcer}. Appendix~\ref{app:loop-tree} derives the identity for the connected vertex family used here, including its signs, scale dependence, and allowed powers.

Each bubble integration removes one loop and transfers a generally noninteger power to its parent line. Repeating this step from the leaves towards the root leaves a triangle whose first power depends on $d$. A Feynman-parameter integral evaluates this triangle. Dividing by the same connected integral with unit physical powers cancels the common Gamma functions, and finite Gamma shifts give a rational coefficient in $d$ and the nonzero external scale. The implementation keeps this coefficient in factored form, which avoids expanding polynomials that would later cancel.

The new family contains stars, chains, and branched trees with one through thirteen loops. All internal lines are massless, two external momenta are lightlike, and their sum has nonzero squared momentum. Positive powers can vary on every physical line. The middle root-triangle power can also be zero or negative, while the auxiliary scalar-product powers remain zero. These conditions define a connected family with an explicit reduction proof. A generic massive insertion or multi-scale root graph needs further identities.

We apply the identity before loading the remaining Kira reduction workflow. If the denominators, kinematics, or powers fall outside its domain, the application uses the preceding exact methods and trained native choices. We retain the existing batch and sparse-seed models without fitting them to the new test results. The added speedup therefore comes from exact integration and its early application. A separate fresh two-loop comparison measures whether the retained learned choices still reduce the remaining native time.
'''
 (REPORT/'loop_coverage13_method.tex').write_text(method)
 results=r'''\section{Connected reductions and coverage through thirteen loops}
\label{sec:loop-tree-results}
The new comparison has three parts. First, 39 requests test connected bubble trees: 34 rational-scale requests cover the distinct star, chain, and branched structures through thirteen loops, and five requests keep the scale symbolic at one, two, three, six, and thirteen loops. Each request contains seven targets: the unit-power integral, three separate positive-power changes, middle-triangle powers zero and minus one, and a simultaneous change of several positive powers. Second, a fresh 110-request grid retains the vacuum, propagator, and scattering definitions of Appendix~\ref{app:families-new} and extends the loop range through thirteen. It includes massive and massless cases, dots, auxiliary numerators, scaleless sectors, and additional symbolic requests. Third, sixteen planar and nonplanar two-loop box batches test the unchanged learned choices at a new kinematic profile.

Every timing starts a fresh process. It includes initialization, domain recognition, model loading and prediction when used, exact reduction, internal checks, recovery, output, and process exit. Independent checks against Gamma expressions or the competing reduction are performed after this application timer. Their cost is benchmark validation overhead and is excluded from both methods. This timer therefore differs from the preceding supplied-basis comparison, which also includes its external reference comparison. We do not combine the two timing totals. Two single-core workers run on shared cluster nodes. Each request compares methods on the same worker, rotates their order, and uses three repetitions for the connected-tree and learned-control tests. The broad coverage grid uses one bounded trial per method. Its completion counts include basis integrals and do not measure how many targets require a nontrivial reduction. The common application limit is twenty seconds; a failed first attempt remains recorded and receives no completed-time ratio.

'''
 results+=f"The development checks compare 42 coefficients exactly with complete symbolic Gamma expressions. Native Kira verifies {dev['native_passes']} of the six requests, supplying {sum(x['native_checks'] for x in dev['rows'])} exact coefficient checks through three loops, including one symbolic-scale request. The remaining three-loop chain reaches the native time limit. The analytic expression passes its symbolic check, and that native timeout remains recorded. Seven tests reject masses, off-shell kinematics, unsupported auxiliary numerators, cuts, symbolic indices, a removed end line, and a cyclic attachment.\n\n"
 results+=f"For the reserved connected trees, independent complete Gamma evaluations check {s['gamma_sample_checks']:,} coefficient values at three dimensions with 80-digit arithmetic. The relative tolerance is $10^{{-60}}$. These evaluations test the implementation; the identity in Appendix~\\ref{{app:loop-tree}} supplies the analytic justification. They are not independent native IBP reductions at high loop order. All {tc['requests']} requests, containing {tc['targets']} target entries, pass these checks and all repeated outputs agree exactly.\n\n"
 results+=r'''\begin{table}[!htbp]\centering\small
\caption{Completion on the fresh requests. The preceding application is the exact-triangle and learned-batch method of Section~\ref{sec:analytic-batch-results}. The broad grid uses one bounded trial. The other collections require three successful repetitions. Failures remain in the denominator.}
\label{tab:loop-tree-completion}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Collection & Requests & New method & Preceding method\\\midrule
'''
 for key,title in [('trees','Connected bubble trees'),('grid','Broader physical grid'),('batches','Fresh native box batches')]:
  z=s['coverage'][key];results+=f"{title} & {z['requests']} & {z['methods']['integrated']['completed']} & {z['methods']['previous']['completed']}"+r' \\'+'\n'
 results+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 results+=r'''\begin{table}[!htbp]\centering\small
\caption{Application times on completed, checked pairs. Times are sums of request medians in seconds. The ML-off control keeps the same exact methods and fixed sparse action. The learned-control row measures both retained native learned choices together.}
\label{tab:loop-tree-times}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Comparison & Pairs & New & Control & Ratio\\\midrule
'''
 for key,title in [('trees','Connected trees / preceding'),('batches_previous','Box batches / preceding'),('batches_ml_off','Box batches / ML off')]:
  v=c[key]
  if v['pairs']:results+=f"{title} & {v['pairs']} & {v['new_seconds']:.3f} & {v['control_seconds']:.3f} & {v['ratio']:.3f}"+r' \\'+'\n'
 results+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 v=c['trees'];lo,hi=s['tree_median_seconds_range']
 results+=f"The connected-tree application takes between {1000*lo:.1f} and {1000*hi:.1f} milliseconds per seven-target request across the tested orders. "
 if v['pairs']:results+=f"On {v['pairs']} pairs completed by both methods, its summed median is {v['new_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds, a speed factor of {v['speedup']:.2f}. "
 results+='The application also returns coefficients for connected requests that the preceding method cannot complete within the declared bounds. Those additional completions have no finite speed factor against a completed control. The matched timings include the exact identity, its one-element basis, and earlier dispatch, so they do not assign every saved second to algebra alone.\n\n'
 if mc['pairs']:
  lo,hi=mc['request_interval'];direction='less' if mc['ratio']<1 else 'more'
  results+=f"On the sixteen fresh native box batches, the retained ML choices use {abs(mc['saving_percent']):.1f}\\% {direction} time than the fixed control. The ratio is {mc['ratio']:.3f}, with request-resampling interval $[{lo:.3f},{hi:.3f}]$. "
  results+=('The interval includes equal time, so this small fresh sample does not resolve a reliable added ML gain. ' if lo<=1<=hi else 'This interval describes variation among the tested requests and does not establish transfer to other graph classes. ')
  results+=f"The learned method is slower on {mc['slower_requests']} individual batches. These results remain separate from the preceding forty-request result, where the added batch choice saved 2.7\\% against its fixed-action control.\n\n"
 results+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/loop_coverage13_time.pdf}
\caption{The connected bubble-tree formula avoids a growing IBP system. Each point is the median complete application time for seven targets at the indicated loop count. The curves show rational-scale requests; the five symbolic requests enter the completion and check totals. Three repetitions measure process-level variation.}
\label{fig:loop-tree-time}
\end{figure}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/loop_coverage13.pdf}
\caption{Finite coverage at each loop order. ``All'' means that the method completed every request in that cell, and zero means none completed. A dash marks an omitted duplicate one-loop definition. The connected-tree row includes rational and symbolic requests; the other rows show the main rational grid. Additional scattering and symbolic cases remain included in Table~\ref{tab:loop-tree-completion}. The figure describes these defined targets, not all integrals at that order.}
\label{fig:loop-tree-coverage}
\end{figure}
'''
 results+=r'''\begin{table}[!htbp]\centering\small
\caption{Completion by loop order on the full broader grid and the added connected trees. Each entry gives completed requests divided by requested cases for the new method. The preceding-method column applies to the broader grid.}
\label{tab:loop-tree-orders}
\begin{tabular}{@{}rrrr@{}}\toprule
Loops & Broader grid & Preceding grid & Connected trees\\\midrule
'''
 for L in range(1,14):
  a=s['by_loop']['grid'][str(L)];b=s['by_loop']['trees'][str(L)];results+=f"{L} & {a['new']}/{a['requests']} & {a['previous']}/{a['requests']} & {b['new']}/{b['requests']}"+r' \\'+'\n'
 results+=r'\bottomrule\end{tabular}\end{table}'+'\n\n'
 results+=f"The broader grid completes {gc['methods']['integrated']['completed']} of 110 requests with the new method and {gc['methods']['previous']['completed']} with the preceding application. "
 results+='The unresolved cases include general massive multi-loop integrals and multi-scale scattering structures that do not have the proved bubble-tree form. The input limits of the configured native path and application deadlines remain explicit outcomes. A complete scalar-product basis can exceed the index limit of that path even when an analytic subintegral formula remains valid. Thus loop count alone does not determine whether the reduction succeeds. The new result extends a connected analytic domain through thirteen loops; it does not establish acceleration for every integral type.\n\\FloatBarrier\n'
 (REPORT/'loop_coverage13_results.tex').write_text(results)
 (REPORT/'loop_coverage13_appendix.tex').write_bytes((HERE/'loop_coverage13_appendix.tex').read_bytes())
 (REPORT/'loop_coverage13_data.json').write_text(json.dumps(s,indent=2)+'\n')
 q=REPORT/'report.tex';z=q.read_text()
 if '\\input{loop_coverage13_method}' not in z:z=z.replace('\\section{Training and comparison design}','\\input{loop_coverage13_method}\n\n\\section{Training and comparison design}')
 if '\\input{loop_coverage13_results}' not in z:z=z.replace('\\section{Overall interpretation}','\\input{loop_coverage13_results}\n\n\\section{Overall interpretation}')
 if '\\input{loop_coverage13_appendix}' not in z:z=z.replace('\\input{analytic_batch_appendix}','\\input{analytic_batch_appendix}\n\\input{loop_coverage13_appendix}')
 z=z.replace('The latest comparison adds a derived triangle formula and trains a complete-cost model to choose shared native reductions. It tests new two-loop target batches, symbolic triangle kinematics, and independent products through thirteen loops.','We first derive a triangle formula and train a complete-cost model to choose shared native reductions. We then extend exact integration to connected massless bubble trees through thirteen loops and test the unchanged learned choices on fresh two-loop batches.')
 z=z.replace('The latest comparison in Section~\\ref{sec:analytic-batch-results}','The batch comparison in Section~\\ref{sec:analytic-batch-results}')
 marker='\\section{Overall interpretation}\n\\label{sec:overall-new}\n'
 if 'The connected-tree calculation in Section~' not in z:z=z.replace(marker,marker+r'''The connected-tree calculation in Section~\ref{sec:loop-tree-results} extends the exact physical domain before further native work. Its proof identifies the allowed integrals, and its coverage table states what the application actually completes at each loop order. The fresh two-loop control then measures the retained ML contribution on work that still needs Kira. This division follows the mathematical structure of the integrals and keeps the sources of time savings separate.

''')
 z=z.replace('Every reported paired timing ratio uses identical targets, kinematics, and final master bases for its competing methods.','The earlier native paired comparisons use identical targets, kinematics, and final master bases. The connected-tree comparison reduces identical physical integrals into each method\'s selected basis. Its external check expresses the new unit-power master in the preceding basis and verifies every target coefficient; the application timer excludes that benchmark conversion.')
 q.write_text(z)
 abstract=r'''\begin{abstract}
We study how exact integral identities and machine learning can reduce the time needed to express loop integrals in terms of master integrals with Kira. The method first integrates supported subgraphs analytically, then uses trained choices to select the remaining native reduction work. We derive rational reduction coefficients for connected massless bubble trees attached to a one-scale triangle. Repeated bubble integration transfers dimension-dependent powers to the root, and a triangle parameter integral closes the reduction. Integer shifts of Gamma functions give finite products, so the coefficients remain exact. '''
 abstract+=f"All 39 new connected-tree requests through thirteen loops pass the stated checks. Exact native checks cover five development requests through three loops; the higher-loop tests use the derived identity and independent high-precision Gamma evaluations. "
 if v['pairs']:abstract+=f"On {v['pairs']} connected requests completed by both applications, the new method takes {v['new_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for the preceding method. "
 abstract+=f"The separate broad grid completes {gc['methods']['integrated']['completed']} of 110 requests, retaining all failures and unsupported cases. "
 if mc['pairs']:abstract+=f"On sixteen fresh two-loop box batches, the retained learned choices have time ratio {mc['ratio']:.3f} against the same exact workflow with fixed native choices. "
 abstract+=r'''Earlier controlled tests establish separate gains for seed and equation selection. Learned row selection remains omitted because its measured improvement is unresolved. The new connected result has explicit mass, kinematic, and numerator restrictions; it does not establish a universal speedup for arbitrary thirteen-loop scattering integrals.
\end{abstract}
'''
 (REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
The integral structure determines which work can be removed exactly and which work remains for a learned choice. For the connected massless bubble trees studied here, successive two-line integrations and a final triangle integral give rational reduction coefficients without generating a large IBP system. The proof applies to the stated rooted-tree family, and the tests cover stars, chains, and branched attachments through thirteen loops, including a symbolic external scale.

'''
 conclusion+=f"All 39 connected requests complete, with seven targets in each request. The broader grid completes {gc['methods']['integrated']['completed']} of 110 requests. General massive and multi-scale graphs still produce failures or exceed the native input limits. These outcomes prevent a claim of speedup for every integral type.\n\n"
 conclusion+=f"The fresh native comparison gives a time ratio of {mc.get('ratio',float('nan')):.3f} for retained ML against fixed choices on sixteen two-loop box batches. "
 if mc['pairs'] and mc['request_interval'][0]<=1<=mc['request_interval'][1]:conclusion+='Its request interval includes equal time, so this fresh sample does not by itself establish a reliable gain. '
 conclusion+=r'''The preceding forty-box comparison found 2.7\% less time from the added batch decision under its own timer, while the earlier local seed and equation comparisons retain their separate measured gains. These ratios use different workloads and controls and cannot be multiplied into a universal speed factor. Learned row selection remains excluded.

The resulting workflow uses exact identities where their physical assumptions hold and measured learned decisions where native reduction remains necessary. This extends connected high-loop coverage while preserving the existing native path. The remaining task is to derive or validate reductions for physical structures outside the supported domains; increasing loop count alone does not supply those identities.
'''
 (REPORT/'paper_conclusion.tex').write_text(conclusion)
 bib=r'''@misc{Ruijl2017Forcer,
  author = {Ruijl, Ben and Ueda, Takahiro and Vermaseren, Jos A. M.},
  title = {{Forcer}, a {FORM} program for the parametric reduction of four-loop massless propagator diagrams},
  year = {2017},
  eprint = {1704.06650},
  archivePrefix = {arXiv},
  primaryClass = {hep-ph},
  doi = {10.48550/arXiv.1704.06650}
}
'''
 for name in ['paper_references.bib','notes_additional_references.bib']:
  q=REPORT/name
  if 'Ruijl2017Forcer' not in q.read_text():q.write_text(q.read_text().rstrip()+'\n\n'+bib)
 for name in ['method','results','appendix']:
  z=(REPORT/f'loop_coverage13_{name}.tex').read_text()
  for prefix in ['sec:loop-tree','app:loop-tree','eq:loop-tree','tab:loop-tree','fig:loop-tree','sec:analytic-batch','app:analytic-batch']:z=z.replace(prefix,prefix.replace(':',':notes-'))
  z=z.replace('of Eq.~\\eqref{eq:integral}','of the integral definition in these notes')
  (REPORT/f'notes_loop_coverage13_{name}.tex').write_text(z)
 q=REPORT/'notes.tex';z=q.read_text();addition=''.join('\\input{notes_loop_coverage13_'+n+'}\n' for n in ['method','results','appendix'])
 if addition not in z:z=z.replace('\\bibliographystyle','% BEGIN CURRENT WORKFLOW UPDATE\n'+addition+'% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle',1)
 q.write_text(z)
 q=REPORT/'Makefile';z=q.read_text();line=next(x for x in z.splitlines() if x.startswith('report.pdf:'))
 if 'loop_coverage13_results.tex' not in line:z=z.replace(line,line+' loop_coverage13_method.tex loop_coverage13_results.tex loop_coverage13_appendix.tex')
 q.write_text(z)
 for q in [REPORT/'report.tex',REPORT/'notes.tex',REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex',*REPORT.glob('*loop_coverage13*.tex')]:q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 print(json.dumps(dict(documents_updated=True)),flush=True)
if __name__=='__main__':main()
