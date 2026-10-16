"""Write the measured coverage, full-cost comparisons, and mathematical scope."""
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
from s05_analyze import NAMES
def write(p,s):p.write_text(s.rstrip()+'\n')
def change(r):return f'{abs(100*(1-r)):.1f}\\% '+('less' if r<=1 else 'more')
def main():
    data=json.loads((HERE/'summary.json').read_text());p=data['paired'];v=data['vacuum_totals']
    ft=p['full_original'];fp=p['full_previous'];ap=p['application_previous'];an=p['application_native']
    totals=v['individual']['totals'];shared=v['shared']['totals']
    assert all(x['ratio'] is not None for x in p.values())
    table='\n'.join(f"{label} & {r['count']} & {r['previous']:.3f} & {r['revised_seconds']:.3f} & {r['ratio']:.3f}\\\\" for label,r in [('Full: original Kira',ft),('Full: previous implementation',fp),('Basis supplied: previous application',ap),('Basis supplied: revised native control',an)])
    vacrows='\n'.join(f"{label} & {totals[k]:.3f} & {shared[k]:.3f}\\\\" for k,label in [('original','Original Kira, separate loop orders'),('dense','Improved Kira, dense identities'),('extreme','Fixed identity selection'),('learned','Learned identity selection'),('recurrence','Deployed exact recurrence')])
    completion='\n'.join(f"{label} & {data['method_completion'][k]['first_requests']} & {data['method_completion'][k]['first_successes']} & {data['method_completion'][k]['first_complete_seconds']:.3f}\\\\" for k,label in [('full_original','Full original Kira'),('full_previous','Full previous implementation'),('full_revised','Full revised implementation'),('previous','Previous application'),('selected','Selected application'),('native','Revised native control')])
    section=r'''\section{How far the improvement extends}
\label{sec:coverage}
The preceding gain was measured on known graph structures with a supplied master basis. To test its wider use, we now vary the physical structure as well as the loop order and include calculations that find their own basis. We keep the deployed models fixed so that these measurements test the current method on new inputs. The study contains @CASES@ native-family requests, of which @ELIGIBLE@ fit the application's current index limit. It also tests a separate restricted vacuum construction at every loop order from one through twelve. This is a finite coverage study; a loop-order label alone does not establish coverage of all graphs at that order.

\subsection{Physical families and complete-time controls}
The native grid includes vacuum families with one or several masses, massless and massive two-point families, four-point ladders, and boxes with bubble subgraphs. We add planar, nonplanar, and five-point examples with independent symbolic kinematic parameters. Appendix~\ref{app:coverage} gives the denominator definitions, parameters, and targets. The @INITIAL@ initial requests contain a sector-corner integral, one raised propagator power, and one numerator integral when an auxiliary denominator is available. Some massive two-point batches return every target unchanged as a master. We therefore preserve those results and add @FOLLOW@ separate batches containing every distribution of up to two dots over the physical denominators. The additional batches cover all six loop orders accepted for that two-point family, plus symbolic cases at one and two loops. Their inputs are fixed before their own comparison, and no model is refitted from either stage.

We first calculate a reference with expanded seeds and the revised implementation. A second calculation uses the previous executable and a larger numerator-rank bound, with the reference basis prescribed. Both must complete and reproduce the same coefficients before a case enters the repeated comparisons. This checks the reductions in the stated basis; it does not prove that the basis has the smallest possible size. Every native attempt has a 120-second allowance, a 6 GiB address-space limit, and a 5,200 MiB process-tree memory limit. An attempt that reaches a limit remains a failed result. Inputs with more than 31 indices exceed the current application's accepted domain and receive no timing estimate.

The first comparison runs the saved original Kira executable, the previous improved implementation, and the revised implementation with the same expanded seed region. These calculations receive no master list, so their times include basis discovery, equation generation, elimination, coefficient checks, and cleanup. This comparison measures the complete effect of the implementation. It makes no learned decision. The second comparison supplies the checked basis and runs the previous learned application, the revised learned application, and a native-choice control with revised preparation. Its times also include prediction and unsuccessful attempts. Both comparisons use three repetitions with rotated method order and fresh Kira processes. Initial caller imports and model loading remain separate from the repeated application times.

An input audit finds two box-with-bubble definitions that match saved training structures exactly but carry new family names. The initial application treats these names as unknown. We add a lookup that resolves a unique match of the ordered momentum forms, sector definition, and zero or nonzero mass pattern before prediction. Numerical mass and kinematic values remain free, as in the existing model signature, and all original feature-range checks remain active. Unmatched structures retain the native fallback. The lookup uses no measured time or reference coefficient. We repeat the paired application comparison for both names and use these corrected pairs in the application totals. The initial unknown-name measurements remain available separately. This correction allows the existing models to recognize their own domain; it does not train a new model or infer equivalence between different momentum representations.

\subsection{Coverage and measured time}
Figure~\ref{fig:coverage-grid} shows the rational grid, including its failures and unsupported inputs. The reference checks pass for @REFS@ requests, and @FULL@ requests complete all three revised full-calculation repetitions. Of these, @NONTRIV@ contain a nontrivial reduction and @IDENTITY@ contain only identity outputs. We exclude identity-only requests from speedup ratios. The supplied-basis selected application completes all repetitions for @SELECTED@ requests. The remaining requests retain their stated failure or support-limit classification. The timings therefore do not establish a nontrivial reduction for every entry in the grid.

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/coverage_grid.pdf}
\caption{Native IBP coverage in the rational grid. Blue requires a checked reference, a nontrivial reduction, and three exact revised full calculations including basis discovery. Pale green records only identity outputs. Orange records a failed reference or calculation within the stated limits. Gray records the current index limit. A cell takes the strongest verified status across initial and additional batches. Blank cells are absent from this grid; the two coincident one-loop definitions appear only once. Symbolic requests enter the timing table and the text totals.}
\label{fig:coverage-grid}
\end{figure}

Table~\ref{tab:coverage-times} uses a separate matched set for each comparison. A request enters a row only when both methods complete all repetitions and the reduction contains a nontrivial coefficient. We sum the median time of each request, so a smaller ratio means less total time on that completed set. The revised full calculation takes @ORIGINALCHANGE@ time than the saved original Kira executable and @PREVIOUSCHANGE@ time than the preceding improved implementation on their respective matched sets. The supplied-basis selected application takes @APPCHANGE@ time than the previous application and @NATIVECHANGE@ time than the revised native control. These aggregates retain slower individual requests and do not turn unsuccessful cases into speedup estimates.

\begin{table}[!htbp]\centering\small
\caption{Summed request median times in seconds. The revised column uses full revised calculations for the first two rows and the selected application for the last two. Each row names its own control and completed request count.}
\label{tab:coverage-times}
\begin{tabular}{@{}lrrrr@{}}\toprule
Control & Requests & Control time & Revised time & Ratio\\\midrule
@TABLE@
\bottomrule\end{tabular}
\end{table}

The repeated native comparisons contain @TIMED@ recorded requests, with @SUCCESS@ exact completions and @FAILED@ unsuccessful requests. The largest recorded process-tree memory use among these timings is @RSS@ MiB. The grid includes new graph definitions, so the existing domain guard often retains native choices. This is part of the deployed method and prevents us from describing the full implementation gain as a gain from newly learned decisions.

Table~\ref{tab:coverage-completion} also includes unsuccessful first timed requests. Its elapsed totals describe the cost actually incurred on that common reference-verified collection. They are not completed-reduction speedups, since a failed request supplies no accepted answer. This view complements the paired timing table and prevents completion failures from disappearing in an aggregate improvement claim.
\begin{table}[!htbp]\centering\small
\caption{First timed requests on the reference-verified collection. Elapsed seconds include failed requests. Later repetitions are excluded from this table so that each method receives one request per case.}
\label{tab:coverage-completion}
\begin{tabular}{@{}lrrr@{}}\toprule
Method & Requested & Exact completions & Elapsed seconds\\\midrule
@COMPLETION@
\bottomrule\end{tabular}
\end{table}

\subsection{Every tested loop order in the restricted vacuum class}
The existing vacuum recurrence has a different domain: unit powers on the massless lines and several massive denominators with the same total loop momentum. We construct three new mass profiles with two, three, or four distinct masses and six target exponent vectors per profile. We compare the saved original Kira, dense and selected supplied-identity systems, the frozen learned identity selector, and the deployed exact recurrence. Each method receives the same targets and passes the independent coefficient check derived in Appendix~\ref{app:vacuum}. The individual requests cover every loop order from one through twelve. Separate shared requests ask for all twelve orders together.

The study records @VACSUCCESS@ exact completions in @VACREQUESTS@ vacuum requests. Table~\ref{tab:coverage-vacuum} separates individual-loop requests from shared requests. In the individual-loop set, learned identity selection takes @LEARNEDCHANGE@ time than the fixed identity rule. The deployed recurrence takes @RECURRENCECHANGE@ time than the saved original Kira calculation. This gain uses the exact restricted-family relations and their implementation; the deployed recurrence uses its existing fixed policy. The native study and this supplied-identity study therefore establish different forms of coverage.

\begin{table}[!htbp]\centering\small
\caption{Restricted vacuum timings in seconds, summed over request medians. There are 36 individual-loop requests and three shared requests, each repeated three times. The original control solves separately for each requested loop order. The other methods can use the exact shared variable $z=L(d-2)$. All times include coefficient verification.}
\label{tab:coverage-vacuum}
\begin{tabular}{@{}lrr@{}}\toprule
Method & Individual loops & Shared loops\\\midrule
@VACROWS@
\bottomrule\end{tabular}
\end{table}

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/coverage_times.pdf}
\caption{Left: revised-to-control time ratios on matched completed native requests; the dashed line marks equal time. The request count changes with each pair's completed coverage. Right: restricted vacuum time at each loop order, summed over the three mass profiles. The logarithmic vertical axis keeps the exact recurrence and Kira-based calculations visible. These panels use different integral definitions and cannot be combined into a universal speedup.}
\label{fig:coverage-times}
\end{figure}

The broader tests identify where the current application completes an exact reduction, where its cost changes, and where its support or resource limits stop the calculation. They retain the earlier known-graph gain while restricting its interpretation to measured inputs. General high-loop scattering, arbitrary numerator rank, cuts, symbolic propagator powers, and every possible mass or kinematic assignment remain outside a universal verified claim.
'''
    values={'CASES':str(data['native_cases']),'ELIGIBLE':str(data['eligible']),'REFS':str(data['reference_verified']),'FULL':str(data['full_revised_verified']),'SELECTED':str(data['selected_verified']),'ORIGINALCHANGE':change(ft['ratio']),'PREVIOUSCHANGE':change(fp['ratio']),'APPCHANGE':change(ap['ratio']),'NATIVECHANGE':change(an['ratio']),'TABLE':table,'TIMED':str(data['native_timed']),'SUCCESS':str(data['native_successful']),'FAILED':str(data['native_failed']),'RSS':f"{data['peak_timed_rss_bytes']/1024**2:.1f}",'VACSUCCESS':str(data['vacuum_successful']),'VACREQUESTS':str(data['vacuum_requests']),'LEARNEDCHANGE':change(totals['learned']/totals['extreme']),'RECURRENCECHANGE':change(totals['recurrence']/totals['original']),'VACROWS':vacrows}
    for k,vv in values.items():section=section.replace('@'+k+'@',vv)
    for k,key in [('INITIAL','initial_cases'),('FOLLOW','followup_cases'),('NONTRIV','nontrivial_full_revised_verified'),('IDENTITY','identity_only_full_revised_verified')]:section=section.replace('@'+k+'@',str(data[key]))
    section=section.replace('@COMPLETION@',completion)
    sensitivity=data['native_control_sensitivity']
    paragraph=f"The revised native control passes through the same input checks and portfolio proposal before overriding the proposed action. For a conservative comparison, we subtract that entire recorded interval and the family-name lookup from its time, while retaining every selected-application cost. The largest removed interval is {1000*sensitivity['maximum_removed_seconds']:.3f} milliseconds. This gives an optimistic native total of {sensitivity['optimistic_seconds']:.3f} seconds, against which the selected application takes {change(sensitivity['selected_over_optimistic'])} time. The subtraction also removes useful input checks, so it supplies a sensitivity bound rather than a separately timed implementation.\n\n"
    section=section.replace('The repeated native comparisons contain',paragraph+'The repeated native comparisons contain',1)
    if data['recorded_attempt_limits'].get('180',0):
        section=section.replace('Every native attempt has a 120-second allowance,','Direct native attempts have a 120-second allowance,')
        section=section.replace('An attempt that reaches a limit remains a failed result.','The unchanged earlier application service retains its 180-second attempt limit when selected; the runtime audit records this exception to the planned direct-attempt limit. Its actual cost remains in the application totals. An attempt that reaches its limit remains a failed result.')
    section=section.replace('Appendix~\\ref{app:vacuum}',r'\CoverageVacuumDerivation{}')
    section=r'\providecommand{\CoverageVacuumDerivation}{Appendix~\ref{app:vacuum}}'+'\n'+section
    section=section.replace('The repeated native comparisons contain','The selected application and revised native control differ by only '+f"{abs(100*(1-an['ratio'])):.1f}"+r'\% in the summed medians. With only three repetitions, this small difference does not establish a reliable additional learned gain on the wider grid. The larger improvement against the preceding application includes the exact preparation changes.'+'\n\nThe repeated native comparisons contain',1)
    write(REPORT/'coverage_results.tex',section)
    appendix=r'''\section{Definitions and timing for the coverage grid}
\label{app:coverage}
The new grid uses the integral convention in Eq.~\eqref{eq:family}; every denominator includes the same implicit Feynman prescription. Let $Q=\sum_{i=1}^{L}\ell_i$. For $L\geq2$, the vacuum families have physical denominators
\begin{equation}
D_i=\ell_i^2-m_i^2\quad(1\leq i\leq L),\qquad
D_{L+1}=Q^2-m_{L+1}^2.
\end{equation}
The one-mass case sets $m_1^2=\cdots=m_L^2=0$ and $m_{L+1}^2=835$. The fully massive case sets $m_i^2=837+6(i-1)$ for each physical position. At one loop we instead use the single massive tadpole denominator $D_1=\ell_1^2-835$, since the two putative vacuum denominators would have dependent scalar-product coefficients. These numbers use a common squared-momentum unit.

The two-point families replace the final vacuum denominator by
\begin{equation}
D_{L+1}=(p-Q)^2-m_{L+1}^2,\qquad p^2=-847.
\end{equation}
The massless case sets every mass to zero; the massive case uses the same distinct squared masses as the fully massive vacuum. The four-point ladders and boxes with bubble subgraphs use Eqs.~\eqref{eq:higher-ladder} and~\eqref{eq:higher-bubble-box}, with $s=-5917$ and $t=-6747$. The main grid uses profile $h=409$. It defines these families through twelve loops before applying the current support limit. The two coincident one-loop definitions are included only once.

For $E$ independent external momenta, the scalar products consist of $L$ loop squares, $L(L-1)/2$ products of distinct loop momenta, and $LE$ loop--external products. Their total is therefore
\begin{equation}
N=L+\frac{L(L-1)}2+LE=\frac{L(L+1)}2+LE.
\end{equation}
This is the complete representation required for native IBP generation~\cite{Kira3}. We append candidate squared momentum differences only when their exact coefficient vector increases the rank of the physical denominator list. The resulting $N\times N$ coefficient matrix has rank $N$ for every declared family. This construction defines numerator coordinates even for cases that cannot enter the current application. In this grid the 31-index limit permits vacuum definitions through seven loops, two-point definitions through six loops, and four-point definitions through five loops. Permitted input size does not imply completion within the common limits.

Let $n$ be the number of physical denominators and let $\boldsymbol a^{(0)}$ have entries one on these denominators and zero on the auxiliary ones. The target batch is
\begin{equation}
\mathcal T=\{\boldsymbol a^{(0)},\ \boldsymbol a^{(0)}+\boldsymbol e_1\}
\cup\{\boldsymbol a^{(0)}-\boldsymbol e_{n+1}\ \text{if }N>n\},
\end{equation}
where $\boldsymbol e_i$ has unit entry at position $i$. The full comparison and first reference use positive-index bound $r=n+1$, numerator bound $s=1$, and dot bound one. The independent reference check raises the numerator bound to two. The full comparisons receive no preferred master list. The application comparisons receive the checked basis and retain their frozen learned choices, domain guards, and expansion recovery.

The symbolic additions are the one-loop tadpole, the one-loop massless two-point family, massive two-point families at one and two loops, and four-point ladders at one and two loops. Their nonzero squared masses and external invariants remain independent symbols. The nonplanar box, pentagon, and virtuality-box definitions in Appendix~\ref{app:families} add rational and symbolic requests. Their rational profile is $h=411$ in the previously defined parameter formulas. Each of these three structures uses the corner target and one extra power on its last physical denominator. These finite cases do not span arbitrary symbolic kinematics.

The additional massive two-point batches use rational profile $h=419$, so $p^2=-867$ and $m_i^2=857+6(i-1)$. Their symbolic variants retain independent masses and $p^2$. The target set includes $\boldsymbol a^{(0)}$, every $\boldsymbol a^{(0)}+\boldsymbol e_i$, every $\boldsymbol a^{(0)}+2\boldsymbol e_i$, and every $\boldsymbol a^{(0)}+\boldsymbol e_i+\boldsymbol e_j$ with $1\leq i<j\leq n$. It contains $1+2n+n(n-1)/2$ targets. The last count follows from choosing an unordered pair of distinct physical denominators. The expanded region uses $r=n+2$, numerator bound one, and dot bound two; the independent check raises the numerator bound to two. These batches supply a separate test of nontrivial reductions after the initial small requests, without replacing the original outcomes.

For the separate restricted vacuum study, the squared-mass ratios are the first $R$ entries of $(823,829,853,857)$, with $R=2,3,4$. We choose six distinct exponent vectors $\boldsymbol b$ with $\sum_j b_j=6$ and at least two positive entries. The vectors are fixed before the comparisons. Each request uses either one loop order or all twelve orders together. The exact recurrence and the Taylor check use the derivations in Appendix~\ref{app:vacuum}; this study does not infer those identities from a high-loop native reduction. The original Kira control generates and solves the full supplied identity system separately at each loop order. Other identity-based controls and the recurrence can substitute $z=L(d-2)$ after their shared calculation.

For method $m$, request $c$, and repetition $j$, let $T_{mcj}$ denote measured complete time. The matched total and reported ratio are
\begin{equation}
S_m(\mathcal C)=\sum_{c\in\mathcal C}\operatorname{median}_{j=1,2,3}T_{mcj},
\qquad R_{A/B}=\frac{S_A(\mathcal C)}{S_B(\mathcal C)}.
\end{equation}
The set $\mathcal C$ contains only requests with three exact completions for both compared methods. It is specified separately for each pair; no failed case receives an imputed completed time. The fractional time saving follows directly by subtracting the revised total from the control total and dividing by the control total:
\begin{equation}
\frac{S_B-S_A}{S_B}=1-\frac{S_A}{S_B}=1-R_{A/B}.
\end{equation}
The coverage table retains every excluded case. This separates a conditional timing gain from the probability that a request completes. Three timing repetitions supply the stated medians, not a confidence interval or a proof of global optimality.
'''
    vacuum_protocol=json.loads((HERE/'vacuum_protocol.json').read_text())
    # Put vectors in math mode and keep the longest row within the page width.
    rows=[]
    for c in vacuum_protocol['cases']:
        for i in [0,3]:
            rows.append((str(len(c['mass_ratios'])) if i==0 else '')+' & $'+',\\;'.join('('+','.join(map(str,b))+')' for b in c['targets'][i:i+3])+'$\\\\')
    vector_table='\n\\begin{table}[!htbp]\\centering\\small\n\\caption{The six target exponent vectors for each restricted vacuum profile.}\\label{tab:coverage-targets}\n\\begin{tabular}{@{}cl@{}}\\toprule\n$R$ & Target vectors $\\boldsymbol b$\\\\\\midrule\n'+'\n'.join(rows)+'\n\\bottomrule\\end{tabular}\n\\end{table}\n'
    appendix=appendix.replace('For method $m$, request $c$, and repetition $j$',vector_table+'\nFor method $m$, request $c$, and repetition $j$')
    appendix += '\nThe supplied-identity Kira workers use a 90-second solver limit, a 1,800 MiB address-space limit, a 1,500 MiB process-tree memory limit, and a 64 MiB temporary-file limit. The recurrence works within the same scheduler allocation and checks the expanded coefficients independently. Native and vacuum calculations run sequentially, so their temporary storage does not overlap.\n'
    appendix=appendix.replace('Appendix~\\ref{app:vacuum}',r'\CoverageVacuumDerivation{}')
    write(REPORT/'coverage_appendix.tex',appendix)
    paper=REPORT/'report.tex';s=paper.read_text()
    s=re.sub(r'\\date\{[^}]*\}',lambda m:'\\date{October 16, 2026}',s,count=1)
    if '\\input{coverage_results}' not in s:s=s.replace('\\input{parametric_results}','\\input{parametric_results}\n\\input{coverage_results}',1)
    if '\\input{coverage_appendix}' not in s:s=s.replace('\\input{parametric_appendix}','\\input{parametric_appendix}\n\\input{coverage_appendix}',1)
    s=s.replace('The latest comparison keeps every trained model fixed','The preparation comparison keeps every trained model fixed').replace('The latest gain comes from','The preparation gain comes from')
    broad=f"The broader coverage study in Section~\\ref{{sec:coverage}} defines {data['native_cases']} native-family requests through twelve loops. The current interface accepts {data['eligible']} of them, and {data['nontrivial_full_revised_verified']} complete three checked nontrivial full reductions with revised preparation. On {ft['count']} matched completed requests, the revised full calculation takes {change(ft['ratio'])} time than the saved original Kira executable. The supplied-basis selected application takes {change(an['ratio'])} time than the revised native control on its separate matched set. Unsupported, failed, and identity-only requests remain outside these timing ratios."
    key='\\subsection{What the model comparisons establish}\n'
    if 'The broader coverage study in Section~' not in s:s=s.replace(key,key+broad+'\n\n',1)
    old='The tests cover known graph structures, fresh rational parameters, selected symbolic targets, and connected scattering through four loops with supplied master bases. The earlier recurrence result through twelve loops retains its separate restricted-vacuum scope. General higher-loop scattering, arbitrary symbolic kinematics, and global optimality remain unverified. The measured application supplies exact recovery and resource limits within this stated scope.'
    s=s.replace(old,broad+'\n\nThe independent restricted-vacuum comparison verifies every loop order from one through twelve under its stated identity assumptions. The expanded native grid records the cases that exceed the interface, memory, or time limits. These results support measured improvements on completed inputs and do not establish a speedup for every integral type or loop order.')
    abstract=r'''Integration-by-parts reduction expresses Feynman integrals in a master basis, while equation choices and exact preparation determine its cost. We train models to select seeds, equations, and complete Kira strategies, and retain fixed choices where validation gives no learned benefit. Exact changes restrict sector polynomial construction and reuse unchanged selected equations within a reduction. An earlier known-graph comparison gives 19.6\% less time with the same model decisions. We then define @CASES@ native requests across vacuum, two-point, and scattering structures through twelve loops; @ELIGIBLE@ fit the current interface, and @FULL@ complete three checked revised full calculations. On @PAIRED@ matched completed requests, full reduction takes @CHANGE@ time than the saved original Kira executable, including master discovery. On the wider grid, the application controls establish no reliable additional gain from learned choices alone. A restricted supplied-identity vacuum study verifies all twelve loop orders. Failed and unsupported cases remain in the coverage record, and learned row elimination remains excluded. The results establish improvements within the measured domains, not universal performance across all loop integrals.'''
    abstract=abstract.replace('three checked revised full calculations','three checked nontrivial revised full calculations')
    for k,vv in {'CASES':str(data['native_cases']),'ELIGIBLE':str(data['eligible']),'FULL':str(data['nontrivial_full_revised_verified']),'PAIRED':str(ft['count']),'CHANGE':change(ft['ratio'])}.items():abstract=abstract.replace('@'+k+'@',vv)
    s=s.replace('Unsupported, failed, and identity-only requests remain outside these timing ratios.', 'The approximately 0.1\\% difference from the revised native control establishes no reliable additional learned gain on this wider set. Unsupported, failed, and identity-only requests remain outside these timing ratios.')
    s=s.replace('The approximately 0.1\\% difference from the revised native control establishes no reliable additional learned gain on this wider set. The approximately 0.1\\% difference from the revised native control establishes no reliable additional learned gain on this wider set.', 'The approximately 0.1\\% difference from the revised native control establishes no reliable additional learned gain on this wider set.')
    s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,count=1,flags=re.S);write(paper,s)
    notes=REPORT/'notes.tex';s=notes.read_text()
    if '\\input{coverage_results}' not in s:s=s.replace('\\input{parametric_results}','\\input{parametric_results}\n\\input{coverage_results}',1)
    if '\\input{coverage_appendix}' not in s:s=s.replace('\\input{parametric_appendix}','\\input{parametric_appendix}\n\\input{coverage_appendix}',1)
    if r'\newcommand{\CoverageVacuumDerivation}' not in s:
        s=s.replace(r'\input{coverage_results}',r'\newcommand{\CoverageVacuumDerivation}{Section~\ref{sec:higher-loop-generation}}'+'\n'+r'\input{coverage_results}',1)
    note_conclusion='\n% BEGIN CURRENT COVERAGE CONCLUSION\n'+broad+' The small difference from the revised native control establishes no reliable additional learned gain on the wider set.\n% END CURRENT COVERAGE CONCLUSION\n'
    if '% BEGIN CURRENT COVERAGE CONCLUSION' in s:
        s=re.sub(r'\n% BEGIN CURRENT COVERAGE CONCLUSION\n.*?% END CURRENT COVERAGE CONCLUSION\n',lambda m:note_conclusion,s,flags=re.S)
    else:s=s.replace('% END CURRENT PORTFOLIO CONCLUSION\n','% END CURRENT PORTFOLIO CONCLUSION\n'+note_conclusion,1)
    write(notes,s)
    p=REPORT/'Makefile';s=p.read_text();s=s.replace('parametric_results.tex parametric_appendix.tex paper_references.bib','parametric_results.tex parametric_appendix.tex coverage_results.tex coverage_appendix.tex paper_references.bib');write(p,s)
    p=REPORT/'s01_check_paper.py';s=p.read_text();s=s.replace("'parametric_results.tex','parametric_appendix.tex']","'parametric_results.tex','parametric_appendix.tex','coverage_results.tex','coverage_appendix.tex']");write(p,s)
    for parent in [HERE,*[p for p in HERE.rglob('*') if p.is_dir() and '__pycache__' not in p.parts]]:
        text='# '+parent.name.replace('_',' ')+'\n\n'
        if parent==HERE:
            text+='This study tests a finite grid. It does not cover every integral or unlimited loop orders.\n'
            text+=f"The native grid has {data['native_cases']} requests. The current interface accepts {data['eligible']} requests.\nRead `summary.json` for exact completions, failures, paired time totals, and unsupported inputs.\n"
            text+='The native runs generate IBP identities. The vacuum runs use supplied Euler and mass identities.\nKeep these two comparisons separate. Existing models remain frozen.\n\n'
            text+='Run all calculations on Hoffman with the existing Python environment.\nUse `s02_job.sh` through `qsub`. Run one job at a time.\nKeep the memory, time, and storage limits in `resource_plan.json`.\n\n'
            text+='`s00_cases.py` defines physical denominators and target indices.\n`s01_study.py` freezes the native protocol and runs the comparisons.\n`s02_job.sh` supplies the scheduler limits.\n`s03_vacuum.py` compares original Kira, identity selection, and exact recurrence through twelve loops.\n`s04_original_runner.py` is the bounded runner with the original executable allowed.\n`s05_analyze.py` checks results and draws the figures.\n`s06_report.py` writes the scientific sections and these guides.\n`s07_finish.py` builds both documents and checks publication inputs.\n\n'
            text+='`s08_nontrivial.py` adds separate massive two-point batches with up to two dots.\n`s09_family_names.py` resolves unique exact definition matches and checks the two corrected family names.\nUse its `--case`, `--basis`, and `--output` options to run a new supplied-basis request.\nRun it without options to repeat the recorded name checks.\nUse the execution order: development pilot, native study, vacuum study, additional batches, name checks, analysis, document build.\nThe native study accepts `--pilot` for its small development check.\nThe saved protocols fix the models and inputs before timing. Do not tune a policy from these tests.\nThe original runner uses the saved Kira executable with custom optimization flags cleared.\nA full request discovers its master basis. An application request receives the checked basis.\nReported paired ratios exclude failed, unsupported, and identity-only requests. The coverage record retains them.\n'
            text+='`s10_audit_coefficients.py` checks saved vacuum coefficients with symbolic algebra and the analytic oracle.\nThe finish script runs this check before the analysis and document build.\n'
            text+='\nGenerated data stay on Hoffman and GitHub. Copy only the report artifacts locally.\n'
            text+='See [native coverage](../../report/paper_figures/coverage_grid.pdf) and [matched times](../../report/paper_figures/coverage_times.pdf).\n'
        else:
            purposes={'coverage':'Each record states whether a request completed, failed, or exceeded the current index limit.','references':'These records contain expanded-seed master bases, exact coefficients, and independent enlarged checks.','model_test':'These records contain timed methods, repetitions, exact checks, recovery attempts, and failure reasons.','development':'These records contain three small checks made before the reserved comparison.','vacuum_test':'These records compare supplied vacuum identities and exact recurrence across all twelve loop orders.','nontrivial_followup':'These records preserve the additional massive two-point batches and their wider target sets.','family_names':'These records check exact definition matching before the existing models choose their settings.'}
            text+=purposes.get(parent.name,'This folder contains coverage-study evidence.')+'\nRead the [parent guide](../README.md) for the full procedure.\n'
            text+='The `.json.gz` files contain compressed JSON records. The study reader restores them without changing their values.\n'
            text+='Keep failed and incomplete records. A failed calculation does not define a completed-time speedup.\n'
        write(parent/'README.md',text)
    for p,text in [(ROOT/'README.md','Read [the broader coverage study](Kira_comparison/coverage_study/README.md) for full-basis calculations, all twelve restricted vacuum loop orders, and remaining limits.'),(ROOT/'Kira_comparison/README.md','The [coverage study](coverage_study/README.md) compares complete reductions and records unsupported or failed cases.'),(REPORT/'README.md','`coverage_results.tex` and `coverage_appendix.tex` describe the broader tests.\n`coverage_data.json` supplies their measured values. The new figures show coverage and matched complete times.'),(REPORT/'paper_figures/README.md','`coverage_grid.pdf` shows verified native coverage and its limits.\n`coverage_times.pdf` separates complete native requests from restricted vacuum identities.')]:
        s=p.read_text();block='\n<!-- BEGIN COVERAGE STUDY -->\n'+text+'\n<!-- END COVERAGE STUDY -->\n'
        if '<!-- BEGIN COVERAGE STUDY -->' in s:s=re.sub(r'\n<!-- BEGIN COVERAGE STUDY -->.*?<!-- END COVERAGE STUDY -->\n',lambda m:block,s,flags=re.S)
        else:s+=block
        write(p,s)
if __name__=='__main__':main()
