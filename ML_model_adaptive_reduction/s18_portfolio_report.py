"""Describe the measured final policy, its controls, and its physical scope."""
import json, re, statistics
from pathlib import Path
import s07_report as previous
HERE, ROOT, REPORT = previous.HERE, previous.ROOT, previous.REPORT
NAMES=previous.NAMES

def change(ratio):return previous.change(ratio)

def main():
    d=json.loads((HERE/'selective_expansion/summary.json').read_text())
    initial=json.loads((HERE/'summary.json').read_text())
    assert d['complete'] and d['all_exact'];t=d['totals']
    rows='\n'.join(f'{NAMES[g]} & {v["seconds"]["native"]:.3f} & {v["seconds"]["published"]:.3f} & {v["seconds"]["fixed"]:.3f} & {v["seconds"]["selected"]:.3f}'+r'\\' for g,v in d['by_graph'].items())
    enabled=', '.join(NAMES[g].lower() for g in d['enabled_graphs']) or 'none of the tested graph structures'
    body=r'''\section{A learned portfolio of complete reduction strategies}
\label{sec:portfolio}
The preceding comparisons show that the useful decision depends on both the denominator structure and the target powers. A seed region that suffices for one batch can leave another batch unreduced, while expanding every seed limit can generate equations that the calculation does not need. We therefore train a model to choose a complete calculation from several strategies before Kira generates the equations. This choice includes the previous workflow as a candidate, so the new policy can retain that workflow when its measured cost is lower.

\subsection{What the model chooses}
For a target batch, let $r_0$ be the largest sum of positive indices, $s_0$ the largest total numerator power, and $d_0$ the largest number of extra denominator powers, or dots. Kira uses limits of this kind to define the seed region~\cite{Kira3}. Our earlier complete-cost policy chooses among seven regions or equation settings, as described in Appendix~\ref{sec:adaptive}. A development comparison reveals a useful additional choice: increase $s_0$ by one while leaving the positive-index and dot limits unchanged. This selective expansion can supply missing identities without the cost of increasing all three limits.

The final portfolio contains five choices: the earlier cost policy with one or two workers, selective numerator-rank expansion with one or two workers, and the previous workflow from Appendix~\ref{app:thread-policy}. A worker carries out tasks in Kira's existing parallel symbolic solver~\cite{KiraOriginal}. The previous workflow combines its existing graph, seed, and worker choices; its parameters remain fixed in this comparison. Each choice uses the same exact preprocessing and a supplied master basis. The three- and four-loop bubble boxes have no trained policy in the previous workflow, so its control uses the documented native fallback. We retain Kira's native row elimination because the learned row model has not reduced complete time reliably.

Each attempt must express every target in the prescribed basis. If it cannot do so, the calculation retries with native seeds and then an expanded seed region. We skip a repeated attempt when its effective seed bounds, ordering, and equation filter are identical to those already tried. The model does not predict reduction coefficients. It predicts the relative time of these complete strategies, including checks, failed attempts, and recovery. Appendix~\ref{app:portfolio} defines the model inputs, objective, guard, and exact recovery procedure.

\subsection{Training and independent tests}
We fit @CANDIDATES@ candidate predictors using @TRAIN@ training batches and select the predictor, fixed control, and decision threshold using @VALID@ separate validation batches. The candidates include regression trees, random forests, and extremely randomized trees~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}. Their twenty inputs describe the graph structure, target powers, numerator ranks, number of targets, and distribution of dots. They contain no reference coefficients or measured test times. The recorded label calculations take @OFFLINE@ seconds, and fitting takes @FIT@ seconds. These costs occur before deployment.

For each graph, validation also selects the fastest fixed portfolio choice. The model replaces this choice only if it reduces summed validation time by at least two percent and gives a saving in both validation repetitions. This rule enables target-dependent portfolio predictions for @ENABLED@. @SELECTEDMODELS@ A retained portfolio choice can itself contain an earlier learned policy; therefore the fixed-portfolio control isolates the added outer decision, rather than removing all earlier learned decisions. Requests outside the recorded graph structures and feature ranges use native settings.

The reserved test uses rational kinematic profile $h=306$ and symbolic targets with a dot position absent from the earlier symbolic training and validation sets. The earlier reserved profiles do not enter fitting or selection. The completed comparison contains @TEST@ batches from nine known graph structures through four loops, with one to three targets per batch. Appendix~\ref{app:portfolio} specifies the targets and reference checks. These tests change kinematics and target positions within known structures; some rational target patterns recur across profiles. They do not test transfer to arbitrary new graphs or larger target batches.

Every method receives the same two-core allocation and an 8\,GiB memory allowance. The native control and earlier cost-policy control use one Kira worker. The previous workflow, fixed portfolio, and selected portfolio can use one or two workers according to their chosen strategy. We rotate method order and repeat each method three times, with a fresh Kira process and temporary files for every attempt. Complete time includes prediction, preparation, exact algebra, coefficient checks, cleanup, and recovery. Model imports, initial model loading, reference construction, and basis discovery are separate. No coefficient cache supplies the test answers.

\subsection{Complete-time results}
Table~\ref{tab:portfolio} sums the three-run median times of the individual batches. The selected portfolio takes @SELECTED@ seconds, compared with @NATIVE@ seconds for native choices and @PUBLISHED@ seconds for the previous workflow in the same improved executable. These results correspond to @NATIVECHANGE@ than native choices and @PUBLISHEDCHANGE@ than the previous workflow. The earlier cost policy takes @ADAPTIVE@ seconds on these same inputs. The graph-specific fixed portfolio takes @FIXED@ seconds, so the added portfolio decision gives @FIXEDCHANGE@ relative to this stronger control. Figure~\ref{fig:portfolio-controls} shows where these differences occur.

@TRIALRESULTS@

\begin{table}[!htbp]\centering\small
\caption{Complete reduction times in seconds. Each row sums batch medians from matched tests with common exact preprocessing. ``Fixed'' selects a portfolio choice per graph using validation only.}
\label{tab:portfolio}
\begin{tabular}{@{}lrrrr@{}}\toprule
Graph & Native & Previous & Fixed & Selected\\\midrule
@ROWS@
\midrule Total & @NATIVE@ & @PUBLISHED@ & @FIXED@ & @SELECTED@\\\bottomrule
\end{tabular}\end{table}

All @WORKFLOWS@ timed reductions and @APPLICATIONS@ further applications reproduce the reference coefficients exactly. The applications receive only the prescribed master basis before reduction; the comparison with reference coefficients follows execution. The selected portfolio requires @FALLBACK@ recovery attempts across the timed tests. Its median outer decision time is @DECISION@ milliseconds. The CPU-time totals are @CPUNATIVE@ seconds for native choices and @CPUSELECTED@ seconds for the selected portfolio. Reporting both wall and CPU time separates elapsed-time savings from changes in CPU use, as shown in Figure~\ref{fig:portfolio-totals}. @UNFINISHED@

@WORKEXAMPLE@

@LOADING@

\begin{figure}[tbp]\centering
\includegraphics[width=\linewidth]{paper_figures/portfolio_controls.pdf}
\caption{Selected-portfolio time relative to the previous workflow and the graph-specific fixed portfolio. Points divide sums of batch median times. Horizontal segments show the range of the three corresponding repetition totals; they are descriptive ranges, not confidence intervals. Values below one indicate a saving.}
\label{fig:portfolio-controls}\end{figure}

\begin{figure}[tbp]\centering
\includegraphics[width=\linewidth]{paper_figures/portfolio_totals.pdf}
\caption{Complete wall time and recorded process CPU time for the same reserved batches. The five methods share exact preprocessing and a two-core allocation. CPU time counts the main driver, Kira child processes, and the timed part of the previous-workflow service. Its message conversion lies outside that service's CPU counter but remains in complete wall time. Initial loading lies outside the repeated timings.}
\label{fig:portfolio-totals}\end{figure}

\subsection{Separating the exact implementation changes}
The portfolio tests use two exact improvements in every method. We index the sector files that exist instead of searching for absent files, while retaining their original processing order. We also simplify the criterion for zero sectors by setting Feynman parameters absent from all declared top sectors to zero before forming that criterion. The complete parametric polynomials remain available for the other operations. Appendix~\ref{app:adaptive} proves why this projection preserves the criterion in the declared sector domain, following the parametric treatment of zero sectors~\cite{Lee2014LiteRed}.

Separate matched tests enable these changes in sequence for connected bubble boxes. @PREPARATIONRESULTS@ These comparisons include exact implementation changes and therefore do not measure an isolated ML gain. Figure~\ref{fig:adaptive-integration} and Table~\ref{tab:adaptive-integration} preserve the intermediate controls in the earlier cost study. The common-preprocessing comparison in Table~\ref{tab:portfolio} measures the subsequent portfolio choices separately.

The measurements support the selected strategies in the stated domain. Timing differences can remain when two methods choose the same strategy, and the three repetitions do not establish a significant gain for every graph. General higher-loop scattering, arbitrary symbolic kinematics, automatic discovery of a minimal master basis, and globally optimal elimination paths remain outside the demonstrated scope.
'''
    integ={c['loops']:c for c in initial['integration']}
    subs={'@CANDIDATES@':str(d['model_candidates']),'@TRAIN@':str(d['training_cases']),'@VALID@':str(d['validation_cases']),
        '@OFFLINE@':f'{d["offline_label_seconds"]:.1f}','@FIT@':f'{d["training_seconds"]:.3f}','@ENABLED@':enabled,
        '@SELECTEDMODELS@':('All enabled outer predictors are single regression trees.'
            if d['enabled_graphs'] and all(d['guard'][g]['trees']==1 for g in d['enabled_graphs'])
            else 'Validation selects the deployed predictor separately for each graph.'),
        '@TEST@':str(d['test_cases']),'@ROWS@':rows,'@WORKFLOWS@':str(d['timed_test_workflows']),
        '@APPLICATIONS@':str(d['applications']),'@FALLBACK@':str(d['fallbacks']['selected']),
        '@DECISION@':f'{1000*d["median_decision_seconds"]:.3f}',
        '@CPUNATIVE@':f'{d["cpu_totals"]["native"]:.3f}','@CPUSELECTED@':f'{d["cpu_totals"]["selected"]:.3f}',
        '@UNFINISHED@':(f'{len(d["unfinished"])} planned test batches lack a completed independent reference check and receive no speedup estimate.' if d['unfinished'] else 'Every planned batch completes both reference calculations.')}
    trial=d['all_trial_ratios']
    subs['@TRIALRESULTS@']=f'''Summing every timed repetition gives {change(trial['native'])} than native choices, {change(trial['published'])} than the previous workflow, and {change(trial['fixed'])} than the fixed portfolio. The small difference from the fixed portfolio changes sign between the two summaries. These measurements establish no stable aggregate saving from the added outer prediction. The practical improvement over the previous workflow includes the revised candidate strategies and worker choices, which also benefit the fixed portfolio.'''
    for key in ['native','published','fixed','adaptive','selected']:
        subs['@'+key.upper()+'@']=f'{t[key]:.3f}'
        if key!='selected':subs['@'+key.upper()+'CHANGE@']=change(t['selected']/t[key])
    example=next((c for c in d['cases'] if c['case']=='ladder3_p306_dots'),None)
    subs['@WORKEXAMPLE@']=''
    if example:
        n=example['methods']['native'];m=example['methods']['selected']
        def bounds(v):return ', then '.join('$('+','.join(map(str,b))+')$' for b in v)
        subs['@WORKEXAMPLE@']=f'''The dotted three-loop two-point ladder illustrates the change in the equation system. Native choices use seed limits {bounds(n['seed_bounds'])}, while the selected portfolio uses {bounds(m['seed_bounds'])}, in the order $(r,s,d_{{\\rm dots}})$. Summing the reported generated-equation counts across all attempts gives medians of {statistics.median(n['generated_equations']):,.0f} equations for native choices and {statistics.median(m['generated_equations']):,.0f} for the selected portfolio. Their complete times are {n['median_seconds']:.3f} and {m['median_seconds']:.3f} seconds. This count measures equation generation; symbolic simplification can require different work per equation. The CPU-time comparison also accounts for the effect of worker count.'''
    preparation=[]
    for loops in [3,4]:
        methods=integ[loops]['methods'];old=methods['previous']['median_seconds'];new=methods['learned']['median_seconds']
        if old is not None and new is not None:
            preparation.append(f'For the {loops}-loop batch, the complete time changes from {old:.3f} to {new:.3f} seconds with the first study\'s validated policy, an overall factor of {old/new:.2f}.')
        else:
            failed=sum(methods['previous']['failed_seconds'])
            preparation.append(f'The {loops}-loop previous-preparation control does not complete after {failed:.1f} seconds across its bounded attempts. Further repetitions of this failed control are omitted, while the remaining settings are completed. The fully improved calculation takes {new:.3f} seconds, but the incomplete control supplies no measured overall speedup factor.')
            files=methods['files']['median_seconds'];projected=methods['projected']['median_seconds']
            if files is not None and projected is not None:
                preparation.append(f'With file indexing already enabled, projection changes its complete time from {files:.3f} to {projected:.3f} seconds, a factor of {files/projected:.2f}.')
    subs['@PREPARATIONRESULTS@']=' '.join(preparation)
    load=d['application_loading']
    subs['@LOADING@']=f'''The application also avoids loading the previous workflow until a selected strategy requires it. On the dotted sunrise batch, three rotated comparisons of a new application instance give median request times of {load['eager']['median_request_seconds']:.3f} seconds with immediate loading and {load['deferred']['median_request_seconds']:.3f} seconds with deferred loading. These times include construction, one reduction, an exact coefficient check, and closure, while common Python imports remain outside the timer. All six requests choose the same strategy and return the same exact coefficients. This separate interface saving applies when the request does not need the previous workflow. A request that first selects that workflow pays its loading cost within the application time. The repeated portfolio timings above already keep the models loaded, so they receive no additional saving from this change.'''
    for key,value in subs.items():body=body.replace(key,value)
    assert not re.search(r'@[A-Z]+@',body)
    (REPORT/'portfolio_results.tex').write_text(body)
    appendix=r'''\section{Complete-cost portfolio: definitions and derivation}
\label{app:portfolio}
\subsection{Targets and seed choices}
For a batch $\mathcal T$ of index vectors $\mathbf a$, define
\begin{equation}
r_0=\max_{\mathbf a\in\mathcal T}\sum_i\max(a_i,0),\qquad
s_0=\max_{\mathbf a\in\mathcal T}\sum_i\max(-a_i,0),\qquad
d_0=\max_{\mathbf a\in\mathcal T}\sum_i\max(a_i-1,0).
\end{equation}
These definitions count positive powers, numerator rank, and dots separately. Selective expansion uses $(r_0,s_0+1,d_0)$, with the positive-index limit floored at the largest declared top-sector size. The full expansion uses $(r_0+1,s_0+1,d_0+1)$. The five portfolio choices combine the earlier validated policy or selective expansion with one or two workers, and retain the previous workflow as a fifth choice. A failed new-policy attempt proceeds to native seeds and then full expansion. Skipping identical effective configurations removes a repeated calculation with the same equations, ordering, basis, and filter; it introduces no new algebraic relation.

The training and validation cases are the 47 and 26 cases defined in Appendix~\ref{app:adaptive}. The reserved rational cases use the same family definitions at $h=306$ and the target constructions with $j=0,1,2$. The three symbolic graphs instead use the corner target with $a_4=3$, so the fourth physical denominator has power three. For the four-loop bubble box, the reference uses $(r,s,d_{\rm dots})=(12,1,2)$ and its independent check uses $(12,2,2)$. All other reserved references use full expansion and then raise its numerator-rank bound by one more unit. These limits were fixed before any new reserved calculation. A common supplied basis permits exact coefficient comparisons; these checks do not prove its minimality.

\subsection{Learning relative complete cost}
Let $T_{ba}>0$ denote the measured complete time for training batch $b$ and portfolio choice $a$. Let $a_0$ denote the earlier cost policy with one worker. We define
\begin{equation}
y_{ba}=\log\frac{T_{ba}}{T_{ba_0}}.
\label{eq:portfolio-label}
\end{equation}
For the same batch, subtracting two labels gives $y_{ba}-y_{ba'}=\log(T_{ba}/T_{ba'})$. Since the logarithm is increasing, the choice with the smallest exact label also has the smallest measured time. A regression model $f$ estimates the five labels from the twenty features $x_b$ given in Appendix~\ref{app:adaptive}. Its fitted objective is
\begin{equation}
\mathcal L(f)=\sum_{b\in\mathcal B_{\rm train}}\sqrt{T_{ba_0}}\sum_a\bigl[f_a(x_b)-y_{ba}\bigr]^2.
\end{equation}
The positive weight increases the influence of costly training batches without changing their preferred action. It is a chosen training objective, not a proof that the fitted model minimizes future wall time. Each label includes native recovery, so an unsuccessful first attempt carries its measured cost.

We fit nine global models: a regression tree, a 48-tree random forest, and a 48-tree extremely randomized ensemble at depths 3, 5, and 8. Each leaf has at least two training cases. Graphs with at least four training cases also receive three local regression trees at depths 1, 2, and 3. Tree methods follow the cited constructions~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}. The saved evaluator reproduces the fitted predictions before validation begins.

\subsection{Validation and the deployment guard}
For graph $g$, let $c_g$ be the fixed portfolio choice with the smallest sum of validation batch median times. If $a_\star=\arg\min_a f_a(x)$, a predictor with gate $\gamma$ proposes $a_\star$ only when
\begin{equation}
f_{a_\star}(x)<f_{c_g}(x)-\gamma,\qquad \gamma\in\{0,0.05,0.15\}.
\end{equation}
Otherwise it uses $c_g$. Under exact labels, exponentiation gives $T_{ba_\star}/T_{bc_g}<e^{-\gamma}$; with fitted labels this is a predicted saving, not a guarantee. Validation selects the predictor and gate for each graph. Deployment enables this outer prediction only if its summed validation median time is at most $0.98$ times the fixed-control time and it wins both validation repetitions. The alternative is $c_g$. Graph structure and feature-range checks send unsupported inputs to native settings. A fixed portfolio choice can contain the earlier policy; the outer guard evaluates only the added decision.

\subsection{Correctness and timing}
The input to each reduction is the family, target batch, and prescribed master basis. Kira generates the exact identities and returns symbolic coefficients in that basis. The test then checks each coefficient by exact rational-function subtraction against the independently checked reference. The caller does not provide those reference coefficients to the deployed predictor or to the application. Thus the learned choice affects which calculation is attempted, while the algebraic identities determine the returned relation. Failure to reach the supplied basis triggers recovery; exhausting the bounded attempts returns failure.

For method $m$, the reported aggregate is $\sum_b\operatorname{median}_{r=1,2,3}T_{bmr}$. The speedup relative to control $c$ is the ratio of its aggregate to the selected aggregate. This follows by dividing the times required for the same collection of batches. We also report totals over all repetitions and process CPU times. These summaries describe the measured collection; they are not statistical confidence intervals or guarantees for unseen integral families. All methods use the same exact executable and two-core allocation. The earlier preparation study uses a separate one-core allocation, so its speedup factors are not multiplied by these portfolio ratios.
'''
    (REPORT/'portfolio_appendix.tex').write_text(appendix)
    p=REPORT/'report.tex';s=p.read_text()
    s=s.replace('A final redesign learns one complete-cost policy and separates its contribution from exact preprocessing improvements.',
        'The final method chooses among complete reduction strategies and measures its added benefit against fixed settings for each graph. Separate controls measure the exact preprocessing improvements.')
    s=s.replace('The main comparisons repeat each calculation five times and use the median to reduce the influence of an unusually fast or slow run.',
        'The original local-model comparisons repeat each calculation five times. The final complete-cost comparisons use three repetitions, with the method order rotated. Each comparison reports batch medians and states its repetition count.')
    s=s.replace('Its results motivate the single complete-cost policy presented afterwards.',
        'Its results motivate choosing among complete reduction strategies in the following section.')
    # Preserve the first policy study as a complete appendix, with its labels.
    if '\\input{portfolio_results}' not in s:
        s=s.replace('\\input{adaptive_results}','\\input{portfolio_results}',1)
        s=s.replace('\\input{adaptive_appendix}','\\input{adaptive_results}\n\\input{adaptive_appendix}\n\\input{portfolio_appendix}',1)
    abstract=f'''Integration-by-parts reduction expresses Feynman integrals in terms of master integrals, but the choice of seeds and reduction settings can change its cost. We train models on complete Kira timings and use validation to select among seed strategies, equation settings, and one or two workers. The final portfolio retains earlier strategies and uses a new prediction only where validation supports it. All choices preserve exact algebra and include recovery from insufficient seed sets. On {d['test_cases']} reserved batches from known graph structures through four loops, the selected portfolio takes {t['selected']:.2f} seconds, compared with {t['native']:.2f} seconds for native choices, {t['published']:.2f} seconds for the previous workflow, and {t['fixed']:.2f} seconds for a fixed portfolio choice per graph. These are sums of batch median times in the same improved executable. All {d['timed_test_workflows']} timed reductions and {d['applications']} additional applications reproduce independent reference coefficients exactly. Separate controls measure the effect of exact sector-file indexing and projection of the zero-sector criterion. Learned row elimination remains excluded because it has not given a reliable complete-time saving. The results identify where the measured strategies help, with explicit limits on graph structure, target patterns, and symbolic kinematics.'''
    abstract=abstract.replace('All '+str(d['timed_test_workflows'])+' timed reductions',
        'The small saving relative to the fixed portfolio changes sign when all repetitions are summed, so the added outer prediction has no stable aggregate advantage. All '+str(d['timed_test_workflows'])+' timed reductions',1)
    s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',s,count=1,flags=re.S)
    start=s.index('\\subsection{What the model comparisons establish}');end=s.index('\\begin{table}',start)
    overview=f'''\\subsection{{What the model comparisons establish}}
The final portfolio selects a complete calculation before equation generation. On its {d['test_cases']} fresh test batches, it takes {t['selected']:.3f} seconds against {t['published']:.3f} seconds for the previous workflow and {t['fixed']:.3f} seconds for graph-specific fixed portfolio choices. Section~\\ref{{sec:portfolio}} gives the matched conditions and the individual graph results. The comparison with the previous workflow measures the practical change from the earlier method, while the fixed-portfolio comparison isolates the added outer prediction.

The earlier model tests and the exact preprocessing study answer separate questions. Seed and equation selection help in their measured domains, while learned row selection remains omitted. Exact preprocessing reduces costs shared by every portfolio candidate. Restricted vacuum recurrence and repeated-request reuse supply further savings under their own assumptions. These experiments use different inputs and controls, so their speedup factors cannot be multiplied.

'''
    s=s[:start]+overview+s[end:]
    marker='% BEGIN FINAL PORTFOLIO SUMMARY';last='% END FINAL PORTFOLIO SUMMARY'
    table=marker+'\n'+f'Final portfolio & Fresh known-graph batches, loops 1--4 & {change(d["ratios"]["published"])} than the previous workflow'+r'\\'+'\n'+f'Added portfolio prediction & Same batches and exact preprocessing & {change(d["ratios"]["fixed"])} than the graph-specific fixed portfolio'+r'\\'+'\n'+last+'\n'
    if marker in s:s=re.sub(re.escape(marker)+'.*?'+re.escape(last)+'\n?',lambda _:table,s,flags=re.S)
    else:s=s.replace('% BEGIN CURRENT COST SUMMARY',table+'% BEGIN CURRENT COST SUMMARY',1)
    start=s.index('\\section{Conclusion}');end=s.index('\\appendix',start)
    conclusion=f'''\\section{{Conclusion}}
We have trained and tested models that choose the calculation used to reduce Feynman integrals with Kira. The final method compares complete strategies, including selective seed expansion, the earlier learned policies, and one or two workers. Its labels include failed attempts, exact checks, and recovery. Validation selects fixed settings for each graph and enables an additional prediction only where the measured validation saving supports it.

On {d['test_cases']} fresh batches, the selected portfolio takes {t['selected']:.3f} seconds in summed batch median time. It uses {change(d['ratios']['native'])} than native choices, {change(d['ratios']['published'])} than the previous workflow, and {change(d['ratios']['fixed'])} than the graph-specific fixed portfolio. All {d['timed_test_workflows']} timed reductions and {d['applications']} further applications agree exactly with their reference coefficients. Individual graph results and CPU times identify both savings and remaining costs. The row model remains excluded because its complete-time tests do not show a reliable benefit.

Across all repetitions, the selected portfolio uses {change(d['all_trial_ratios']['published'])} than the previous workflow and {change(d['all_trial_ratios']['fixed'])} than the fixed portfolio. The added outer prediction therefore has no stable aggregate advantage over the stronger fixed control. The revised strategy set and its integration with Kira account for much of the practical saving.

The exact implementation changes make a separate contribution by avoiding searches for absent sector files and simplifying the zero-sector criterion within the declared sector domain. Their matched controls distinguish this contribution from prediction. The earlier recurrence and shared-request methods remain separate forms of exact reuse.

The completed tests cover known graph structures, fresh rational kinematics, selected symbolic targets, and connected scattering families through four loops. They assume a prescribed master basis. Broader higher-loop scattering, unrestricted symbolic kinematics, and globally optimal reduction paths remain unverified. The current evidence supports the measured choices within this domain and provides explicit fallback and resource limits for other requests.

'''
    s=s[:start]+conclusion+s[end:]
    s=s.replace('October 15, 2026','October 16, 2026');p.write_text(s)
    p=REPORT/'notes.tex';s=p.read_text()
    if '\\input{portfolio_results}' not in s:
        s=s.replace('\\input{adaptive_results}','\\input{adaptive_results}\n\\input{portfolio_results}',1)
        s=s.replace('\\input{adaptive_appendix}','\\input{adaptive_appendix}\n\\input{portfolio_appendix}',1)
    begin='% BEGIN CURRENT PORTFOLIO CONCLUSION';end='% END CURRENT PORTFOLIO CONCLUSION'
    conclusion=f'''{begin}
The current portfolio in Section~\\ref{{sec:portfolio}} compares complete strategies using measured costs. On {d['test_cases']} fresh batches, its summed median time is {t['selected']:.3f} seconds, against {t['published']:.3f} seconds for the previous workflow and {t['fixed']:.3f} seconds for a fixed portfolio choice per graph. Summing all repetitions gives {change(d['all_trial_ratios']['fixed'])} than the fixed portfolio, so the added outer prediction has no stable aggregate advantage over that control. All {d['timed_test_workflows']} timed reductions and {d['applications']} further applications reproduce the reference coefficients exactly. Its selection rule uses validation data only, retains native row elimination, and has explicit recovery steps. The separate preprocessing controls distinguish exact implementation gains from prediction. The supported native tests cover known graph structures through four loops with supplied master bases; the earlier twelve-loop recurrence result retains its separate restricted-family scope.
{end}
'''
    if begin in s:s=re.sub(re.escape(begin)+'.*?'+re.escape(end)+'\n?',lambda _:conclusion,s,flags=re.S)
    else:s=s.replace('\\clearpage\n\\renewcommand{\\refname}{Citations}',
        '% BEGIN CURRENT WORKFLOW UPDATE\n'+conclusion+'% END CURRENT WORKFLOW UPDATE\n\\clearpage\n\\renewcommand{\\refname}{Citations}',1)
    p.write_text(s)
    p=REPORT/'s01_check_paper.py';s=p.read_text()
    if "'portfolio_results.tex'" not in s:s=s.replace("'adaptive_appendix.tex']","'adaptive_appendix.tex','portfolio_results.tex','portfolio_appendix.tex']",1)
    p.write_text(s)
    p=REPORT/'Makefile';s=p.read_text()
    if 'portfolio_results.tex' not in s:s=s.replace('adaptive_appendix.tex paper_references.bib','adaptive_appendix.tex portfolio_results.tex portfolio_appendix.tex paper_references.bib')
    p.write_text(s)
    document(d)
    print(json.dumps(dict(portfolio_report_complete=True,test_cases=d['test_cases'],ratios=d['ratios'])),flush=True)

def document(d):
    from s10_document import block
    folder=HERE/'selective_expansion'
    text='''This study adds selective numerator-rank expansion and compares the previous workflow on the same fresh targets.
The new selector predicts complete costs for five choices.
It uses 47 training batches, 26 validation batches, and a separate reserved group.
Rational profile 306 and symbolic dot index 3 belong only to the reserved test.
Training and validation do not read the earlier reserved results.

Run these scripts from the project root in the existing seed-model Python environment.
Use a scheduled two-core job with 8 GB total memory.
Keep at most two scientific jobs active, with at most 16 GB reserved in total.
Each native attempt has a 6,144 MiB address limit, a 5,200 MiB RSS limit, and 32 MiB of scratch space.
The whole adaptive study has a 64 MiB retained-output cap.

1. Run `s14_portfolio.py` for the two development checks.
2. Run `s15_portfolio_study.py` to measure training costs, fit models, select settings, and test fresh targets.
3. Run `s17_reduce.py --self-test` to check the public interface and unsupported-graph fallback.
4. Run `s16_portfolio_analyze.py` to audit the evidence and create plots.
5. Run `s18_portfolio_report.py` after the earlier report writers.
6. Build both PDFs and run the report checks. `s11_finalize.py` performs steps 3 through 6.

`s13_previous_server.py` runs the earlier workflow in a separate Python process.
This separates modules with repeated names. It keeps the original model weights.
It uses the same current Kira executable as the new policy and limits worker count to two.
The server stays loaded between requests. Every request still starts fresh Kira processes.
No target coefficients are reused.

`s14_portfolio.py` measures five strategies and includes native recovery.
`adaptive1` and `adaptive2` use the earlier validated cost policy with one or two workers.
`rank1` and `rank2` increase only the numerator-rank limit, with one or two workers.
`published` uses the previous graph, seed, and worker models.
For the new bubble-box graphs, the previous workflow uses its native fallback.
All choices use exact file indexing and zero-sector projection.

The five strategies have complete wall and process CPU time labels.
Training fits global trees and tree ensembles, plus local trees where enough cases exist.
Validation chooses a fixed strategy for each graph.
It enables the new prediction only with at least two percent saving and a saving in both repetitions.
A fixed portfolio strategy can contain an earlier model.
Thus the fixed comparison tests the added outer decision, not the removal of all ML.
The model files contain JSON arrays, not executable serialized objects.

`protocol.json` fixes case definitions, split groups, reference limits, and source versions before testing.
`trained_model/freeze.json` records the selected models and validation guard.
`summary.json` contains checked times and graph-specific results.
The original cost study remains unchanged and has its own reserved group.
Three repetitions give descriptive timing ranges. They do not prove a universal or globally optimal speedup.
'''
    (folder/'README.md').write_text('# Selective expansion and complete-cost portfolio\n\n'+text)
    purposes={'development':'Development comparisons that motivated selective numerator-rank expansion.',
        'training':'Measured complete costs for the training groups. One repetition per choice.',
        'validation':'Separate cost measurements for model, threshold, and fixed-control selection. Two repetitions per choice.',
        'references':'Fresh reserved references and independently enlarged-seed checks. Four-loop bounds follow the fixed protocol.',
        'trained_model':'Candidate trees, fitted cost arrays, selected predictors, feature ranges, and validation guards.',
        'model_test':'Five matched methods with three repetitions on each completed reserved batch.',
        'applications':'Applications with reference coefficients withheld until reduction finishes.',
        'application_test':'Public interface checks, input validation, deferred service loading, and an unsupported-graph fallback.',
        'application_loading':'Three rotated comparisons of immediate and deferred loading. Each request uses a new application instance, the same target batch, and an exact reference check. Common Python imports lie outside the timer.'}
    for name,purpose in purposes.items():
        p=folder/name
        if p.exists():(p/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+purpose+'\n\nRead the [study guide](../README.md) for producers, readers, inputs, and limits.\nJSON records use seconds for time. Compressed JSON files retain exact coefficients.\nKeep completed records unchanged.\n')
    block(folder/'README.md','Measured results',f'''All {d['timed_test_workflows']} timed test reductions and {d['applications']} further applications pass exact checks.
The summed batch median times are {d['totals']['native']:.6f} seconds for native choices, {d['totals']['published']:.6f} seconds for the previous workflow, and {d['totals']['selected']:.6f} seconds for the selected portfolio.
The selected/previous ratio is {d['ratios']['published']:.6f}.
The selected/fixed-portfolio ratio is {d['ratios']['fixed']:.6f}.
The all-repetition selected/fixed ratio is {d['all_trial_ratios']['fixed']:.6f}.
The added outer prediction has no stable aggregate saving over the fixed portfolio.
Read `summary.json` for individual graphs, process CPU times, and failed references.''','PORTFOLIO RESULTS')
    usage='''The current application is `ML_model_adaptive_reduction/s17_reduce.py`.
It selects a complete strategy from validation-supported models and fixed settings.
Read [selective_expansion/README.md](selective_expansion/README.md) for the final comparison with the previous workflow.
Use a scheduled two-core allocation with 8 GB total memory.
Pass one family-and-target JSON file and a JSON list of master index vectors.
The case format follows `selective_expansion/protocol.json`.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/s17_reduce.py --case case.json --basis basis.json --output ML_model_adaptive_reduction/selective_expansion/application_test/result.json.gz
```

For repeated calls, create `s17_reduce.Reducer()` once, call `reduce(case, basis)`, then call `close()`.
Keep the supplied basis explicit. Completion does not prove that this basis is minimal.
The interface accepts integer index vectors with at most 31 entries and no cut propagators.
All targets and masters must belong to the declared top sectors or their subsectors.
An empty master list is valid for a batch that reduces to zero.
Initial loading is reported separately. Every reduction recomputes its coefficients.
The previous-workflow service loads only when a selected strategy needs it.
Its first-use loading cost is part of that reduction's application time.
Later calls keep this service loaded until `close()`.
The optional `eager_previous=True` constructor is a timing control.
Read `selective_expansion/application_loading/` for six matched single-request checks.
The earlier immediate-loading source and checks remain in `selective_expansion/application_eager/`.
Unknown graph structures or feature ranges use native settings.
The current portfolio tests contain one to three targets per batch.
Earlier larger-batch and restricted-vacuum methods retain their separate guides and results.
Failures after all bounded attempts return an unsuccessful result.'''
    block(HERE/'README.md','Current portfolio application',usage,'CURRENT PORTFOLIO')
    guide=HERE/'README.md';guide.write_text(guide.read_text().replace('Each production job reserves one slot with 8 GB of memory.','Each first-study job reserves one slot with 8 GB of memory.'))
    block(HERE/'README.md','Document checks during training','''`s20_check_initial_report.py` audits and builds the completed first study while the portfolio run continues.
It changes no training data, fitted models, or reserved choices.
`initial_document.log` preserves the first notes build, which stopped at a missing notation command.
`initial_document_fixed.log` records the repaired build and the successful document checks.
`s11_finalize.py` adds the completed portfolio results, builds both final PDFs, and checks the full result.
`s21_check_application.py` can run the public checks as a separate two-core job after the model is frozen.
It checks exact results, an unsupported graph, invalid input types, cut-propagator rejection, and a scaleless zero integral.
It also checks deferred service loading and measures six complete application requests.
Read `job_plan.json` for the scheduled stage dependencies.''','DOCUMENT CHECKS')
    short='''The current application uses a [validated complete-cost portfolio](ML_model_adaptive_reduction/selective_expansion/README.md).
It compares selective seed expansion, earlier learned settings, and one or two workers.
The final test uses fresh inputs and compares the previous workflow and fixed choices per graph.
Exact preprocessing is common to these controls and has separate measured gains.
Read `ML_model_adaptive_reduction/selective_expansion/summary.json` for checked results.'''
    block(ROOT/'README.md','Current reduction method',short)
    for name in ['ML_model_seed_selection','ML_model_reduction','ML_model_equation_selection','ML_model_workflow_selection']:
        block(ROOT/name/'README.md','Current reduction method',short.replace('(ML_model_adaptive_reduction/','(../ML_model_adaptive_reduction/'))
    block(REPORT/'README.md','Final complete-cost portfolio','''`portfolio_results.tex` gives the current method and its matched results.
`portfolio_appendix.tex` derives the cost labels and prediction gate.
`portfolio_data.json` contains compact checked evidence without model weights.
`notes_native_families.tex` supplies the denominator definitions needed to read the notes independently.
The original cost-policy study remains in the paper appendix and in the notes.
Use `s11_finalize.py` to rebuild the evidence and both documents in order.''','PORTFOLIO REPORT')
    block(REPORT/'paper_figures/README.md','Portfolio figures','''`portfolio_controls.pdf` compares the final portfolio with the previous workflow and the graph-specific fixed portfolio.
Its line segments show the range of three repetition totals, not confidence intervals.
`portfolio_totals.pdf` compares complete wall and process CPU time.
The producer is `ML_model_adaptive_reduction/s16_portfolio_analyze.py`.
The input evidence is `report/portfolio_data.json`.''','PORTFOLIO FIGURES')
    if (HERE/'integration_completion.json').exists():
        block(HERE/'README.md','Bounded preprocessing control','''The four-loop control without the two new exact changes exhausted both bounded attempts.
The original record and log remain unchanged.
`s19_finish_controls.py` completes the other pre-specified settings.
It omits further repetitions of a control after its bounded failure.
`integration_continuation.json` records this continuation and its trigger.
`integration_completion.json` lists failed controls and omitted repetitions.
Failed controls receive no completion-time median or speedup factor.
The three-loop matched comparison and the four-loop indexing-to-projection comparison retain their completed repetitions.''','BOUNDED CONTROL')

if __name__=='__main__':main()
