"""Document cost-aware training and the separately measured preparation change."""
from s00_common import *
from s14_prepare import P

def main():
 s=READ(P/'summary.json');tr=s['training'];comparisons=s['comparisons'];counts=s['counts'];report=ROOT/'report'
 names={'expanded':'Expanded discovery','cached_native':'Compact, no ML','cached_learned':'Compact, neural model','cached_risk':'Compact, cost and risk'}
 body=r'''\section{Reducing preparation failures}
\label{sec:preparation}
The shared-model result separates two costs that require different changes. Its supplied-basis calls complete, while some initial reference calculations or enlarged-region checks fail. We therefore change the preparation workflow and train a second model on individual successful and failed attempts. This comparison includes basis lookup or discovery, both exact reductions, prediction, recovery, and process exit.

The compact workflow first looks for previously checked master indices with the same ordered propagator structure and zero-mass pattern. It reuses these indices while recomputing all coefficients at the new kinematic values. Without a stored basis, it begins with a compact seed region and treats the resulting basis as provisional. A second reduction uses that basis and a different integral ordering, and its coefficients must agree exactly. Kira's supplied-basis check rejects additional masters~\cite{Kira3}. Agreement checks the requested reductions; it does not prove that the provisional basis has the globally smallest possible number of masters. Incomplete attempts expand the seed region, and duplicate attempts are removed.

The new model takes the same 44 structural quantities as the neural model, together with the three seed bounds, the truncation flag and level, the presence and size of a supplied basis, and the integral-ordering setting. Its 52 inputs predict log attempt time and a failure score. We fit random forests and extremely randomized forests~\cite{Breiman2001Forest,Geurts2006ExtraTrees} and select the action with the smallest sum of predicted time and a validation-selected failure penalty. Appendix~\ref{app:risk} defines the outputs and objective. The failure score ranks actions; it is not a calibrated probability.

'''
 body+=f"Training uses {tr['training_attempts']:,} earlier attempts, including {tr['failed_training_attempts']} failures, and {tr['validation_requests']} separate validation requests select the model. The selected random forest has 32 trees of maximum depth {tr['selection']['depth']} and uses a {tr['penalty_seconds']:.0f}-second failure penalty. Fitting and model selection take {tr['fitting_seconds']:.2f} seconds, excluding the earlier cost of collecting labels. Training includes the initial shared-model trial, but excludes the distinct-mass vacuum family, nonplanar boxes, pentagons, and loop orders six and above. The new physical profile supplies no fitting or selection labels.\n\n"
 body+=f"The reserved comparison contains {s['requests']} requests at one through seven loops, using the physical definitions in Appendix~\\ref{{app:families-new}} with profile $h=1237$. It compares expanded discovery and its enlarged-region check with three versions of the compact workflow: native bounds, the frozen neural model, and the cost-and-risk model. Each method receives the same 110-second request deadline and a 60-second cap per native call. Every first attempt is retained, and each initially successful method receives two further repetitions. All four methods use the same 128-bit integral-ordering labels, which Kira supports~\\cite{{Kira3}}; this setting changes the internal ordering representation rather than the exact coefficient arithmetic. The 31-coordinate interface limit remains.\n\n"
 body+=r'''\begin{table}[!htbp]\centering\small
\caption{Preparation outcomes over the full reserved set. The first-pass timer includes successful and unsuccessful requests. Failed-attempt time counts the unsuccessful native calls within that pass. These totals describe work performed; a shorter failed request is not a successful speedup.}
\label{tab:preparation-coverage}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Method & First complete & All 3 complete & First pass (s) & Failed calls (s)\\\midrule
'''
 for m in s['methods']:
  c=counts[m];body+=f"{names[m]} & {c['first_completed']}/{s['requests']} & {c['three_completed']}/{s['requests']} & {c['first_elapsed_seconds']:.1f} & {c['first_failed_seconds']:.1f}\\\\\n"
 body+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 body+=r'''\begin{table}[!htbp]\centering\small
\caption{Preparation completions by loop order. Each entry requires all three repetitions. The compact columns use the same reuse and checking procedure with the stated decision rule. These results are separate from the earlier supplied-basis coverage in Table~\ref{tab:general-coverage}.}
\label{tab:preparation-loops}
\begin{tabular}{@{}rrrrrr@{}}\toprule
Loops & Requests & Expanded & Compact native & Neural & Cost and risk\\\midrule
'''
 for loop,entry in s['by_loop'].items():
  requested=sum(r['loops']==int(loop) for r in s['rows'])
  body+=f"{loop} & {requested} & {entry['expanded']} & {entry['cached_native']} & {entry['cached_learned']} & {entry['cached_risk']}\\\\\n"
 body+=r'\bottomrule\end{tabular}\end{table}'+'\n\n'
 body+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete preparation time on matched requests. Every included method completes all three repeats in the same master-index basis with exact coefficient agreement. The compact/native comparison includes reuse and the changed check; the two ML comparisons isolate prediction within that workflow.}
\label{tab:preparation-times}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Comparison & Matched & Time ratio & Repeat interval\\\midrule
'''
 for key,label in [('cached_native/expanded','Compact without ML / expanded'),('cached_learned/cached_native','Neural model / compact without ML'),('cached_risk/cached_native','Cost and risk / compact without ML'),('cached_risk/cached_learned','Cost and risk / neural model')]:
  c=comparisons[key]
  if c['cases']:body+=f"{label} & {c['cases']} & {c['ratio']:.3f} & [{c['interval'][0]:.3f},{c['interval'][1]:.3f}]\\\\\n"
  else:body+=f"{label} & 0 & --- & ---\\\\\n"
 body+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 body+=f"The analysis performs {s['coefficient_checks']:,} coefficient comparisons across the repeated and competing outputs. The reused index cache contains {s['cached_structures']} earlier checked structures. Their retained discovery and check records cost {s['selected_cache_source_seconds']:.1f} seconds before this experiment; failed attempts during the earlier search add further cost. The compact timings therefore describe use of an existing cache, not cost-free master discovery. In the earlier supplied-basis experiment, {s['earlier_shared_attempts']} neural-model native attempts contain {s['earlier_shared_failed_attempts']} failures. This audit locates the larger failure cost in preparation.\n\n"
 body+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/preparation_results.pdf}
\caption{The preparation comparison keeps failed work and the added ML effect separate. The left panel includes failed calls from every first request. The right panel uses only exact matched completions and compares both models with the same compact workflow without ML. The dashed line marks equal time.}
\label{fig:preparation}
\end{figure}
\FloatBarrier
'''
 (report/'preparation_results.tex').write_text(body)
 appendix=r'''\section{Learning attempt cost and failure risk}
\label{app:risk}
For recorded attempt $i$, let $t_i$ be its elapsed time in seconds and $f_i$ be one if it fails and zero otherwise. We define the two regression targets as $u_i=\log\max(0.001,t_i)$ and $v_i=3f_i$. A tree leaf predicts the mean of each target; averaging the trees gives predictions $\widehat u$ and $\widehat v$~\cite{Breiman2001Forest}. The factor three gives the failure output more weight in the two-output squared-error split objective. For $n$ attempts, that objective is proportional to
\begin{equation}
 \sum_{i=1}^n\bigl[(\widehat u_i-u_i)^2+(\widehat v_i-3f_i)^2\bigr].
 \label{eq:risk-fit}
\end{equation}
To obtain the leaf means, differentiate each sum of squared residuals with respect to its constant leaf prediction. The derivatives are $2\sum_i(\widehat u-u_i)$ and $2\sum_i(\widehat v-3f_i)$; setting them to zero gives the two sample means. Equation~\eqref{eq:risk-fit} is the chosen fitting objective, without an assumption that every failure has the same physical cause.

The runtime score for candidate action $a$ is defined as
\begin{equation}
 C_a=\exp[\operatorname{clip}(\widehat u_a,-5,8)]
       +\lambda\operatorname{clip}(\widehat v_a/3,0,1).
 \label{eq:risk-score}
\end{equation}
Here $\operatorname{clip}(z,l,h)=\min(h,\max(l,z))$ and $\lambda$ has units of seconds. The exponential reverses the log-time target, and division by three reverses the failure-label scaling. Their sum defines a time-based ranking with a failure penalty; it is not a calibrated expected-time estimate. Without a supplied basis, candidate actions exclude the three settings that reduce dot or numerator bounds below the native target limits. All ten settings are available when a basis is supplied.

We compare 32-tree random and extremely randomized forests at depths four and six, with at least five training attempts per leaf~\cite{Breiman2001Forest,Geurts2006ExtraTrees}. Each candidate is evaluated with $\lambda\in\{0,20,60,120\}$ seconds. For each validation request, it chooses one recorded action. Model selection minimizes
\begin{equation}
 V=\frac{\sum_c T_{c,a(c)}+60\sum_c f_{c,a(c)}}{\sum_c T_{c,0}},
 \label{eq:risk-selection}
\end{equation}
where $T$ is the earlier complete action cost including its recovery, $f$ records failure of that action's first attempt, and action zero uses native bounds. Unsuccessful complete validation records receive a 180-second penalty. The denominator is independent of the candidate, so minimizing $V$ minimizes the penalized numerator. The extra 60 seconds deliberately emphasizes avoiding a failed first action even when recovery already contributes to $T$. The model, penalty, and basis cache are fixed before the reserved comparison.

The new grid contains one target shape per selected family and loop order: dotted targets at odd orders and mixed targets at even orders, as defined in Appendix~\ref{app:families-new}. The one-mass vacuum uses orders 1, 2, 4, 5, 6, 7; the distinct-mass vacuum uses 2, 4, 5, 6, 7; each two-point class uses 2 through 6; the ladder uses 1 through 5; and the box with bubbles uses 2 through 5. The nonplanar box, pentagon, and box with one virtual leg add three requests. The cache uses only the master indices from the earlier profile 1201. Stored coefficients never enter prediction or the new reduction. Its structure key distinguishes the ordered momenta and zero versus nonzero mass and invariant assignments. A matching key is only a proposed basis: the new exact calculations must establish target reduction at the new parameters.

Every initially successful method receives three measurements. A paired time ratio includes only requests that complete all three repeats for both methods, use the same master-index set, and agree coefficient by coefficient. Repetition and cross-method checks use exact rational simplification. Different provisional bases, incomplete repetitions, and failed requests remain in the outcome records without a matched ratio. This makes the time comparison conditional on equal completed work.
'''
 (report/'preparation_appendix.tex').write_text(appendix)
 # Idempotent integration; s10 writes the earlier conclusions first.
 paper=report/'report.tex';text=paper.read_text()
 text=text.replace('Every timing comparison uses identical targets, kinematics, and master bases','Every reported paired timing ratio uses identical targets, kinematics, and master bases')
 if '\\input{preparation_results}' not in text:text=text.replace('\\section{Overall interpretation}','\\input{preparation_results}\n\n\\section{Overall interpretation}')
 if '\\input{preparation_appendix}' not in text:text=text.replace('\\input{paper_derivations}','\\input{paper_derivations}\n\\input{preparation_appendix}')
 text=text.replace('The study has two related parts. First,','We first')
 text=text.replace('We first we identify','We first identify')
 preparation_intro='A final comparison trains on failed attempts and includes the preparation workflow. '
 text=text.replace(preparation_intro,'')
 text=text.replace('We first define the notation used in this paper, then explain the models and compare their results.',preparation_intro+'We first define the notation used in this paper, then explain the models and compare their results.')
 paper.write_text(text)
 notes=report/'notes.tex';text=notes.read_text()
 if '\\input{preparation_results}' not in text:text=text.replace('\\input{general_policy_initial_notes}','\\input{general_policy_initial_notes}\n\\input{notes_general_methods}\n\\input{preparation_results}\n\\input{preparation_appendix}')
 # Include the new shared-model and physical definitions in the notes as well.
 methods=(report/'paper_derivations.tex').read_text()
 methods=methods[methods.index('\\section{Shared structural model'):]
 methods=methods.replace('\\eqref{eq:integral}','\\eqref{history:eq:family}')
 (report/'notes_general_methods.tex').write_text(methods)
 if '\\renewcommand{\\thesection}{A\\arabic{section}}' not in text:
  text=text.replace('\\appendix\n','\\appendix\n\\renewcommand{\\thesection}{A\\arabic{section}}\n\\renewcommand{\\theHsection}{appendix.\\arabic{section}}\n')
 notes.write_text(text)
 make=report/'Makefile';text=make.read_text().replace('report.pdf: paper_abstract.tex','report.pdf: preparation_results.tex preparation_appendix.tex paper_abstract.tex');make.write_text(text)
 print('PREPARATION DOCUMENTED',s['requests'],flush=True)

if __name__=='__main__':main()
