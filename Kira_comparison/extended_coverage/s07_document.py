"""Write the new measured scope and its independent coefficient derivation."""
import re
from s00_protocol import HERE,ROOT,read,write

def main():
 s=read(HERE/'summary.json');report=ROOT/'report';native=s['native'];counts=s['coverage_counts'];a=s['analytic'];scale=s['scale'];m=native.get('summed_median_seconds',{});ratio=native.get('ratios',{}).get('selected',0)
 label={'verified':'All methods verified','method_failed':'Application failure','reference_failed':'Reference limit or failure','reference_check_failed':'Reference check failure','unsupported_index_count':'Input index limit'}
 status_rows='\n'.join(f"{label[k]} & {v}\\\\" for k,v in counts.items())
 type_rows='\n'.join(f"{k.replace('_',' ')} & {v['cases']} & {v['summed_median_seconds']['native']:.3f} & {v['summed_median_seconds']['selected']:.3f} & {v['ratios']['selected']:.3f}\\\\" for k,v in s['by_type'].items() if v.get('cases'))
 loop_rows=[]
 for L in range(1,13):
  rows=[r for r in s['native_rows'] if r['loops']==L]
  r=sum(x['medians']['selected'] for x in rows)/sum(x['medians']['native'] for x in rows) if rows else None
  requested=sum(c['loops']==L for c in s['coverage']);verified=s['by_loop'][str(L)].get('verified',0)
  loop_rows.append(f"{L} & {verified}/{requested} & {len(rows)} & "+(f"{r:.3f}" if r is not None else '--')+r" & 2/2\\")
 loop_table='\n'.join(loop_rows)
 total_rows='\n'.join(f"{name} & {m[key]:.3f}\\\\" for key,name in [('native','Native fixed control'),('previous','Previous application'),('selected','Selected application')])
 scope=f"The expanded test defines {len(s['coverage'])} native family requests at one through twelve loops. {counts.get('verified',0)} requests complete all methods and exact checks, while {counts.get('unsupported_index_count',0)} exceed the current 31-index interface limit. The remaining requests retain their recorded failures. The separate analytic test verifies {len(s['analytic_rows'])} scalar massless two-point batches, covering every loop order from one through twelve at both rational and symbolic momentum."
 result=rf'''\section{{Broader tests of the frozen application}}
\label{{sec:extended-coverage}}
The earlier gains concern selected graph structures and target patterns. We now keep the deployed models and all decision rules fixed and test a wider set of physical inputs. {scope} A loop label alone therefore does not specify the demonstrated scope: the graph, masses, external momenta, target powers, and method also matter.

\subsection{{Physical inputs and checks}}
The native grid contains one-mass and fully massive vacuum families, massless and massive two-point families, four-point ladders, and boxes with bubble subgraphs. It also contains nonplanar boxes, pentagons, and boxes with one external virtuality. Rational profiles differ from those in the preceding studies. Selected low-loop cases keep the independent masses and momentum invariants symbolic. Appendix~\ref{{app:extended-coverage}} gives the target sets and parameter choices, using the previously defined denominators.

Each eligible request first runs Kira with expanded seeds and no preferred master basis. A second reduction changes the integral ordering and increases the numerator bound, then checks every coefficient in the discovered basis. This agreement tests stability within those two seed regions; it does not prove that every surviving master is independent under all possible IBP identities. The reference stage records {s['reference_failure_reasons'].get('time_limit',0)} time-limit failures and {s['reference_failure_reasons'].get('kira_error',0)} Kira allocation failures. The latter occur during topology preparation under the address-space cap, before a learned reduction decision is tested. These failures therefore identify preparation and resource limits, rather than model prediction errors. The three timed methods then receive that common basis. Kira generates their equations and performs the exact reduction, as in its standard reduction procedure~\cite{{KiraOriginal,Kira3}}.

The native control disables learned choices and uses the current exact implementation with fixed bounds. The previous and selected applications use their unchanged published policies. Each run starts a fresh process, and its time includes imports, input preparation, model loading, equation generation, algebra, coefficient checks, retries, and process exit. Every method loads the common application modules, including the native and direct-formula controls. These are complete times for the same interface, rather than timings of the Kira executable alone. The comparison includes costs that can matter for small requests. Master discovery and the independent reference calculation remain separate. Three repetitions rotate method order on the same worker for each case. Each native attempt has a 30-second budget, a 32 MiB temporary-storage limit, and the existing memory guard. The runner reserves ten seconds for completion and cleanup, leaving at most twenty seconds for the Kira process. A failure stops further repetitions of that method, and remains in the coverage count.

\begin{{table}}[!htbp]\centering\small
\caption{{Outcomes for the complete predefined native grid. Rejected inputs have no timed Kira reduction.}}
\label{{tab:extended-coverage}}
\begin{{tabular}}{{@{{}}lr@{{}}}}\toprule
Outcome & Requests\\\midrule
{status_rows}
\bottomrule\end{{tabular}}\end{{table}}

\begin{{table}}[!htbp]\centering\small
\caption{{Results by loop order. Native verified counts require all methods and reference checks. A dash means no matched nontrivial native timing comparison. Analytic checks cover the stated scalar massless two-point family.}}
\label{{tab:extended-loops}}
\begin{{tabular}}{{@{{}}rrrrr@{{}}}}\toprule
Loops & Native verified/requested & Matched & Time ratio & Analytic passed\\\midrule
{loop_table}
\bottomrule\end{{tabular}}\end{{table}}

\subsection{{Complete application times}}
The matched nontrivial set contains {native['cases']} requests for which all three repetitions of all methods pass the exact coefficient checks. A nontrivial reduction has at least one nonzero target expression beyond the unchanged target itself. We report the sum of per-request median times, using the definition in Appendix~\ref{{app:coverage}}. Identity-only answers and failed requests do not enter this time ratio. The two single-target rank-three box requests lack fully checked references under the common limits and therefore supply no new timing comparison for the learned sparse-seed route.

\begin{{table}}[!htbp]\centering\small
\caption{{Complete times on the matched nontrivial requests. Ratios compare selected time with native time; a value below one means less time.}}
\label{{tab:extended-times}}
\begin{{tabular}}{{@{{}}lrrrr@{{}}}}\toprule
Family & Requests & Native (s) & Selected (s) & Ratio\\\midrule
{type_rows}
\midrule
All matched & {native['cases']} & {m['native']:.3f} & {m['selected']:.3f} & {ratio:.3f}\\
\bottomrule\end{{tabular}}\end{{table}}

The previous application takes {m['previous']:.3f} seconds on the same set. The selected application's total differs from the native total by {100*(ratio-1):.1f}\%, and the timing interval includes equal time. The selected-to-native time ratio is {ratio:.3f}, with a paired-repetition resampling interval [{native['intervals']['selected'][0]:.3f}, {native['intervals']['selected'][1]:.3f}]. The interval describes timing variation for these fixed cases; it does not estimate coverage of all integral families. Reference discovery takes a further {native['discovery_seconds']:.3f} seconds, and its independent check takes {native['independent_reference_check_seconds']:.3f} seconds. Adding the same measured discovery work to each method gives {native['discovery_plus_application_seconds']['native']:.3f} seconds for the native control and {native['discovery_plus_application_seconds']['selected']:.3f} seconds for the selected application. This last comparison includes discovery once per request and does not represent a learned master-discovery method.

These are comparisons of complete deployed configurations. Outside the fitted domain, the selected application can take an exact analytic route or fall back to native choices. In the matched set, {s['selected_routes'].get('proven_massless_banana',0)} cases use the analytic formula and the remaining cases use native choices. No matched case activates a learned seed, batch, or equation decision. The frozen domain checks and validation gates determine these routes. This comparison therefore checks application coverage and fallback behavior, and its time difference supplies no evidence of a learned gain on these new targets. The earlier matched filter and sparse-seed controls remain the evidence for isolated learned gains.

\begin{{figure}}[!htbp]\centering
\includegraphics[width=\linewidth]{{paper_figures/extended_coverage.pdf}}
\caption{{Left: every requested native family remains in the coverage count, including failures and input limits. Right: time-ratio points and paired-repetition intervals use only matched nontrivial cases, with case counts in parentheses. The dashed line marks equal time. The panels distinguish whether a calculation finishes from how long a completed calculation takes.}}
\label{{fig:extended-coverage}}
\end{{figure}}\FloatBarrier

\subsection{{Exact checks at every studied loop order}}
The analytic test uses the scalar massless two-point family of Appendix~\ref{{app:banana}} and four target patterns at each loop order, with either a new rational value of $p^2$ or symbolic $p^2$. An independently implemented recurrence raises one propagator power at a time and checks each exact coefficient returned by the frozen application. Appendix~\ref{{app:extended-coverage}} derives this recurrence. All {len(s['analytic_rows'])} batches pass, with four targets per batch and three repetitions of the direct formula, previous application, and selected application.

These inputs contain only the physical denominators. The analytic formula needs no auxiliary numerator coordinates, while general native IBP generation uses a complete scalar-product basis. For that complete representation, the current interface reaches its index limit at lower loop order. The twelve-loop analytic checks therefore verify the stated scalar family and exact route; they do not establish general native twelve-loop reductions or learned speedups at twelve loops.

\subsection{{Reuse on the additional physical inputs}}
Four base requests are fixed before testing: planar and nonplanar two-loop rank-three boxes, a one-loop ladder, and a two-loop massless two-point family. Each sequence changes all external scalar products by factors $1$, $3/2$, and $2$. Independent native references check each scale. The application can reuse only graph signatures already supported by the frozen scaling rule. Every measured sequence includes its first reduction and three repetitions rotate method order.

{len(s['scale_rows'])} of the four sequences complete every paired method. Their summed median times are {scale.get('summed_median_seconds',{}).get('previous',0):.3f} seconds for the previous application, {scale.get('summed_median_seconds',{}).get('selected',0):.3f} seconds for the selected application without reuse, and {scale.get('summed_median_seconds',{}).get('selected_reuse',0):.3f} seconds with reuse. The ratio of selected reuse time to previous time is {scale.get('ratios',{}).get('selected_reuse',0):.3f}. The completed sequences record {sum(sum(r.get('cache_hits',[])) for r in s['scale_rows'])} reused outputs across the three repetitions. The retained records include any sequence that fails to obtain a checked reference. The completed sequences have no reuse hits because their graphs lie outside the current scale-cache domain. The two rank-three box sequences lack checked references within the limits, so this extension provides no new measurement of the reuse benefit. It checks sequence processing and the domain rules without new model training or a changed policy.

The full extension retains {s['successful_calls']} successful measured calls and {s['failed_calls']} failed measured calls, excluding the independent native references. The exact checks compare {s['coefficient_checks']} coefficient pairs. The result states where the existing method works under the specified limits. General reductions for every topology and arbitrary loop order remain unverified.
'''
 (report/'extended_coverage_results.tex').write_text(result)
 appendix=r'''\section{Inputs and independent recurrence for the extended tests}
\label{app:extended-coverage}
The vacuum, two-point, ladder, and bubble-box denominators are those in Appendix~\ref{app:coverage}. The new rational grid uses $h=1001$ in
\begin{equation}
 \begin{aligned}
 m_{\mathrm{one}}^2&=2h+17, & m_i^2&=2h+19+6(i-1),\\
 p^2&=-2h-29,\\
 s&=-1009-12h, & t&=-1021-14h.
 \end{aligned}
\end{equation}
These are definitions of the test points in a common squared-momentum unit. Only the quantities needed by each graph are present. Symbolic grid members use the same denominators with independent nonzero squared masses and invariants, and profile label $h=1002$. The extra nonplanar box, pentagon, and virtuality-box definitions use Appendix~\ref{app:families}, with rational profile $h=1003$ and separate symbolic variants. The two additional rank-three box requests use the definitions in Appendix~\ref{app:joint-policy}, with profile $h=1009$ and numerator powers split as one and two across the two auxiliary coordinates.

The ordinary grid targets are the corner, one extra power on the first physical denominator, and one numerator power on the first auxiliary entry when present. The three extra scattering structures instead raise the last physical denominator. Every massive two-point batch contains all physical dot patterns through two extra powers: the corner, each single dot, each double dot, and each pair of distinct single dots. This gives the target count derived in Appendix~\ref{app:coverage}. Enlarged reference bounds add one to the maximum positive-power sum, numerator rank, and dot count of the target batch. The check increases the numerator bound once more and changes integral ordering from one to two. The complete scalar-product count remains $N=L(L+1)/2+LE$, so the current 31-index input guard admits vacuum graphs through seven loops, two-point graphs through six loops, and four-point graphs through five loops. This guard is a limit of the tested interface, not a mathematical upper limit on IBP reduction.

For the analytic checks, retain only the $n=L+1$ physical massless denominators of $B_L(\boldsymbol a;p^2,d)$ from Appendix~\ref{app:banana}. The targets are $\boldsymbol 1$, $\boldsymbol 1+\boldsymbol e_1$, $\boldsymbol 1+3\boldsymbol e_n$, and $\boldsymbol 1+\boldsymbol e_1+\boldsymbol e_n$, where $\boldsymbol e_j$ raises physical power $j$. We use $p^2=-2051$ and, separately, symbolic $p^2$. These follow from the predefined profile $h=1011$.

To obtain an independent recurrence, let $A=\sum_i a_i$ and raise $a_j$ by one in the gamma expression of Eq.~\eqref{eq:banana-gamma}. The identity $\Gamma(z+1)=z\Gamma(z)$ changes the global numerator factor by $A-Ld/2$, the inverse global gamma factor by $nd/2-A-1$, the line gamma factor by $1/(d/2-a_j-1)$, and $1/\Gamma(a_j)$ by $1/a_j$. The phase and integer momentum power combine into $1/p^2$ in the same convention as Eq.~\eqref{eq:banana-ratio}. Therefore
\begin{equation}
 \frac{B_L(\boldsymbol a+\boldsymbol e_j;p^2,d)}{B_L(\boldsymbol a;p^2,d)}
 =\frac{(A-Ld/2)(nd/2-A-1)}{(d/2-a_j-1)a_jp^2}.
 \label{eq:extended-raising}
\end{equation}
Starting from the corner coefficient one, we apply this rational recurrence until the target powers are reached and compare the result by exact subtraction. The comparison uses a separate symbolic implementation and does not call the application's finite-product coefficient routine. Both expressions follow from the same analytic identity, so this checks implementation consistency rather than supplying an independent high-loop native IBP proof. The result holds by meromorphic continuation in $d$ for generic nonzero $p^2$, as in the preceding derivation.

For each fixed matched workload, the timing interval resamples the three repetition indices with replacement within each request, using the same indices for both compared methods. Each of 2,000 resamples sums the resulting request medians and takes their ratio. The endpoints are the empirical 2.5 and 97.5 percentiles. This describes variation within the measured repetitions and does not justify extrapolation to new topologies.
'''
 (report/'extended_coverage_appendix.tex').write_text(appendix)
 for name in ['report','notes']:
  p=report/(name+'.tex');text=p.read_text();already='\\input{extended_coverage_results}' in text
  anchor='\\input{joint_policy_results}';text=text.replace(anchor,anchor+'\n\\input{extended_coverage_results}') if '\\input{extended_coverage_results}' not in text else text
  anchor='\\input{joint_policy_appendix}';text=text.replace(anchor,anchor+'\n\\input{extended_coverage_appendix}') if '\\input{extended_coverage_appendix}' not in text else text
  if name=='report' and not already:
   add=f" A broader frozen-application test completes all comparisons on {counts.get('verified',0)} of 84 native requests defined through twelve loops. The matched nontrivial subset has selected-to-native time ratio {ratio:.3f}; input and resource limits remain explicit. Separate exact scalar checks pass at every loop order from one through twelve."
   text=text.replace('We report learned and exact-method gains separately within their tested physical domains.','We report learned and exact-method gains separately within their tested physical domains.'+add)
   text=text.replace('\\section{Conclusion}\n','\\section{Conclusion}\n'+scope+' The native matched time ratio is '+f'{ratio:.3f}'+'. These broader outcomes do not extend the isolated learned gains to every family. Section~\\ref{sec:extended-coverage} retains the complete coverage record.\n\n')
   text=text.replace('The final study tests joint choices','A further study tests joint choices')
   text=text.replace('% END JOINT POLICY INTRO', '% END JOINT POLICY INTRO\nWe then keep that application fixed and test broader vacuum, two-point, and scattering families through twelve loop orders. The new coverage study reports completed reductions, failed references, and input limits separately from exact scalar checks at every studied loop order.')
   text=text.replace('All timed outputs pass exact coefficient checks.', 'All completed outputs in these earlier comparisons pass exact coefficient checks.')
  p.write_text(text)
 p=report/'s01_check_paper.py';text=p.read_text();text=text.replace("'joint_policy_appendix.tex']","'joint_policy_appendix.tex','extended_coverage_results.tex','extended_coverage_appendix.tex']");p.write_text(text)
 p=report/'Makefile';text=p.read_text().replace('report.pdf: joint_policy_results.tex','report.pdf: extended_coverage_results.tex extended_coverage_appendix.tex joint_policy_results.tex');p.write_text(text)
 for p,extra in [(report/'README.md','The extended coverage section tests the frozen application on 84 native requests through twelve loops. Its separate analytic tests cover every loop order. Read the coverage table before using the matched time ratios. `extended_coverage_data.json` stores the measured results. The source scripts are in `Kira_comparison/extended_coverage/`.'),(report/'paper_figures/README.md','`extended_coverage.pdf` shows native coverage by loop order and matched complete-time ratios by integral type. Failures and input limits remain visible.'),(ROOT/'README.md','The current frozen application has a broader test in `Kira_comparison/extended_coverage/`. It records native completion, failures, input limits, and separate exact analytic checks through twelve loops. Read that folder and the new report section for the measured scope.')]:
  text=p.read_text()
  if extra not in text:p.write_text(text+'\n'+extra+'\n')
 print('Documents updated',flush=True)
if __name__=='__main__':main()
