"""Write the measured physics result and retain the full method in the notes."""
from s00_triangle_common import *
import re

def normalize(s):return '\n'.join(x.rstrip() for x in s.splitlines()).strip()+'\n'
def main():
 final=read(HERE/'monitor_summary.json');eq=final['equation_validation'];finaltimes=final['methods'];s=read(HERE/'summary.json');training=read(HERE/'training_summary.json');formula=read(HERE/'formula_checks.json');report=ROOT/'report'
 enabled=training['enabled'];native=s['native'];tri=s['groups']['one_scale_triangle'];bulk=s['batch']
 method=r'''\subsection{A direct one-scale triangle formula}
A massless triangle with two lightlike external momenta admits an explicit Gamma-function value~\cite{DavydychevOsland1998}. We use this identity to return both its reduction coefficient and its analytic value. Let $T_{abc}$ have denominators $k^2$, $(k-p_1)^2$, and $(k-p_1-p_2)^2$, with $p_1^2=p_2^2=0$ and $Q=-(p_1+p_2)^2>0$. The integers $a,b,c$ are their powers. With $B(Q,d)=T_{101}$, the unit-power example is
\begin{equation}
 T_{111}=\frac{2(d-3)}{Q(d-4)}B(Q,d).
 \label{eq:triangle-main}
\end{equation}
Appendix~\ref{app:triangle} derives the general coefficient as a finite product of linear factors in $d$ and gives the Gamma-function value of $B$. The code accepts nonnegative powers through four with $a+b+c\leq8$, rational $Q>0$, and no extra occupied denominator. It also treats independent products of accepted triangles through thirteen loops.

The preceding application already returned analytic ratios to a triangle master on these inputs. The new implementation evaluates the coefficient directly in a bubble basis and supplies its explicit analytic value. We compare the two outputs after an exact basis conversion, and we also compare the single-loop results with Kira. The timing comparison therefore measures the change from the preceding analytic application, including its setup, rather than attributing all of the gain to avoided IBP elimination.
'''
 (report/'triangle_method.tex').write_text(normalize(method))
 model_text=('The additional native cost selector passes the validation condition and is enabled.' if enabled else 'The additional native cost selector does not pass the validation condition. The application therefore uses the validated fixed settings and retains the fitted model for inspection.')
 mlmethod=r'''\subsection{A further native cost-model comparison}
The new native study tests whether the preferred probe batch size changes with the requested integrals. We measure 48 training requests and 20 validation requests across the same planar box, nonplanar box, sunrise, and three-loop vacuum structures. For the two-loop families, the five actions are the preceding application and full reconstruction with probe batch sizes 1, 4, 8, and 16. One three-loop training comparison failed and could not be reproduced by the subsequent symbolic and reconstruction checks. We therefore retain the preceding application for the vacuum structure and exclude its candidate reconstruction costs from model fitting. The fitted training set contains 36 two-loop requests; the complete comparison retains all four structures. Each action retains the preceding learned seed procedure, exact algebra, and bounded recovery. Complete action times include the initial choice and any recovery.

We fit 32 extremely randomized trees~\cite{Geurts2006ExtraTrees} to predict each action's complete time relative to the preceding application. Baseline seconds weight the squared regression error. Validation selects tree depth from 2, 4, and 6, minimum leaf population from 2 and 4, and the required predicted saving from zero, five, and ten percent. The fixed control selects its action separately for each propagator structure. We enable the learned selector only if it saves at least three percent on validation and selects no failed algebra procedure. This condition tests the value of the added model beyond structure-dependent settings. We use the same 29 physical features and weighted cost objective as Appendix~\ref{app:reconstruction-cost}. Here the training cost is the measured complete time, including actual recovery. The model predicts five relative costs; the stated structure guard and observed validation outcomes determine admission.
'''
 # Use the existing cost appendix's actual label, without guessing a cross-reference.
 source=(report/'focused_derivations.tex').read_text();labels=re.findall(r'\\label\{([^}]+)\}',source)
 cost='app:shared';assert cost in labels;mlmethod=mlmethod.replace('app:reconstruction-cost',cost)
 mlmethod+=f'\nSummed action costs on validation give {training["fixed_seconds"]:.3f} seconds for the fixed control and {training["model_seconds"]:.3f} seconds for the best fitted selector. {model_text}\n'
 if training.get('live_validation'):
  live=training['live_validation'];mlmethod+=f' A further complete-call validation includes the added selector itself: fixed settings take {live["seconds"]["fixed"]:.3f} seconds and the learned selection takes {live["seconds"]["integrated"]:.3f} seconds. The same three-percent condition determines deployment.\n'
 mlmethod+=f'\nWe also test the preceding nonplanar equation classifier with the new reconstruction setting at its frozen threshold of 0.05. Five validation requests with two repetitions give {eq["seconds"]["off"]:.3f} seconds without this additional filter and {eq["seconds"]["on"]:.3f} seconds with it, including recovery. The classifier skips 17,808 of 53,430 candidate equation constructions, but all ten filtered attempts fail the prescribed-master-basis check and require recovery. We therefore leave this additional filter disabled; the earlier seed policy remains active.\n'
 (report/'triangle_learning.tex').write_text(normalize(mlmethod))
 rows=[]
 for label0,key in [('One-scale triangles and products','one_scale_triangle'),('Planar boxes','double_box'),('Nonplanar boxes','nonplanar_box'),('Massive sunrise','sunrise'),('Three-loop vacuum','vacuum3')]:
  g=s['groups'][key];rows.append(f'{label0} & {g["requests"]} & {g["seconds"]["previous"]:.3f} & {g["seconds"]["integrated"]:.3f} & {g["ratio"]:.3f} '+r'\\')
 result=r'''\subsection{Direct triangles and refined native choices}
\label{sec:triangle-results}
We freeze the added formula and cost policy before testing 40 new requests. Twenty contain native two- or three-loop reductions, and twenty contain single triangles or independent triangle products. The product tests cover every loop order from one through thirteen. We measure three fresh-process repetitions for each request and method. These first measurements retain the original runtime monitor. The preceding application, the new fixed control, and the new integrated method receive the same physical inputs. Times include application loading, model use where enabled, algebra, output reading, and cleanup. Independent coefficient comparisons remain outside all timers.

\begin{table}[htbp]\centering\small
\caption{New reserved requests. Times sum per-request medians of three complete calls. The ratio divides new time by preceding time.}
\label{tab:triangle-times}
\begin{tabular}{lrrrr}\toprule
Requests & Number & Preceding (s) & New (s) & Ratio\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}\end{table}
'''
 result+=f'\nThe native requests give a total-time ratio of {native["ratio"]:.3f}, with a paired request-bootstrap interval of $[{native["interval"][0]:.3f},{native["interval"][1]:.3f}]$. The integrated-to-fixed ratio is {native["ml_ratio"]:.3f}, with interval $[{native["ml_interval"][0]:.3f},{native["ml_interval"][1]:.3f}]$. '
 result+=('This comparison measures the added selector while retaining the inherited seed policy in both methods. '+('Its interval supports an additional time saving on these native requests.\n' if native['ml_interval'][1]<1 else 'Its interval does not establish an additional time saving on these native requests.\n') if enabled else 'Both new methods use the same fixed choices because the added selector is disabled. Their timing difference does not measure a new ML gain.\n')
 result+=f' The seven-loop product request has a time ratio of {s["triangle_loops"]["7"]["ratio"]:.3f} in this fresh-process comparison. The measurements therefore include a slower triangle case, and they do not establish a monotonic trend with loop order.\n'
 result+=r'''
\begin{figure}[htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/triangle_extension.pdf}
\caption{Complete-time ratios on the new requests. The dashed line marks equal time. The left panel shows the direct triangle implementation at each tested product loop order. The right panel shows native requests by propagator structure, with paired request-bootstrap intervals. Product tests do not establish connected higher-loop scattering performance.}
\label{fig:triangle-extension}
\end{figure}

We also compare shared calls containing these 40 requests and the 53 preceding analytic regression requests. This preserves the setup benefit of the previously deployed method. Three complete repetitions use alternating method order and reverse the request order in the middle repetition. Two workers share an Intel Gold compute node, with one computation thread per application. The collection timer includes loading, all reductions, output reading, and cleanup.
\begin{table}[htbp]\centering\small
\caption{Shared-call time for the matched collection of 93 requests. The interval is the observed range of three complete repetitions, not a confidence interval.}
\label{tab:triangle-batch}
\begin{tabular}{lrr}\toprule
Method & Median (s) & Observed range (s)\\\midrule
'''
 for a,l in [('previous','Preceding application'),('fixed','New fixed control'),('integrated','New integrated method')]:
  r=bulk[a];result+=f'{l} & {r["median"]:.3f} & {r["minimum"]:.3f}--{r["maximum"]:.3f} '+r'\\'+'\n'
 result+=r'\bottomrule\end{tabular}\end{table}'+'\n'
 result+=f'\nThe new-to-preceding collection ratio is {s["batch_ratio"]:.3f}. All {s["separate_applications"]+s["regression_applications"]+s["batch_applications"]:,} tested application results pass {s["checks"]:,} exact coefficient comparisons after the stated basis conversion. The timed native procedures record {s["inner_failed_attempts"]} unsuccessful internal attempts across the fresh-call and shared-call comparisons; their recovery costs remain inside the timers. The separate formula checks add {formula["gamma_comparisons"]} high-precision Gamma-function comparisons, {formula["exact_recurrence_checks"]} exact index-shift checks, and {formula["product_gamma_checks"]} product checks. Native one-loop comparisons and the derivation support the triangle identity; the product tests check its separated-loop implementation.\n'
 result+=r"""
\subsection{Final complete-call comparison}
A native reduction removes temporary files while it runs. The earlier resource monitor could stop a reduction if a directory disappeared during its inspection. We change the monitor to tolerate removal while preserving its storage bound. A controlled check reproduces the old exception and verifies the new behavior. This change affects runtime supervision and leaves the algebra and learned decisions unchanged.

We compare the preceding published application, the new mathematical method with the original monitor, and the final application with the corrected monitor on the same 93 requests. Each method runs three times on the same compute node with one worker, rotating method order, and reversed request order in the middle repetition. A preceding two-worker comparison showed timing differences larger than the measured monitor cost. It also stopped when recovery in the preceding application returned a 20-integral basis instead of the 16-integral reference basis for one vacuum request. We retain that failed comparison separately. The complete serial check uses every planned request and method. The complete timer includes unsuccessful internal attempts and recovery. Independent comparisons check the saved exact coefficients outside the timer.
\begin{table}[htbp]\centering\small
\caption{Final matched shared-call comparison. Times are complete collection times. The range shows the three observations. Internal failures count attempts across all three repetitions.}
\label{tab:triangle-final}
\begin{tabular}{lrrrr}\toprule
Method & Median (s) & Mean (s) & Range (s) & Failures\\\midrule
"""
 for a,l in [('published','Preceding application'),('previous','New method, original monitor'),('integrated','Final application')]:
  q=finaltimes[a];result+=f'{l} & {q["median"]:.3f} & {q["mean"]:.3f} & {q["minimum"]:.3f}--{q["maximum"]:.3f} & {q["inner_failures"]} '+r'\\'+'\n'
 result+=r'\bottomrule\end{tabular}\end{table}'+'\n'
 result+=f'The final-to-preceding median ratio is {final["ratio"]:.3f}, which reduces time by {(1-final["ratio"])*100:.1f} percent on this collection. The final-to-original-monitor ratio is {final["scanner_ratio"]:.3f}. All {final["application_results"]} application results pass {final["checks"]:,} exact coefficient comparisons. This finite timing comparison does not prove a universal speedup or a globally shortest reduction.\n'
 primary_result=result[:result.index('We also compare shared calls')]+result[result.index(r'\subsection{Final complete-call comparison}'):]
 (report/'triangle_results.tex').write_text(normalize(primary_result))
 # Physics inputs supplement existing definitions; preserve exact reserved index vectors.
 protocol=read(HERE/'test_protocol.json.gz');box=[c for c in protocol['cases'] if c.get('topology_group')=='double_box']
 extra=r'''\subsection{Inputs for the additional comparison}
The four native propagator structures are those in Appendix~\ref{app:reconstruction-inputs}. For the new planar and nonplanar box requests, the invariants are $s=-(137+6i)$ and $t=-(167+4i)$, with the incoming/outgoing momentum conventions stated there. Training uses $i=2,\ldots,13$, validation uses $i=14,\ldots,18$, and reserved tests use $i=19,\ldots,23$. Each box target has powers $(1,1,1,1,1,1,1,-a,-b)$. The reserved pairs are listed below; both box structures use the same pairs at each $i$.
\begin{center}\small\begin{tabular}{cl}\toprule
$i$ & Pairs $(a,b)$ in the target request\\\midrule
'''
 for c in box:
  i=c['id'].rsplit('_',1)[1];pairs=', '.join('('+str(-t[-2])+','+str(-t[-1])+')' for t in c['targets']);extra+=i+' & $'+pairs+'$ '+r'\\'+'\n'
 extra+=r'''\bottomrule\end{tabular}\end{center}
The sunrise masses remain $(3,7,13)$ and its external invariant is $p^2=-386221-12i$. The three-loop vacuum masses remain $(1,1,1,13,13,64255+2i)$. These families use the same index splits. Even $i$ requests the sector corner, and odd $i$ requests the raised-power targets defined for that structure. Full physical inputs differ between splits. Graph structures and individual index vectors recur; box target batches are distinct across the new splits.

For a triangle product with $L$ loops, every factor has $Q=101+2L$. We choose factor powers from $(1,1,1)$, $(2,1,1)$, $(1,2,1)$, $(1,1,2)$, $(2,2,1)$, $(1,0,1)$, and $(2,0,2)$. We form six products per loop order and remove duplicate full targets. Cross-loop auxiliary powers are zero. Seven additional single-loop requests use $Q=211+2j$, $j=1,\ldots,7$, and the targets $(1,1,1)$, $(1+(j\bmod3),1+(j\bmod2),1)$, $(1,0,1)$, $(2,0,1)$, and $(0,1,1)$, again with duplicate targets removed.

The preceding triangle basis uses unit-power triangle masters. For verification, each such master is replaced by $2(d-3)B/[Q(d-4)]$, and independent components multiply. Kira provides a separate bubble-basis reference for each new single-loop request. The higher-loop comparison combines this exact basis conversion with the product derivation and independent Gamma-function checks.
'''
 (report/'triangle_inputs.tex').write_text(normalize(extra))
 main=(report/'report.tex').read_text()
 if '\\input{triangle_method}' not in main:main=main.replace('\\subsection{Connected trees and higher loop counts}','\\input{triangle_method}\n\n\\subsection{Connected trees and higher loop counts}')
 if '\\input{triangle_learning}' not in main:main=main.replace('\\section{Comparison design}','\\input{triangle_learning}\n\n\\section{Comparison design}')
 if '\\input{triangle_results}' not in main:main=main.replace('\\input{batch_application_results}','\\input{batch_application_results}\n\\input{triangle_results}')
 if '\\input{triangle_appendix}' not in main:main=main.replace('\\bibliographystyle{unsrt}','\\input{triangle_appendix}\n\\input{triangle_inputs}\n\\bibliographystyle{unsrt}')
 if 'One-scale massless triangles &' not in main:main=main.replace('Independent products & Product of accepted component reductions;',r'One-scale massless triangles & Two lightlike legs and one spacelike invariant; direct Gamma ratios with powers through four and total power at most eight\\'+'\n'+r'Independent products & Product of accepted component reductions;')
 main=main.replace('The native test contains 22 new physical requests.','The first reconstruction comparison contains 22 new native requests.').replace('Four applications process the same requests.','In that first comparison, four applications process the same requests.')
 (report/'report.tex').write_text(normalize(main))
 bib=r'''@article{DavydychevOsland1998,
 author={Davydychev, Andrei I. and Osland, Per},
 title={On-shell two-loop three-gluon vertex},
 journal={Physical Review D}, volume={59}, pages={014006}, year={1998},
 doi={10.1103/PhysRevD.59.014006}, eprint={hep-ph/9806522}, archivePrefix={arXiv}
}
'''
 for name in ['paper_references.bib','notes_additional_references.bib']:
  text=(report/name).read_text()
  if '@article{DavydychevOsland1998,' not in text:(report/name).write_text(normalize(text+'\n'+bib))
 # Keep the historical notes reconstructable by placing additions within their update markers.
 combined=(report/'triangle_appendix.tex').read_text()+extra+method+mlmethod+result
 combined+=f'\nThe preceding parallel monitor comparison used two workers and stopped at the third published-application collection after the vacuum basis mismatch. Its recorded outputs pass 650 of 651 request comparisons. Its two complete matched repetitions give a final-to-published ratio of {final["parallel_comparison"]["ratio"]:.3f}, and a corrected-to-original-monitor ratio of {final["parallel_comparison"]["scanner_ratio"]:.3f}. The controlled serial repetition retains every physical input and algorithm. It changes the worker schedule to examine the unexplained timing difference. These two comparisons are reported separately.\n'
 combined+=r'''
\subsection{Verification imports}
Two verification helpers initially imported historical modules with the same names. We corrected these imports without changing the application, fitted model, or physical test inputs. We retained the completed timings and rechecked the saved results. The runtime-monitor comparison uses the corrected checks.

\subsection{Preparation checks and conservative admission}
The first native collection stopped at the three-loop vacuum request with squared masses $(1,1,1,13,13,64269)$. A probe batch size of eight disagreed with the preceding reference in the coefficient comparator. The collector stopped before it saved that candidate output, so its original difference cannot be reconstructed from the surviving record. The reference and failure log remain available. We corrected the collector to save a failed output before stopping.

Independent reruns compared symbolic algebra and several reconstruction settings. The original reference agreed with the symbolic result. Additional repetitions checked the disputed setting at four nearby mass profiles. These diagnostics did not justify treating the original failed check as a measured speedup. The new cost selector therefore retains the preceding application for this three-loop structure. The reserved comparison tests that conservative configuration. Independent symbolic reductions also check every action record used for fitting and validation.
'''
 # Notes already contain a prefixed copy of the preceding reconstruction appendix.
 combined=combined.replace('app:reconstruction-inputs','notes-reconstruction-app:reconstruction-inputs').replace(cost,'notes-reconstruction-'+cost)
 own=set(re.findall(r'\\label\{([^}]+)\}',combined))
 for label0 in sorted(own,key=len,reverse=True):combined=combined.replace('{'+label0+'}','{notes-triangle:'+label0+'}')
 (report/'notes_triangle_extension.tex').write_text(normalize(combined))
 notes=(report/'notes.tex').read_text()
 if '\\input{notes_triangle_extension}' not in notes:notes=notes.replace('\\bibliographystyle{unsrt}','% BEGIN CURRENT WORKFLOW UPDATE\n\\input{notes_triangle_extension}\n% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle{unsrt}')
 (report/'notes.tex').write_text(notes)
 conclusion=(report/'paper_conclusion.tex').read_text().replace('across the the direct','across the direct').replace('The new cost model fails','The first reconstruction cost model fails')
 conclusion=conclusion.replace('The integrated method reduces summed complete time by 37.4\% relative to the preceding application on 75 matched requests.', 'In the earlier comparison of 75 matched requests, the integrated method reduces summed complete time by 37.4\% relative to its preceding application.').replace('Processing the same collection in one call reduces repeated setup. The current collection time', 'For those 75 requests, processing the collection in one call reduces repeated setup. The measured collection time')
 conclusion=re.sub(r'% TRIANGLE SUMMARY BEGIN.*?% TRIANGLE SUMMARY END\n?','',conclusion,flags=re.S)
 paragraph=f'% TRIANGLE SUMMARY BEGIN\nThe additional matched collection gives {finaltimes["published"]["median"]:.3f} seconds for the preceding shared-call method and {finaltimes["integrated"]["median"]:.3f} seconds for the new method. Direct triangle coefficients and validated native settings produce this result within the stated domains. {model_text}\n% TRIANGLE SUMMARY END\n\n'
 conclusion=paragraph+conclusion;(report/'paper_conclusion.tex').write_text(normalize(conclusion))
 abstract=r"""\begin{abstract}
We study how to reduce the time required to express loop integrals in terms of master integrals. The method uses exact formulas and recurrences when their mathematical conditions hold, then calls Kira with reduction settings chosen from measured complete costs. Analytic methods cover specified vacuum families and independent products through thirteen loops. We add an explicit Gamma-function evaluation for a massless triangle with two lightlike external momenta, retain its factorized form for independent products, and test native reduction choices on planar boxes, nonplanar boxes, massive sunrise integrals, and a three-loop vacuum family. The existing seed model remains active within its accepted domain. A newly trained cost model and an added equation filter fail their validation conditions and remain disabled.
"""
 abstract+=f'On a matched collection of 93 requests, the final shared-call application takes {finaltimes["integrated"]["median"]:.3f} seconds, compared with {finaltimes["published"]["median"]:.3f} seconds for the preceding shared-call application, reducing time by {(1-final["ratio"])*100:.1f} percent. These medians include application loading, exact algebra, output reading, cleanup, and recovery. All {final["application_results"]} application results from the final comparison pass their exact coefficient checks. The gain combines direct formulas, validated native settings, and runtime changes; it does not establish an additional learned-policy gain. The demonstrated range includes selected structures through thirteen loops, while general connected high-loop scattering remains outside the verified domain.\n'
 abstract+=r'\end{abstract}'+'\n';(report/'paper_abstract.tex').write_text(normalize(abstract))
 make=(report/'Makefile').read_text().replace('triangle_method.tex triangle_learning.tex triangle_results.tex triangle_appendix.tex triangle_inputs.tex ','').replace('notes_triangle_extension.tex ','');make=make.replace('report.pdf: ','report.pdf: triangle_method.tex triangle_learning.tex triangle_results.tex triangle_appendix.tex triangle_inputs.tex ',1);make=make.replace('notes.pdf: ','notes.pdf: notes_triangle_extension.tex ',1);(report/'Makefile').write_text(make)
 print('report sources updated',flush=True)
if __name__=='__main__':main()
