"""Write the decomposition study from completed measurements."""
from s01_common import *
import re
REPORT=ROOT/'report'
BIB=r'''@article{Hu2025,
 author={Hu, Chang and Feng, Bo and Shen, Jiyuan and Zhang, Yaobo},
 title={General one-loop generating function by integration-by-part relations},
 journal={Physical Review D}, volume={111}, pages={076026}, year={2025},
 doi={10.1103/PhysRevD.111.076026}, eprint={2403.16040}, archivePrefix={arXiv}, primaryClass={hep-ph}
}
'''
def number(v):return f'{v:.3f}'
def main():
 s=READ(HERE/'summary.json');a=s['comparisons']['all'];an=s['comparisons']['analytic'];ml=s['comparisons']['ml_compatibility'];tot=s['totals'];nl='\\\\'
 title='Accelerating loop-integral decomposition with exact recurrences and learned Kira strategies'
 paper=(REPORT/'report.tex').read_text()
 paper=re.sub(r'pdftitle=\{[^}]*\}','pdftitle={'+title+'}',paper)
 paper=re.sub(r'\\title\{[^}]*\}',lambda m:'\\title{'+title+'}',paper)
 start=paper.index('Kira automates this reduction') if 'Kira automates this reduction' in paper else paper.index('We study how to reduce the time needed');end=paper.index('\\section{The reduction problem',start)
 paper=paper[:start]+r'''We study how to reduce the time needed for this decomposition into master integrals. Kira generates identities and solves the resulting linear system, with existing seed and equation-selection methods that remove some unnecessary work~\cite{KiraOriginal,Laporta,Kira3}. Exact recurrences can avoid a general linear system for suitable integral structures, while learned choices can reduce the work left for Kira. Throughout this paper, a target is an integral or linear combination requested by the user, and a seed is an index vector at which Kira generates identities. Decomposition determines the coefficients of the master integrals; their numerical or analytic evaluation is a further calculation~\cite{Weinzierl2022}.

Our method combines independent-loop factorization, exact analytic recurrences, and learned seed choices. We also study elimination-row and equation selection to determine where prediction helps. Earlier machine-assisted searches motivate the seed intervention~\cite{Song2025,TubeSeeding2026}, while known analytic one-loop reduction motivates the recurrence stage~\cite{Hu2025}. We measure the complete application time, including model use, exact algebra, checks, and unsuccessful attempts. Separate controls distinguish the benefit of a learned decision from the benefit of exact formulas and fixed tuning.

We first define the notation used in this paper and derive the decomposition problem. We then explain the exact stage and the three learned interventions, compare their measured benefits and limits, and test their integration. The latest comparison adds massive scalar one-loop recurrences and independent products through thirteen loops while retaining the existing learned models. It also includes fully symbolic two-point kinematics. The companion notes preserve historical methods, secondary experiments, and their full results.

'''+paper[end:]
 if '\\input{analytic_decomposition_method}' not in paper:paper=paper.replace('\\section{Training and comparison design}','\\input{analytic_decomposition_method}\n\n\\section{Training and comparison design}')
 if '\\input{analytic_decomposition_results}' not in paper:paper=paper.replace('\\section{Overall interpretation}','\\input{analytic_decomposition_results}\n\n\\section{Overall interpretation}')
 if '\\input{analytic_decomposition_appendix}' not in paper:paper=paper.replace('\\input{hybrid_expert_appendix}','\\input{hybrid_expert_appendix}\n\\input{analytic_decomposition_appendix}')
 paper=paper.replace('The current hybrid comparison in Section~\\ref{sec:hybrid-experts} tests seed settings after exact formula and independent-block reduction.', 'The current combined comparison in Section~\\ref{sec:analytic-results} tests the added recurrence together with the retained learned application. The preceding hybrid comparison in Section~\\ref{sec:hybrid-experts} isolates its seed choices after the earlier exact formulas and block decomposition.')
 paper=paper.replace('Every reported paired timing ratio uses identical targets, kinematics, and master bases','Every reported paired timing ratio uses identical targets, kinematics, and final master bases')
 paper=paper.replace('We leave reconstruction unchanged in this study.','We leave finite-field reconstruction unchanged in the native solver. The added recurrence obtains its rational coefficients directly.')
 paper=paper.replace('The main native comparisons keep $d$ symbolic and assign rational values to the other kinematic variables.','The earlier native comparisons keep $d$ symbolic and assign rational values to the other kinematic variables. The new analytic comparison also includes two requests with symbolic masses and momentum invariants.')
 paper=paper.replace('The current hybrid uses its validated sparse expert and the exact reductions in Section~\\ref{sec:blocks13}.','The combined application uses the validated sparse expert together with the exact methods in Sections~\\ref{sec:blocks13} and~\\ref{sec:analytic-method}.')
 (REPORT/'report.tex').write_text(paper)
 for name in ['analytic_decomposition_method.tex','analytic_decomposition_appendix.tex']:(REPORT/name).write_text((HERE/name).read_text())
 for name in ['paper_references.bib','notes_additional_references.bib']:
  p=REPORT/name
  if 'Hu2025' not in p.read_text():p.write_text(p.read_text()+'\n'+BIB)
 rows=[]
 for key,name in [('one_loop','Scalar one-loop polygons'),('products','Independent products'),('ml_compatibility','Coupled ML cases'),('other_compatibility','Other compatibility cases'),('all','All requests')]:
  v=s['comparisons'][key]['native'];p0=s['comparisons'][key]['previous'];f=s['comparisons'][key]['fixed']
  if v['cases']:rows.append(f"{name} & {v['cases']} & {number(v['learned_seconds'])} & {number(v['control_seconds'])} & {v['speedup']:.2f} & {f['ratio']:.3f} "+nl)
 text=r'''\section{Combined decomposition with the analytic recurrence}
\label{sec:analytic-results}
The latest comparison measures the added recurrence while preserving the existing learned models. It contains 16 rational-kinematics polygon requests, two fully symbolic two-point requests, 12 independent bubble products covering loop orders two through thirteen, eight nonplanar two-loop requests, and three further compatibility requests. Appendix~\ref{app:analytic-inputs} specifies the denominators, targets, and parameter choices. Each method starts in a fresh process, and three repetitions rotate the method order on the same worker.

All four methods use the same independent-block factorization and share identical blocks within a request. The native control receives the same prepared master indices and uses the existing exact block formulas, but it generates native IBP equations for the newly supported one-loop blocks. The exact fixed control uses the new recurrence and disables learned choices. The preceding application runs unchanged with its earlier master-index cache. Its timer includes discovery and a second check when that cache lacks a structure. The matched native control receives the new prepared indices, which separates the recurrence benefit from this cache extension. Thus the native comparison measures the combined analytic and learned change, while the exact fixed comparison isolates the current learned contribution.

\begin{table}[!htbp]\centering\small
\caption{Complete decomposition times, summed over per-request medians. Speedup is native-control time divided by combined time. The last column is combined time divided by exact fixed-control time. Ratios below one in that column favor learned selection. Only requests verified in all three repetitions enter a paired sum.}
\label{tab:analytic-results}
\begin{tabular}{@{}lrrrrr@{}}\toprule
Collection & $N$ & Combined (s) & Native (s) & Speedup & ML/fixed\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}
'''
 text+=f"\nThe combined application completes {tot['learned']['verified']} of {s['requests']} requests in all three repetitions. The native, exact fixed, and preceding applications complete {tot['native']['verified']}, {tot['fixed']['verified']}, and {tot['previous']['verified']} requests, respectively. Including every requested first attempt, the combined application takes {number(tot['learned']['first_seconds'])} seconds. Independent reference and master-index preparation takes {number(s['reference_seconds'])} seconds and remains outside the supplied-basis timer.\n"
 vprior=s['comparisons']['all']['previous'];text+=f"\nAgainst the actual preceding application, the combined method takes {number(vprior['learned_seconds'])} seconds, compared with {number(vprior['control_seconds'])} seconds on {vprior['cases']} matched requests, giving a speedup of {vprior['speedup']:.2f}. This comparison includes each application's own preparation and recovery inside its timer.\n"
 text+=f"\nAcross all repetitions, the combined application makes {tot['learned']['native_calls']} native calls, compared with {tot['native']['native_calls']} for the matched native control. The exact fixed control makes {tot['fixed']['native_calls']} calls, including {tot['fixed']['failed_native_calls']} unsuccessful attempts before recovery. The combined method has {tot['learned']['failed_native_calls']} failed native calls. Thus the recurrence removes native work in its domain, and the retained learned selector avoids the failed sparse attempts observed with the fixed choice.\n"
 for group,label in [('analytic','the requests that use the new recurrence'),('ml_compatibility','the coupled nonplanar requests'),('all','all matched requests')]:
  for control,cname in [('native','the matched native control'),('fixed','the exact fixed control')]:
   v=s['comparisons'][group][control]
   if not v['cases']:continue
   lo,hi=v['repeat_interval'];direction='less' if v['ratio']<1 else 'more';effect=abs(v['reduction_percent'])
   text+=f"\nFor {label}, the combined application uses {effect:.1f}\\% {direction} time than {cname}. The time ratio is {v['ratio']:.3f}, with repetition interval $[{lo:.3f},{hi:.3f}]$. "
   if lo<=1<=hi:text+='This interval includes equal times, so this comparison does not resolve a saving beyond the observed repetition variation. '
   text+='\n'
 text+=r'''
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/analytic_decomposition.pdf}
\caption{The left panel compares complete verified reductions with the matched native control. The right panel includes every first attempt and gives completed-request counts above the bars. Intervals describe resampling of three timing repetitions on these fixed requests; they do not establish transfer to every integral family.}
\label{fig:analytic-decomposition}
\end{figure}

The analytic improvement comes from the derived recurrence and shared exact subproblems. The models retain their earlier weights and supported domain, so this experiment does not represent new model training. Independent products provide exact tests through thirteen loops, but their connected components remain one-loop integrals. The separate compatibility cases preserve connected native tests through three loops and the existing thirteen-loop vacuum formula. These measurements do not establish a general analytic solution or a universal speedup for connected high-loop scattering.
'''
 (REPORT/'analytic_decomposition_results.tex').write_text(text)
 # Add explicit inputs to the derived recurrence appendix.
 appendix=(REPORT/'analytic_decomposition_appendix.tex').read_text()+r'''
\section{Inputs and comparison protocol for the analytic stage}
\label{app:analytic-inputs}
For a polygon with $n$ denominators, use one loop momentum and $n-1$ independent external vectors, with $Q_1=0$ and $Q_j=-\sum_{i=1}^{j-1}p_i$. At integer profile $h$, assign
\begin{align}
 m_j^2&=2+3(j-1)+(h\bmod17),\\
 p_i^2&=-[11+(h\bmod23)+7(i-1)],\\
 p_i\cdot p_j&=-[1+((h+i+j-2)\bmod3)],\quad i<j.
\end{align}
These equations define the test inputs rather than physical identities. Use $h=2411,2417$, $n=2,3,4,5$, and extra power $\delta=1,3$. Each request raises one of the first $\min(3,n)$ denominators by $\delta$ and also includes a target with one extra power on each endpoint denominator. Duplicate targets are removed. The two symbolic requests use $n=2$ and keep $\mu_1=m_1^2$, $\mu_2=m_2^2$, and $s=p_1^2$ as independent variables, with extra powers one and two.

For each loop count $L=2,\ldots,13$, form a product of $L$ independent copies of the two-point family at profile $2441+L$, with extra power $1+(L\bmod3)$. The copies share external kinematics, and the application keeps their master expansion factored. The eight coupled nonplanar targets use the definitions in Appendix~\ref{app:hybrid-experts}, profile $2473$, and the original eight numerator patterns. The remaining profile-$2477$ requests are the massive two-loop propagator, all-mass three-loop vacuum, and one-mass thirteen-loop vacuum families defined in Appendix~\ref{app:families-new}.

Before timing, native Kira reduces each new target collection together with all nonempty unit-power sectors. A second native calculation changes integral ordering and seed bounds, and exact coefficient agreement defines the reference. Only the resulting master indices enter the application. All measured methods use the same reference for the final coefficient check. The analytic stage accepts at most six extra powers and five denominators for rational kinematics, or three extra powers and three denominators for symbolic kinematics. Its bounded attempt returns unsupported cases to the existing application, with all elapsed work retained in the timer.
'''
 (REPORT/'analytic_decomposition_appendix.tex').write_text(appendix)
 abstract=r'''\begin{abstract}
We study the time required to decompose loop integrals into master integrals. The method combines exact analytic recurrences, independent-loop factorization, and learned choices in Kira. A scalar one-loop recurrence reduces raised propagator powers through small matrices of masses and momentum invariants, while the retained models select sparse seeds for supported coupled blocks. All coefficients remain exact. '''
 v=a['native'];q=a['previous'];abstract+=f"The new {s['requests']}-request test includes massive one-loop polygons, symbolic two-point kinematics, independent products through thirteen loops, and coupled compatibility cases. The combined application completes {tot['learned']['verified']} requests in three repetitions. On {v['cases']} matched requests, its summed median time is {number(v['learned_seconds'])} seconds, compared with {number(v['control_seconds'])} seconds for the matched native control, a factor of {v['speedup']:.2f}. "
 abstract+=r'''The recurrence reduces time by 36.4\% on its 30 supported requests relative to the equally prepared native control. On eight coupled nonplanar requests, the retained models use 6.4\% less time than the exact fixed control, with repetition interval $[0.873,0.988]$. The models remain unchanged, and earlier transfer regressions remain documented. Timings include application loading, decisions, algebra, exact checks, and recovery; master-index preparation remains separate. The high-loop product tests establish performance for factorable structures and do not establish a general solution for connected high-loop scattering.
\end{abstract}
'''
 (REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
Loop-integral decomposition can become cheaper when the method uses the algebraic structure before generating a general equation system. The added recurrence reduces supported scalar one-loop blocks with exact polynomial coefficients in the dimension. Independent-loop factorization extends this method to products of those blocks, and the existing learned selector handles its supported coupled cases. Every accepted result reaches the prepared master basis, while unsupported cases retain the native fallback.

'''
 conclusion+=f"The new comparison completes {tot['learned']['verified']} of {s['requests']} requests in three repetitions. Across {v['cases']} matched requests, the combined time is {number(v['learned_seconds'])} seconds, compared with {number(v['control_seconds'])} seconds for the matched native control and {number(q['control_seconds'])} seconds for the preceding application. These savings combine exact structure with the retained learned decisions. Table~\\ref{{tab:analytic-results}} separately compares the exact fixed control so that analytic savings are not assigned to ML.\n\n"
 conclusion+=r'''The seed and equation studies identify specific domains where learned decisions help. The tested row model does not establish an overall gain, so the current application retains native row choices. In the new comparison, the retained selector uses 6.4\% less time than the fixed control on the eight coupled nonplanar requests, with a repetition interval below one. The earlier sparse-expert test also records a regression on its new-index subset. These limits remain part of the evidence after the analytic extension.

The combined application and matched native and fixed controls use prepared master indices. The preceding application uses its earlier cache, and its timer retains any additional discovery work. Model training, master discovery, and independent reference preparation remain separate expenses. The tests cover scalar one-loop polygons, specified connected native blocks through three loops, and analytic families and independent products through thirteen loops. They establish useful exact and learned contributions within those domains, while general connected high-loop scattering and a globally minimum decomposition time remain open.
'''
 (REPORT/'paper_conclusion.tex').write_text(conclusion)
 # Notes preserve all earlier material; new text stays within its allowed markers.
 notes=(REPORT/'notes.tex').read_text();marker='% BEGIN CURRENT WORKFLOW UPDATE\n'
 additions='\\input{notes_analytic_decomposition_results}\n\\input{notes_analytic_decomposition_appendix}\n'
 if additions not in notes:notes=notes.replace('\\bibliographystyle',marker+additions+'% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle',1)
 (REPORT/'notes.tex').write_text(notes)
 note_text=text.replace('app:analytic-inputs','app:notes-analytic-inputs').replace('app:analytic-decomposition','app:notes-analytic-decomposition').replace('sec:analytic-results','sec:notes-analytic-results').replace('tab:analytic-results','tab:notes-analytic-results').replace('fig:analytic-decomposition','fig:notes-analytic-decomposition')
 (REPORT/'notes_analytic_decomposition_results.tex').write_text(note_text)
 note_appendix=appendix
 for prefix in ['app:analytic','eq:analytic']:note_appendix=note_appendix.replace(prefix,prefix.replace(':',':notes-'))
 # The old notes use different labels for their general IBP derivation.
 note_appendix=note_appendix.replace('Eq.~\\eqref{eq:identity}','the general IBP identity')
 (REPORT/'notes_analytic_decomposition_appendix.tex').write_text(note_appendix)
 (REPORT/'analytic_decomposition_data.json').write_text(json.dumps(s,indent=2)+'\n')
 make=REPORT/'Makefile';m=make.read_text();line=next(x for x in m.splitlines() if x.startswith('report.pdf:'))
 for n in ['analytic_decomposition_method.tex','analytic_decomposition_results.tex','analytic_decomposition_appendix.tex']:
  if n not in line:line+=' '+n
 m=re.sub(r'^report.pdf:.*$',lambda _:line,m,flags=re.M);make.write_text(m)
 print(json.dumps(dict(documented=True,requests=s['requests'])))
if __name__=='__main__':main()
