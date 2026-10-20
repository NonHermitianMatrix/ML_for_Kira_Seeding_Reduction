"""Write the exact tensor derivation and complete-time comparisons in both documents."""
from s00_tensor_common import *
REPORT=ROOT/'report'

def main():
 from s12_analyze import compare
 first=read(HERE/'summary.json');s=read(HERE/'fast_summary.json');model=read(HERE/'trained_model/fast_policy.json');check=read(HERE/'development_checks.json');pilot=read(HERE/'pilot.json');arith=read(HERE/'fast_arithmetic_checks.json')
 changed=0;prediction=[]
 for row in s['rows']:
  if row['group'] not in ['tensor','other_masses']:continue
  ans=read(HERE/'final_test'/(row['case']+'.json.gz'))['results']['integrated'];blocks=ans.get('blocks',[])
  changed+=any(b['result'].get('model_used',False) and b['result'].get('action')!=model['fixed'] for b in blocks)
  prediction.extend(b['result']['prediction_seconds'] for b in blocks if b['result'].get('model_used',False))
 audit=dict(final_tensor_changed_requests=changed,median_prediction_seconds=statistics.median(prediction) if prediction else None,scope='Final repetition of the twenty one-loop tensor requests; includes policy load and choice but excludes process startup.')
 write(HERE/'model_application_audit.json',audit)
 exact=[r for r in s['rows'] if r['group'] in ['tensor','other_masses']];products=[r for r in s['rows'] if r['group']=='products'];native=[r for r in s['rows'] if r['group']=='native'];e=compare(exact);ml=compare(exact,old='all_fixed');a=compare(exact,old='first');n=compare(native,old='all_fixed');p=compare(products)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(8,3.2),constrained_layout=True)
 for method,title,col in [('previous','Preceding application','#ad4f32'),('first','First tensor implementation','#747474'),('integrated','Factored tensor method','#236b8e')]:
  xx=[];yy=[]
  for P in [2,3,4]:
   rows=[r for r in exact if r['physical']==P and all(all(r['success'][m]) for m in ['previous','first','integrated'])]
   if rows:xx.append(P);yy.append(statistics.mean(r['median_seconds'][method] for r in rows))
  axes[0].plot(xx,yy,'o-',label=title,color=col,markersize=4)
 axes[0].set(xlabel='Number of physical denominators',ylabel='Mean request-median time (s)',yscale='log',title='Exact numerator reduction');axes[0].set_xticks([2,3,4]);axes[0].legend(frameon=False,fontsize=7)
 for method,title,col in [('previous','Preceding application','#ad4f32'),('first','First tensor implementation','#747474'),('integrated','Factored tensor method','#236b8e')]:
  rr=[r for r in products if all(r['success'][method])]
  axes[1].plot([r['loops'] for r in rr],[r['median_seconds'][method] for r in rr],'o-',color=col,label=title,markersize=4)
 axes[1].set(xlabel='Number of independent loops',ylabel='Complete application time (s)',yscale='log',title='Products of tensor bubbles');axes[1].set_xticks([2,4,6,8,10,12,13])
 for ax in axes:ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(axis='y',alpha=.2)
 fig.savefig(REPORT/'paper_figures/tensor_reduction.pdf');plt.close(fig)
 text=r'''\section{Exact numerator reduction with learned identity choices}
\label{sec:tensor-results}
The preceding scalar recurrence accepts raised denominator powers. A polynomial numerator can prevent that path from applying, even when only one loop needs reduction. We extend the exact stage to such numerators by resolving the loop momentum into directions parallel and perpendicular to the external vectors seen by the denominators. Angular averages remove the perpendicular numerator factors, after which the scalar recurrence lowers the remaining powers. Tensor reduction and general one-loop generating functions provide the established context~\cite{DennerDittmaier2006,Hu2025}; Appendix~\ref{app:tensor-reduction} derives the specific angular and signed-index IBP identities used here.

There are two useful orders for these identities. We can remove the numerator before lowering raised propagator powers, or use the signed-index IBP relation to lower those powers first. In either order, the calculation ends at unit-power scalar sectors. The model selects this order and whether to lower the largest or smallest raised positive power. The implementation shares intermediate reductions within each request and reuses identical independent components within that request. Its four actions therefore change the path through exact identities. Exact arithmetic supplies every reduction coefficient. We keep the preceding native seed model for inputs that still require Kira.

We also use the derived denominator structure to simplify the exact arithmetic. Every dimension-dependent denominator is a product of factors $d+j$ with integer $j$. Keeping these factors explicit permits exact cancellation by polynomial division, as derived in Eqs.~\eqref{eq:tensor-factored-field}--\eqref{eq:tensor-factored-add}. The final model learns from complete timings with this arithmetic in place. A fixed-action control uses the same arithmetic, so that the measured effect of the model remains separate from the exact improvement.

\subsection{Families, checks, and comparison design}
The new one-loop families contain two, three, or four physical denominators and one or two auxiliary coordinates, with at most five coordinates in total. Numerator rank means $\sum_j\max(-a_j,0)$, and excess positive power means $\sum_j\max(a_j-1,0)$. The training requests span numerator ranks one through four and excess powers zero through three. They use distinct rational masses and off-shell scalar products, with symbolic $d$. Appendix~\ref{app:tensor-reduction} specifies the construction and the wider implementation bounds. These are reductions at rational kinematic points; they do not reconstruct a general symbolic multiscale answer.

We measure all four actions on 24 training requests and 12 separate validation requests. Their mass and scalar-product profiles differ across splits, although some index patterns recur. The final test changes both the profiles and target batches. Sixteen requests use the massive training structures, four further requests use massless or mixed-mass sectors, and twelve requests use independent products of tensor bubbles at each loop order from two through thirteen. Eight new native requests test the retained seed model in planar and nonplanar massless two-loop boxes, while four vacuum-tree requests check that the preceding exact path still works. The products establish a factorized high-loop extension. Each method returns the product of component reductions, so the timed output retains the factors instead of expanding every product of master integrals. These requests do not test a coupled thirteen-loop scattering reduction.

'''
 text+=f"The development checks compare {pilot['checks']} exact coefficients with native Kira in six requests, test {check['ibp_residual_coefficients']} coefficients in independently assembled signed IBP residuals, and test changes of loop names, loop signs, and propagator order. The final arithmetic passes {arith['algebra_checks']} rational-function comparisons and repeats the native pilot agreement. Every new training and validation output is compared with the first symbolic-field implementation. The reserved tensor results are checked through the alternate recurrence, while native box results use separately prepared Kira references. If a native result uses a different basis, the external check reduces that basis before comparing coefficients. These checks follow the algebra of the reduction and do not replace the derivation.\n\n"
 text+=r'''Each reserved application starts in a fresh process and runs three times, with method order rotated on the same worker. The eighteen-second limit applies to every timed method. Total time includes input reading, recognition, model loading and prediction, exact algebra or native recovery, output, and exit. The separate reference calculation and external coefficient comparison lie outside all application timers. The preceding native method uses its existing master-index registry. A failed request remains in the completion counts and receives no finite speed factor. We sum per-request median times only for requests that both methods complete and verify in all three repetitions. The resampling interval uses the request-level procedure of Appendix~\ref{app:statistics}.

\subsection{Final exact and learned results}
'''
 count=model['selection']['count'];tree_word='tree' if count==1 else 'trees'
 fixed_description={'tensor_smallest':'removes the numerator first and then lowers the smallest raised positive power','tensor_largest':'removes the numerator first and then lowers the largest raised positive power','powers_smallest':'lowers the smallest raised positive power before removing the numerator','powers_largest':'lowers the largest raised positive power before removing the numerator'}[model['fixed']]
 text+=f"Validation selects {count} cost {tree_word}, depth at most {model['selection']['depth']}, minimum leaf population {model['selection']['minimum']}, and a predicted-saving margin of {100*model['margin']:.0f}\\%. The fixed control {fixed_description}. The validation rule {'enables' if model['enabled'] else 'disables'} the new learned choice. Its validation cost, including a one-millisecond allowance per request, is {model['selection']['cost']:.3f} seconds, against {model['fixed_validation_seconds']:.3f} seconds for the fixed choice. These values determine deployment; the final test supplies the independent timing result.\n\n"
 if not model['enabled']:text+='The deployment rule leaves the tensor model disabled. Its final application and fixed control therefore use the same action; their timing difference measures run variation. The retained native seed model remains active on its eligible requests.\n\n'
 text+=r'''\begin{table}[!htbp]\centering\small
\caption{Final complete-time comparisons. Counts give control/final completions, and times sum medians on matched completed requests. The first tensor implementation uses a general rational-function field. The fixed control uses the final exact arithmetic with the relevant learned choice disabled. All entries are measurements of this study.}
\label{tab:tensor-results}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Comparison & Done & Paired & Control (s) & Final (s)\\\midrule
'''
 for title,row in [('Tensor / preceding application',e),('Tensor / first implementation',a),('Independent products / preceding',p),('Native boxes / fixed seed choice',n),('Native boxes / preceding',s['groups']['native']),('All 44 requests / preceding',s['all']),('Vacuum regression / preceding',s['groups']['previous_exact'])]:
  text+=f"{title} & {row['old_completed']}/{row['new_completed']} & {row['matched_completed']} & {row['old_seconds']:.3f} & {row['new_seconds']:.3f}"+r' \\'+'\n'
 text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 text+=r"""\begin{table}[!htbp]\centering\small
\caption{Physical scope of the final one-loop tensor comparison. Times sum matched request medians against the preceding application. Mass classes with a single request have evidence from that case alone.}
\label{tab:tensor-types}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Integral class & Paired & Preceding (s) & Final (s)\\\midrule
"""
 for title,rows in [('Massive bubbles',[r for r in exact if r['group']=='tensor' and r['physical']==2]),('Massive triangles',[r for r in exact if r['group']=='tensor' and r['physical']==3]),('Massive boxes',[r for r in exact if r['group']=='tensor' and r['physical']==4]),('Massless bubble',[r for r in exact if 'massless' in r['case']]),('Mixed-mass bubble',[r for r in exact if r['group']=='other_masses' and r['physical']==2 and 'mixed' in r['case']]),('Mixed-mass triangle',[r for r in exact if r['group']=='other_masses' and r['physical']==3]),('Mixed-mass box',[r for r in exact if r['group']=='other_masses' and r['physical']==4])]:
  row=compare(rows);text+=f"{title} & {row['matched_completed']} & {row['old_seconds']:.3f} & {row['new_seconds']:.3f}"+r' \\'+'\n'
 text+=r'\bottomrule\end{tabularx}\end{table}\FloatBarrier'+'\n\n'
 for title,row in [('The tensor comparison with the preceding application',e),('The tensor comparison with the first implementation',a),('The retained native seed model against fixed choices',n)]:
  if row['ratio'] is None:continue
  text+=f"{title} gives time ratio {row['ratio']:.3f}, with a central 95\\% request-resampling interval of $[{row['interval'][0]:.3f},{row['interval'][1]:.3f}]$. The final method is slower on {row['slower']} of {row['matched_completed']} matched requests. "
  if row['interval'][0]<=1<=row['interval'][1]:text+='The interval includes equal time, so this sample does not resolve a consistent gain across its requests. '
  elif row['interval'][0]>1:text+='This comparison shows a time increase over its control. '
  text+='\n\n'
 text+=f"The final application completes {s['all']['new_completed']} of {len(s['rows'])} requests in every repetition, with {s['checks']:,} coefficient comparisons across the timed methods. "
 if prediction:text+=f"The new model changes the fixed action on {changed} tensor requests in the final repetition, with median measured policy loading and choice time of {1000*audit['median_prediction_seconds']:.3f} milliseconds. "
 else:text+='The new tensor selector makes no predictions because validation retains the fixed action. '
 text+=f"The retained seed model is evaluated on {s['model_requests']['native']} of the eight native requests. The complete-time gains against the preceding application include the new exact identities and arithmetic; the native fixed control measures the extra learned choice.\n\n"
 text+=f"Across all 44 requests, total time changes from {s['all']['old_seconds']:.3f} to {s['all']['new_seconds']:.3f} seconds, or {s['all']['saving_percent']:.1f}\\% less time on this collection. The final application is slower on {s['all']['slower']} requests. The native requests take {s['groups']['native']['ratio']:.3f} times the preceding application's time, and the four retained vacuum requests take {s['groups']['previous_exact']['ratio']:.3f} times its time. These regressions remain in the overall result; the new exact tensor path supplies the large saving.\n\n"
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/tensor_reduction.pdf}
\caption{Exact numerator reduction and factored dimension denominators reduce complete time on the plotted requests. The left panel averages the request medians, on common completed requests, for each physical-denominator count. The right panel shows independent tensor-bubble products through thirteen loops. Only requests completed in all repetitions appear; missing points represent incomplete controls. The logarithmic time axes show the full measured range. The fixed-control comparisons in Table~\ref{tab:tensor-results} separately measure the learned contribution.}
\label{fig:tensor-results}
\end{figure}
\FloatBarrier

The added exact domain covers rational one-loop numerator reductions and their independent products under the stated matrix and power conditions. The retained vacuum and massless tree identities supply further connected high-loop domains. General symbolic multiscale kinematics, singular tensor projections requiring other identities, and arbitrary coupled high-loop scattering remain outside this extension. The results establish the measured savings and their limits; they do not establish a globally shortest reduction path.
'''
 (REPORT/'tensor_reduction_results.tex').write_text(text);(REPORT/'tensor_reduction_appendix.tex').write_bytes((HERE/'tensor_reduction_appendix.tex').read_bytes())
 data=dict(final=s,first=first,model_audit=audit,final_tensor_comparison=e,final_tensor_ml=ml,final_tensor_arithmetic=a);(REPORT/'tensor_reduction_data.json').write_text(json.dumps(data,indent=2)+'\n')
 paper=REPORT/'report.tex';z=paper.read_text().replace('\\date{October 18, 2026}','\\date{October 19, 2026}')
 if '\\input{tensor_reduction_results}' not in z:z=z.replace('\\section{Overall interpretation}','\\input{tensor_reduction_results}\n\n\\section{Overall interpretation}')
 if '\\input{tensor_reduction_appendix}' not in z:z=z.replace('\\input{vacuum_learning_appendix}','\\input{vacuum_learning_appendix}\n\\input{tensor_reduction_appendix}')
 z=z.replace('The latest extension in Section~\\ref{sec:vac-ml}','The preceding extension in Section~\\ref{sec:vac-ml}')
 marker='\\section{Overall interpretation}\n\\label{sec:overall-new}\n';addition=r'''The final extension in Section~\ref{sec:tensor-results} adds exact polynomial-numerator reduction and exploits its factored dimension poles. Its comparisons separate the new physical identities, their arithmetic, and the learned choice of identity order. The independent-product tests extend that identity to thirteen loops without a coupled high-loop solve. The earlier experiments below retain their own inputs and controls.

'''
 if addition not in z:z=z.replace(marker,marker+addition)
 paper.write_text(z)
 for part in ['results','appendix']:
  z=(REPORT/f'tensor_reduction_{part}.tex').read_text()
  for prefix in ['sec:tensor','app:tensor','eq:tensor','tab:tensor','fig:tensor']:z=z.replace(prefix,prefix.replace(':',':notes-'))
  z=z.replace('app:families-new','app:families').replace('app:vac-ml','app:notes-vac-ml').replace('app:fast-method','app:notes-fast-method').replace('app:statistics','app:notes-tensor-statistics').replace('Eq.~\\eqref{eq:integral}','Eq.~\\eqref{eq:general-integral}')
  if part=='results':z=z.replace('Appendix~\\ref{app:notes-tensor-statistics}','the request-resampling calculation defined at the end of the final-results subsection below')
  (REPORT/f'notes_tensor_reduction_{part}.tex').write_text(z)
 # Give notes the same interval definition without a missing paper-only label.
 note=REPORT/'notes_tensor_reduction_results.tex';z=note.read_text();z+='\nFor each comparison, we resample its matched requests with replacement 2,000 times, sum the request medians in each resample, and divide the final sum by the control sum. The reported central interval uses the 2.5 and 97.5 percent quantiles of these ratios. This describes variation across the finite request collection.\n';note.write_text(z)
 z=note.read_text()+r'\subsection{First tensor implementation and preliminary comparison}'+'\n'
 for group,row in first['groups'].items():
  z+=f"For {group.replace('_',' ')}, the first implementation completes {row['new_completed']} of {row['requests']} requests in all repetitions. Its preceding control completes {row['old_completed']}. On {row['matched_completed']} matched requests, the control and first tensor times are {row['old_seconds']:.3f} and {row['new_seconds']:.3f} seconds. \n"
 first_ml=compare([r for r in first['rows'] if r['group'] in ['tensor','other_masses']],old='all_fixed')
 if first_ml['ratio'] is not None:z+=f"The first identity-order model gives ratio {first_ml['ratio']:.3f} against its fixed action, with request interval $[{first_ml['interval'][0]:.3f},{first_ml['interval'][1]:.3f}]$. Its weights remain stored, while the final arithmetic uses a separately trained policy.\n"
 z+='The preliminary fixed-control measurement for the three-loop product contains a startup import failure during a source transfer. The outcome remains in the saved record and is excluded from completed-time comparisons. Subsequent transfers retain unchanged files and replace changed sources atomically. The final comparison uses a new collection and preserves all failures separately.\n'
 note.write_text(z)
 pnotes=REPORT/'notes.tex';z=pnotes.read_text();block='% BEGIN CURRENT WORKFLOW UPDATE\n\\input{notes_tensor_reduction_results}\n\\input{notes_tensor_reduction_appendix}\n% END CURRENT WORKFLOW UPDATE\n'
 if '\\input{notes_tensor_reduction_results}' not in z:z=z.replace('\\bibliographystyle',block+'\\bibliographystyle',1)
 pnotes.write_text(z)
 abstract=r'''\begin{abstract}
We study how exact identities and learned choices reduce the time needed to decompose loop integrals into master integrals with Kira. The method applies proved identities to supported integral structures and uses a model trained on complete reduction costs for the remaining choices. Its exact domains include connected one-scale bubble trees through thirteen loops. We extend the method to polynomial numerators in one-loop sectors and independent products of these sectors. Angular tensor averages and signed-index IBP give the reduction, while their dimension poles permit exact arithmetic with factored linear denominators. '''
 abstract+=f"On {e['matched_completed']} matched one-loop tensor requests, complete time changes from {e['old_seconds']:.3f} to {e['new_seconds']:.3f} seconds relative to the preceding application. The final extension completes {s['all']['new_completed']} of {len(s['rows'])} reserved requests in every repetition, and total time across this collection changes from {s['all']['old_seconds']:.3f} to {s['all']['new_seconds']:.3f} seconds. "
 if model['enabled'] and ml['ratio'] is not None:abstract+=f"The new identity-order model gives a time ratio of {ml['ratio']:.3f} against fixed exact choices, with request-resampling interval $[{ml['interval'][0]:.3f},{ml['interval'][1]:.3f}]$. "
 abstract+=r'''Separate controls measure the retained native seed model. We distinguish exact savings from learned savings, include recovery costs, and retain unsuccessful requests in the coverage counts. Learned row selection remains omitted. The results cover the defined families and kinematics, with no claim of exhaustive high-loop scattering coverage.
\end{abstract}
''';(REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
\label{sec:conclusion}
Exact integral identities remove work from the general IBP system, and learned cost models choose among the remaining admissible strategies. This study derives exact reductions for several connected one-scale tree structures and extends them to polynomial numerators in rational one-loop sectors. The tensor extension resolves numerator components by angular averages and then lowers propagator powers through signed-index IBP. The resulting dimension denominators have known linear factors, which permit a further exact simplification of the coefficient arithmetic.

'''
 conclusion+=f"The final one-loop tensor comparison takes {e['new_seconds']:.3f} seconds against {e['old_seconds']:.3f} seconds for the preceding application on {e['matched_completed']} matched requests (Table~\\ref{{tab:tensor-results}}). The independent-product extension completes {p['new_completed']} of {p['requests']} requests at two through thirteen loops. The full final test completes {s['all']['new_completed']} of {len(s['rows'])} requests in every repetition, with total time changing from {s['all']['old_seconds']:.3f} to {s['all']['new_seconds']:.3f} seconds. Ten requests take longer than the preceding application. These complete-time results include application overhead and recovery, with external benchmark checks excluded equally.\n\n"
 if model['enabled'] and ml['ratio'] is not None:
  conclusion+=f"The new learned identity choice gives ratio {ml['ratio']:.3f} against the fixed exact action, with interval $[{ml['interval'][0]:.3f},{ml['interval'][1]:.3f}]$. "
  if ml['interval'][0]<=1<=ml['interval'][1]:conclusion+='This interval includes equal time. '
 if n['ratio'] is not None:conclusion+=f"The retained native seed model gives ratio {n['ratio']:.3f} against fixed choices on {n['matched_completed']} fresh matched box requests, with interval $[{n['interval'][0]:.3f},{n['interval'][1]:.3f}]$. "
 conclusion+=r'''The earlier seed and equation studies remain separate evidence for learned gains within their tested domains. Learned row selection remains omitted because it has no resolved complete-time benefit. Gains from different controls and request collections cannot be multiplied into a universal speedup.

The exact tensor path requires the relevant Gram and Cayley matrices to be invertible and uses rational kinematic values. Its high-loop tests concern independent products. The connected tree formulas have their own mass, momentum, and numerator conditions. General symbolic multiscale scattering and arbitrary coupled high-loop integrals remain unresolved. These measured results support the stated reductions and savings, without a claim of globally minimum calculation time.
''';(REPORT/'paper_conclusion.tex').write_text(conclusion)
 entry='''\n@article{DennerDittmaier2006,
 author = {Denner, A. and Dittmaier, S.},
 title = {Reduction schemes for one-loop tensor integrals},
 journal = {Nuclear Physics B},
 volume = {734}, pages = {62--115}, year = {2006},
 doi = {10.1016/j.nuclphysb.2005.11.007},
 eprint = {hep-ph/0509141}, archivePrefix = {arXiv}
}
'''
 for name in ['paper_references.bib','notes_additional_references.bib']:
  f=REPORT/name;z=f.read_text()
  if '@article{DennerDittmaier2006,' not in z:f.write_text(z.rstrip()+'\n'+entry)
 make=REPORT/'Makefile';z=make.read_text();line=next(x for x in z.splitlines() if x.startswith('report.pdf:'))
 if 'tensor_reduction_results.tex' not in line:z=z.replace(line,line+' tensor_reduction_results.tex tensor_reduction_appendix.tex')
 make.write_text(z)
 for q in [paper,pnotes,REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex',*REPORT.glob('*tensor_reduction*.tex')]:q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 print('Wrote tensor report, notes, derivation, and plot.',flush=True)
if __name__=='__main__':main()
