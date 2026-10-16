"""Write the measured component effects and scattering limits into both documents."""
import collections,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/'report'
NAMES={'sunrise':'Sunrise','double_box':'Planar double box','vacuum3':'Vacuum',
       'ladder3':'Two-point ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Box with external virtuality'}
METHODS={'native':'Native choices','graph_fixed':'Fixed graph strategy','graph_model':'Selected graph strategy',
 'seed_fixed':'Fixed seed expansion','seed_model':'Selected seed expansion','worker_fixed':'Fixed worker count',
 'worker_model':'Full selected method','equation_filter':'Equation filter','seed_filter':'Seed filter','row_model':'Row model'}
def change(r):return f'{abs(100*(1-r)):.1f}\\% '+('less' if r<1 else 'more')+' time'
def pct(r):return ('-' if r<1 else '+')+f'{abs(100*(r-1)):.1f}\\%'
def replace_once(s,old,new):
    assert s.count(old)==1,old[:100]
    return s.replace(old,new)

def main():
    d=json.loads((HERE/'summary.json').read_text());assert d['complete'] and d['parity_all_exact']
    a=d['ablation'];causal=d['choice_controls'];assert a['trials']==420 and a['successful']==420 and causal['trials']==96
    total=sum(c['median_seconds']['native'] for c in a['cases']);final=sum(c['median_seconds']['worker_model'] for c in a['cases'])
    table=[]
    for m,label in METHODS.items():
        t=sum(c['median_seconds'][m] for c in a['cases'])
        table.append(f'{label} & {t:.2f} & {pct(t/total)}'+r'\\')
    ct=[]
    for stage,label in [('graph','Graph strategy'),('seed','Seed expansion'),('worker','Worker count')]:
        v=causal['summary'][stage];ratio=v['selected_sum']/v['control_sum']
        ct.append(f'{label} & {v["cases"]} & {v["control_sum"]:.2f} & {v["selected_sum"]:.2f} & {pct(ratio)}'+r'\\')
    family=[]
    for k,v in sorted(a['by_family'].items(),key=lambda p:(p[1]['loops'],p[0])):
        b=v['seconds']['native'];s=v['seconds']['worker_model']
        family.append(f'{NAMES[k]} & {v["loops"]} & {b:.2f} & {s:.2f} & {pct(s/b)}'+r'\\')
    complete_high=[c for c in d['higher_cases'] if all('median_seconds' in c['methods'].get(m,{}) for m in ['original','sector_native','sector_equation','separate_requests'])]
    high_orig=sum(c['methods']['original']['median_seconds'] for c in complete_high)
    high_native=sum(c['methods']['sector_native']['median_seconds'] for c in complete_high)
    high_eq=sum(c['methods']['sector_equation']['median_seconds'] for c in complete_high)
    high_sep=sum(c['methods']['separate_requests']['median_seconds'] for c in complete_high)
    example=complete_high[0]['methods']['sector_equation'];metrics=example['equation_counts']
    equation_detail=f'For the first profile, the equation tree retains {metrics["unique_retained"]:,} of {metrics["unique_candidates"]:,} candidate seed--operator pairs. Its median filtering cost is {example["median_filter_seconds"]:.3f} seconds. This saving acts before symbolic coefficient construction, which explains why it can help even when the graph-specific strategy selectors retain native settings.'
    extended_rows=[];verified_four=[]
    for c in d['extended_cases']:
        label=('Box with bubbles' if c['kind'].startswith('bubble') else 'Four-point ladder')
        ms=c['methods'];ok=c['reference_status']=='completed' and c['check_status']=='completed'
        if ok:
            vals=[f'{ms[m]["median_seconds"]:.2f}' if 'median_seconds' in ms.get(m,{}) else '---' for m in ['native','equation','separate_requests']]
            extended_rows.append(f'{label} & {c["loops"]} & '+' & '.join(vals)+r'\\')
        else:
            reason='Reference did not finish' if c['reference_status']!='completed' else 'Enlarged check did not finish'
            extended_rows.append(f'{label} & {c["loops"]} & '+r'\multicolumn{3}{l}{'+reason+'}'+r'\\')
    memory_rows=[];checked_four=[]
    for c in d['memory_cases']:
        label='Box with bubbles' if c['kind'].startswith('bubble') else 'Four-point ladder'
        ms=c['methods'];ok=c['reference_status']=='completed' and c['check_status']=='completed'
        if ok:
            if c['loops']==4:checked_four.append(c)
            vals=[f'{ms[m]["median_seconds"]:.2f}' if 'median_seconds' in ms.get(m,{}) else '---' for m in ['native','equation']]
            ratio=ms['equation']['median_seconds']/ms['native']['median_seconds'] if all('median_seconds' in ms.get(m,{}) for m in ['native','equation']) else None
            memory_rows.append(f'{label} & {c["loops"]} & '+' & '.join(vals)+' & '+(pct(ratio) if ratio else '---')+r'\\')
            if c['loops']==4 and 'median_seconds' in ms.get('native',{}):verified_four.append(c)
        else:
            status=c['check_status'] if c['reference_status']=='completed' else c['reference_status']
            reason={'memory_limit':'Memory limit','allocation_limit':'Allocation limit','time_limit':'Time limit','scratch_limit':'Storage limit'}.get(status,status.replace('_',' '))
            memory_rows.append(f'{label} & {c["loops"]} & '+r'\multicolumn{3}{l}{'+reason+'}'+r'\\')
    choice_prose=[]
    for stage,label in [('graph','Graph-strategy prediction'),('seed','Seed-expansion prediction'),('worker','Worker-count prediction')]:
        v=causal['summary'][stage]
        choice_prose.append(f'{label} gives {change(v["selected_sum"]/v["control_sum"])} than its matching fixed control.')
    choice_prose=' '.join(choice_prose)+' These small comparisons describe the measured workloads; three repetitions do not by themselves establish a stable advantage on other targets.'
    if verified_four:
        c=verified_four[0];b=c['methods']['native']['median_seconds'];e=c['methods'].get('equation',{}).get('median_seconds')
        name='box with bubble subgraphs' if c['kind'].startswith('bubble') else 'four-point ladder'
        if e is not None:
            extension=f'With the larger memory allowance, the four-loop {name} completes and passes its enlarged-basis check. Its equation-filtered calculation takes {e:.2f} seconds compared with {b:.2f} seconds for native equation choices, giving {change(e/b)} on this profile. This establishes a result for that connected scattering family. The vacuum recurrence remains outside its domain, and arbitrary four-loop graphs require their own comparisons.'
            short_extension=f'A connected four-loop {name} also passes the enlarged-basis check; its equation-filtered time is {e:.2f} seconds against {b:.2f} seconds for matched native choices.'
            retries=c['methods']['equation']['fallbacks']
            if retries:
                extension+=f' The three filtered trials require {retries} native retries in total. Their reported times include those retries, so successful final output does not imply that the model supplied sufficient equations on its first attempt.'
                short_extension+=f' This filtered route includes {retries} native retries across its three repetitions.'
                missing=c['methods']['equation'].get('insufficient_basis_attempts',0)
                if missing:
                    extension+=f' In {missing} filtered attempts, Kira reports an additional unreduced integral outside the prescribed basis. The retained equations therefore do not supply the required reduction, even though the filter avoids coefficient construction.'
        else:
            extension=f'The longer comparison completes the four-loop {name} and its enlarged-basis check. Native equation choices take {b:.2f} seconds. The filtered method does not complete every repetition, so this case establishes a native reduction without a measured equation-model speedup.'
            short_extension=f'A connected four-loop {name} passes the enlarged-basis check, but the filtered method does not establish a complete-time speedup.'
        extension+=f' The offline reference takes {c["reference_seconds"]:.2f} seconds, and its successful enlarged check takes {c["check_seconds"]:.2f} seconds. These are setup and verification costs under their respective limits, separate from the repeated application times. The application comparison supplies both methods with the same checked master basis.'
    elif checked_four:
        c=checked_four[0]
        extension='A connected four-loop scattering reference passes its enlarged-basis coefficient check. The repeated timing comparison does not complete all native trials, so it supplies no matched speedup estimate. The completed reference and the unsuccessful repeated attempts are distinct outcomes.'
        short_extension='A connected four-loop scattering reference passes its enlarged-basis check, but the repeated native timing comparison does not supply a matched speedup.'
    else:
        extension='The time and memory follow-ups still do not establish a completed four-loop reduction in the prescribed, independently checked basis. We therefore report their stopping conditions and give no four-loop speedup. The successful new scattering result remains the three-loop box with bubble subgraphs.'
        short_extension='The new three-loop scattering comparison completes, while the bounded four-loop attempts do not establish a checked complete-time speedup.'
    section=r'''\section{Separating the gains and testing higher-loop scattering}
\label{sec:components}
\subsection{What each choice contributes on the same targets}
The preceding studies use different workloads, so their savings cannot identify the contribution of each part of one calculation. We now compare the frozen methods on a common set of fourteen batches from the seven earlier graphs. Each batch contains three targets with an additional denominator power of two, and each graph has two new rational parameter profiles. Dimension remains symbolic. The caller and models are loaded before timing; each measured request includes prediction, a fresh Kira calculation, checks, and any retry. Appendix~\ref{app:higher-scattering} specifies the inputs, controls, and timing rules.

All 420 timed reductions pass exact coefficient checks, after an enlarged reference calculation has confirmed the basis. Table~\ref{tab:components} sums the median times from three repetitions of each batch. The full selected method takes @FINAL@ seconds, compared with @NATIVE@ seconds for native choices, giving @TOTALCHANGE@ for this collection. Both methods share the same executable improvements. Their measured difference comes from the fixed settings, learned choices, and associated overhead enabled by the strategy; the whole saving cannot be assigned to prediction.

\begin{table}[!htbp]
\centering\small
\caption{Complete time on fourteen matched batches. Each entry sums one three-run median per batch. The final column compares this sum with native choices; a negative value means less time.}
\label{tab:components}
\begin{tabular}{@{}lrr@{}}\toprule
Method & Time (s) & Change from native\\\midrule
@COMPONENTTABLE@
\bottomrule\end{tabular}
\end{table}

The seed and equation filters increase complete time on this particular workload, even though earlier tests found savings on other targets. The seed-filter option uses the three fitted scattering seed trees where available and native choices on the other four graph types. The row model also adds cost. Fixed seed expansion accounts for a substantial part of the reduction in total time, which makes a matched control necessary before crediting the learned selector. Table~\ref{tab:component-families} shows how the combined result varies across the integral families. The three-loop ladder in this table is a two-point family; the four-point ladder introduced below is a different graph.

\begin{table}[!htbp]
\centering\small
\caption{The combined strategy on the same fourteen batches. Each family contributes two batches. These are new measurements, separate from the broader target-pattern test in Table~\ref{tab:thread-policy}.}
\label{tab:component-families}
\begin{tabular}{@{}lrrrr@{}}\toprule
Family & Loops & Native (s) & Selected (s) & Change\\\midrule
@FAMILYTABLE@
\bottomrule\end{tabular}
\end{table}

The fixed strategies in Table~\ref{tab:components} were selected during the earlier training studies. A deployed policy can instead retain a different control selected during validation. To isolate the prediction itself, we make a second comparison that changes only the current learned choice to that validation control. Earlier stages, the solver, targets, and basis stay the same. This test includes only the graphs for which that model is enabled and gives 96 further reductions, all with exact agreement. Table~\ref{tab:isolated-choices} reports the measured effect of each decision. Its workloads differ by stage because the graph and seed models are enabled for three graphs, while the worker model is enabled for two.

\begin{table}[!htbp]
\centering\small
\caption{Disabling only one learned choice. Times sum batch medians. The last column compares the selected method with its matched validation control. These differences include prediction overhead and all subsequent algebra.}
\label{tab:isolated-choices}
\begin{tabular}{@{}lrrrr@{}}\toprule
Decision & Batches & Control (s) & Selected (s) & Change\\\midrule
@CHOICETABLE@
\bottomrule\end{tabular}
\end{table}

\begin{figure}[!htbp]
\centering\includegraphics[width=\linewidth]{paper_figures/component_ablation.pdf}
\caption{Separating the total strategy from the added learned decision. The upper panel compares complete methods on all fourteen batches. The lower panel changes only one enabled learned choice on its matching graph subset. Both panels use ratios of summed batch medians and retain the equal-time line. Their horizontal ranges differ so that the smaller decision effects remain visible.}
\label{fig:component-ablation}
\end{figure}
\FloatBarrier

@CHOICEPROSE@

These comparisons explain why the benefit depends on the targets. A learned choice has less opportunity to help when a single fixed setting already suits every batch in the comparison. Its usefulness must therefore be assessed against that setting on the intended target patterns. The tests retain the published weights and do not use these new timings to alter the deployment policy.

\subsection{Connected scattering graphs beyond the original training structures}
We next examine massless four-point ladders and boxes with bubble subgraphs, keeping two independent external invariants. The initial probes use four, five, and six loops, including one four-loop input with symbolic invariants. The completed timing comparisons use rational values of the invariants and symbolic dimension. These graphs differ from the restricted vacuum family used for the twelve-loop recurrence result. Their full denominators and the completion of the auxiliary scalar-product basis appear in Appendix~\ref{app:higher-scattering}.

The initial failures occur before a learned elimination choice can help. Four-loop calculations reach the solver time limit during sector initialization. At five loops the executable fails an allocation under the imposed memory limit. Six-loop four-point families require 39 independent inverse propagators, exceeding the tested executable's 31-entry limit. These are measured or directly checked limits of this configuration, and they provide no completed-time speedup estimate.

The four-loop traces also show that initialization examines sectors containing positive auxiliary indices outside the declared reduction domain. We therefore add an optional initialization that classifies only the declared top sectors and their subsectors. Appendix~\ref{app:higher-scattering} derives the closure of this domain under IBP. The change retains exact zero-sector tests within the domain and passes coefficient comparisons on the seven earlier graphs. It is a deterministic restriction of the calculation, with the learned models kept unchanged.

The new three-loop box with bubble subgraphs completes at both reserved parameter profiles. Summing its batch median times, the original initialization takes @HIGHORIG@ seconds, while restricted initialization with native equation choices takes @HIGHNATIVE@ seconds, giving @HIGHINITCHANGE@. Adding the frozen equation filter reduces this to @HIGHEQ@ seconds, giving @HIGHEQCHANGE@ relative to the same restricted calculation. Two separate requests take @HIGHSEP@ seconds; combining their targets gives the single native calculation of @HIGHNATIVE@ seconds, giving @HIGHSHARECHANGE@. These comparisons distinguish the benefit of initialization, equation prediction, and shared work on identical targets. Every completed result agrees with the enlarged reference reduction.

The complete strategy selectors recognize these graph structures as outside their trained domain and retain native decisions. The transferred equation tree is tested separately, with native fallback if its equations are insufficient. The row-model trials retain their costs and exact checks. Thus a successful equation-filter result does not imply that every model transfers to these graphs.

@EQUATIONDETAIL@

To determine whether the four-loop failures only reflect the short time allowance, we repeat the feasibility and matched tests at a fresh profile with a 600-second allowance per native attempt. The memory and temporary-storage limits remain unchanged. The original unsuccessful probes remain part of the evidence. Table~\ref{tab:extended-scattering} gives completed median times only when the enlarged-basis check also succeeds.

\begin{table}[!htbp]
\centering\small
\caption{The longer scattering comparison at one fresh profile per family. Completed entries are medians of three repetitions. Native and filtered methods both use restricted initialization. Separate requests use native equation choices and return the same targets as the combined native method.}
\label{tab:extended-scattering}
\begin{tabular}{@{}lrrrr@{}}\toprule
Family & Loops & Native (s) & Equation ML (s) & Separate (s)\\\midrule
@EXTENDEDTABLE@
\bottomrule\end{tabular}
\end{table}

The longer native runs produce reference coefficients for the four-loop bubble box and the three-loop four-point ladder, but their enlarged checks reach the memory limit. We therefore reserve more memory and repeat the checks, keeping the earlier attempts in the evidence. The new resident-memory limit is 5,200 MiB, within the scheduler allocation, and the solver address-space limit is 6,144 MiB. Both timed methods use these same limits, with the 600-second time allowance and unchanged temporary-storage bound. Table~\ref{tab:memory-scattering} reports this follow-up.

\begin{table}[!htbp]
\centering\small
\caption{Scattering checks with a larger reserved memory allowance. Times are medians of three complete reductions after the enlarged check passes. Equation filtering includes prediction, verification, and any native retry. A stopping condition supplies no speedup estimate.}
\label{tab:memory-scattering}
\begin{tabular}{@{}lrrrr@{}}\toprule
Family & Loops & Native (s) & Equation ML (s) & Change\\\midrule
@MEMORYTABLE@
\bottomrule\end{tabular}
\end{table}

@EXTENSION@

The vacuum recurrence is excluded from all of these scattering calculations because its derivation does not supply the dependence on the external invariant ratio. Shared requests remain useful whenever the family, kinematics, and required basis agree. These are distinct forms of reuse, and their timing benefits must be stated separately. The finite tests identify working cases and concrete stopping conditions; they do not establish a general result for all higher-loop scattering integrals.
'''
    tokens={'@FINAL@':f'{final:.2f}','@NATIVE@':f'{total:.2f}','@TOTALCHANGE@':change(final/total),
      '@COMPONENTTABLE@':'\n'.join(table),'@FAMILYTABLE@':'\n'.join(family),'@CHOICETABLE@':'\n'.join(ct),
      '@HIGHORIG@':f'{high_orig:.2f}','@HIGHNATIVE@':f'{high_native:.2f}','@HIGHEQ@':f'{high_eq:.2f}',
      '@HIGHSEP@':f'{high_sep:.2f}','@HIGHEQCHANGE@':change(high_eq/high_native),
      '@HIGHINITCHANGE@':change(high_native/high_orig),'@HIGHSHARECHANGE@':change(high_native/high_sep),
      '@EXTENDEDTABLE@':'\n'.join(extended_rows),'@EXTENSION@':extension,'@MEMORYTABLE@':'\n'.join(memory_rows),'@CHOICEPROSE@':choice_prose,'@EQUATIONDETAIL@':equation_detail}
    for old,new in tokens.items():section=section.replace(old,new)
    assert not re.search('@[A-Z]+@',section)
    (REPORT/'higher_scattering_results.tex').write_text(section)
    (REPORT/'higher_scattering_appendix.tex').write_text((HERE/'higher_scattering_appendix.tex').read_text())
    p=REPORT/'report.tex';s=p.read_text()
    if '\\input{higher_scattering_results}' not in s:
        s=replace_once(s,'\\input{thread_policy_results}','\\input{thread_policy_results}\n\\input{higher_scattering_results}')
        s=replace_once(s,'\\input{thread_policy_appendix}','\\input{thread_policy_appendix}\n\\input{higher_scattering_appendix}')
    s=s.replace('\\date{October 14, 2026}','\\date{October 15, 2026}')
    old_title='Learned selection for exact Feynman integral reduction with Kira'
    s=s.replace(old_title,'Learned selection and exact reuse for Feynman integral reduction with Kira')
    abstract=f'''Reducing Feynman integrals to master integrals requires exact algebra whose cost depends on the chosen equations and reduction strategy. We study learned seed, row, and equation selection in Kira and compare their complete calculation times with fixed controls. Earlier tests establish savings in selected domains, while row prediction gives no reliable gain and is omitted from the retained method. A new comparison on fourteen batches from seven known graph structures uses 420 exact reductions and reduces the sum of batch median times from {total:.2f} to {final:.2f} seconds. This combined saving includes fixed settings and learned decisions. Another 96 exact comparisons disable one learned choice at a time to identify its added effect. Connected scattering tests examine initialization, model transfer, and shared requests beyond the original graph structures. {short_extension} A separate fixed recurrence method gives a 543.8-fold speedup in a restricted vacuum family through twelve loops. The results distinguish gains from prediction, deterministic reduction choices, and mathematical reuse, and state the physical and resource limits of each comparison.'''
    s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,count=1,flags=re.S)
    s=s.replace('The final sections bring the results together and state their physical scope.','We then separate the contributions on common targets and test connected scattering families beyond the original graph structures. The final sections bring the results together and state their physical scope.')
    s=s.replace('The study also examines how these decisions interact with Kira.', 'The study also examines how these decisions interact with Kira. We distinguish a model\'s added effect from the gain of the complete strategy by comparing each learned decision with its matching fixed control.')
    s=s.replace('The large saving in this study includes mathematical reuse and implementation changes, so it is not an isolated measure of machine learning performance.',
      'The deployed calculation uses a fixed recurrence rule. A trained selector for five recurrence strategies takes 1.7\\% more time than the selected fixed rule, with descriptive ratio interval $[0.969,1.070]$, so it supplies no established additional saving. The 543.8-fold result therefore measures mathematical reuse and implementation changes without a learned decision at application time.')
    s=s.replace('general high-loop scattering requires a separate comparison.', 'Section~\\ref{sec:components} provides the separate scattering comparison and states which reductions complete.')
    # Keep the overview aligned with the current measurements, while preserving
    # the earlier studies as separate experiments with their own baselines.
    start=s.index('\\subsection{What the model comparisons establish}')
    end=s.index('\\begin{table}',start)
    overview=f'''\\subsection{{What the model comparisons establish}}
The measurements identify useful methods within stated domains. On the new common workload, the complete strategy takes {final:.2f} seconds compared with {total:.2f} seconds for native choices, giving {100*(1-final/total):.1f}\\% less time. The executable improvements are shared by both methods, and the saving includes fixed settings as well as learned decisions. The additional controls change only one learned choice: graph-strategy prediction saves {100*(1-causal['summary']['graph']['selected_sum']/causal['summary']['graph']['control_sum']):.1f}\\%, while seed-expansion prediction and worker prediction use {100*(causal['summary']['seed']['selected_sum']/causal['summary']['seed']['control_sum']-1):.1f}\\% and {100*(causal['summary']['worker']['selected_sum']/causal['summary']['worker']['control_sum']-1):.1f}\\% more time, respectively. These effects concern the enabled subsets and target patterns in Table~\\ref{{tab:isolated-choices}}.

The earlier comparisons cover different targets. The original seed network saves time for single-target requests from existing equation pools, and the equation tree saves time in its four trained native graph structures. Learned row selection gives no reliable saving and remains omitted. The earlier graph-specific, seed-expansion, and worker studies also report gains relative to their matched controls, as summarized in Table~\\ref{{tab:overall}}. The new controls show why those results must retain their workload definitions: a learned choice can add little, or add cost, when a fixed setting already suits the targets.

The new three-loop scattering calculation provides a separate use for the equation tree. It reduces complete time by {100*(1-high_eq/high_native):.1f}\\% after the same initialization restriction is applied to both methods. Shared requests reduce the repeated native work by {100*(1-high_native/high_sep):.1f}\\% on these targets. {short_extension} The basis checks and incomplete attempts remain part of the result.

These percentages use different controls and cannot be multiplied. Table~\\ref{{tab:method-use}} states where each method has supporting evidence and what limits its use. The original shared-request comparison gives a separate 48.3\\% saving, while its cost model gives no reliable improvement over the shared native calculation. The much larger vacuum result comes from a direct recurrence whose domain is specified below.

\\begin{{table}}[!htbp]
\\centering\\small
\\caption{{Where the methods are useful. Each application requires the physical assumptions and exact checks stated in the corresponding experiment.}}
\\label{{tab:method-use}}
\\begin{{tabularx}}{{\\linewidth}}{{@{{}}lYY@{{}}}}\\toprule
Method & Supported use & Limitation\\\\\\midrule
Seed prediction & Select a small sufficient subset for single targets in an existing pool & Native generation and larger batches can cost more.\\\\
Equation prediction & Skip coefficient construction when the retained equations still reduce the targets & Transfer varies by graph; insufficient choices need a native retry.\\\\
Row prediction & No retained application based on current timings & Prediction and retries remove the measured benefit.\\\\
Complete-strategy selection & Choose among validated settings for known graphs and target patterns & Unknown graphs use native choices; fixed controls account for much of the gain.\\\\
Shared requests & Reduce compatible targets from one family, kinematics, and basis together & The comparison must count all requested outputs and repeated work.\\\\
Restricted initialization & Classify only the declared sector domain for the tested uncut families & Optional symmetry and relation modes require separate checks.\\\\
Vacuum recurrence & Reuse exact coefficients across powers and loop orders in the derived vacuum family & The formula supplies no general scattering dependence.\\\\\\bottomrule
\\end{{tabularx}}
\\end{{table}}

'''
    s=s[:start]+overview+s[end:]
    begin=s.index('\\section{Conclusion}')
    end=s.index('\\appendix',begin)
    conclusion=f'''\\section{{Conclusion}}
We have compared learned choices, fixed reduction strategies, and exact reuse through the complete time required to reduce Feynman integrals with Kira. The three local models address different work: seeds determine which groups of identities are available, equation selection can avoid constructing unnecessary relations, and row selection changes the elimination sequence. Their benefit depends on the target integrals and on the cost of making the decision. The row model gives no reliable general saving in the measured comparisons and remains outside the retained method.

The combined strategy saves {100*(1-final/total):.1f}\\% of the summed batch median time on the new fourteen-batch comparison, with all 420 reductions agreeing exactly. The 96 additional controls show the added effect of each enabled learned decision while leaving the other stages unchanged. This separation is necessary because a faster fixed seed region or worker count can account for much of the total saving. The earlier broader-pattern worker study remains a separate result: its corresponding total changes from 110.67 to 78.73 seconds, and its additional worker choice uses 18.9\\% more CPU time than the preceding one-worker method.

The new scattering study identifies initialization as a cost that the existing local models do not remove. Restricting initialization to the declared sector domain passes the matched coefficient checks and permits new three-loop scattering comparisons. {short_extension} Five-loop allocation failures and the six-loop family-size limit remain explicit limits of the tested configuration. These outcomes distinguish a completed exact reduction from an unfinished calculation and avoid assigning speedups to failed attempts.

Exact reuse has two separate roles. Compatible requests can share one reduction, while the restricted vacuum family admits a direct recurrence that avoids repeated Kira calls and gives the earlier 543.8-fold result. That deployed recurrence uses a fixed rule, and its derivation does not cover general scattering. The evidence supports selecting methods within the domains where complete-time tests justify them. It establishes neither a speedup for every integral family nor globally optimal reduction paths.

'''
    s=s[:begin]+conclusion+s[end:]
    (REPORT/'report.tex').write_text(s)
    # The current notes additions remain removable by the original preservation audit.
    p=REPORT/'notes.tex';s=p.read_text()
    if '\\input{higher_scattering_results}' not in s:
        s=replace_once(s,'\\input{thread_policy_results}','\\input{thread_policy_results}\n\\input{higher_scattering_results}')
        s=replace_once(s,'\\input{thread_policy_appendix}','\\input{thread_policy_appendix}\n\\input{higher_scattering_appendix}')
        anchor='% END CURRENT WORKFLOW UPDATE\n\\clearpage\n\\renewcommand{\\refname}{Citations}'
        text=f'\nThe component comparison in Section~\\ref{{sec:components}} adds 420 exact reductions and 96 controls that disable one learned choice at a time. Its combined total changes from {total:.2f} to {final:.2f} seconds on fourteen batches. {short_extension} The new section records the limits for larger scattering families and separates prediction from fixed settings and reuse.\n'
        s=replace_once(s,anchor,text+'\n'+anchor)
    p.write_text(s)
    # Show the native comparison behind the previously quoted 28.9 percent saving.
    p=REPORT/'thread_policy_results.tex';s=p.read_text();old=json.loads((REPORT/'thread_policy_figure_data.json').read_text())
    groups=collections.defaultdict(list)
    for c in old['cases']:groups[c['topology']].append(c)
    rows=[]
    for k in ['sunrise','double_box','vacuum3','ladder3','nonplanar_box','pentagon','one_mass_box']:
        cs=groups[k];b=sum(c['median_seconds']['native'] for c in cs);v=sum(c['median_seconds']['previous'] for c in cs);n=sum(c['median_seconds']['selected'] for c in cs)
        label={'one_mass_box':'Virtuality box','double_box':'Planar box','ladder3':'Two-point ladder'}.get(k,NAMES[k])
        rows.append(f'{label} & {cs[0]["loops"]} & {b:.3f} & {v:.3f} & {n:.3f} & {n/b:.3f}'+r'\\')
    table=r'''\begin{tabular}{@{}lrrrrr@{}}\toprule
Graph & Loops & Native (s) & Previous (s) & Selected (s) & Selected/native\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}'''
    s=re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}',lambda m:table,s,count=1,flags=re.S)
    s=s.replace('The final column divides selected time by previous time.','The native column uses Kira\'s own decisions in the same executable. The final column divides selected time by native time.')
    marker='Selection therefore gives 4.5\\% less time than the fixed-per-graph control.'
    if '28.9\\%' not in s:s=s.replace(marker,marker+' Relative to native choices, the sum falls by 28.9\\%; this includes the preceding fixed and learned strategies.')
    p.write_text(s)
    checker=REPORT/'s01_check_paper.py';s=checker.read_text()
    if "'higher_scattering_results.tex'" not in s:
        s=s.replace("'thread_policy_appendix.tex']","'thread_policy_appendix.tex','higher_scattering_results.tex','higher_scattering_appendix.tex']",1)
    checker.write_text(s)
    p=REPORT/'Makefile';s=p.read_text()
    s=s.replace('thread_policy_appendix.tex paper_references.bib','thread_policy_appendix.tex higher_scattering_results.tex higher_scattering_appendix.tex paper_references.bib')
    p.write_text(s)
    print(json.dumps(dict(report_updated=True,combined_native_seconds=total,combined_selected_seconds=final,verified_four_loop_cases=len(verified_four))))
if __name__=='__main__':main()
