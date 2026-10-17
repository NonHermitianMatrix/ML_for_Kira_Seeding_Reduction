"""Write the learned seed-bound methods and measured results into both documents."""
import json,re
from pathlib import Path
from s00_inputs import HERE,ROOT
from s08_analyze import NAMES
REPORT=ROOT/'report'
def write(p,s):p.write_text(s.rstrip()+'\n')
def change(r):return f'{abs(100*(1-r)):.1f}\\% '+('less' if r<=1 else 'more')
def modelname(name):
 if name.startswith('tree_'):return 'a regression tree'
 if name.startswith('extra_trees'):return 'an ensemble of extremely randomized trees'
 if name.startswith('random_forest'):return 'a random forest'
 return 'a multilayer perceptron'
def main():
 d=json.loads((HERE/'summary.json').read_text());fit=json.loads((HERE/'trained_model/selection.json').read_text());freeze=json.loads((HERE/'trained_model/freeze.json').read_text());assert d['complete']
 rows=[]
 for g,r in d['graphs'].items():
  l=next(c['loops'] for c in d['cases'] if c['graph']==g)
  rows.append(f"{NAMES[g]} & {l} & {r['cases']} & {r['seconds']['native']:.2f} & {r['seconds']['fixed']:.2f} & {r['seconds']['learned']:.2f}\\\\")
 eq={m:sum(c['equations'][m] for c in d['cases']) for m in ['native','fixed','learned']}
 fields=dict(COUNT=d['matched'],REQUESTED=d['requested'],TRAIN=fit['training_cases'],VAL=fit['validation_cases'],EXCLUDED=len(d['reference_failed']),INCOMPLETE=len(d['incomplete']),IDENTITY=len(d['identity_only']),MODEL=modelname(d['model']),TIMED=d['timed'],SUCCESS=d['successful'],CHECKS=d['coefficient_checks'],NATIVE=f"{d['totals']['native']:.3f}",FIXED=f"{d['totals']['fixed']:.3f}",LEARNED=f"{d['totals']['learned']:.3f}",NATIVECHANGE=change(d['ratios']['native']),FIXEDCHANGE=change(d['ratios']['fixed']),NATIVEFACTOR=f"{1/d['ratios']['native']:.3f}",FIXEDFACTOR=f"{1/d['ratios']['fixed']:.3f}",MODELLOAD=f"{d['loading_mean_seconds']*1000:.3f}",PREDICT=f"{d['prediction_mean_seconds']*1000:.3f}",TABLE='\n'.join(rows),NATIVECI=', '.join(f'{x:.3f}' for x in d['intervals']['native']['graph_bootstrap']),FIXEDCI=', '.join(f'{x:.3f}' for x in d['intervals']['fixed']['graph_bootstrap']),NATIVEREPEATCI=', '.join(f'{x:.3f}' for x in d['intervals']['native']['repeat_bootstrap']),FIXEDREPEATCI=', '.join(f'{x:.3f}' for x in d['intervals']['fixed']['repeat_bootstrap']),EQNATIVE=f"{int(eq['native']):,}",EQML=f"{int(eq['learned']):,}",OFFLINE=f"{d['offline_seconds']/3600:.2f}",FITSECONDS=f"{fit['training_seconds']:.2f}",NATIVEAMORT=str(d['amortization_requests']['native']),FIXEDAMORT=str(d['amortization_requests']['fixed']),GATE=freeze['gate'],RSS=f"{d['peak_rss_mib']:.1f}")
 selected=next(r for r in fit['candidates'] if r['name']==fit['selected'] and r['gate']==fit['gate'])
 pars=selected['parameters']
 if freeze['model']['kind']=='mlp':
  fields['PARAMETERS']='The selected network has hidden widths $'+str(pars['hidden_layer_sizes']).replace(' ','')+'$, uses '+('a rectified-linear activation' if pars['activation']=='relu' else 'a hyperbolic-tangent activation')+', and has regularization parameter $'+str(pars['alpha'])+'$.'
 else:
  fields['PARAMETERS']='The selected predictor uses '+str(len(freeze['model']['trees']))+' tree'+('s' if len(freeze['model']['trees'])!=1 else '')+', maximum depth '+str(pars['max_depth'])+', and at least '+str(pars['min_samples_leaf'])+' training cases per leaf.'
 def fill(s):
  for k,v in fields.items():s=s.replace('@'+k+'@',str(v))
  assert not re.search(r'@[A-Z]+@',s)
  return s
 section=r'''\section{Learning seed bounds from complete reduction time}
\label{sec:learned-bounds}
The broader test found that the earlier models often kept native choices and provided little additional benefit. We therefore train a new model for a decision that directly changes equation generation: the seed limits for the requested target batch. The model chooses these limits before Kira starts. All earlier seed, row, and equation models are disabled in this comparison, and every method uses the same exact preparation. The fixed-control comparison measures the extra benefit of a learned choice after tuning the seed settings.

\subsection{What the model learns and how Kira uses it}
A target batch can need a larger numerator bound even when its denominators require no further increase. Other batches can use fewer seeds in lower sectors. Kira provides bounds on positive powers, numerator rank, and extra denominator powers, as well as a separate restriction for lower sectors~\cite{Kira3}. These settings define ten candidate configurations in the present study. They include unshifted bounds, selective expansion, reduced bounds, full expansion, and four configurations with lower sector truncation. Appendix~\ref{app:learned-bounds} specifies every configuration and its recovery sequence.

The model receives 27 quantities that describe the graph and target indices. For each target $\boldsymbol a$, the extra denominator powers are $\delta(\boldsymbol a)=\sum_i\max(a_i-1,0)$, and the numerator rank is $\rho(\boldsymbol a)=\sum_i\max(-a_i,0)$. The first sum counts denominator powers beyond one, often called dots, and the second is the total numerator power. Together with the loop count and denominator structure, these quantities help the model predict the relative complete time of each configuration. Its training labels come from actual Kira reductions, including any failed first attempt and the subsequent recovery. The prediction therefore concerns the cost of reaching a checked answer, rather than the number of selected seeds alone. Related work uses learned search to discover sparse seed patterns~\cite{Song2025,TubeSeeding2026}; the present experiment uses Kira's existing seed-region controls and does not implement tube seeding. The application checks the ordered momentum structure and the target-count and overall index-power ranges recorded in training and validation. Inputs outside this domain use native bounds and the same exact recovery procedure.

We compare 30 fitted models: regression trees, random forests, extremely randomized trees, and multilayer perceptrons~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees,Pedregosa2011Bounds}. Each model predicts ten costs. Validation selects @MODEL@ with a gate on predicted log cost of @GATE@. @PARAMETERS@ The model receives no reference coefficients, case identifier, or kinematic profile number. Its inputs and fitted parameters remain fixed during the reserved test. Details of the objective, model choices, and selection rule appear in Appendix~\ref{app:learned-bounds}.

For each request, the application loads the fitted parameters, calculates the features, and selects a configuration. Kira then generates IBP equations and performs exact algebra in the supplied master basis. If the chosen seed region cannot reach that basis, the application tries the unshifted bounds and then full expansion, skipping duplicate configurations. A request that exhausts these attempts remains unsuccessful. Coefficient comparisons occur after Kira has produced its result and are included in the reported time.

\subsection{Independent inputs and controls}
The input grid contains ten graph structures at one through four loops, with one to three target integrals per batch. It includes vacuum and two-point integrals, planar and nonplanar boxes, a pentagon, a box with an external virtuality, and boxes with bubble subgraphs. We define 74 training requests, 37 validation requests, and 74 reserved requests at separate rational kinematic profiles, keeping the dimension symbolic. After reference checks, complete candidate comparisons, and removal of identity-only cases, @TRAIN@ training batches and @VAL@ validation batches supply the fitted comparison. Target positions change with the profile, but graph structures and target patterns are shared. This tests transfer to new requests within known structures, not arbitrary new topologies or general symbolic kinematics.

Each reserved request first receives a reference reduction and a second exact check with a larger numerator bound. These preparation calculations provide a common basis and comparison coefficients. Agreement after one enlarged seed region does not prove that this basis has the smallest possible size. They remain outside the timed application, whose purpose is reduction in an available basis. The tests therefore include native IBP generation but do not include finding the master basis from the beginning. Some target patterns coincide when a family has no auxiliary numerator. Each declared batch remains a separate workload request, and the uncertainty calculation across graphs keeps such related requests together.

The first control uses Kira's native equation and elimination choices with the unshifted target bounds and the common expansion fallback. This is a specified seed policy, not a claim that Kira has a universal default seed region. The stronger fixed control chooses the cheapest of the same ten configurations separately for each graph, using both training and validation costs. It performs no model prediction and can use lower sector truncation. The learned method may change its choice between target batches in the same graph. All three methods use the same executable, exact optimizations, one Kira worker, basis, coefficient checks, and resource limits. Five repetitions rotate their order on the same node. The timer includes model loading, prediction, equation generation, exact elimination, retries, verification, and cleanup. Initial Python imports occur before this timer.

\subsection{Measured benefit and remaining limits}
Of the @REQUESTED@ reserved requests, @COUNT@ supply matched nontrivial reductions for all three methods and all repetitions. The record also contains @EXCLUDED@ failed reference checks, @INCOMPLETE@ incomplete timed requests, and @IDENTITY@ matched identity-only requests. The full timed record contains @SUCCESS@ exact completions in @TIMED@ requests and @CHECKS@ coefficient comparisons. Failed or identity-only requests do not enter the paired speedup estimate.

Summing the median time of each matched batch gives @NATIVE@ seconds for the control with native bounds, @FIXED@ seconds for the tuned fixed control, and @LEARNED@ seconds for the learned choice. The learned method therefore takes @NATIVECHANGE@ time than the control with native bounds and @FIXEDCHANGE@ time than the tuned fixed control. The corresponding speedup factors are @NATIVEFACTOR@ and @FIXEDFACTOR@. Table~\ref{tab:learned-bounds} gives the graph results, including slower groups. These are complete application-time comparisons on the same inputs; they are separate from the earlier exact-code speedups.

\begin{table}[!htbp]\centering\small
\caption{Sum of batch median times in seconds for the new seed-bound comparison. Every row uses matched nontrivial reductions. The fixed control uses one configuration per graph.}
\label{tab:learned-bounds}
\begin{tabular}{@{}lrrrrr@{}}\toprule
Graph & Loops & Batches & Native bounds & Fixed & Learned\\\midrule
@TABLE@
\bottomrule\end{tabular}
\end{table}

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/learned_bounds_times.pdf}
\caption{The left panel shows how the learned choice changes complete time for each graph; a ratio below one means a saving. The right panel shows the summed matched workload time. Both controls disable all learned choices. The graph labels refer to the explicit denominator definitions in the appendices.}
\label{fig:learned-bounds-times}
\end{figure}

The learned-to-control time ratios have descriptive 95\% intervals $[@NATIVECI@]$ against native bounds and $[@FIXEDCI@]$ against the tuned fixed settings when whole graphs are resampled. Resampling repetitions within the fixed workload instead gives $[@NATIVEREPEATCI@]$ and $[@FIXEDREPEATCI@]$. The first calculation describes variation across this small graph collection; the second describes observed timing variation on these particular inputs. Neither interval proves a speedup on all integrals.

The summed generated-equation count changes from @EQNATIVE@ under native bounds to @EQML@ under learned choices, including equations from failed attempts. Average parameter loading and prediction take @MODELLOAD@ and @PREDICT@ milliseconds per learned request. Figure~\ref{fig:learned-bounds-effects} shows both the time ratios for each batch and the equation counts. The domain check and its time remain part of every learned request. The largest observed process-tree memory use is @RSS@ MiB within the common limit.

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/learned_bounds_effects.pdf}
\caption{Left: the distribution of batch time ratios retains every matched batch, including regressions. Right: generated equations under the learned and native-bound choices, with retries included. Points below the diagonal use fewer equations. The axes use a linear scale near zero and a logarithmic scale above 100 equations. Equation count explains part of the timing change but does not replace the complete-time measurement.}
\label{fig:learned-bounds-effects}
\end{figure}

Development, training-cost collection, validation, and their reference calculations take @OFFLINE@ hours of recorded calculation time, including @FITSECONDS@ seconds for model fitting and selection. If future requests have the same mean saving as this matched workload, approximately @NATIVEAMORT@ requests would recover that cost relative to native bounds and @FIXEDAMORT@ relative to the fixed control. This extrapolation uses the measured workload and the derivation in Appendix~\ref{app:learned-bounds}; it is not a prediction for a different workload. The interval against the tuned fixed control includes equal time. Thus, this test establishes a saving from tuned seed settings but does not establish a reliable extra saving from learning which setting to use. The wider high-loop and symbolic coverage results retain the separate scope given in Section~\ref{sec:coverage}.
'''
 app=json.loads((HERE/'application_test/summary.json').read_text())
 if app['cases']:
  section+=r'''
\subsection{Fresh application comparison}
A separate comparison starts a new application process for every request. It uses one fixed target pattern from each graph at the first reserved profile and three repetitions. The timer includes Python imports, input parsing, model loading, calculation, result storage, process exit, and coefficient checks. On '''+str(len(app['cases']))+r''' matched nontrivial batches, summed median time is '''+f"{app['totals']['native']:.3f}"+r''' seconds for native bounds, '''+f"{app['totals']['previous']:.3f}"+r''' seconds for the previous published application, and '''+f"{app['totals']['learned']:.3f}"+r''' seconds for the new model. This is '''+change(app['ratios']['native'])+r''' time than the fresh native-bound application and '''+change(app['ratios']['previous'])+r''' time than the previous application. The previous application retains its own validated portfolio and worker choices. Its comparison therefore measures the deployed workflow as a whole; the primary comparison above isolates the new learned choice.
'''
 write(REPORT/'learned_bounds_results.tex',fill(section))
 appendix=r'''\section{Learning seed bounds: inputs, objective, and timing definitions}
\label{app:learned-bounds}
\subsection{Integral definitions and target batches}
The new study uses the family definition of Eq.~\eqref{eq:family}. The sunrise, planar double box, three-loop vacuum, and massive three-loop two-point ladder retain the ordered denominator momenta in Appendix~\ref{app:families}, with the masses and kinematic assignments in Eq.~\eqref{eq:adaptive-kinematics}. The nonplanar box, pentagon, and external-virtuality box use that equation's corresponding assignments and the denominator definitions in the same appendix. The three- and four-loop boxes with bubbles use Eq.~\eqref{eq:higher-bubble-box}. The four-loop massless two-point family uses $D_i=\ell_i^2$ for $i=1,\ldots,4$ and $D_5=(p-\ell_1-\ell_2-\ell_3-\ell_4)^2$, with $p^2=-2h-29$. Auxiliary squared momentum differences complete its scalar-product coordinates as in Appendix~\ref{app:coverage}. The training profiles are $h=511,512$, validation uses $h=513$, and the reserved test uses $h=515,516$. Development uses $h=501$ and supplies no reserved labels.

Write $n$ for the number of physical denominators, $N$ for the total number of family entries, and $\boldsymbol a^{(0)}=(1,\ldots,1,0,\ldots,0)$ with $n$ leading ones. For $j=0,1,2$, define $i_j=1+[(h+j)\bmod n]$ and $i_j^+=1+(i_j\bmod n)$. When $N>n$, define $k_j=n+1+[(h+j)\bmod(N-n)]$. The first seven structures use four target patterns:
\begin{align}
\boldsymbol a^{\rm dots}_j&=\boldsymbol a^{(0)}+2\boldsymbol e_{i_j},&
\boldsymbol a^{\rm pinch}_j&=\boldsymbol a^{(0)}-\boldsymbol e_{i_j}+\boldsymbol e_{i_j^+},\nonumber\\
\boldsymbol a^{\rm mixed}_j&=\boldsymbol a^{(0)}+\boldsymbol e_{i_j}-\boldsymbol e_{k_j},&
\boldsymbol a^{\rm rank2}_j&=\boldsymbol a^{(0)}-2\boldsymbol e_{k_j}.
\label{eq:bounds-targets}
\end{align}
Here $\boldsymbol e_i$ is the unit index vector. For families without auxiliary entries, the last two patterns become $\boldsymbol a^{(0)}+\boldsymbol e_{i_j}+\boldsymbol e_{i_j^+}$ and $\boldsymbol a^{\rm dots}_j$. The remaining three structures use the corner, $\boldsymbol a^{(0)}+\boldsymbol e_{i_j}$, and $\boldsymbol a^{(0)}-\boldsymbol e_{k_j}$. Repeated vectors within a batch appear once. These equations define the requested integrals directly, with no assumed optimal reduction path.

\subsection{The ten candidate configurations}
Let $(r_0,s_0,d_0)$ be the target maxima in Eq.~\eqref{eq:adaptive-bounds}, and let $t_{\rm top}$ be the largest number of positive indices in a declared top sector. Table~\ref{tab:bounds-actions} specifies the ten candidates as changes to these maxima. Negative bounds become zero, and the positive-index bound is at least $t_{\rm top}$. The word ``native'' in the table denotes the unshifted target-bound configuration.
\begin{table}[!htbp]\centering\small
\caption{Candidate seed settings. A dash means that the lower sector truncation is disabled.}
\label{tab:bounds-actions}
\begin{tabular}{@{}lrrrr@{}}\toprule
Choice & $\Delta r$ & $\Delta s$ & $\Delta d_0$ & $l$\\\midrule
Native bounds &0&0&0&---\\
Numerator expansion &0&1&0&---\\
Tight bounds &$-1$&$-1$&$-1$&---\\
Reduced dots &$-1$&0&$-1$&---\\
Reduced numerator rank &0&$-1$&0&---\\
Full expansion &1&1&1&---\\
Truncated native &0&0&0&$t_{\rm top}-s_0$\\
Truncated numerator expansion &0&1&0&$t_{\rm top}-s_0$\\
Truncated reduced dots &$-1$&0&$-1$&$t_{\rm top}-s_0$\\
Relaxed truncation &0&0&0&$t_{\rm top}-s_0-1$\\
\bottomrule\end{tabular}
\end{table}
Kira's lower sector restriction has the form~\cite{Kira3}
\begin{equation}
 s\leq\max\{1,t-l+1,s_{\max,\mathrm{sector}}\},
\label{eq:bounds-truncate}
\end{equation}
where $t$ is the number of positive indices in that sector, $l$ is the chosen truncation parameter, and $s_{\max,\mathrm{sector}}$ is an explicitly assigned sector limit. This bound supplements the candidate seed limits. Every unsuccessful candidate is followed by native bounds and full expansion, with repeated effective bound-and-truncation pairs removed. All attempts use integral ordering 1 and one worker.

\subsection{Features and fitted objective}
The first eighteen features are those defined in Appendix~\ref{app:adaptive}. The remaining nine are the minimum dots and numerator rank, mean number of positive indices, largest absolute index, mean dots on massive entries, mean numerator-weighted loop incidence, mean dot-weighted loop incidence, maximum sum of positive indices, and maximum number of absent physical denominators. All means run over the target batch. If $B_{i\ell}=1$ when loop momentum $\ell$ appears in denominator momentum $q_i$ and zero otherwise, the two weighted incidence quantities are
\begin{equation}
 \frac1{|\mathcal T|}\sum_{\boldsymbol a\in\mathcal T}\sum_i\max(-a_i,0)\sum_\ell B_{i\ell},
 \qquad
 \frac1{|\mathcal T|}\sum_{\boldsymbol a\in\mathcal T}\sum_i\max(a_i-1,0)\sum_\ell B_{i\ell}.
\label{eq:bounds-incidence}
\end{equation}
These definitions describe index structure; they do not encode a target's reference reduction or measured runtime.

For a training case $c$ and candidate $a$, let $T_{ca}>0$ be its measured time with recovery, and let $a=0$ denote native bounds. We fit $y_{ca}=\log(T_{ca}/T_{c0})$. Subtracting two such labels gives
\begin{equation}
 y_{ca}-y_{cb}=\log T_{ca}-\log T_{cb}=\log(T_{ca}/T_{cb}).
\end{equation}
The logarithm is increasing, so minimizing the exact label selects the least measured time for that case. This statement concerns the labels; prediction error can change the selected configuration. The tree models fit weighted squared errors with $w_c=\sqrt{T_{c0}/\operatorname{median}_{c'}T_{c'0}}$. The twelve single trees have maximum depths $2,3,5,8$ and minimum leaf sizes $1,2,4$. Six ensembles combine random forests or extremely randomized trees with depths $3,5,8$, 48 trees, and minimum leaf size two~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}.

The twelve neural candidates use hidden widths $(16)$, $(32)$, or $(32,16)$, a rectified-linear or hyperbolic-tangent activation, and regularization parameter $0.01$ or $0.1$. They standardize features using training means and standard deviations, fit unweighted squared errors with a squared-weight penalty, and use L-BFGS with a 1,500-iteration limit~\cite{Pedregosa2011Bounds}. Their hidden states satisfy $\boldsymbol h^{(j+1)}=\sigma(W_j^\mathsf{T}\boldsymbol h^{(j)}+\boldsymbol b_j)$, while the output layer is linear. This equation defines the implemented network. Validation compares actual candidate costs, so differences between the fitting objectives do not determine the final choice by themselves. Every stochastic fit uses random seed 41.

Let $b_H$ be the fixed candidate with the smallest summed training-plus-validation time for graph $H$, and let $a_\star=\arg\min_a f_a(\boldsymbol x_c)$ be the predicted best candidate. A model with gate $g$ uses $a_\star$ when
\begin{equation}
 f_{a_\star}(\boldsymbol x_c)<f_{b_H}(\boldsymbol x_c)-g,
 \qquad g\in\{0,0.03,0.10,0.20\},
\label{eq:bounds-gate}
\end{equation}
and otherwise uses $b_H$. Under exact labels, this inequality becomes $T_{ca_\star}/T_{cb_H}<e^{-g}$ by exponentiation. With fitted labels it expresses a predicted saving. Validation selects the model and gate with the lowest sum of recorded configuration times. No reserved result enters that choice. The saved evaluator is checked against the training library for every validation prediction before the model is frozen.

\subsection{Measured ratios, uncertainty, and training cost}
Let $\widetilde T_{cm}$ be the median of five complete times for case $c$ and method $m$. For a matched set $\mathcal C$, define
\begin{equation}
 Q_m=\sum_{c\in\mathcal C}\widetilde T_{cm},\qquad
 R_b=Q_{\rm ML}/Q_b,\qquad S_b=1/R_b.
\label{eq:bounds-times}
\end{equation}
Summing accounts for the time required by the same batch collection; division gives its relative time, and inversion gives its speedup factor. The percentage time saving is $100(1-R_b)$. Matched cases must complete all methods and repetitions with a nontrivial reduction. We also retain the total elapsed time and completion counts for every timed request, including failures and identity-only outputs.

For the graph interval, we sample the observed graph groups with replacement and recompute $R_b$, preserving each selected graph's complete batch block. For the repetition interval, each batch samples five paired repetition positions with replacement and recomputes its medians and then $R_b$. Both calculations use 5,000 draws and report the 2.5th and 97.5th percentiles. These are descriptive resampling intervals for the specified collection. The graph count is small, and repeated index patterns remain correlated within a graph.

Let $T_{\rm off}$ be the recorded development, training, validation, and associated reference cost, including fitting. If the future mean saving equals the estimate from the matched workload $\Delta_b=(Q_b-Q_{\rm ML})/|\mathcal C|>0$, then $N$ requests recover this cost when $N\Delta_b\geq T_{\rm off}$. Solving this inequality gives
\begin{equation}
 N_{\rm break}=\left\lceil T_{\rm off}/\Delta_b\right\rceil.
\end{equation}
This calculation excludes reserved-test expense and assumes that an appropriate master basis is already available. It states the cost of collecting the model's evidence as well as its application saving. It does not prove that future workloads will have the same mean saving.
'''
 write(REPORT/'learned_bounds_appendix.tex',appendix)
 summary=fill(r'The new seed-bound study in Section~\ref{sec:learned-bounds} isolates a learned choice with all earlier models disabled. On @COUNT@ matched nontrivial batches, complete application time changes from @NATIVE@ seconds under native bounds and @FIXED@ seconds under tuned fixed settings to @LEARNED@ seconds with the new model. This gives @NATIVECHANGE@ time than native bounds and @FIXEDCHANGE@ time than the tuned fixed control. The comparison includes model loading, native IBP generation, exact reduction, coefficient checks, and recovery, with a supplied basis. It uses known structures at one through four loops and separate rational profiles; the additional saving over tuned fixed settings remains within timing variation.')
 p=REPORT/'report.tex';s=p.read_text()
 if '\\input{learned_bounds_results}' not in s:s=s.replace('\\input{coverage_results}','\\input{coverage_results}\n\\input{learned_bounds_results}')
 if '\\input{learned_bounds_appendix}' not in s:s=s.replace('\\input{coverage_appendix}','\\input{coverage_appendix}\n\\input{learned_bounds_appendix}')
 marker='% BEGIN LEARNED BOUNDS SUMMARY\n'+summary+'\n% END LEARNED BOUNDS SUMMARY\n'
 s=re.sub(r'% BEGIN LEARNED BOUNDS SUMMARY\n.*?% END LEARNED BOUNDS SUMMARY\n','',s,flags=re.S)
 s=s.replace('\\subsection{What the model comparisons establish}\n','\\subsection{What the model comparisons establish}\n'+marker)
 s=s.replace('\\section{Conclusion}\n','\\section{Conclusion}\n'+marker+'\n')
 s=re.sub(r'% BEGIN LEARNED BOUNDS TABLE\n.*?% END LEARNED BOUNDS TABLE\n','',s,flags=re.S)
 row=fill(r'Learned seed bounds & @COUNT@ matched batches; loops 1--4 & @NATIVECHANGE@ time than native bounds; @FIXEDCHANGE@ than tuned fixed settings\\')
 s=s.replace('% BEGIN FINAL PORTFOLIO SUMMARY','% BEGIN LEARNED BOUNDS TABLE\n'+row+'\n% END LEARNED BOUNDS TABLE\n% BEGIN FINAL PORTFOLIO SUMMARY',1)
 s=s.replace('New cost model & Known graph structures','Earlier cost model & Known graph structures').replace('Validated policy & Same targets','Earlier gated policy & Same targets')

 abstract=fill(r'Integration-by-parts reduction expresses Feynman integrals in a master basis, but the equations generated for that reduction can cost much more than the equations needed in the final answer. We train a model to select Kira seed bounds before equation generation, using complete reduction times as labels. A comparison of 30 tree and neural models selects @MODEL@ on separate validation inputs. On @COUNT@ matched nontrivial test batches at one through four loops, the fitted choice takes @NATIVECHANGE@ time than a control with native bounds and @FIXEDCHANGE@ time than graph-specific fixed settings chosen from the same candidates. All earlier learned selectors are disabled in these controls. The timings include parameter loading, prediction, native equation generation, exact algebra, checks, and recovery in a supplied master basis. Earlier exact implementation changes separately give 88.2\% less full reduction time than the saved original executable on 37 matched requests, including basis discovery. The wider coverage study retains its failed and unsupported cases. Learned row elimination remains omitted. The gain over tuned fixed settings is within timing variation; the broader twelve-loop results retain their stated physical limits.')
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _: '\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,count=1,flags=re.S)
 s=s.replace('The final method chooses among complete reduction strategies and measures its added benefit against fixed settings for each graph.','The final comparison trains a new model for seed bounds and measures its benefit against fixed settings for each graph, with all earlier learned selectors disabled.')
 s=s.replace('We have trained and tested models for decisions that affect exact Feynman integral reduction with Kira. The retained method chooses seeds and complete strategies before equation generation, uses equation selection in its validated domains, and keeps native row elimination. Its complete-time comparisons include prediction, exact algebra, checks, and recovery.','We have trained and tested models for decisions that affect exact Feynman integral reduction with Kira. The new seed-bound method chooses its configuration before equation generation and keeps native equation and row selection. Earlier local models and complete-strategy models retain their separate measured results. The new comparison of complete reduction time includes parameter loading, prediction, exact algebra, checks, and recovery.')
 # Put the current tested model before the historical experiments.
 if d['intervals']['fixed']['graph_bootstrap'][1]<1 and '% LEARNED BOUNDS MAIN ORDER' not in s:
  a=s.index('\\section{Training data and experimental design}')
  b=s.index('\\section{Overall performance and physical scope}')
  history=s[a:b].replace('\\input{learned_bounds_results}\n','')
  s=s[:a]+'\\input{learned_bounds_results}\n\n'+s[b:]
  s=s.replace('\\appendix\n','\\appendix\n% LEARNED BOUNDS MAIN ORDER\n'+history+'\n',1)
  s=s.replace('We first define the notation used in this paper and explain the reduction procedure. We then describe the training data and comparison rules before presenting the three local models and the models that select complete strategies. The final comparison trains a new model for seed bounds and measures its benefit against fixed settings for each graph, with all earlier learned selectors disabled. Separate controls measure the exact preprocessing improvements. The final sections bring the results together and state their physical scope. The appendices provide the integral definitions, model specifications, derivations, and conditions needed to reproduce each comparison.','We first define the notation used in this paper and explain the reduction procedure. We then present the new model for seed bounds, its training data, and its comparison of complete reduction time with controls that disable all learned choices. The overall results distinguish this learned gain from the earlier exact implementation changes and state their physical scope. The appendices retain the earlier local-model experiments, wider coverage tests, integral definitions, model specifications, and derivations.')
 if '\\usepackage{alphalph}' not in s:s=s.replace('\\usepackage{hyperref}','\\usepackage{alphalph}\n\\usepackage{hyperref}',1)
 if '\\AlphAlph{\\value{section}}' not in s:
  s=s.replace('\\appendix\n','\\appendix\n\\renewcommand{\\thesection}{\\AlphAlph{\\value{section}}}\n\\renewcommand{\\theHsection}{appendix.\\arabic{section}}\n',1)
 write(p,s)
 p=REPORT/'notes.tex';s=p.read_text();keep_equations='\\input{equation_refinement_results}' in s
 s=re.sub(r'% BEGIN CURRENT WORKFLOW UPDATE\n% LEARNED BOUNDS CURRENT\n.*?% END CURRENT WORKFLOW UPDATE\n','',s,flags=re.S)
 block='% BEGIN CURRENT WORKFLOW UPDATE\n% LEARNED BOUNDS CURRENT\n\\input{learned_bounds_results}\n'+('\\input{equation_refinement_results}\n' if keep_equations else '')+summary+'\n% END CURRENT WORKFLOW UPDATE\n'
 s=s.replace('\\clearpage\n\\renewcommand{\\refname}{Citations}',block+'\\clearpage\n\\renewcommand{\\refname}{Citations}')
 if '\\input{learned_bounds_appendix}' not in s:s=s.replace('\\input{coverage_appendix}','\\input{coverage_appendix}\n\\input{learned_bounds_appendix}')
 write(p,s)
 # Extend only the paper bibliography and the separately mutable notes supplement.
 bib=r'''@misc{TubeSeeding2026,
 author={Berman, Justin and Charton, Francois and Luna, Andres and Wilhelm, Matthias and Zeng, Mao},
 title={Efficient AI-Inspired Reduction of Feynman Integrals via Tube Seeding},
 year={2026}, eprint={2606.10698}, archivePrefix={arXiv}, primaryClass={hep-ph},
 note={\href{https://arxiv.org/abs/2606.10698}{arXiv:2606.10698}}
}
@article{Pedregosa2011Bounds,
 author={Pedregosa, Fabian and Varoquaux, Gael and Gramfort, Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel, Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss, Ron and Dubourg, Vincent and Vanderplas, Jake and Passos, Alexandre and Cournapeau, David and Brucher, Matthieu and Perrot, Matthieu and Duchesnay, Edouard},
 title={Scikit-learn: Machine Learning in Python}, journal={Journal of Machine Learning Research},
 volume={12}, pages={2825--2830}, year={2011},
 note={\href{https://jmlr.org/papers/v12/pedregosa11a.html}{Journal article}}
}'''
 for name in ['paper_references.bib','type_specialist_references.bib']:
  p=REPORT/name;s=p.read_text()
  if '@misc{TubeSeeding2026,' not in s:write(p,s+'\n'+bib)
 # The shared section also cites the seed-search paper in the archived notes.
 # Extend their mutable bibliography without changing the preserved original.
 p=REPORT/'type_specialist_references.bib';s=p.read_text()
 if not re.search(r'@\w+\{Song2025,',s):
  entry=re.search(r'(?ms)^@\w+\{Song2025,.*?(?=^@|\Z)',(REPORT/'paper_references.bib').read_text())
  assert entry is not None
  write(p,s+'\n'+entry.group(0))
 p=REPORT/'Makefile';s=p.read_text()
 if 'learned_bounds_results.tex' not in s:s=s.replace('report.pdf: report.tex','report.pdf: learned_bounds_results.tex learned_bounds_appendix.tex report.tex')
 write(p,s)
 p=REPORT/'s01_check_paper.py';s=p.read_text()
 if "'learned_bounds_results.tex'" not in s:s=s.replace("'coverage_results.tex','coverage_appendix.tex']","'coverage_results.tex','coverage_appendix.tex','learned_bounds_results.tex','learned_bounds_appendix.tex']")
 write(p,s)
 print('Learned-bound report sections written',flush=True)
if __name__=='__main__':main()
