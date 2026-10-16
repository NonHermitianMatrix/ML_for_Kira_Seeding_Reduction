"""Write measured results into both documents without changing archived notes."""
import json,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPORT=ROOT/'report'
NAMES={'one_mass_box':'Virtuality box','nonplanar_box':'Nonplanar box','double_box':'Planar double box','sunrise':'Sunrise','pentagon':'Pentagon','vacuum3':'Three-loop vacuum','ladder3':'Three-loop two-point ladder','bubble_box3':'Three-loop bubble box','bubble_box4':'Four-loop bubble box'}
def change(r):return f'{100*abs(1-r):.1f}\\% '+('less time' if r<1 else 'more time')
def update(p,title,body):
    begin='% BEGIN '+title;end='% END '+title;s=p.read_text() if p.exists() else ''
    block=begin+'\n'+body.strip()+'\n'+end+'\n'
    if begin in s:s=re.sub(re.escape(begin)+'.*?'+re.escape(end)+'\n?',lambda _:block,s,flags=re.S)
    else:s=s.rstrip()+'\n\n'+block
    p.write_text(s)
def main():
    d=json.loads((HERE/'summary.json').read_text());assert d['complete'] and d['all_exact']
    old=json.loads((REPORT/'higher_scattering_data.json').read_text());assert old['complete']
    totals=d['totals'];native=totals['native'];fixed=totals['fixed'];learned=totals['learned']
    gc=d['graph_controls'];gt=gc['totals']
    rows=[]
    for k,v in d['by_graph'].items():
        t=v['seconds'];rows.append(f'{NAMES.get(k,k)} & {v["loops"]} & {v["cases"]} & {t["native"]:.3f} & {t["fixed"]:.3f} & {t["learned"]:.3f}'+r'\\')
    integration=[]
    for c in d['integration']:
        t={k:v['median_seconds'] for k,v in c['methods'].items()}
        values=[f'{t[m]:.3f}' if t[m] is not None else 'Incomplete' for m in ['previous','files','projected','learned']]
        factor=f'{t["previous"]/t["learned"]:.2f}' if t['previous'] is not None and t['learned'] is not None else '--'
        integration.append(str(c['loops'])+' & '+' & '.join(values)+' & '+factor+r'\\')
    model={'tree':'a regression tree','forest':'a random forest','extra':'an ensemble of extremely randomized trees'}[d['model'].split('_')[0]]
    section=r'''\section{Learning one policy for complete reduction time}
\label{sec:adaptive}
The component controls show that adding another learned decision can increase time when a fixed setting already suits the targets. We therefore replace the sequence of strategy selectors with one policy that compares complete calculations before equation generation. Its purpose is to choose a small sufficient calculation when possible and to avoid an expensive failed attempt when more seeds are needed. Kira continues to generate and solve the exact identities.

\subsection{Model, training data, and comparison}
The policy uses the target indices and the family's loop, momentum, mass, and denominator structure. It compares seven choices: the target-based native seed limits, three smaller seed regions, integral ordering 5, the existing equation filter, and direct expansion of the seed limits. Each training label is the measured time of a complete reduction, including retries and exact coefficient checks. The new model therefore learns the cost of an insufficient equation set as well as the cost of a successful first attempt. Appendix~\ref{app:adaptive} gives the inputs, cost function, prediction rule, and recovery steps.

We fit regression trees, random forests, and ensembles of extremely randomized trees~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}. The comparison uses nine candidate models, with validation selecting both the model and a minimum predicted saving required to depart from its fixed control. The selected model is @MODEL@ with maximum depth @DEPTH@ and @TREECOUNT@. Training supplies @TRAIN@ complete cases, validation supplies @VALID@ cases, and the reserved test contains @TEST@ completed batches. Constructing and validating the cost data takes @OFFLINE@ seconds of recorded reduction time, while fitting the nine models takes @FIT@ seconds. These are offline costs; a saved policy can serve later requests without repeating them. The tests cover the earlier seven graph structures and connected bubble-box scattering families at three and four loops. Rational kinematics change between splits, while dimension remains symbolic. The symbolic scattering tests use disjoint target indices within each graph. These are tests within known structures, with complete definitions in the appendices.

Before fitting the models, we also remove two deterministic costs from Kira's preparation. The first reads the existing sector files directly in their original order. The second simplifies the test for zero sectors, whose integrals vanish in dimensional regularization. That test uses parametric polynomials formed from the propagator denominators~\cite{Lee2014LiteRed,Kira3}. We set the parameters of propagators absent from every declared top sector to zero before constructing the test. Equation~\eqref{eq:adaptive-projection} proves that this change preserves the test within the declared domain. The complete polynomials remain available for other operations. Nine coefficient comparisons against earlier independent references pass before the new training begins. Both exact changes are present in every method in Table~\ref{tab:adaptive-results}, so that table measures the policy after the common implementation improvement.

\subsection{Results on the reserved targets}
Table~\ref{tab:adaptive-results} gives sums of three-run batch median times. Native choices take @NATIVE@ seconds, the validation-selected fixed choice takes @FIXED@ seconds, and the learned policy takes @LEARNED@ seconds. The selected fixed choice is @FIXEDNAME@. The learned result uses @NATIVECHANGE@ than native choices and @FIXEDCHANGE@ than the fixed control. Summing all repetitions gives learned/native and learned/fixed ratios of @TRIALNATIVE@ and @TRIALFIXED@, respectively. These additional ratios show the effect of keeping every measured time. The same targets and prescribed master basis are used in each comparison, and every attempt uses one Kira worker within the same one-core, 8\,GiB allocation. Figure~\ref{fig:adaptive} shows how the added effect varies across graph structures.

\begin{table}[!htbp]\centering\small
\caption{Complete times on reserved targets, in seconds. Each graph row sums its batch medians. All three methods use the same improved executable; the fixed choice is selected on validation data.}
\label{tab:adaptive-results}
\begin{tabular}{@{}lrrrrr@{}}\toprule
Graph & Loops & Batches & Native & Fixed & Learned\\\midrule
@ROWS@
\midrule Total & & @TEST@ & @NATIVE@ & @FIXED@ & @LEARNED@\\\bottomrule
\end{tabular}\end{table}

All @WORKFLOWS@ timed reductions and @APPLICATIONS@ further applications agree exactly with their reference coefficients. The additional applications receive the master basis but no target coefficients before execution. A separate check of the public application interface completes @PUBLIC@ batches. Native choices require @NATIVEFALLBACK@ recovery attempts across the timed tests, compared with @LEARNEDFALLBACK@ for the learned policy. The median decision time across the test batches is @INFERENCE@ milliseconds, including feature construction and tree evaluation. The prediction cost, all failed attempts, and recovery are included in complete time. Model loading, offline reference construction, and basis discovery are outside this repeated-reduction comparison. @UNFINISHED@

\begin{figure}[tbp]\centering
\includegraphics[width=\linewidth]{paper_figures/adaptive_reduction.pdf}
\caption{The upper panel compares the learned policy with native choices after the common exact improvements. The lower panel compares it with the best fixed validation choice. Each point divides sums of batch medians within one graph structure. Values below one indicate less time; the equal-time line remains visible. Three repetitions support descriptive comparisons, rather than a general speed guarantee.}
\label{fig:adaptive}\end{figure}

\subsection{Separating preprocessing and prediction}
We repeat the connected three- and four-loop bubble-box calculations with each exact change enabled in turn, followed by the learned choice. Table~\ref{tab:adaptive-integration} reports matched complete times from these separate trials. Every method receives the same 600-second allowance per attempt. The previous-preparation control retains declared-sector initialization and uses native equation choices in the same executable. It disables the two new exact changes. Thus the overall factor includes deterministic preprocessing as well as any subsequent benefit from the model. The policy's added effect is the final change from projected preparation to learned choice; Figure~\ref{fig:adaptive-integration} keeps these contributions separate.

\begin{table}[!htbp]\centering\small
\caption{Matched preparation comparison for the connected bubble boxes. Times are medians of three complete reductions, in seconds. The final column divides previous-preparation time by learned time.}
\label{tab:adaptive-integration}
\begin{tabular}{@{}rrrrrr@{}}\toprule
Loops & Previous & File index & Projection & Learned & Overall factor\\\midrule
@INTEGRATION@
\bottomrule\end{tabular}\end{table}

\begin{figure}[tbp]\centering
\includegraphics[width=\linewidth]{paper_figures/adaptive_integration.pdf}
\caption{Complete time for the matched preparation study. The logarithmic vertical axis displays the large deterministic change and the smaller final change from prediction. All points represent reductions into the same prescribed basis with exact coefficient checks.}
\label{fig:adaptive-integration}\end{figure}

The new policy makes one inexpensive decision before the costly work begins and retains native row elimination. Its tests cover stated target patterns and kinematics in known families. They do not establish a gain for every integral type, a minimal master basis, or a globally fastest reduction sequence. Reference failures and bounded higher-loop attempts remain part of the evidence. These limits determine where the current measurements support use of the method.
'''
    substitutions={'@MODEL@':model,'@DEPTH@':d['model'].split('_')[1],'@TREECOUNT@':str(d['trees'])+(' tree' if d['trees']==1 else ' trees'),
        '@OFFLINE@':f'{d["offline_recorded_reduction_seconds"]:.1f}','@FIT@':f'{d["fitting_seconds"]:.3f}',
        '@NATIVEFALLBACK@':str(d['fallback_totals']['native']),'@LEARNEDFALLBACK@':str(d['fallback_totals']['learned']),
        '@TRAIN@':str(d['training_cases']),'@VALID@':str(d['validation_cases']),'@TEST@':str(d['test_cases']),
        '@FIXEDNAME@':{'native':'the target-based native seed region','tight':'the seed region with all three limits reduced by one','dots':'the seed region with the positive-index and dot limits reduced by one','rank':'the seed region with numerator rank reduced by one','order5':'integral ordering 5','equation':'the existing equation filter','expanded':'direct expansion of all three seed limits'}[d['best_fixed']],
        '@NATIVE@':f'{native:.3f}','@FIXED@':f'{fixed:.3f}','@LEARNED@':f'{learned:.3f}',
        '@NATIVECHANGE@':change(learned/native),'@FIXEDCHANGE@':change(learned/fixed),'@ROWS@':'\n'.join(rows),
        '@TRIALNATIVE@':f'{d["all_trial_learned_to_native"]:.4f}','@TRIALFIXED@':f'{d["all_trial_learned_to_fixed"]:.4f}',
        '@WORKFLOWS@':str(d['workflows']),'@APPLICATIONS@':str(d['applications']),'@PUBLIC@':str(len(d['public_applications'])),
        '@INFERENCE@':f'{1000*d["inference_median_seconds"]:.3f}','@INTEGRATION@':'\n'.join(integration),
        '@UNFINISHED@':(f'{len(d["unfinished"])} planned reserved batch(es) lack a completed reference or enlarged check and receive no speedup estimate.' if d['unfinished'] else 'Every planned reserved batch completes its reference and enlarged-seed check.')}
    for a,b in substitutions.items():section=section.replace(a,b)
    if d['conditional_confirmation']:
        extra='The four-loop confirmation follows a condition registered before fitting the model. When the original reserved reference check does not complete, a fresh profile uses the two nested seed regions already verified during development. The model remains fixed, and the original incomplete case remains in the failure count.'
        section=section.replace('\\begin{figure}[tbp]\\centering\n\\includegraphics[width=\\linewidth]{paper_figures/adaptive_reduction.pdf}',extra+'\n\n\\begin{figure}[tbp]\\centering\n\\includegraphics[width=\\linewidth]{paper_figures/adaptive_reduction.pdf}',1)
    guard_rows='\n'.join(f'{NAMES[g]} & {v["graph_fixed"]:.3f} & {v["learned"]:.3f} & {v["guarded"]:.3f}'+r'\\' for g,v in gc['by_graph'].items())
    enabled=', '.join(NAMES[g].lower() for g in gc['enabled_graphs']) or 'none of the tested graph structures'
    guard_text=r'''\subsection{A stronger fixed control and the deployed policy}
One fixed setting for all graphs can be a weak control because different denominator structures can favour different seed regions. We therefore select a separate fixed setting for each graph using validation data only. We also fit @EXPERTCOUNT@ small regression trees separately for the graphs with sufficient training cases. They use the same measured cost labels and can specialize in the effect of target powers and numerator rank within one denominator structure. Validation compares these trees with the global model and selects a predictor and gate for each graph. Fitting the additional trees takes @EXPERTFIT@ seconds, with no additional label-generation cost.

We compare the graph-specific fixed settings, the original global model, and a validated policy that uses its selected predictor only where validation supports an additional saving. This procedure was specified before any reserved timings were collected. The final rule requires at least two percent less summed validation time and a saving in both validation repetitions; otherwise the graph's fixed setting is used. All choices remain fixed during the matched comparison. Appendix~\ref{app:adaptive} defines the local models and selection rule.

Validation enables target-dependent predictions for @ENABLED@. Table~\ref{tab:adaptive-graph} gives a separate matched comparison on the same reserved targets, with three repetitions per method. The graph-specific fixed choices take @GFIXED@ seconds, the cost model takes @GMODEL@ seconds, and the validated policy takes @GGUARD@ seconds, using sums of batch medians. The validated policy uses @GCHANGE@ than the graph-specific control. Across all repetitions, its time ratio is @GTRIAL@. All @GCOUNT@ reductions pass exact coefficient checks. The fixed choices and validated policy require @GFALLBACK@ and @PFALLBACK@ recovery attempts, respectively. Figure~\ref{fig:adaptive-graph} shows where predictions add value beyond a fixed choice for each graph.

\begin{table}[!htbp]\centering\small
\caption{Matched complete times in seconds against the stronger fixed control. The validated policy keeps fixed choices where validation does not support the model.}
\label{tab:adaptive-graph}
\begin{tabular}{@{}lrrr@{}}\toprule
Graph & Fixed per graph & Cost model & Validated policy\\\midrule
@GROWS@
\midrule Total & @GFIXED@ & @GMODEL@ & @GGUARD@\\\bottomrule
\end{tabular}\end{table}

\begin{figure}[tbp]\centering
\includegraphics[width=\linewidth]{paper_figures/adaptive_graph_controls.pdf}
\caption{Added effect of target-dependent choices relative to the best fixed validation setting for each graph. Each point divides summed batch medians in the matched comparison. The validated policy uses the model only in the graph structures selected by its validation rule. Timing differences also remain when two methods choose the same setting.}
\label{fig:adaptive-graph}\end{figure}

The public application uses the validated policy and completes the separate exact checks reported above. It keeps native choices for requests outside the recorded family structures and target ranges. An additional application check confirms this fallback for an unsupported graph label. This guard limits the domain in which the learned prediction is used; it does not establish performance on unseen graph structures.

'''
    for key,value in {'@ENABLED@':enabled,'@EXPERTCOUNT@':str(gc['expert_candidates']),'@EXPERTFIT@':f'{gc["expert_fitting_seconds"]:.3f}',
                      '@GFIXED@':f'{gt["graph_fixed"]:.3f}','@GMODEL@':f'{gt["learned"]:.3f}',
                      '@GGUARD@':f'{gt["guarded"]:.3f}','@GCHANGE@':change(gc['guarded_to_fixed']),
                      '@GTRIAL@':f'{gc["all_trial_totals"]["guarded"]/gc["all_trial_totals"]["graph_fixed"]:.4f}',
                      '@GFALLBACK@':str(gc['fallback_totals']['graph_fixed']),'@PFALLBACK@':str(gc['fallback_totals']['guarded']),
                      '@GCOUNT@':str(gc['workflows']),'@GROWS@':guard_rows}.items():guard_text=guard_text.replace(key,value)
    section=section.replace('\\subsection{Separating preprocessing and prediction}',guard_text+'\\subsection{Separating preprocessing and prediction}',1)
    section=section.replace('followed by the learned choice.','followed by the validated policy.')
    section=section.replace('subsequent benefit from the model.','subsequent benefit from its selected settings.')
    section=section.replace("The policy's added effect is the final change from projected preparation to learned choice;",'The final change from projected preparation includes the validated policy and its graph-specific fixed settings;')
    section=section.replace('by learned time.','by validated-policy time.')
    section=section.replace('Projection & Learned & Overall factor','Projection & Validated policy & Overall factor')
    section=section.replace('smaller final change from prediction.','final change from the validated policy. The separate graph-specific comparison measures the added effect of prediction.')
    failed=[c for c in d['integration'] if any(v['median_seconds'] is None for v in c['methods'].values())]
    if failed:
        detail=[]
        for c in failed:
            for method,v in c['methods'].items():
                if v['median_seconds'] is None:
                    detail.append(f'The {c["loops"]}-loop {method} control does not complete within its bounded attempts, after {sum(v["failed_seconds"]):.1f} seconds of recorded work. Its remaining {v["omitted_repetitions"]} repetitions are omitted after this failure, while the other pre-specified settings are completed. It receives no median completion time or speedup factor.')
        section=section.replace('\\begin{table}[!htbp]\\centering\\small\n\\caption{Matched preparation comparison', ' '.join(detail)+'\n\n\\begin{table}[!htbp]\\centering\\small\n\\caption{Matched preparation comparison',1)
        section=section.replace('All points represent reductions into the same prescribed basis with exact coefficient checks.','All plotted points represent completed reductions into the same prescribed basis with exact coefficient checks. Incomplete controls are omitted from the curve and reported in the table.')
    assert not re.search(r'@[A-Z]+@',section)
    (REPORT/'adaptive_results.tex').write_text(section)
    appendix=(HERE/'adaptive_appendix.tex').read_text()
    if d['conditional_confirmation']:
        appendix+='\n\\subsection{Conditional four-loop reference confirmation}\nThe generic enlarged-reference check does not complete for the original reserved four-loop bubble box. A rule registered before model fitting therefore adds profile $h=305$, with reference seed limits $(r,s,d_{\\rm dots})=(12,1,2)$ and check limits $(12,2,2)$. Here $d_{\\rm dots}$ is the dot limit, distinct from the spacetime dimension. The development study had already verified this pair of nested regions. The new profile uses the same frozen model and the same three timing repetitions for native, fixed, and learned choices. It supplies a separate bounded confirmation; the unfinished original profile is retained in the failure count.\n'
    (REPORT/'adaptive_appendix.tex').write_text(appendix)
    definitions=(REPORT/'paper_appendices.tex').read_text()
    native_definitions=definitions.split('\\subsection{Native multiloop comparisons}',1)[1].split('For the final early-equation test',1)[0]
    scattering_definitions=definitions.split('\\subsection{New scattering structures and symbolic invariants}',1)[1].split('The rational nonplanar profiles',1)[0]
    notes_definitions=r'''\section{Integral families for the native cost comparisons}
\label{app:families}
The denominator convention is $D_i=q_i^2-m_i^2+\mathrm{i}0$, with the measure in Eq.~\eqref{eq:family}. This appendix collects the ordered momenta used by the later cost studies so that the notes specify their physical inputs independently of the companion paper. Appendix~\ref{app:adaptive} gives the masses, kinematic profiles, and target indices for the new comparisons. Appendix~\ref{app:higher-scattering} adds the connected higher-loop scattering families.

The sunrise uses
\begin{equation}
\boldsymbol q_{\rm S}=(\ell_1,\ell_2,p-\ell_1-\ell_2,p-\ell_1,p-\ell_2).
\end{equation}
Its first three entries are physical denominators and its last two entries are auxiliary. Their indices remain nonpositive.

\subsection{Native multiloop families}
'''+native_definitions+'\n\\subsection{Scattering structures and symbolic invariants}\n'+scattering_definitions
    (REPORT/'notes_native_families.tex').write_text(notes_definitions)
    higher(old)
    append_bibliography()
    p=REPORT/'workflow_appendix.tex';s=p.read_text()
    s=s.replace('squared masses $(2,7,11)$ and $p^2','squared masses $(3,7,13)$ and $p^2')
    s=s.replace('$(1,1,1,1,1,53+2h)$','$(1,1,1,13,13,53+2h)$')
    p.write_text(s)
    p=REPORT/'report.tex';s=p.read_text()
    phrase='These definitions give Kira a common way to label the integrals and organize the equations between them.'
    if 'A top sector specifies a maximal declared set' not in s:
        s=s.replace(phrase,'A top sector specifies a maximal declared set of positive propagator indices, and its subsectors follow by removing propagators~\\cite{KiraOriginal}. '+phrase,1)
    if '\\input{adaptive_results}' not in s:
        s=s.replace('\\input{thread_policy_results}','\\input{thread_policy_results}\n\\input{higher_scattering_results}\n\\input{adaptive_results}',1)
        s=s.replace('\\input{thread_policy_appendix}','\\input{thread_policy_appendix}\n\\input{higher_scattering_appendix}\n\\input{adaptive_appendix}',1)
    s=s.replace('October 14, 2026','October 15, 2026')
    s=s.replace('Learned selection for exact Feynman integral reduction with Kira','Machine learning and exact preprocessing for Feynman integral reduction with Kira')
    # Keep the scientific narrative focused on the current model. Earlier
    # strategy measurements remain available, with all labels and figures.
    if '\\label{app:earlier-strategies}' not in s:
        start=s.index('\\section{Selecting a complete calculation before equation generation}')
        end=s.index('\\input{higher_scattering_results}',start)
        earlier=s[start:end]
        main_strategy=r'''\section{Selecting a complete calculation before equation generation}
\label{sec:strategies}
The local-model tests show that selecting useful equations does not by itself ensure a faster complete reduction. We therefore train models on measured calculation time and move their decision to the start of a target batch. The earlier experiments examine graph-specific strategies, selective seed expansion, integral ordering, and worker count. Appendix~\ref{app:earlier-strategies} preserves their model definitions and results. Their gains use different target batches and cannot be multiplied into one speedup.

These experiments also raise an attribution question: how much of the saving comes from the learned choice, and how much comes from the fixed settings around it? The next section holds the other settings fixed to answer that question. Its results motivate the single complete-cost policy presented afterwards.

'''
        s=s[:start]+main_strategy+s[end:]
        earlier=earlier.replace('\\section{Selecting a complete calculation before equation generation}','\\section{Earlier models for complete calculations}',1)
        earlier=earlier.replace('\\label{sec:strategies}','\\label{app:earlier-strategies}',1)
        s=s.replace('\\appendix\n','\\appendix\n'+earlier+'\n',1)
    abstract=f'''Integration-by-parts reduction expresses Feynman integrals through master integrals, but its cost depends on which identities and reduction settings are used. We study learned seed, row, and equation selection in Kira, then train a single policy to predict complete reduction cost. Its inputs describe the target powers and family structure, while its labels include unsuccessful attempts, recovery, and exact checks. We also remove repeated searches for absent sector files and simplify the zero-sector criterion through an exact polynomial projection. On {d['test_cases']} reserved batches from known graph structures, the selected model takes {learned:.2f} seconds compared with {native:.2f} seconds for native choices and {fixed:.2f} seconds for the validation-selected fixed setting, using sums of batch median times. These comparisons share the improved executable and therefore separate learned selection from preprocessing. All {d['workflows']} timed reductions and {d['applications']} additional applications pass exact coefficient checks. The tests include connected scattering at three and four loops and separate symbolic scattering targets. Learned row selection remains omitted because its earlier complete-time comparisons show no reliable gain. The results identify supported uses of prediction and exact preprocessing without assuming that either gives a universal speedup.'''
    abstract=abstract.replace('Learned row selection remains omitted',f'A stronger matched control selects a fixed setting for each graph. The deployed policy uses predictions only where validation supports them and takes {gt["guarded"]:.2f} seconds against {gt["graph_fixed"]:.2f} seconds for that control. Learned row selection remains omitted')
    s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',s,count=1,flags=re.S)
    anchor='The final sections bring the results together and state their physical scope.'
    if 'A final redesign learns one complete-cost policy' not in s and 'The final method chooses among complete reduction strategies' not in s:
        s=s.replace(anchor,'A final redesign learns one complete-cost policy and separates its contribution from exact preprocessing improvements. '+anchor)
    start=s.index('\\subsection{What the model comparisons establish}')
    end=s.index('\\begin{table}',start)
    overview=f'''\\subsection{{What the model comparisons establish}}
The current policy uses one model to select a complete calculation before equation generation. Its test total is {learned:.3f} seconds, compared with {native:.3f} seconds for native choices and {fixed:.3f} seconds for the best fixed validation choice. The comparisons in Section~\\ref{{sec:adaptive}} use the same exact preprocessing and include failed attempts, so they measure the added effect of prediction. The separate preparation study identifies the larger changes caused by file indexing and the projected zero-sector criterion.

The earlier experiments in Table~\\ref{{tab:overall}} cover different targets and stages. Seed and equation prediction save time in particular domains, whereas the row model gives no reliable saving and remains omitted. The component controls in Section~\\ref{{sec:components}} show that some gains attributed to a complete strategy come from its fixed settings. This result motivates both the new single policy and its fixed control.

Each percentage belongs to its stated inputs and baseline. Gains from different experiments cannot be multiplied. The restricted vacuum recurrence and shared-request results below are separate examples of exact reuse, while the new native tests include connected scattering and symbolic targets under the conditions given in the appendices.

'''
    overview+=f'The deployed policy adds a validation guard against fixed settings selected separately for each graph. In its separate matched comparison, the policy takes {gt["guarded"]:.3f} seconds against {gt["graph_fixed"]:.3f} seconds for those fixed choices, with all {gc["workflows"]} reductions passing exact checks. This comparison provides the stronger test of the value added by target-dependent predictions.\n\n'
    s=s[:start]+overview+s[end:]
    current_rows='% BEGIN CURRENT COST SUMMARY\n'+f'New cost model & Known graph structures, loops 1--4 & {change(learned/native)} than native choices in the improved executable'+r'\\'+'\n'+f'Validated policy & Same targets; fixed settings selected per graph & {change(gc["guarded_to_fixed"])} than the graph-specific fixed control'+r'\\'+'\n% END CURRENT COST SUMMARY\n'
    if '% BEGIN CURRENT COST SUMMARY' in s:
        s=re.sub(r'% BEGIN CURRENT COST SUMMARY.*?% END CURRENT COST SUMMARY\n?',lambda _:current_rows,s,flags=re.S)
    else:s=s.replace('Seed network & One target',current_rows+'Seed network & One target',1)
    s=s.replace('The large saving in this study includes mathematical reuse and implementation changes, so it is not an isolated measure of machine learning performance.','The deployed recurrence uses a fixed rule. Its large saving comes from exact mathematical reuse and implementation changes. A separately trained selector for recurrence strategies takes 1.7\\% more time than the fixed rule and supplies no established additional saving.')
    s=s.replace('general high-loop scattering requires a separate comparison.','the connected scattering comparisons in Sections~\\ref{sec:components} and~\\ref{sec:adaptive} have separate definitions and timings.')
    start=s.index('\\section{Conclusion}');end=s.index('\\appendix',start)
    conclusion=f'''\\section{{Conclusion}}
We have tested learned decisions against the complete time required for exact Feynman integral reduction. The experiments distinguish seed selection, equation selection, and row selection, and then combine the useful choices in one policy trained on measured cost. The row model remains excluded because its complete-time tests show no reliable gain.

The new policy selects among seven calculations from the target indices and family structure. On {d['test_cases']} reserved batches, its summed batch median time is {learned:.3f} seconds. This gives {change(learned/native)} than native choices and {change(learned/fixed)} than the best fixed validation setting in the same improved executable. All {d['workflows']} timed reductions and {d['applications']} additional applications reproduce the reference coefficients exactly. The reported times include prediction, checks, and unsuccessful attempts followed by recovery.

Exact preprocessing removes work that prediction alone cannot avoid. Indexing the existing sector files preserves the loaded equations, and projecting the zero-sector criterion preserves its polynomial constraints within the declared sector domain. The matched preparation tests separate these deterministic changes from the final learned choice. The earlier shared-request and restricted vacuum-recurrence results remain separate gains from exact reuse.

The tests cover known graph structures, new rational kinematics and target positions, selected symbolic scattering targets, and connected bubble-box families through four loops. They use supplied master bases and include separate reference checks. Broader high-loop graphs, unrestricted symbolic kinematics, and global path optimality remain beyond the demonstrated scope. The method can therefore be used where its matched tests support a saving, with exact recovery and explicit resource limits.

'''
    conclusion=conclusion.replace('Exact preprocessing removes work',f'The deployed policy uses target-dependent predictions only where validation beats the best fixed setting for that graph. Its separate matched test gives {change(gc["guarded_to_fixed"])} than these graph-specific fixed choices, with all {gc["workflows"]} reductions passing exact checks. This guard prevents unsupported model choices from replacing the fixed settings in deployment.\n\nExact preprocessing removes work',1)
    s=s[:start]+conclusion+s[end:];p.write_text(s)
    p=REPORT/'notes.tex';s=p.read_text()
    if '\\input{notes_native_families}' not in s:s=s.replace('\\input{workflow_appendix}','\\input{notes_native_families}\n\\input{workflow_appendix}',1)
    if '\\input{adaptive_results}' not in s:
        s=s.replace('\\input{thread_policy_results}','\\input{thread_policy_results}\n\\input{higher_scattering_results}\n\\input{adaptive_results}',1)
        s=s.replace('\\input{thread_policy_appendix}','\\input{thread_policy_appendix}\n\\input{higher_scattering_appendix}\n\\input{adaptive_appendix}',1)
    p.write_text(s)
    p=REPORT/'s01_check_paper.py';s=p.read_text()
    if "'adaptive_results.tex'" not in s:s=s.replace("'thread_policy_appendix.tex']","'thread_policy_appendix.tex','higher_scattering_results.tex','higher_scattering_appendix.tex','adaptive_results.tex','adaptive_appendix.tex']",1)
    p.write_text(s)
    p=REPORT/'Makefile';s=p.read_text()
    if 'adaptive_results.tex' not in s:s=s.replace('thread_policy_appendix.tex paper_references.bib','thread_policy_appendix.tex higher_scattering_results.tex higher_scattering_appendix.tex adaptive_results.tex adaptive_appendix.tex paper_references.bib')
    p.write_text(s)
    print(json.dumps(dict(report_sources_updated=True,model=d['model'],test_cases=d['test_cases'])),flush=True)
def higher(d):
    a=d['ablation'];comparisons=a['comparisons'];native=comparisons['worker_model_to_native']['denominator_sum'];final=comparisons['worker_model_to_native']['numerator_sum']
    rows=[]
    for key,name in [('graph_model_to_native','Graph-strategy model'),('seed_model_to_native','Through seed expansion'),('worker_model_to_native','Through worker selection'),('equation_filter_to_native','Equation filter'),('seed_filter_to_native','Seed filter'),('row_model_to_native','Row model')]:
        r=comparisons[key];rows.append(f'{name} & {r["numerator_sum"]:.3f} & {change(r["numerator_sum"]/native)}'+r'\\')
    control=[]
    for key,name in [('graph','Graph choice'),('seed','Seed expansion'),('worker','Worker count')]:
        r=d['choice_controls']['summary'][key];control.append(f'{name} & {r["cases"]} & {r["control_sum"]:.3f} & {r["selected_sum"]:.3f} & {change(r["selected_sum"]/r["control_sum"])}'+r'\\')
    highs=[c for c in d['higher_cases'] if 'median_seconds' in c['methods'].get('sector_equation',{})]
    high_native=sum(c['methods']['sector_native']['median_seconds'] for c in highs);high_eq=sum(c['methods']['sector_equation']['median_seconds'] for c in highs)
    four=next(c for c in d['memory_cases'] if c['kind']=='bubble_box4')
    four_native=four['methods']['native']['median_seconds'];four_eq=four['methods']['equation']['completed_seconds']
    section=r'''\section{Checking the contribution of each component}
\label{sec:components}
The previous models form a sequence of choices, so a faster final calculation does not identify which choice supplies the saving. We compare ten methods on fourteen fresh batches from seven known graph structures and then disable individual learned decisions while keeping the other stages unchanged. Every method uses the same targets and prescribed basis. All 420 reductions in the first comparison and all 96 additional decision controls pass exact coefficient checks.

The native-choice total is @NATIVE@ seconds, using sums of three-run batch medians. Table~\ref{tab:component-common} shows the complete strategies relative to that control. The result through worker selection takes @FINAL@ seconds, but this saving includes fixed seed settings as well as learned decisions. The equation, seed, and row filters increase time on this particular target pattern. Earlier savings on other targets remain separate results.

\begin{table}[!htbp]\centering\small
\caption{Component comparison on the same fourteen batches. Complete times include decisions, exact checks, and recovery. The first three rows retain preceding stages.}
\label{tab:component-common}
\begin{tabular}{@{}lrl@{}}\toprule
Method & Complete time (s) & Change from native\\\midrule
@ROWS@
\bottomrule\end{tabular}\end{table}

\begin{table}[!htbp]\centering\small
\caption{The added learned decision, with other stages held fixed. Each row uses the subset on which that decision is enabled. Fixed settings were selected before this test.}
\label{tab:isolated-choices}
\begin{tabular}{@{}lrrrl@{}}\toprule
Decision & Batches & Fixed (s) & Learned (s) & Change\\\midrule
@CONTROLS@
\bottomrule\end{tabular}\end{table}

The isolated controls in Table~\ref{tab:isolated-choices} show why complete-time gains need a fixed comparison. On these batches, graph choice saves a small amount, while the added seed and worker choices increase time. Figure~\ref{fig:component-controls} presents both comparisons. These results motivate replacing the sequence of selectors with the single cost policy in the next section.

\begin{figure}[tbp]\centering\includegraphics[width=\linewidth]{paper_figures/component_ablation.pdf}
\caption{Complete strategies and their added learned decisions. The upper panel uses all fourteen batches. The lower panel changes one learned decision on its enabled subset. Both show ratios of summed batch medians and retain the equal-time reference.}
\label{fig:component-controls}\end{figure}

\subsection{Connected scattering and bounded higher-loop tests}
We also construct connected four-point ladders and boxes with bubble subgraphs, defined in Appendix~\ref{app:higher-scattering}. The two completed three-loop bubble-box profiles take @HIGHNATIVE@ seconds with restricted initialization and native equation choices, compared with @HIGHEQ@ seconds with the frozen equation filter. This is @HIGHCHANGE@ under the same initialization. The complete strategy selectors otherwise retain native choices on these previously unsupported graph structures.

The bounded four- through six-loop probes identify separate costs and limits. Four-loop initialization exceeds the initial short time allowance. Five-loop attempts exceed the memory allowance, and the six-loop four-point representation requires 39 inverse propagators, above the tested executable's 31-entry limit. Later runs produce a four-loop bubble-box reference and reproduce its coefficients with enlarged seeds. Three native repetitions have median time @FOURNATIVE@ seconds. Two completed filtered repetitions take @FOUREQ@ seconds, each requiring native recovery after an insufficient equation set. Only these two filtered repetitions complete, so this diagnostic supplies no matched three-run speedup estimate. The incomplete attempt is excluded from timing results.

The new work therefore addresses both preparation and the learned choice. A complete four-loop reduction is established for the stated bubble-box family, while the failed larger-family probes supply no speedup claim. The vacuum recurrence used elsewhere in this paper does not determine the scattering coefficients, as explained in Appendix~\ref{app:higher-scattering}.
'''
    for key,value in {'@NATIVE@':f'{native:.3f}','@FINAL@':f'{final:.3f}','@ROWS@':'\n'.join(rows),'@CONTROLS@':'\n'.join(control),
                      '@HIGHNATIVE@':f'{high_native:.3f}','@HIGHEQ@':f'{high_eq:.3f}','@HIGHCHANGE@':change(high_eq/high_native),
                      '@FOURNATIVE@':f'{four_native:.3f}','@FOUREQ@':' and '.join(f'{x:.3f}' for x in four_eq)}.items():section=section.replace(key,value)
    (REPORT/'higher_scattering_results.tex').write_text(section)
    source=(ROOT/'Kira_comparison/higher_scattering/higher_scattering_appendix.tex').read_text()
    source=source.replace('A separate initial probe keeps both $s$ and $t$ symbolic.','An attempted symbolic probe produces no retained measurement and is excluded from the numerical results.')
    source=source.replace('Each new scattering batch contains','Each batch in the earlier scattering comparison contains')
    (REPORT/'higher_scattering_appendix.tex').write_text(source)
def append_bibliography():
    entries={
      'Breiman2001Forest':r'''@article{Breiman2001Forest,
 author={Breiman, Leo}, title={Random Forests}, journal={Machine Learning},
 volume={45}, pages={5--32}, year={2001}, doi={10.1023/A:1010933404324}
}''',
      'Geurts2006ExtraTrees':r'''@article{Geurts2006ExtraTrees,
 author={Geurts, Pierre and Ernst, Damien and Wehenkel, Louis},
 title={Extremely randomized trees}, journal={Machine Learning},
 volume={63}, pages={3--42}, year={2006}, doi={10.1007/s10994-006-6226-1}
}''',
      'Lee2014LiteRed':r'''@article{Lee2014LiteRed,
 author={Lee, Roman N.}, title={{LiteRed} 1.4: a powerful tool for the reduction of the multiloop integrals},
 journal={Journal of Physics: Conference Series}, volume={523}, pages={012059}, year={2014},
 doi={10.1088/1742-6596/523/1/012059}, eprint={1310.1145}, archivePrefix={arXiv}, primaryClass={hep-ph}
}'''}
    for name in ['paper_references.bib','type_specialist_references.bib']:
        p=REPORT/name;s=p.read_text()
        for key,text in entries.items():
            if name=='type_specialist_references.bib' and ('{'+key+',') in (REPORT/'references.bib').read_text():continue
            if '{'+key+',' not in s:s+='\n'+text+'\n'
        p.write_text(s)
if __name__=='__main__':main()
