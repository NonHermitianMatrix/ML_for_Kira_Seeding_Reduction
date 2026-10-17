"""Explain the equation classifier and its matched complete-time results."""
import json,re
from s00_probe import HERE,ROOT,BOUNDS,rt,inputs
from s08_analyze import NAMES
R=ROOT/'report'
def write(p,s):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(s.rstrip()+'\n')
def block(p,tag,text):
 s=p.read_text();begin='% BEGIN '+tag;end='% END '+tag
 s=re.sub(re.escape(begin)+r'\n.*?'+re.escape(end)+r'\n','',s,flags=re.S)
 return s,begin+'\n'+text+'\n'+end+'\n'
def main():
 d=rt.read(HERE/'summary.json');f=rt.read(HERE/'trained_model/freeze.json');train=rt.read(HERE/'trained_model/candidates.json');ix=d['index_transfer']
 rows=[]
 for g,v in d['graphs'].items():rows.append(f"{NAMES[g]} & {next(c['loops'] for c in d['cases'] if c['graph']==g)} & {v['cases']} & {v['active']} & {v['totals']['off']:.2f} & {v['totals']['learned']:.2f} & {v['ratio']:.3f}\\\\")
 choices=[]
 for g,v in f['selection'].items():
  if v['option']:
   m=rt.read(HERE/'trained_model'/(v['option']['name']+'.json.gz'))
   mode='Seed' if m.get('kind')=='seed_union' else 'Equation'
   threshold=m.get('origin_threshold',v['option']['threshold'])
   choices.append(f"{NAMES[g]} & {mode} & {len(m['nodes'])} & {m['depth']} & {m['min_leaf']} & {threshold:.4g}\\\\")
 fields=dict(IXCOUNT=ix['matched'],IXCHANGE=f"{abs(100*(1-ix['ratio'])):.1f}\\% "+('less' if ix['ratio']<=1 else 'more'),IXCI=', '.join(f'{v:.3f}' for v in ix['repeat_interval']),REJECT=f"{100*d['candidate_rejection_fraction']:.1f}",FILTERMS=f"{1000*d['filter_seconds_per_active_request']:.3f}",MATCHED=d['matched'],ACTIVE=d['active_matched'],REQUESTED=d['requested'],TIMED=d['timed'],SUCCESS=d['successes'],CHECKS=d['coefficient_checks'],FAILED=len(d['reference_failed']),IDENTITY=len(d['identity_only']),INCOMPLETE=len(d['incomplete']),OFF=f"{d['totals']['off']:.3f}",ON=f"{d['totals']['learned']:.3f}",CHANGE=f"{100*(1-d['ratio']):.1f}",AOFF=f"{d['active_totals']['off']:.3f}",AON=f"{d['active_totals']['learned']:.3f}",ACHANGE=f"{100*(1-d['active_ratio']):.1f}",ACI=', '.join(f'{v:.3f}' for v in d['repeat_intervals']['active']),CI=', '.join(f'{v:.3f}' for v in d['repeat_intervals']['all']),TRAIN=train['training_cases'],VAL=train['validation_cases'],ROWS=train['training_rows'],POSITIVES=train['training_positives'],FALLBACKS=d['fallbacks']['learned'],TABLE='\n'.join(rows),CHOICES='\n'.join(choices),OFFLINE=f"{d['offline_seconds']/60:.1f}")
 def fill(s):
  for k,v in fields.items():s=s.replace('@'+k+'@',str(v))
  assert not re.search(r'@[A-Z]+@',s);return s
 section=r'''\section{Learning which equations to construct after seed tuning}
\label{sec:equation-refinement}
The seed-bound experiment shows that tuning a fixed configuration explains most of its time saving. We therefore keep those tuned seed limits and train a model for a finer decision: whether to construct each equation inside the selected region. This comparison asks whether learned equation selection supplies an additional saving after the coarse seed region has already been improved.

\subsection{Model and integration with exact reduction}
Each candidate consists of a seed integral and one IBP or Lorentz-invariance operator. A classification tree uses the seventeen quantities in Table~\ref{tab:refinement-features}, including seed powers, target powers, distance to a target, and operator index. All these quantities are available before symbolic coefficient construction. The tree follows feature-threshold tests to a terminal node, called a leaf. The leaf score is the weighted positive fraction of its training examples, and Kira constructs the equation when that score meets the selected threshold. We also test a learned seed choice that retains every operator from a seed when at least one operator receives a score above the threshold. This uses the same trained scores and keeps more identities from each retained seed, which can prevent a failed reduction. Validation compares both uses of the model. Native symmetries, exact elimination, and back substitution remain in use. A failed attempt triggers the same tuned seed configuration with the filter disabled, followed by native and expanded bounds if needed. Thus the reported cost includes the consequences of an insufficient equation set.

The training label records whether the equation's integral support appears in Kira's final selected system. Support means the set of integrals with nonzero coefficients. This label is a proxy for usefulness and does not identify a unique necessary equation set. We collect new labels with the tuned seed settings because changing those settings changes which equations Kira can select. Collection uses a Kira build that records selected supports, and every collected reduction must agree with the independent exact reference. The timed comparisons use the same current build for both methods. The earlier filters frequently need a complete retry on these inputs, so their previous performance does not justify using them without new validation.

The four-loop box with bubbles has no completed label collection within the resource allowance, so it uses unfiltered reduction in this test. We preserve those collection failures. For the nine remaining structures, we fit eight shared classification trees and eight separate trees per graph~\cite{CART1984,Pedregosa2011Bounds}, with maximum depths 6, 10, 14, or 18 and minimum leaf populations 4 or 16, and a limit of 4,096 leaves. The data contain @ROWS@ sampled equation records, including @POSITIVES@ positive labels, from @TRAIN@ training batches. Sampling weights preserve the native class proportions and give each batch equal total weight. The model receives no final reduction coefficients. Validation uses @VAL@ separate batches, first to find filters that retain nearly all positive labels and then to measure complete reduction cost. A graph uses a learned seed or equation filter only when its median validation cost is at least 5\% below the same tuned calculation with all ML disabled. Appendix~\ref{app:equation-refinement} specifies the fitting, threshold selection, and recovery rules.

\subsection{Reserved comparison and the additional learned gain}
We freeze the trees, thresholds, graph choices, and domain limits before evaluating two new rational kinematic profiles, $h=525,526$. The dimension remains symbolic. The ten graph structures and target patterns are the same as in Appendix~\ref{app:learned-bounds}; the new profiles supply distinct kinematic requests. Some index patterns repeat training patterns, including the planar and nonplanar boxes at these two profiles. This is a test within known structures at one through four loops. A separate comparison below changes the target-index batches as well. As in the seed-bound study, each timed request receives a common master basis, and independent reference coefficients enter only the final exact comparison.

Both methods use the same executable, tuned seed limits, native row choices, exact implementation improvements, worker count, and recovery limits. The control disables every learned selector. Five repetitions alternate the order of the two methods. Time includes policy loading, the domain check, equation prediction and generation, exact algebra, verification, retries, and cleanup. Initial Python imports and construction of the common reference basis remain outside this repeated timer. A domain check disables filtering for an unrecognized ordered graph or target complexity outside the saved ranges.

The reserved grid has @REQUESTED@ requests. It supplies @MATCHED@ matched nontrivial batches, with @FAILED@ failed reference checks, @INCOMPLETE@ incomplete timed batches, and @IDENTITY@ identity-only batches kept separately. All successful outputs pass exact coefficient comparisons: @SUCCESS@ completions among @TIMED@ timed requests, with @CHECKS@ comparisons. Table~\ref{tab:equation-refinement} retains each graph, including any slower result.

\begin{table}[!htbp]\centering\small
\caption{Additional effect of the equation model after fixed seed tuning. Times are sums of batch medians in seconds. ``Active'' counts batches on which the frozen policy enables filtering. A ratio below one means less complete time.}
\label{tab:equation-refinement}
\begin{tabular}{@{}lrrrrrr@{}}\toprule
Graph & Loops & Batches & Active & ML off & Policy & Ratio\\\midrule
@TABLE@
\bottomrule\end{tabular}
\end{table}

The full matched workload changes from @OFF@ to @ON@ seconds, a time saving of @CHANGE@\%. For the @ACTIVE@ batches on which the frozen policy enables a filter, the corresponding times are @AOFF@ and @AON@ seconds, giving @ACHANGE@\% less time. The 95\% intervals from resampling paired repetitions are $[@CI@]$ for the full workload ratio and $[@ACI@]$ for the active subset. The active subset follows the pre-test policy and is not selected from the observed test speedups. These intervals describe timing variation on the tested requests, not generalization to arbitrary graphs.

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/equation_refinement_times.pdf}
\caption{The left panel shows the complete-time ratio for every matched graph. Blue marks graphs with filtering enabled; grey marks graphs using the unchanged exact calculation. Horizontal intervals show the 95\% range from resampling paired repetitions within each graph. The right panel isolates the batches on which the preselected policy uses the trained filter. The control shares all exact optimizations and tuned seed settings, so the difference includes only the learned policy and its consequences.}
\label{fig:equation-refinement}
\end{figure}

On active requests, the filters reject @REJECT@\% of candidate construction calls, with a mean recorded filtering cost of @FILTERMS@ milliseconds per request. Repeated generation passes contribute to this count. Recovery can construct some rejected equations later, and its full cost remains in the timing comparison. The learned policy makes @FALLBACKS@ recovery attempts in the reserved comparison. Recorded development, label collection, validation, and fitting take @OFFLINE@ minutes, excluding earlier seed-tuning costs. This expense precedes application and must be recovered over repeated use. A useful model on this collection does not establish a benefit for an unsupported topology, symbolic kinematics beyond the dimension, or all high-loop integrals. The separate wider coverage results retain their stated scope.
'''
 app=rt.read(HERE/'application_test/summary.json')
 section+=r'''
\subsection{Complete application launches}
A separate check starts a fresh application process for each request and supplies only the target definition and master basis. It uses the first supported reserved request for each graph where validation enabled filtering, with three rotated repetitions. These are a subset of the same reserved physical inputs. The timer includes Python startup, input parsing, model loading, output storage, process exit, and the exact coefficient check. Across '''+str(len(app['cases']))+r''' matched requests, summed median time changes from '''+f"{app['totals']['off']:.3f}"+r''' seconds with all ML disabled to '''+f"{app['totals']['learned']:.3f}"+r''' seconds with the filter, giving a time saving of '''+f"{100*(1-app['ratio']):.1f}"+r'''\%. This comparison checks the live application overhead; it does not add new graph structures to the physical scope.
'''
 ixrows='\n'.join(f"{NAMES[g]} & {v['cases']} & {v['totals']['off']:.3f} & {v['totals']['learned']:.3f} & {v['ratio']:.3f}\\\\" for g,v in ix['graphs'].items())
 section+=r'''
\subsection{Transfer to new target-index batches}
The primary comparison changes kinematics but partly repeats the index patterns seen in training. To test index transfer separately, we keep the original fitted models, thresholds, and graph choices and define profiles $h=605,606$. We retain a batch only if its set of index vectors is absent from both training and validation and contains at least one individual index vector absent from those sets. We also remove repeated batches within each profile. These conditions select inputs from the graph structures enabled by the original validation; no primary test timing enters this selection. The selection rules and all resulting inputs are fixed before their reductions begin. The test therefore changes the indices within known graph structures and degree ranges, while transfer to new topologies remains untested.

Each request receives the same reference reduction and enlarged-region check as the primary comparison. Three repetitions rotate the two methods. The live application reads only a target definition and a master basis. Time includes basis reading, policy loading, prediction, exact reduction, recovery, and coefficient checks; it excludes initial Python imports and reference construction. Both methods retain the same seed settings and exact implementation.

\begin{table}[!htbp]\centering\small
\caption{The unchanged learned policy on new index batches. Times are sums of batch medians in seconds. The control disables every learned selector.}
\label{tab:index-transfer}
\begin{tabular}{@{}lrrrr@{}}\toprule
Graph & Batches & ML off & Policy & Ratio\\\midrule
'''+ixrows+r'''
\bottomrule\end{tabular}
\end{table}

'''
 section+=f"The structural rule defines {ix['requested']} requests, of which {ix['matched']} give matched nontrivial reductions. The record retains {len(ix['reference_failed'])} failed reference checks, {len(ix['incomplete'])} incomplete comparisons, and {len(ix['identity_only'])} identity-only batches. All {ix['successful']} successful outputs among {ix['timed']} timed requests pass exact comparison, with {ix['coefficient_checks']} coefficient checks. "
 section+=fill(r'The summed median time changes from ')+f"{ix['totals']['off']:.3f}"+r' to '+f"{ix['totals']['learned']:.3f}"+fill(r' seconds, giving @IXCHANGE@ time. The 95\% paired-repetition interval for the learned-to-control ratio is $[@IXCI@]$. Table~\ref{tab:index-transfer} retains every matched graph, including any slower result. This check provides separate evidence about changes in target indices and is not combined with the primary timings to form a cumulative speedup.')+'\n'
 write(R/'equation_refinement_results.tex',fill(section))
 appendix=r'''\section{Equation refinement: fitting and evaluation}
\label{app:equation-refinement}
\subsection{Inputs available before coefficient construction}
Let $\boldsymbol\sigma$ be a seed with $N$ indices, and let $\mathcal T$ be the target batch. Define the number of positive indices, the extra denominator powers, and the numerator rank by
\begin{equation}
 n_+(\boldsymbol\sigma)=\sum_i\mathbf 1[\sigma_i>0],\qquad
 \delta(\boldsymbol\sigma)=\sum_i\max(\sigma_i-1,0),\qquad
 \rho(\boldsymbol\sigma)=\sum_i\max(-\sigma_i,0).
\end{equation}
The target maxima are $\delta_{\max}=\max_{\boldsymbol a\in\mathcal T}\delta(\boldsymbol a)$ and $\rho_{\max}=\max_{\boldsymbol a\in\mathcal T}\rho(\boldsymbol a)$. For the seed's sector $S$, let $b_S$ be one if the batch contains a target in that sector and zero otherwise. Define $\delta_S,\rho_S$ as the corresponding maxima over targets in $S$, or zero when that sector has no target. The minimum target distance is
\begin{equation}
 \Delta(\boldsymbol\sigma,\mathcal T)
 =\min_{\boldsymbol a\in\mathcal T}\sum_i|\sigma_i-a_i|.
\end{equation}
These quantities depend only on indices. Table~\ref{tab:refinement-features} specifies the complete input vector. The power differences are signed; a negative value means that the seed has fewer powers than the stated target maximum. Here $L$ is the number of loops, $E$ is the number of independent external momenta, and $o$ is the operator index in Kira's candidate list.

\begin{table}[!htbp]\centering\small
\caption{The seventeen inputs to the new equation classifiers. A whole-seed choice uses the same inputs with the operator index removed.}
\label{tab:refinement-features}
\begin{tabular}{@{}lp{0.57\linewidth}r@{}}\toprule
Group & Quantities & Number\\\midrule
Family and request & $L,E,N,\log(1+|\mathcal T|)$ & 4\\
Seed powers & $n_+(\boldsymbol\sigma),\delta(\boldsymbol\sigma),\rho(\boldsymbol\sigma)$ & 3\\
Target differences & $\delta(\boldsymbol\sigma)-\delta_{\max}$ and $\rho(\boldsymbol\sigma)-\rho_{\max}$ & 2\\
Sector information & $b_S$, $\delta(\boldsymbol\sigma)-\delta_S$, and $\rho(\boldsymbol\sigma)-\rho_S$ & 3\\
Target proximity & $\Delta(\boldsymbol\sigma,\mathcal T)$ and $\mathbf 1[\boldsymbol\sigma\in\mathcal T]$ & 2\\
Operator & Index $o$ for an IBP or Lorentz-invariance identity & 1\\
Overall limits & $\delta_{\max},\rho_{\max}$ & 2\\\bottomrule
\end{tabular}
\end{table}

\subsection{Sampling and tree scores}
The physical families, target patterns, and tuned seed configurations are those in Appendix~\ref{app:learned-bounds}. Training uses $h=511,512$, validation uses $h=513$, and the new reserved test uses $h=525,526$. The earlier reserved profiles $515,516$ supply no training or validation labels for this filter. Within a batch $c$, let $N_{cy}$ be the number of native equation records with label $y\in\{0,1\}$ and let $N_c=N_{c0}+N_{c1}$. We sample $n_{cy}=\min(2000,N_{cy})$ records without replacement from each nonempty class, using a deterministic batch-specific random seed. For fitting, every sampled record in that class receives weight
\begin{equation}
 w_{cy}=\frac{N_{cy}}{n_{cy}N_c}.
\label{eq:refinement-weight}
\end{equation}
For fitting, its class has total sampled weight $n_{cy}w_{cy}=N_{cy}/N_c$, so summing over classes gives unit weight per batch. This calculation explains both the correction for class sampling and the equal batch contribution. Validation recall and retained fractions instead use $N_{cy}/n_{cy}$, which reconstructs native record counts across the validation batches.

For a tree leaf $\ell$, let $W_{\ell 1}$ and $W_{\ell 0}$ be the sums of these weights for positive and negative training records. Its score is
\begin{equation}
 p_\ell=\frac{W_{\ell 1}}{W_{\ell 0}+W_{\ell 1}}.
\label{eq:refinement-leaf}
\end{equation}
This is the weighted positive fraction in the leaf. It does not assert calibrated probabilities for new equations. The tree chooses splits through weighted Gini impurity~\cite{CART1984}, using the classification-tree implementation of Ref.~\cite{Pedregosa2011Bounds}. At a node, let $W_0$ and $W_1$ be the negative and positive total weights, $W=W_0+W_1$, and $p=W_1/W$. The weighted impurity is
\begin{equation}
 G=W[1-p^2-(1-p)^2]
   =2Wp(1-p)=\frac{2W_0W_1}{W_0+W_1}.
 \label{eq:refinement-gini}
\end{equation}
The equalities follow by expanding the two squares and substituting the weighted class fractions. For each allowed split, subtract the two child impurities from the parent impurity. The tree selects the largest decrease, subject to its depth, leaf-count, and minimum-population limits. The eight depth and leaf-size choices appear in the main text. We compare shared fits with separate fits for each graph before the complete-cost validation. All fits use random seed 611.

\subsection{Validation and frozen deployment}
For each graph, candidate thresholds include $10^{-12}$, 0.01, 0.05, 0.1, 0.25, and 0.5, together with the 0, 0.1, 0.5, 1, and 2 percentiles of positive validation scores. For each required weighted recall of 0.9999, 0.995, and 0.98, we choose the tree and threshold with the smallest retained fraction among candidates that meet that recall. Repeated choices appear once. These thresholds concern reference labels; they do not guarantee a complete reduction.

We run each shortlisted filter and the all-ML-disabled control three times for every validation batch. For each graph, we sum the per-batch median times and choose the cheapest candidate, retaining it only if it beats the control by at least 5\%. This threshold for deployment is fixed before the reserved experiment. For the shortlisted source trees, we also calculate the maximum score over operators and select seed thresholds using the same recall levels and retained-fraction criterion. The seed threshold grid adds 0.75, 0.9, and 1 to the equation grid. We compare up to three seed variants with the equation filters in the same complete-cost validation. The selected filters are
\begin{table}[!htbp]\centering\small
\caption{Filters fixed by complete-time validation. The columns give the filter type, compiled node count, source-tree depth limit, minimum leaf population, and original score threshold.}
\begin{tabular}{@{}llrrrr@{}}\toprule
Graph & Filter & Nodes & Depth limit & Leaf size & Threshold\\\midrule
@CHOICES@
\bottomrule\end{tabular}
\end{table}
The model tests 17 features before symbolic coefficient construction. It retains a candidate when $p_\ell\geq\tau$, where $\tau$ is the graph's threshold. If that attempt fails, the next attempt uses the tuned seed setting without the model. Native and fully expanded bounds follow if necessary, with identical configurations removed. Every attempt must express all mandatory targets in the prescribed basis. Independent exact coefficient comparisons then check the exported answer. Every failed attempt remains in the timing record.

\subsection{A learned choice of whole seeds}
For a seed $\boldsymbol\sigma$, target batch $\mathcal T$, and candidate operator $o$, let $p_\theta(\boldsymbol\sigma,o,\mathcal T)$ be the equation score. The equation filter retains the candidate when this score is at least $\tau$. Its whole-seed variant instead uses
\begin{equation}
 K_\theta(\boldsymbol\sigma,\mathcal T)
 =\mathbf 1\!\left[\max_{o\in\mathcal O}p_\theta(\boldsymbol\sigma,o,\mathcal T)\geq\tau\right].
 \label{eq:seed-union-choice}
\end{equation}
Here $\mathcal O$ is the finite list of candidate operators, and $\mathbf 1$ is one when its condition holds and zero otherwise. A maximum reaches $\tau$ exactly when at least one member reaches it. Therefore Eq.~\eqref{eq:seed-union-choice} is the logical union of the original equation decisions. If $K_\theta=1$, all operators from that seed remain available. The resulting set contains every equation that the source filter would retain, although it can contain more. This inclusion does not prove that the reduction will complete.

For $L$ loop momenta and $E$ independent external momenta, Kira's candidate list contains $L(L+E)$ IBP operators and $E(E-1)/2$ external Lorentz-invariance operators~\cite{KiraOriginal}. The first count follows by choosing a loop derivative and a contraction vector from the loop and external momenta. The second counts unordered pairs of external vectors for antisymmetric contractions. These are candidate counts before redundancies are removed. The seed filter takes the maximum over that full list. Its decision no longer depends on which operator is being considered, so it uses sixteen of the seventeen features. We evaluate the same logical decision directly during generation and check its equivalence to the original operator scores. Kira still enumerates the configured seed region, applies its native symmetries, and performs exact algebra.

\subsection{Ratios and uncertainty}
For each complete matched batch, take the median of five times for each method, then sum the medians as in Eq.~\eqref{eq:bounds-times}. This gives the learned-to-control ratio and the percentage saving $100(1-R)$. The active subset consists of batches for which the frozen domain and graph policy enable a filter. It uses the same ratio definition. We resample paired repetition positions within each batch 5,000 times and report the 2.5th and 97.5th percentiles. Failed reference checks, incomplete method comparisons, and identity-only targets remain outside the nontrivial paired ratios. Their counts remain in the main results.
'''
 write(R/'equation_refinement_appendix.tex',fill(appendix))
 summary=fill(r'After fixed seed tuning, newly trained equation filters give @ACHANGE@\% less complete time on @ACTIVE@ matched batches where validation enables them, with @CHANGE@\% time saving across all @MATCHED@ matched batches. These controls disable all ML and retain the same seed settings and exact implementation. Section~\ref{sec:equation-refinement} gives the failures, timing intervals, and physical limits.')
 for name in ['report.tex','notes.tex']:
  p=R/name;s=p.read_text()
  if name=='report.tex':
   if '\\input{equation_refinement_results}' not in s:s=s.replace('\\input{learned_bounds_results}','\\input{learned_bounds_results}\n\\input{equation_refinement_results}')
   if '\\input{equation_refinement_appendix}' not in s:s=s.replace('\\input{learned_bounds_appendix}','\\input{learned_bounds_appendix}\n\\input{equation_refinement_appendix}')
   s=re.sub(r'% BEGIN EQUATION REFINEMENT SUMMARY\n.*?% END EQUATION REFINEMENT SUMMARY\n','',s,flags=re.S)
   s=s.replace('\\section{Conclusion}\n','\\section{Conclusion}\n% BEGIN EQUATION REFINEMENT SUMMARY\n'+summary+'\n% END EQUATION REFINEMENT SUMMARY\n')
   s=re.sub(r'% BEGIN EQUATION REFINEMENT OVERALL\n.*?% END EQUATION REFINEMENT OVERALL\n','',s,flags=re.S)
   s=s.replace('\\subsection{What the model comparisons establish}\n','\\subsection{What the model comparisons establish}\n% BEGIN EQUATION REFINEMENT OVERALL\n'+summary+'\n% END EQUATION REFINEMENT OVERALL\n\n')
   s=s.replace('The gain over tuned fixed settings is within timing variation;',fill(r'The seed-choice gain over tuned fixed settings is within timing variation. Separately retrained seed and equation filters give @ACHANGE@\% less complete time on @ACTIVE@ matched batches selected by pre-test validation, and @CHANGE@\% time saving across @MATCHED@ matched batches;'))
   if d['repeat_intervals']['active'][1]<1 and '% EQUATION REFINEMENT MAIN ORDER' not in s:
    start=s.index('\\section{Training data and experimental design}')
    end=s.index('\\section{Overall performance and physical scope}')
    history=s[start:end].replace('\\input{learned_bounds_results}\n','').replace('\\input{equation_refinement_results}\n','')
    bridge=r'''The following comparisons retain native row elimination. The original row network took 1.305 times the stock reduction time in 84 exact trials, while a later compiled row policy gave a ratio of $0.982$ with interval $[0.959,1.003]$. We therefore omit learned row choice and focus on seed regions and equations. Appendix~\ref{sec:rows} gives the models and checks behind that decision.

'''
    s=s[:start]+bridge+'\\input{learned_bounds_results}\n\\input{equation_refinement_results}\n\n'+s[end:]
    s=s.replace('\\appendix\n','\\appendix\n% EQUATION REFINEMENT MAIN ORDER\n'+history+'\n',1)
    s=s.replace('We first define the notation used in this paper and explain the reduction procedure. We then describe the training data and comparison rules before presenting the three local models and the models that select complete strategies. The final comparison trains a new model for seed bounds and measures its benefit against fixed settings for each graph, with all earlier learned selectors disabled. Separate controls measure the exact preprocessing improvements. The final sections bring the results together and state their physical scope. The appendices provide the integral definitions, model specifications, derivations, and conditions needed to reproduce each comparison.','We first define the notation used in this paper and explain the reduction procedure. We then compare learned seed bounds with tuned fixed settings and use that result to motivate the new equation filters. The main results measure their added effect on complete calculation time. The final sections distinguish learned gains from exact implementation changes and state the physical scope. The appendices retain earlier model tests, wider coverage checks, integral definitions, model specifications, and derivations.')

   abstract=fill(r'Integration-by-parts reduction expresses Feynman integrals in a master basis, and its cost depends partly on the equations constructed for the requested targets. We train classification trees to select equations before Kira constructs their symbolic coefficients. Separate validation compares shared and graph-specific trees, including a variant that retains all operators from a selected seed. Both timing controls use the same tuned seed limits, exact implementation, master basis, and native row elimination. On @MATCHED@ matched nontrivial test batches of one to three integrals at one through four loops, the learned policy changes summed median time from @OFF@ to @ON@ seconds, a saving of @CHANGE@\%. The @ACTIVE@ batches where the frozen policy enables filtering take @ACHANGE@\% less time, with a learned-to-control ratio interval of $[@ACI@]$ from paired timing repetitions. The measurements include prediction, equation generation, exact algebra, checks, and retries. Every successful output matches its exact reference. A separate check with @IXCOUNT@ new index batches takes @IXCHANGE@ time under the unchanged models. A comparison of learned seed bounds finds no reliable extra gain after fixed tuning, and learned row selection remains excluded. The new test uses rational kinematics, symbolic dimension, and known graph structures; broader high-loop and symbolic comparisons retain their separate limits.')
   s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _: '\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,count=1,flags=re.S)
   old='The study also examines how these decisions interact with Kira. We train models to choose a complete strategy before equation generation, compare shared reductions for compatible requests, and test exact recurrence relations in a restricted family. The resulting evidence supports different methods in different domains: some learned choices save time, row prediction gives no reliable gain, and the largest saving in the vacuum study comes from mathematical reuse.'
   new='The main comparisons separate two levels of decision. We first train models to choose the bounds of the seed region, using measured complete reduction times as labels. Tuned fixed bounds explain nearly all of that saving. We therefore hold those bounds fixed and train shared and graph-specific classification trees to select individual equations or whole seeds inside the region. This second comparison measures the additional effect of learned filtering. Earlier tests of row selection, exact preprocessing, and restricted high-loop recurrences provide the separate evidence needed to identify where each saving comes from.'
   s=s.replace(old,new)
   conclusion=fill(r'''\section{Conclusion}
We train models for decisions that affect exact Feynman integral reduction and evaluate their effect on complete calculation time. The new equation filters act before symbolic coefficient construction, using target and seed indices to select individual identities or whole groups from a seed. Kira performs exact elimination and retries without the filter when the first equation set is insufficient.

With tuned seed bounds and exact implementation changes held fixed, the reserved comparison changes summed median time from @OFF@ to @ON@ seconds across @MATCHED@ matched nontrivial batches. Filtering is enabled on @ACTIVE@ batches, whose corresponding times are @AOFF@ and @AON@ seconds. The 95\% paired-repetition interval for this subset's time ratio is $[@ACI@]$. The comparison includes prediction and recovery, and every successful output passes exact coefficient checks. The separate index-transfer check takes @IXCHANGE@ time across @IXCOUNT@ matched batches, with ratio interval $[@IXCI@]$. Section~\ref{sec:equation-refinement} reports individual graphs, incomplete references, and the fresh-application check.

The seed-bound study explains why a matched fixed control is necessary. Its learned choice saves 27.8\% against unshifted bounds, but the additional 0.5\% over tuned fixed settings lies within timing variation. Learned row elimination also supplies no reliable gain in its recorded comparisons, so the retained application uses native row choices. These results guide deployment: use the validated filters with tuned seed settings and retain exact fallback.

The earlier full-calculation comparison gives 88.2\% less time than the saved original executable on 37 matched requests, including master discovery. That saving comes from exact implementation changes and has a different workload. The restricted vacuum recurrence verifies all twelve studied loop orders under its identity assumptions. Neither result can be multiplied by the new filter gain. The new ML test supplies a master basis and covers known structures at one through four loops with rational kinematics and symbolic dimension. Larger target batches, general high-loop scattering, unrestricted symbolic kinematics, and globally minimal reduction paths remain outside its demonstrated scope.
''')
   s=re.sub(r'\\section\{Conclusion\}\n.*?(?=\\appendix\n)',lambda _:conclusion+'\n',s,count=1,flags=re.S)
   row=fill(r'Trained equation filters & @MATCHED@ matched batches; loops 1--4 & @CHANGE@\% less time than tuned ML-off control; @ACHANGE@\% on @ACTIVE@ active batches\\')
   s=re.sub(r'% BEGIN EQUATION REFINEMENT TABLE\n.*?% END EQUATION REFINEMENT TABLE\n','',s,flags=re.S)
   s=s.replace('% BEGIN LEARNED BOUNDS TABLE','% BEGIN EQUATION REFINEMENT TABLE\n'+row+'\n% END EQUATION REFINEMENT TABLE\n% BEGIN LEARNED BOUNDS TABLE',1)
  else:
   if '\\input{equation_refinement_results}' not in s:s=s.replace('\\input{learned_bounds_results}','\\input{learned_bounds_results}\n\\input{equation_refinement_results}')
   if '\\input{equation_refinement_appendix}' not in s:s=s.replace('\\input{learned_bounds_appendix}','\\input{learned_bounds_appendix}\n\\input{equation_refinement_appendix}')
   s=re.sub(r'% BEGIN CURRENT WORKFLOW UPDATE\n% EQUATION REFINEMENT CURRENT\n.*?% END CURRENT WORKFLOW UPDATE\n','',s,flags=re.S)
   current=fill(r'\paragraph{Current measured method.} The latest comparison keeps tuned seed bounds and trains classifiers that select equations before symbolic coefficient construction. It gives @CHANGE@\% less complete time across @MATCHED@ matched batches, including @ACHANGE@\% less time on the @ACTIVE@ batches where the frozen policy enables filtering. Both controls use the same exact implementation and native row elimination. Section~\ref{sec:equation-refinement} gives the models, exact checks, failures, intervals, and physical scope. The earlier experiments remain below as the detailed record of the study.')
   tag='% BEGIN CURRENT WORKFLOW UPDATE\n% EQUATION REFINEMENT CURRENT\n'+current+'\n% END CURRENT WORKFLOW UPDATE\n'
   s=s.replace('\\end{abstract}\n','\\end{abstract}\n'+tag,1)
  write(p,s)
 p=R/'s01_check_paper.py';s=p.read_text();s=s.replace("'learned_bounds_results.tex','learned_bounds_appendix.tex']","'learned_bounds_results.tex','learned_bounds_appendix.tex','equation_refinement_results.tex','equation_refinement_appendix.tex']");write(p,s)
 p=R/'Makefile';s=p.read_text()
 if 'equation_refinement_results.tex' not in s:s=s.replace('report.pdf:','report.pdf: equation_refinement_results.tex equation_refinement_appendix.tex',1)
 write(p,s)
 print('Equation refinement documented',flush=True)
if __name__=='__main__':main()
