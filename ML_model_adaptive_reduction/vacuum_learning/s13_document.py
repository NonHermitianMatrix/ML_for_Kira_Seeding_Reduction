"""Write the new exact derivation and separate native ML measurements."""
from s00_vac_common import *
REPORT=ROOT/'report'

def main():
 from s12_analyze import compare
 s=read(HERE/'summary.json');v=s['groups']['vacuum'];ml=s['ml'];nat=s['groups']['native'];model=read(HERE/'trained_model/policy.json');dev=read(HERE/'development.json')
 audit={}
 matched=[r for r in s['rows'] if r['group']=='native' and all(r['success']['integrated']) and all(r['success']['all_fixed'])]
 for method in ['integrated','all_fixed']:
  attempts=[];prediction=[]
  for row in matched:
   result=read(HERE/'results'/(row['case']+'.json.gz'))['results'][method]
   for block in result.get('blocks',[]):
    b=block['result'];attempts.extend(b.get('attempts',[]))
    if b.get('batch_model_used'):prediction.append(b['batch_prediction_seconds'])
  audit[method]=dict(requests=len(matched),attempts=len(attempts),unsuccessful_attempts=sum(not a.get('success',False) for a in attempts),generated_equation_instances=sum(sum(a.get('counters',{}).get('generated_equations',[])) for a in attempts),median_recorded_prediction_seconds=statistics.median(prediction) if prediction else 0.)
 audit['scope']='Final repetition only, for native requests completed and independently verified by both learned and fixed methods in every repetition. Generated equation instances include regeneration.'
 write(HERE/'model_application_audit.json',audit);s['final_repetition_audit']=audit
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(8,3.15),constrained_layout=True)
 rr=[r for r in s['rows'] if r['group']=='vacuum']
 for method,label,col in [('integrated','Exact vacuum rule','#236b8e'),('previous','Previous completed requests','#a94432')]:
  xs=[];ys=[]
  for L in range(1,14):
   rows=[r for r in rr if r['loops']==L and all(r['success'][method])]
   if rows:xs.append(L);ys.append(statistics.mean(r['median_seconds'][method] for r in rows))
  axes[0].plot(xs,ys,'o-',color=col,label=label,markersize=4)
 axes[0].set(xlabel='Number of loops',ylabel='Complete application time (s)',yscale='log',title='Single-mass vacuum trees');axes[0].set_xticks([1,3,5,7,9,11,13]);axes[0].legend(frameon=False,fontsize=8)
 nr=[r for r in s['rows'] if r['group']=='native' and all(r['success']['integrated']) and all(r['success']['all_fixed'])]
 ratios=[r['median_seconds']['integrated']/r['median_seconds']['all_fixed'] for r in nr]
 ordered=sorted(zip(ratios,nr),key=lambda pair:pair[0])
 for kind,label,color in [('double_box','Planar','#236b8e'),('nonplanar_box','Nonplanar','#a94432')]:
  points=[(i+1,a) for i,(a,r) in enumerate(ordered) if kind in r['case']]
  axes[1].plot([x for x,y in points],[y for x,y in points],'o',markersize=4,color=color,label=label)
 axes[1].legend(frameon=False,fontsize=8)
 axes[1].axhline(1,color='0.45',linestyle='--');axes[1].set(xlabel='Reserved request, sorted by time ratio',ylabel='Learned time / fixed-choice time',title='Native ML gain varies by request',ylim=(max(0,min(.95,min(ratios)*.9)),max(1.05,max(ratios)*1.08)))
 for ax in axes:ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(axis='y',alpha=.2)
 fig.savefig(REPORT/'paper_figures/vacuum_learning.pdf');plt.close(fig)
 text=r'''\section{Exact massive vacuum reduction and retrained seed choices}
\label{sec:vac-ml}
The two-point reduction can also close when the tree ends at a massive vacuum line. We add this identity to cover connected vacuum integrals with one massive root denominator and massless bubble branches. Each branch changes the power of the root momentum, and a beta integral then evaluates the root. Appendix~\ref{app:vac-ml} defines the family and derives its rational coefficient relative to the unit-power master. This calculation uses the same subintegral principle as parametric massless reduction~\cite{Ruijl2017Forcer}, with the massive root derived explicitly here. The application checks the momenta, masses, and index powers before applying the identity, applies the rule within independent loop blocks when present, and retains the existing exact rules and Kira choices for other inputs.

For integrals that still require Kira, we train a new model to choose the sparse seed boundary before equation generation. Kira already supplies optimized seeding and equation selection~\cite{Kira3}; the learned decision chooses among three boundaries in the existing exact reduction interface. The wider and tighter boundaries come from the preceding implementation, and a third boundary gives an intermediate seed region. Appendix~\ref{app:vac-ml} derives the training objective. The seed-boundary parameters use the definition in Appendix~\ref{app:sparse}:
\begin{equation}
 \begin{split}
 \boldsymbol\theta_{\mathrm{wide}}&=(2.5,0,0,1.25,0,1,-0.25),\\
 \boldsymbol\theta_{\mathrm{tight}}&=(1,0,0,0,1,1,0),\\
 \boldsymbol\theta_{\mathrm{middle}}&=(1.5,0,0,0.5,0,1,0).
 \end{split}
 \label{eq:vac-ml-choices}
\end{equation}
These are specified candidate settings rather than physical identities. All candidates use the same protected master basis, native truncation setting, exact checks, and recovery mechanism.

The model uses 25 input features. They describe loop and external-momentum counts, propagator incidence, target count, numerator ranks, positive powers, and distances between target index vectors. The added features describe the minimum, maximum, and mean power of each of the two auxiliary denominators and the fraction of targets with zero power in each. No family name or known reduction coefficient enters the prediction. We collect complete timings for 32 training requests and 16 validation requests from planar and nonplanar massless two-loop boxes, whose propagators are defined in Appendix~\ref{app:families-new}. Their numerator ranks range from one to four, and all seven physical denominators have unit power. Each batch contains one to four targets. The sets of numerator-power pairs that define the batches are disjoint across training, validation, and the 32 reserved native requests; individual pairs can occur in different batches. Each split also uses different rational kinematics. These are new target batches within two known topology classes, so they do not establish transfer to unseen graph classes. The eligibility gate checks counts, masses, powers, and feature ranges; it does not certify that an arbitrary graph belongs to the training classes. Native basis checks and recovery retain responsibility for algebraic completion.

Candidate models contain one cost tree or an ensemble of 24 trees, using tree and bootstrap-ensemble methods~\cite{CART1984,Breiman2001Forest} with the time objective derived here. Each ensemble tree draws 32 training requests with replacement and considers a random set of 12 of the 25 features at each split. Leaves store the mean measured cost of each action, and the ensemble averages these costs. Validation compares depths one through four, minimum leaf sizes two, four, or eight, and predicted-saving margins of zero, three, eight, or fifteen percent. We enable the selected policy only if it changes at least one validation choice, adds no unverified result, and improves the fixed validation cost by at least one percent after the prediction allowance.

'''
 text+=f"Validation selects {model['selection']['count']} tree(s), maximum depth {model['selection']['depth']}, minimum leaf size {model['selection']['minimum']}, and predicted-saving margin {100*model['margin']:.0f}\\%. The fixed comparison uses the tighter boundary, which has the lowest total validation time. The learned policy is {'enabled' if model['enabled'] else 'disabled'} by the validation criterion. Its selected validation cost, including a two-millisecond prediction allowance per request, is {model['selection']['cost']:.3f} seconds, compared with {model['fixed_validation_seconds']:.3f} seconds for the fixed choice. These validation values select the policy and do not serve as its independent result.\n\n"
 text+=r'''We freeze the policy and implementation before testing. The exact test contains 34 distinct rooted vacuum structures, with seven targets each and a symbolic mass scale, covering every loop order from one through thirteen. Eight additional requests check the retained two-point and triangle rules. Each reserved request runs three times in fresh processes, with method order rotated and an eighteen-second application limit. The timer includes process loading, input, recognition, model loading and inference when used, native algebra and recovery, output, and exit. Direct analytic requests defer native and model imports until they are needed. Independent comparisons of returned coefficients run outside both timers. Native comparisons use the same previously verified master-index information; reference preparation is excluded equally. The previous-method comparison launches the preceding published application directly. We draw 2,000 resamples of matched requests with replacement, retain each request's paired medians, and take the 2.5 and 97.5 percentiles of the time ratios. These intervals describe variation within the finite request collection.

'''
 text+=f"The new rule completes {v['new_completed']} of {v['requests']} vacuum requests in every repetition, while the preceding application completes {v['old_completed']}. The reserved vacuum coefficients pass {s['gamma_checks']} independent Gamma evaluations at 80-digit precision, with scaled error below $10^{{-60}}$. The scaled error is the absolute difference divided by the larger of one and the reference magnitude. Separate development checks supply {sum(r['checks'] for r in dev['native'])} exact coefficient comparisons with native Kira.\n\n"
 text+=f"Before the reserved comparison, six transformation checks preserve the coefficients under loop renaming, common momentum-sign reversal, and physical-denominator reordering. Three product checks verify the integrated rule on independent vacuum blocks with four, eight, and thirteen total loops. These product checks establish composition of the supported identity and supply no separate timing claim.\n\n"
 text+=r'''\begin{table}[!htbp]\centering\small
\caption{Sums of three-run median complete times. Times use requests completed and verified by both methods. Completion counts retain all requests and require all repetitions to pass.}
\label{tab:vac-ml}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Comparison & Control/new complete & Paired & Control (s) & New (s)\\\midrule
'''
 for label,r in [('Vacuum trees versus previous',v),('Native application versus previous',nat),('Native model versus fixed',ml),('Two-point regression checks',s['groups']['propagator']),('Triangle regression checks',s['groups']['triangle'])]:
  text+=f"{label} & {r['old_completed']}/{r['new_completed']} & {r['matched_completed']} & {r['old_seconds']:.3f} & {r['new_seconds']:.3f}"+r' \\'+'\n'
 text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 for label,r in [('The matched vacuum comparison',v),('The revised native application against the preceding application',nat),('The new native model against fixed choices',ml)]:
  if r['ratio'] is None:continue
  text+=f"{label} gives time ratio {r['ratio']:.3f}, with a central 95\\% request-resampling interval of $[{r['interval'][0]:.3f},{r['interval'][1]:.3f}]$. "
  text+=f"The new method takes longer on {r['slower']} of the {r['matched_completed']} matched requests. "
  if r['interval'][0]<=1<=r['interval'][1]:text+='The interval includes equal time, so this sample does not resolve a consistent gain across its requests. '
  text+='\n\n'
 a=audit['integrated'];b=audit['all_fixed']
 text+=f"The final-repetition audit of the {len(matched)} matched native requests records {a['unsuccessful_attempts']} unsuccessful internal attempts with the learned choices and {b['unsuccessful_attempts']} with the fixed choice. The corresponding sums of logged equation-generation counts are {a['generated_equation_instances']:,} and {b['generated_equation_instances']:,}; these count regenerated rows as further equation instances. Thus the audit distinguishes failed internal attempts that later recover from requests that never complete. The complete-time comparison includes both kinds of cost.\n\n"
 for kind,label in [('double_box','planar'),('nonplanar_box','nonplanar')]:
  sub=compare([r for r in s['rows'] if r['group']=='native' and kind in r['case']],old='all_fixed')
  text+=f"For the {label} boxes alone, the learned-to-fixed ratio is {sub['ratio']:.3f}, with request interval $[{sub['interval'][0]:.3f},{sub['interval'][1]:.3f}]$ on {sub['matched_completed']} matched requests. "
 text+='\n\n'
 text+=f"The new model runs on {s['model_requests']} of the 32 reserved native requests. The application retains the selected fixed choice outside the training feature ranges. The ML comparison holds the exact identities and native machinery fixed, while the vacuum comparison measures the new analytic identity. We do not assign finite speed factors to failed controls or combine gains from different experiments by multiplication. These results extend the exact domain to the specified single-mass vacuum trees and test native learned choices on the stated two-loop boxes. General massive scattering, unrestricted numerators, and arbitrary high-loop graphs remain outside this demonstrated coverage.\n\n"
 o=read(HERE/'output_summary.json');s['final_application_test']=o
 text+=r'''\subsection{Final application test with the trained policy fixed}
The preceding comparison showed that application overhead can matter when the exact coefficient takes little time to compute. We therefore reduce repeated output bookkeeping and keep the formulas, trained weights, seed choices, and recovery unchanged. We then freeze this revision before a separate test on 22 fresh requests. Fourteen requests use the exact rules: twelve chain requests cover vacuum, two-point, and triangle roots at one, three, seven, and thirteen loops, while two branched thirteen-loop requests each contain 128 targets. Eight native requests use new numerator-batch sets in the same two box classes. These sets occur in neither fitting nor the preceding reserved comparison. The rational native kinematics also change. Each request runs three times in a fresh process with the same complete-time convention and exact checks.

\begin{table}[!htbp]\centering\small
\caption{Separate test of the final application. Each row sums request medians over matched completed requests. The fixed control disables the new model in the final application. These results use a new collection and do not replace the preceding comparison.}
\label{tab:vac-ml-final}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Comparison & Paired & Control (s) & Final (s)\\\midrule
'''
 for label,r in [('Exact rules versus first revision',o['exact']),('Native application versus first revision',o['native']),('Retained exact rules versus preceding method',o['retained_exact']),('Native model versus fixed choice',o['ml'])]:
  text+=f"{label} & {r['matched_completed']} & {r['old_seconds']:.3f} & {r['new_seconds']:.3f}"+r' \\'+'\n'
 text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 text+=f"The final application completes {o['all']['new_completed']} of the 22 requests in every repetition. On the eight native requests, the learned application completes all eight in every repetition, while the fixed control completes {o['ml']['old_completed']} in every repetition. Its time ratio therefore uses {o['ml']['matched_completed']} paired requests; the incomplete control receives no finite speed factor. The exact-output comparisons verify {o['checks']} coefficients across the timed methods and repetitions. "
 for label,r in [('All final requests relative to the first revision',o['all']),('The retained exact requests relative to the preceding method',o['retained_exact']),('The unchanged native model relative to the final fixed choice',o['ml'])]:
  text+=f"{label} give time ratio {r['ratio']:.3f}, with request interval $[{r['interval'][0]:.3f},{r['interval'][1]:.3f}]$. "
  if r['interval'][0]<=1<=r['interval'][1]:text+='This interval includes equal time. '
 text+='The two native test collections remain separate: the final test checks the deployed application with unchanged weights, and supplies no further model selection. Short analytic requests can still take longer than the preceding specialized application because recognition and dispatch have a cost.\n\n'
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/vacuum_learning.pdf}
\caption{The left panel shows mean request medians at each loop order for the vacuum trees; absent control points indicate that no control completed at that order. The right panel shows each matched native request relative to the fixed validation-selected seed setting. Ratios below one indicate less complete time. The equal-time line makes regressions visible.}
\label{fig:vac-ml}
\end{figure}
\FloatBarrier
'''
 (REPORT/'vacuum_learning_results.tex').write_text(text);(REPORT/'vacuum_learning_appendix.tex').write_bytes((HERE/'vacuum_learning_appendix.tex').read_bytes());(REPORT/'vacuum_learning_data.json').write_text(json.dumps(s,indent=2)+'\n')
 p=REPORT/'report.tex';z=p.read_text()
 if '\\input{vacuum_learning_results}' not in z:z=z.replace('\\section{Overall interpretation}','\\input{vacuum_learning_results}\n\n\\section{Overall interpretation}')
 if '\\input{vacuum_learning_appendix}' not in z:z=z.replace('\\input{propagator_trees_appendix}','\\input{propagator_trees_appendix}\n\\input{vacuum_learning_appendix}')
 marker='\\section{Overall interpretation}\n\\label{sec:overall-new}\n'
 addition=r'''The latest extension in Section~\ref{sec:vac-ml} adds a massive vacuum root to the exact tree identities and trains a new seed-choice model from complete native costs. Its fixed-choice comparison holds the exact formulas, protected master indices, and reduction interface constant. Its comparison with the preceding application includes the revised dispatcher and learned policy. These controls separate the added model effect from analytic and integration changes. The remaining paragraphs describe earlier comparisons with their original workloads.

'''
 if addition not in z:z=z.replace(marker,marker+addition)
 p.write_text(z)
 for part in ['results','appendix']:

  z=(REPORT/f'vacuum_learning_{part}.tex').read_text()
  for prefix in ['sec:vac-ml','app:vac-ml','eq:vac-ml','tab:vac-ml','fig:vac-ml','app:prop-tree','app:gamma-cancel']:z=z.replace(prefix,prefix.replace(':',':notes-'))
  z=z.replace('app:sparse','app:seed-geometry').replace('app:families-new','app:families')
  (REPORT/f'notes_vacuum_learning_{part}.tex').write_text(z)
 p=REPORT/'notes.tex';z=p.read_text();block='% BEGIN CURRENT WORKFLOW UPDATE\n\\input{notes_vacuum_learning_results}\n\\input{notes_vacuum_learning_appendix}\n% END CURRENT WORKFLOW UPDATE\n'
 if '\\input{notes_vacuum_learning_results}' not in z:z=z.replace('\\bibliographystyle',block+'\\bibliographystyle',1)
 p.write_text(z)
 abstract=r'''\begin{abstract}
We study how exact identities and machine learning reduce the time needed to express loop integrals in terms of master integrals with Kira. We first integrate supported subgraphs analytically and then use a model trained on complete reduction times to choose the remaining seed work. The exact identities cover connected massless bubble trees with two-point or one-scale triangle roots, and a new extension covers a single massive vacuum root. Their Gamma-function ratios reduce to finite rational products. '''
 abstract+=f"The new vacuum rule completes {v['new_completed']} of {v['requests']} defined structures through thirteen loops. On {v['matched_completed']} matched completed requests, time changes from {v['old_seconds']:.3f} to {v['new_seconds']:.3f} seconds. A separately retrained seed model uses 32 training and 16 validation requests. On 32 reserved native box requests, it takes {ml['new_seconds']:.3f} seconds against {ml['old_seconds']:.3f} seconds for fixed choices, with time ratio {ml['ratio']:.3f}. "
 if ml['interval'][0]<=1<=ml['interval'][1]:abstract+='Its request-resampling interval includes equal time. '
 abstract+=f"A final application revision completes a separate 22-request test; its native part completes eight requests with the model and seven with fixed choices, and the ratio on the seven matched requests is {o['ml']['ratio']:.3f}. "
 abstract+=r'''We separate analytic gains from learned gains, include application and recovery costs, and retain failures in the coverage results. Learned row selection remains omitted. The tested domains have explicit mass, kinematic, and numerator restrictions; the results do not establish a speedup for arbitrary high-loop scattering.
\end{abstract}
''';(REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
\label{sec:conclusion}
Exact subintegral identities reduce the work presented to Kira, and a learned policy selects among admissible seed settings for the remaining native problems. The solver retains responsibility for the algebra. The identities in this study cover several one-scale structures, including connected bubble trees with a massless two-point root, a one-scale triangle root, or a single massive vacuum root. We derive their target-to-master coefficients and check the new vacuum identity independently.

'''
 conclusion+=f"The latest vacuum extension completes {v['new_completed']} of {v['requests']} defined structures through thirteen loops. On {v['matched_completed']} matched completed requests, total time changes from {v['old_seconds']:.3f} to {v['new_seconds']:.3f} seconds (Table~\\ref{{tab:vac-ml}}). This saving comes from exact integration. The earlier cancellation of Gamma factors reduced large triangle-batch time from 14.305 to 6.731 seconds in its separate comparison (Section~\\ref{{sec:gamma-cancel}}).\n\n"
 conclusion+=f"The newly trained native model takes {ml['new_seconds']:.3f} seconds against {ml['old_seconds']:.3f} seconds for the matched fixed choices. Its time ratio is {ml['ratio']:.3f}, with request interval $[{ml['interval'][0]:.3f},{ml['interval'][1]:.3f}]$. "
 conclusion+=('This interval includes equal time, so the fresh sample does not establish a consistent learned gain across these requests. ' if ml['interval'][0]<=1<=ml['interval'][1] else 'The interval describes the finite reserved collection. ')
 conclusion+=f"The final application completes a separate set of 22 requests, including two thirteen-loop batches with 128 targets each. Its complete-time ratio against the first revision is {o['all']['ratio']:.3f}, with request interval $[{o['all']['interval'][0]:.3f},{o['all']['interval'][1]:.3f}]$. The unchanged model completes all eight new native requests; the fixed control completes seven in every repetition. The seven matched requests give time ratio {o['ml']['ratio']:.3f} against the final fixed choice, with interval $[{o['ml']['interval'][0]:.3f},{o['ml']['interval'][1]:.3f}]$ (Table~\\ref{{tab:vac-ml-final}}). "
 conclusion+=r'''The preceding controlled seed and equation-selection measurements remain separate evidence. Learned row selection stays outside the retained method because it has no resolved complete-time benefit. Speed factors from different collections and baselines cannot be multiplied into a universal gain.

The native build retains its 31-index input restriction, including auxiliary scalar-product coordinates. Exact integration avoids native input only for the recognized domains. The new native test concerns numerator batches in two known massless box topology classes, while the analytic tests extend through thirteen loops within the derived families. General multiscale, massive-scattering, and irreducible high-loop reductions remain unresolved. These finite comparisons establish their stated completions and timings, with no claim of exhaustive integral coverage or globally minimum reduction time.
''';(REPORT/'paper_conclusion.tex').write_text(conclusion)
 p=REPORT/'Makefile';z=p.read_text();line=next(x for x in z.splitlines() if x.startswith('report.pdf:'))
 if 'vacuum_learning_results.tex' not in line:z=z.replace(line,line+' vacuum_learning_results.tex vacuum_learning_appendix.tex')
 p.write_text(z)
 for p in [REPORT/'report.tex',REPORT/'notes.tex',REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex',*REPORT.glob('*vacuum_learning*.tex')]:p.write_text(''.join(x.rstrip()+'\n' for x in p.read_text().splitlines()).rstrip('\n')+'\n')
 print('Report and notes source updated.',flush=True)
if __name__=='__main__':main()
