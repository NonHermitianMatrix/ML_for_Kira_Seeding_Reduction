"""Write measured results and physical input definitions from the frozen records."""
from s00_reconstruction_common import *
from s10_cases import cases
import re

def save(p,s):p.write_text(s.strip()+'\n')
def interval(v):return rf"$[{v['interval'][0]:.3f},{v['interval'][1]:.3f}]$"
def pairs(v):return f"{v['old_completed']}/{v['new_completed']}"

def inputs():
 p=read(HERE/'test_protocol.json.gz')
 native=[c for c in p['cases'] if c['test_group']=='native']
 text=r"""
\section{Native reconstruction inputs}
\label{app:reconstruction-inputs}
The planar and nonplanar boxes use Eqs.~\eqref{eq:planar-input} and \eqref{eq:nonplanar-input}, respectively. The high-rank targets are $(1,1,1,1,1,1,1,-u,-v)$ with $u,v\geq0$ and $1\leq u+v\leq4$. Each graph contributes fourteen training, six validation, and six reserved high-rank batches. The complete target sets differ between splits and exclude the preceding comparison batches. Individual target vectors can occur in more than one batch.

For batch index $i=0,\ldots,25$, define $j=i\bmod6$ and $q=\lfloor i/6\rfloor$. Let
\begin{align}
 (A_0,\ldots,A_5)&=(3,13,103,1009,10007,100003),\nonumber\\
 (B_0,\ldots,B_5)&=(7,19,107,1013,10009,100019).
 \label{eq:reconstruction-scales}
\end{align}
We set $s=-(A_j+2q)$ and $t=-(B_j+4q)$ in both graphs, using each graph's scalar-product convention. Indices $0$--$13$ train the model, $14$--$19$ select it, and $20$--$25$ test it. These equations define the chosen input points. In the planar graph the fourth momentum is $-p_1-p_2-p_3$, and in the nonplanar graph it is $p_1+p_2-p_3$. Expanding their squares with the listed scalar products gives zero in both cases. The test batches are specified in Table~\ref{tab:reconstruction-batches}.
\begin{table}[!htbp]\centering\small
\caption{Reserved high-rank target batches. The same $(u,v)$ sets and invariants enter both box routings. Every row defines a complete request for each graph.}
\label{tab:reconstruction-batches}
\begin{tabularx}{\linewidth}{@{}rrrY@{}}\toprule
$i$ & $s$ & $t$ & Numerator powers $(u,v)$\\\midrule
"""
 for c in native:
  if c['topology_group']!='double_box' or c['shape']!='rank2':continue
  i=int(c['id'].rsplit('_',1)[1]);d=c['definition']['parameters']
  terms=', '.join(f'({-a[-2]},{-a[-1]})' for a in c['targets'])
  text+=f"{i} & {d['s']} & {d['t']} & ${terms}$ \\\\\n"
 text+=r"""\bottomrule\end{tabularx}\end{table}

For the lower-rank box requests, the sector corner is $(1,1,1,1,1,1,1,0,0)$. A numerator request uses the supplied first-rank auxiliary targets, and a raised-power request increases one physical index. Table~\ref{tab:reconstruction-low-targets} lists their precise target vectors. Their profiles are $h=27701,27713$ for training, $27733$ for validation, and $27739$ for testing, with the low-rank kinematics of Appendix~\ref{app:families-new}.

The sunrise family has loop momenta $(\ell_1,\ell_2)$ and one external momentum $p$. Its inverse-propagator momenta and squared masses are
\begin{equation}
 (Q_1,\ldots,Q_5)=(\ell_1,\ell_2,p-\ell_1-\ell_2,p-\ell_1,p-\ell_2),
 \qquad (m_1^2,\ldots,m_5^2)=(3,7,13,0,0).
 \label{eq:reconstruction-sunrise}
\end{equation}
The first three coordinates are physical denominators and the last two are auxiliary. The three-loop vacuum uses
\begin{align}
 (Q_1,\ldots,Q_6)&=(\ell_1,\ell_2,\ell_3,\ell_1-\ell_2,\ell_2-\ell_3,\ell_1-\ell_3),\nonumber\\
 (m_1^2,\ldots,m_6^2)&=(1,1,1,13,13,2h+53).
 \label{eq:reconstruction-vacuum}
\end{align}
All six coordinates are physical. Both structures use the same profile split as the low-rank boxes. For the sunrise, $p^2=-1009-12h$. These assignments specify test families, rather than universal relations between masses and invariants. In every native request the kinematic quantities are fixed rational numbers and $d$ remains symbolic, so the coefficients belong to $\Q(d)$. This test does not reconstruct general symbolic scattering invariants.

\begin{table}[!htbp]\centering\small
\caption{Lower-rank reserved targets. Training and validation use the same index patterns at different physical points. A corner request contains the all-unit physical sector.}
\label{tab:reconstruction-low-targets}
\begin{tabularx}{\linewidth}{@{}lY@{}}\toprule
Structure and request & Target indices\\\midrule
"""
 for c in native:
  if c['shape']=='rank2':continue
  name={'double_box':'Planar box','nonplanar_box':'Nonplanar box','sunrise':'Sunrise','vacuum3':'Vacuum'}[c['topology_group']]
  shape={'dot':'raised power','corner':'corner','numerator':'numerator'}[c['shape']]
  vectors=', '.join('('+','.join(map(str,t))+')' for t in c['targets'])
  text+=name+', '+shape+' & $'+vectors+r'$ \\'+'\n'
 text+=r"""\bottomrule\end{tabularx}\end{table}

The protected native bases consist of the integral indices below. Each listed vector $\boldsymbol b$ denotes $M_{\boldsymbol b}=I_{\boldsymbol b}$ in its corresponding family. The independently prepared symbolic and reconstructed calculations use the same basis for each request. The lists specify the comparison basis; they do not assert a proof of global master independence from a finite seed system.
"""
 bases={}
 for c in native:
  r=read(HERE/'model_test'/(c['id']+'.json.gz'))['results']['previous']
  attempts=[a for b in r.get('blocks',[]) for a in b['result'].get('attempts',[]) if a.get('success')]
  assert attempts and attempts[-1].get('prescribed_basis') is not None,c['id']
  basis=tuple(sorted(map(tuple,attempts[-1]['prescribed_basis'])))
  bases.setdefault(c['topology_group'],set()).add(basis)
 for kind,variants in bases.items():
  name={'double_box':'Planar box','nonplanar_box':'Nonplanar box','sunrise':'Sunrise','vacuum3':'Three-loop vacuum'}[kind]
  for j,basis in enumerate(sorted(variants)):
   text+='\n'+name+(f', basis {j+1}' if len(variants)>1 else '')+r":\[\begin{aligned}\{&"
   for i in range(0,len(basis),2):
    if i:text+=r',\\&'
    text+=','.join('('+','.join(map(str,b))+')' for b in basis[i:i+2])
   text+=r"\}.\end{aligned}\]"+'\n'
 text+=r"""

\section{Coefficient reconstruction}
\label{app:reconstruction-algebra}
Kira and FireFly provide the finite-field algorithms used here~\cite{Kira2,FireFly2019,FireFly2020}. To explain the relation to an exact rational coefficient, suppose
\begin{equation}
 r(d)=P(d)/Q(d),\qquad
 P(d)=\sum_{j=0}^{n}p_jd^j,\quad Q(d)=\sum_{j=0}^{m}q_jd^j.
 \label{eq:reconstruction-rational}
\end{equation}
One nonzero denominator coefficient fixes the overall normalization. At a nonsingular point $d=z$ modulo a prime, a numerical reduction returns $r(z)$. Multiplying by the denominator gives the linear constraint
\begin{equation}
 \sum_{j=0}^{n}p_jz^j-r(z)\sum_{j=0}^{m}q_jz^j=0\pmod p.
 \label{eq:reconstruction-sample}
\end{equation}
This follows directly from Eq.~\eqref{eq:reconstruction-rational}. With correct degree bounds and sufficiently many independent nonsingular samples, the constraints determine the normalized coefficients over the field. Combining suitable primes and reconstructing rational numbers then supplies rational coefficients~\cite{FireFly2019,FireFly2020}. FireFly determines the necessary information adaptively; our model chooses the native procedure and probe batch size.

The field operations are exact, while reconstruction termination relies on its degree discovery and checks. Our evaluation therefore also subtracts every reconstructed coefficient from a separately computed symbolic reference and requires the rational difference to vanish. This checks the actual tested answer. Neither a model score nor a successful reduction to the supplied basis alone proves every coefficient for an arbitrary unseen request.
"""
 return text

def main():
 s=read(HERE/'summary.json');t=read(HERE/'training_summary.json');p=read(HERE/'trained_model/policy.json');retained=read(HERE/'retained_summary.json');assert retained['complete']
 assert s['complete'];out=ROOT/'report'
 v=s['all'];cum=s['cumulative'];native=s['native'];ml=s['new_ml']
 text=r"""\section{Measured results}
\label{sec:results}
The following results come from the frozen comparison defined in Section~\ref{sec:design}. Table~\ref{tab:reconstruction-times} gives completion and elapsed time by physical structure. Each time is a sum of per-request medians on the same completed inputs for both methods.
\begin{table}[!htbp]\centering\small
\caption{Current application versus the preceding application with direct vacuum formulas. Done gives preceding/integrated completions; paired gives the number completed by both.}
\label{tab:reconstruction-times}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Domain & Done & Paired & Preceding (s) & Integrated (s)\\\midrule
"""
 names={'vacuum_products':'Vacuum products, 1--13 loops','connected_vacuum':'Connected trees, 1--13 loops','lightlike':'Zero-invariant tensors','ordinary_tensor':'Ordinary one-loop tensors'}
 for g,z in s['groups'].items():
  if g=='native':continue
  text+=f"{names.get(g,g.replace('_',' '))} & {pairs(z)} & {z['matched_completed']} & {z['old_seconds']:.3f} & {z['new_seconds']:.3f} \\\\\n"
 for g,z in s['native_structures'].items():
  name={'double_box':'Two-loop planar boxes','nonplanar_box':'Two-loop nonplanar boxes','sunrise':'Two-loop massive sunrise','vacuum3':'Three-loop massive vacuum'}[g]
  text+=f"{name} & {pairs(z)} & {z['matched_completed']} & {z['old_seconds']:.3f} & {z['new_seconds']:.3f} \\\\\n"
 text+=f"All {v['requests']} requests & {pairs(v)} & {v['matched_completed']} & {v['old_seconds']:.3f} & {v['new_seconds']:.3f} \\\\\n"
 text+=r"\bottomrule\end{tabularx}\end{table}"+'\n\n'
 text+=f"The integrated-to-preceding ratio is {v['ratio']:.3f}, with central 95\\% request-resampling interval {interval(v)}. Its point estimate corresponds to {100*(1-v['ratio']):.1f}\\% less time. The integrated application is slower on {v['slower']} matched requests. These are complete application times, so the reduction includes the cost of loading and choosing the method.\n\n"
 text+=r"\subsection{Native algebra and learned selection}"+'\n'
 text+=f"The {native['matched_completed']} matched native requests change from {native['old_seconds']:.3f} to {native['new_seconds']:.3f} seconds, a ratio of {native['ratio']:.3f} with interval {interval(native)}. The selected finite-field reconstruction is an established Kira capability. Its effect must be separated from the model that selects its settings.\n\n"
 best=t['best_validation'];fixed=t['fixed_validation']
 text+=f"Training uses {t['training']} verified requests and validation uses {t['validation']}. Validation selects maximum tree depth {best['depth']}, minimum leaf population {best['min_leaf']}, and saving margin {best['margin']:.2f}. The selected model gives {best['seconds']:.3f} seconds of validation cost, compared with {fixed['seconds']:.3f} seconds for the structure-dependent fixed control. "
 if s['model_enabled']:
  text+="This satisfies the deployment condition, so the integrated application uses the new model.\n\n"
 else:
  text+="This does not satisfy the deployment condition, so the integrated application uses the validated fixed settings. The fitted model and its measurements are preserved, and its weights are not loaded for production decisions.\n\n"
 text+=f"On the reserved native sample, the fixed application takes {ml['old_seconds']:.3f} seconds and the integrated application takes {ml['new_seconds']:.3f} seconds. Their ratio is {ml['ratio']:.3f}, with interval {interval(ml)}. "
 if s['model_enabled'] and ml['interval'][1]<1:
  text+=f"This comparison resolves an additional learned saving of {100*(1-ml['ratio']):.1f}\\% on this workload. "
 elif s['model_enabled']:
  text+="This comparison does not resolve a consistent additional learned saving. "
 else:
  text+="Both applications use the same selected settings, so their difference measures run-to-run variation and the shared entry procedure. It is not an added ML speedup. "
 text+=f"The final repetition changes {s['changed_actions']} of {len([r for r in s['rows'] if r['group']=='native'])} actions relative to the fixed control. The feature-range guard sends {s['choices'].get('previous',0)} requests to the preceding symbolic procedure. Median configuration-loading and decision time is {1000*s['median_loading_and_prediction_seconds']:.3f} milliseconds, including the first loading of the feature dependencies. This quantity is not pure forest evaluation time. The preceding seed model remains shared by both applications.\n\n"
 text+=r"""\begin{figure}[!htbp]\centering
\includegraphics[width=.97\linewidth]{paper_figures/reconstruction_native.pdf}
\caption{Native speed changes depend on the physical request. Each circle shows the integrated-to-preceding ratio for one completed request. Diamonds show ratios of summed median times within each structure, with paired request-resampling intervals. Values below one mean less elapsed time.}
\label{fig:reconstruction-native}
\end{figure}
\begin{figure}[!htbp]\centering
\includegraphics[width=.97\linewidth]{paper_figures/reconstruction_ml.pdf}
"""
 text+=r"\caption{"+("The additional model is compared with the same formulas and native implementation using validated fixed settings. The aggregate ratio separates this learned contribution from the standard reconstruction improvement." if s['model_enabled'] else "Separate validation determines whether the new model is used. The dashed threshold requires at least three percent less cost than the fixed setting selected for each structure. The current deployment retains the fixed settings because the model does not meet this condition.")+r"}"+"\n"+r"\label{fig:reconstruction-ml}"+"\n"+r"\end{figure}"+'\n\n'
 text+=r"\subsection{Cumulative change and exact reductions}"+'\n'
 text+=f"The matched comparison across the last two extensions changes from {cum['old_seconds']:.3f} to {cum['new_seconds']:.3f} seconds on {cum['matched_completed']} completed requests. Its ratio is {cum['ratio']:.3f}, with interval {interval(cum)}, or {100*(1-cum['ratio']):.1f}\\% less time at the point estimate. This result uses one input set and one timing procedure. It is a cumulative comparison with the earlier application, not with unmodified Kira, and it does not multiply percentages from older experiments.\n\n"
 text+=r"""The direct vacuum formulas and connected-tree recurrences remain active through thirteen loops. They provide rational master decompositions and explicit Gamma-function values in the domains derived in the appendices. The present analytic grid verifies their preservation while the new algebra method changes the native calculations. General coupled multiscale scattering through thirteen loops is outside this grid.
\begin{figure}[!htbp]\centering
\includegraphics[width=.97\linewidth]{paper_figures/reconstruction_components.pdf}
\caption{Cumulative elapsed time is measured on the same requests for all four applications. The second application adds direct vacuum formulas; the third adds validated fixed reconstruction settings; the fourth applies the admitted selection procedure. The bars do not combine unrelated historical speed factors.}
\label{fig:reconstruction-components}
\end{figure}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/reconstruction_exact.pdf}
\caption{The analytic stage covers each loop order from one through thirteen in its stated domains. The left panel shows independent vacuum factors. The right panel shows connected one-mass trees, with the median over available shapes and their full range. Logarithmic time axes show the small complete application times without hiding their variation.}
\label{fig:reconstruction-exact}
\end{figure}
\subsection{Completion and scope}
"""
 text+=f"The timed outputs receive {s['checks']:,} exact coefficient comparisons. The integrated application has {v['new_failed_applications']} unverified timed applications and {s['failed_native_attempts']['integrated']} recorded unsuccessful inner native attempts. It uses reconstruction recovery {s['reconstruction_fallbacks']['integrated']} times. Reference preparation fails for {len(s['reference_failures'])} final requests. Application failure counts include a terminated run even when it cannot return an inner-attempt record.\n\n"
 text+=r"""The current native test measures new kinematic points and complete target batches within four known structures at two and three loops. Higher-loop evidence comes from the derived product and tree identities. It does not establish performance for every high-loop graph, every symbolic kinematic system, or unrestricted numerator powers. The measured configuration also depends on the tested processor and resource bounds. A finite model and setting search does not prove globally minimum time.
"""
 z=retained['all']
 text+=r"\subsection{Retained ML in the reconstruction workflow}"+'\n'
 text+=f"The additional paired comparison holds the new algebra settings fixed and switches the inherited learned choices to their existing fixed procedure. On {z['matched_completed']} matched native requests, the fixed procedure takes {z['old_seconds']:.3f} seconds and the learned procedure takes {z['new_seconds']:.3f} seconds. Their ratio is {z['ratio']:.3f}, with interval {interval(z)}. "
 if z['interval'][1]<1:text+="This comparison resolves a saving from the inherited learned choices within the reconstruction workflow. "
 elif z['interval'][0]>1:text+="This comparison finds that the inherited learned choices increase elapsed time on this sample. "
 else:text+="This interval includes equal time, so the sample does not resolve a consistent additional learned saving. "
 text+=f"The recorded seed-attempt sequences differ on {retained['changed_seed_sequences']} requests. The learned and fixed procedures have {z['new_failed_applications']} and {z['old_failed_applications']} unverified applications, respectively. Across all three repetitions, their total times are {z['all_attempt_seconds']['retained_ml']:.3f} and {z['all_attempt_seconds']['retained_fixed']:.3f} seconds. The distinction between total repeated time and summed medians illustrates the timing variation. This ablation has its own paired timings; its ratio is not multiplied into the cumulative result.\n\n"
 text+=r"""\begin{table}[!htbp]\centering\small
\caption{Inherited learned choices versus their existing fixed procedure, with the new reconstruction settings shared. The columns use matched completed requests within each structure.}
\label{tab:reconstruction-retained}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Structure & Paired & Fixed (s) & Learned (s) & Ratio\\\midrule
"""
 for kind,row in retained['structures'].items():
  name={'double_box':'Planar box','nonplanar_box':'Nonplanar box','sunrise':'Massive sunrise','vacuum3':'Three-loop vacuum'}[kind]
  text+=f"{name} & {row['matched_completed']} & {row['old_seconds']:.3f} & {row['new_seconds']:.3f} & {row['ratio']:.3f} \\\\\n"
 text+=f"All native requests & {z['matched_completed']} & {z['old_seconds']:.3f} & {z['new_seconds']:.3f} & {z['ratio']:.3f} \\\\\n"
 text+=r"\bottomrule\end{tabularx}\end{table}"+'\n\n'
 old=(out/'direct_results.tex').read_text()
 start=old.index(r'\subsection{The other learned interventions}')
 end=old.index(r'\subsection{Scope of the result}',start)
 text+='\n'+old[start:end]+r"\FloatBarrier"+'\n'
 save(out/'reconstruction_results.tex',text)
 save(out/'reconstruction_appendix.tex',inputs())
 abstract=r"\begin{abstract}"+'\n'+f"We study the time required to express loop integrals in terms of master integrals. The method combines exact formulas and recurrences with Kira reduction and learned choices based on measured complete cost. Direct partial fractions and connected-tree formulas provide analytic values for specified vacuum families through thirteen loops. For remaining native reductions, we retain the seed policy and compare symbolic algebra with finite-field reconstruction. A frozen comparison contains 22 new native requests and 53 analytic regression requests. The integrated application completes {v['new_completed']} of {v['requests']} requests, and its summed median time changes from {v['old_seconds']:.3f} to {v['new_seconds']:.3f} seconds on {v['matched_completed']} matched completed inputs. The cumulative comparison across the two latest extensions gives {100*(1-cum['ratio']):.1f}\\% less time. "
 abstract+=("Separate validation enables the new algebra-cost model. Its reserved comparison with validated fixed settings gives a time ratio of "+f"{ml['ratio']:.3f}." if s['model_enabled'] else "Separate validation rejects the new algebra-cost model, so the retained method uses fixed reconstruction settings and the preceding seed model.")
 abstract+=" We omit learned row selection because the earlier controls did not establish a saving. Exact coefficient checks support the tested reductions, while general multiscale high-loop scattering remains outside the demonstrated scope.\n"+r"\end{abstract}"
 save(out/'paper_abstract.tex',abstract.replace('analytic regression requests','previously verified analytic requests'))
 conclusion=f"The integrated method reduces summed complete time by {100*(1-v['ratio']):.1f}\\% relative to the preceding application on {v['matched_completed']} matched requests. The matched cumulative comparison across the two extensions gives {100*(1-cum['ratio']):.1f}\\% less time. Exact partial fractions and recurrences handle the stated analytic families, and finite-field reconstruction reduces the remaining native algebra where the measured settings support it.\n\n"
 conclusion+=("The added cost model passes separate validation. Its reserved fixed-control comparison gives "+f"a ratio of {ml['ratio']:.3f} with interval {interval(ml)}. " if s['model_enabled'] else "The new cost model fails its deployment condition, so the production method retains the validated fixed reconstruction settings. ")
 conclusion+=f"The paired ablation of inherited learned choices gives a ratio of {z['ratio']:.3f} with interval {interval(z)}. Earlier equation-selection measurements remain separate, and learned row selection is omitted. This separation identifies which gains come from analytic identities, established algebra methods, and learned decisions.\n\nThe formulas apply under explicit mathematical conditions, and the tests cover selected structures through thirteen loops. New native inputs are restricted to the four stated two- and three-loop families with rational kinematics and symbolic dimension. These results support the reported reduction times within that domain; they do not establish a fastest method for all integrals."
 save(out/'paper_conclusion.tex',conclusion)
 save(out/'reconstruction_data.json',json.dumps(s,indent=2))
 save(out/'reconstruction_retained_data.json',json.dumps(retained,indent=2))
 print('Results and physical input appendix written',flush=True)
if __name__=='__main__':main()
