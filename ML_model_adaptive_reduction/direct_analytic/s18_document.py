"""Write current physics, analytic derivations, and measured ML results."""
from s00_direct_common import *
import re
REPORT=ROOT/'report'
def main(final=False):
 s=read(HERE/('final_summary.json' if final else 'summary.json'));m=read(HERE/'trained_model/policy.json');checks=read(HERE/'checks.json');q=s['all'];n=s['native_ml'];names={'order1':'tight sparse','dense':'complete','wide':'wide sparse'}
 if not (REPORT/'paper_before_direct.tex').exists():(REPORT/'paper_before_direct.tex').write_bytes((REPORT/'report.tex').read_bytes())
 for src,dst in [(('focused_final_main.tex' if final else 'focused_main.tex'),'report.tex'),(('focused_final_derivations.tex' if final else 'focused_derivations.tex'),'focused_derivations.tex'),(('direct_final_appendix.tex' if final else 'direct_appendix.tex'),'direct_appendix.tex')]:(REPORT/dst).write_bytes((HERE/src).read_bytes())
 text=r'''\section{Measured results}
\label{sec:results}
The following values are measurements from the frozen comparison in this study. Table~\ref{tab:direct-times} separates the physical domains and includes completion counts. Summed median times refer only to the matched completed requests.
\begin{table}[!htbp]\centering\small
\caption{Complete times against the preceding application. Done gives preceding/integrated completions. Each domain uses the same requests for both methods.}
\label{tab:direct-times}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Domain & Done & Paired & Preceding (s) & Integrated (s)\\\midrule
'''
 titles={'vacuum_products':'Two-mass products, 1--13 loops','connected_vacuum':'Connected vacuum trees, 1--13 loops','lightlike':'Zero-invariant tensor bubbles','ordinary_tensor':'Ordinary one-loop tensors','native':'Native two-loop boxes'}
 for g in titles:
  r=s['groups'][g];text+=f"{titles[g]} & {r['old_completed']}/{r['new_completed']} & {r['matched_completed']} & {r['old_seconds']:.3f} & {r['new_seconds']:.3f}"+r' \\'+'\n'
 text+=f"All {q['requests']} requests & {q['old_completed']}/{q['new_completed']} & {q['matched_completed']} & {q['old_seconds']:.3f} & {q['new_seconds']:.3f}"+r' \\\bottomrule\end{tabularx}\end{table}'+'\n\n'
 text+=f"On the {q['matched_completed']} matched requests, the integrated-to-preceding time ratio is {q['ratio']:.3f}, with a central 95\\% request-resampling interval of $[{q['interval'][0]:.3f},{q['interval'][1]:.3f}]$. The point estimate corresponds to {100*abs(1-q['ratio']):.1f}\\% {'less' if q['ratio']<1 else 'more'} time. The integrated application is slower on {q['slower']} matched requests. This is an incremental comparison with the preceding application on these inputs, rather than a new comparison with unmodified Kira. Earlier percentages use other workloads and cannot be added to this change.\n\n"
 text+=r'\subsection{Direct formulas and their high-loop scope}'+'\n'
 v=s['groups']['vacuum_products'];t=s['groups']['connected_vacuum']
 text+=f"The two-mass product grid changes from {v['old_seconds']:.3f} to {v['new_seconds']:.3f} seconds on {v['matched_completed']} matched requests. Direct partial fractions avoid generic one-loop reduction and its preparation for these inputs. The connected vacuum grid changes from {t['old_seconds']:.3f} to {t['new_seconds']:.3f} seconds on {t['matched_completed']} matched requests. The connected identity is preserved, while its early dispatch avoids generic symbolic preparation when the simpler tree formula already applies. Both grids contain every loop order from one through thirteen.\n\n"
 text+=f"The separate analytic coverage grid completes {s['extended_completed']} of {s['extended_requests']} requests and takes {s['extended_seconds']:.3f} seconds in summed median time. Its thirteen repeated-mass requests use an independent symbolic partial-fraction reference, while thirteen coupled massless vacuum requests use the scaleless-integral identity. We report this as exact-domain coverage without assigning a speedup over an unsupported native input. The implementation returns Gamma-function values for the resulting tadpoles and the connected one-mass tree masters, so these domains have an analytic value as well as a decomposition.\n\n"
 text+=f"The tests contain {s['checks']:,} coefficient comparisons across timed outputs. Development additionally checks {checks['random_rational_identities']} rational-function identities, {checks['independent_coefficient_checks']} product coefficients, {checks['native_tadpole_coefficient_checks']} native tadpole coefficients, {checks['native_scaleless_target_checks']} native scaleless target relations, and two convergent radial integrals. These checks test algebra and normalization separately.\n\n"
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/direct_vacuum.pdf}
\caption{Complete elapsed time at every tested loop order. The left panel tests independent factors. In the connected-tree panel, each line gives the median across the tested shapes at that loop order and the shaded band gives their full range. Logarithmic time axes retain the short exact calculations and the slower preparation costs. These domains require the structures stated in the derivations.}
\label{fig:direct-vacuum}
\end{figure}
\subsection{Native seed choices and the ML contribution}
'''
 text+=f"The preliminary ordering experiment verifies all 32 development reductions. Ordering 1 has the lowest sum of development times, so the final native actions retain it. The subsequent model chooses the seed procedure. Validation selects {m['selection']['count']} cost {'tree' if m['selection']['count']==1 else 'trees'} with maximum depth {m['selection']['depth']} and a minimum leaf population of {m['selection']['minimum']}. Its fixed control is the {names[m['fixed']]} region. The selected validation cost is {m['selection']['cost']:.3f} seconds, including the prediction allowance and failure penalties; the fixed control gives {m['fixed_validation_seconds']:.3f} seconds. Validation {'enables the replacement' if m['enabled'] else 'rejects the replacement because the deployment condition is not met'}. {'The final application retains the preceding validated native seed model.' if final else 'This candidate comparison therefore uses the selected fixed choice.'}\n\n"
 text+=f"On the {n['matched_completed']} matched reserved native batches, the fixed application takes {n['old_seconds']:.3f} seconds and the integrated application takes {n['new_seconds']:.3f} seconds. Their ratio is {n['ratio']:.3f}, with interval $[{n['interval'][0]:.3f},{n['interval'][1]:.3f}]$. "
 if not final and not m['enabled']:text+='Validation disabled the new learned selector, so both frozen controls use the same fixed seed procedure. This comparison measures run-to-run variation and does not estimate an ML saving. '
 elif n['interval'][1]<1:text+='This comparison supports an additional learned saving on the sampled batches. '
 elif n['interval'][0]>1:text+='This comparison shows a measured increase over the fixed choice. '
 else:text+='This interval includes equal time and does not resolve a consistent additional learned saving. '
 text+=f"The integrated method is slower on {n['slower']} matched batches. The {'retained native policy' if final else 'new model'} changes the fixed action on {s['changed_native_requests']} of the sixteen requests in the final repetition. "
 if final and not s['changed_native_requests']:text+='Thus the retained model selects the fixed action throughout this final sample; the measured difference includes prediction overhead and run-to-run variation, and supplies no additional learned speedup. '
 pred=[x for x in s['prediction_seconds'] if x is not None]
 if pred:text+=f"Median measured model loading and decision time is {1000*statistics.median(pred):.3f} milliseconds. "
 text+='Exact formulas, the native interface, and recovery checks are shared by the learned and fixed controls.\n\n'
 text+=f"Across 48 native applications per method, unverified output counts are {s['failed_applications']['integrated']} for the integrated application, {s['failed_applications']['fixed']} for the fixed control, and {s['failed_applications']['previous']} for the preceding application. Recorded failed inner attempts total {s['native_failed_attempts']['integrated']}, {s['native_failed_attempts']['fixed']}, and {s['native_failed_attempts']['previous']}, respectively. A terminated application can lack an inner-attempt record and remains in the separate application-failure count. Complete-region selection can avoid a sparse failure, but these measurements do not guarantee success for unseen inputs.\n\n"
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=.96\linewidth]{paper_figures/direct_native.pdf}
\caption{The separate ML comparison uses the same exact methods and native implementation for both controls. Points below one favor the integrated choice. Individual batches show variation, while the aggregate point reports the ratio of summed median times and its request-resampling interval.}
\label{fig:direct-native}
\end{figure}
'''
 prior=(REPORT/'lightlike_results.tex').read_text();a=prior.index('\\subsection{The other learned interventions}');b=prior.index('\\subsection{Scope of the result}',a);text+=prior[a:b]
 text+=r'''\subsection{Scope of the result}
The direct formulas prove reductions and analytic values within their stated domains. The test covers every loop order through thirteen for independent vacuum products and connected one-mass trees. The native test covers new target batches and kinematic points within two known two-loop scattering graphs. General coupled multiscale scattering at every loop order remains outside this evidence. Loop count alone does not classify the difficulty or determine whether a particular exact rule applies.

The controls separate changes in the integrated application from the additional effect of learned selection. A finite search over models and native settings cannot establish globally minimum time for every integral. The retained measurements include slower requests, unsuccessful attempts, and incomplete applications so that these limits remain part of the result.
\FloatBarrier
'''
 if not final and not m['enabled']:
  text=text.replace('The separate ML comparison uses the same exact methods and native implementation for both controls. Points below one favor the integrated choice. Individual batches show variation, while the aggregate point reports the ratio of summed median times and its request-resampling interval.', 'Validation costs explain why the new learned selector remains disabled. Each point divides a candidate procedure\'s median complete time by the selected fixed procedure\'s time on the same request. The dashed line marks the fixed cost; points above it identify slower alternatives.')
 if final and not s['changed_native_requests']:
  text=text.replace('The separate ML comparison uses the same exact methods and native implementation for both controls. Points below one favor the integrated choice.', 'The retained model chooses the fixed action on every final batch, so this sample demonstrates no additional ML saving. Both controls use the same exact methods and native implementation. Points below one indicate a lower measured integrated time.')
 if v['ratio']<1 and t['ratio']<1:
  text=text.replace('Complete elapsed time at every tested loop order. The left panel tests independent factors.', 'Direct formulas reduce aggregate time in both measured vacuum grids. The panels show complete elapsed time at every tested loop order, with independent factors on the left.')
 (REPORT/'direct_results.tex').write_text(text)
 deployment=("Validation rejects the new complete-region selector, so the final application retains the preceding native seed model." if final else ("Validation retains the fixed region because learned selection does not improve its cost." if not m['enabled'] else "Validation enables the learned selector."))
 abstract=f"""\\begin{{abstract}}
We study the time required to decompose Feynman integrals using Kira, exact analytic identities, and machine learning. Recognized vacuum factors are evaluated by partial fractions and analytic tadpole formulas, while connected one-mass trees return explicit Gamma-function values. For supported remaining two-loop boxes, we train a measured-cost selector for sparse and complete seed regions, including failed attempts in its objective. {deployment} A frozen comparison tests 69 requests, with vacuum products and connected trees at every loop order from one through thirteen. The integrated and preceding applications complete {q['new_completed']} and {q['old_completed']} requests. Their {q['matched_completed']} matched requests take {q['new_seconds']:.3f} and {q['old_seconds']:.3f} seconds, respectively. On {n['matched_completed']} matched native batches, the integrated-to-fixed time ratio is {n['ratio']:.3f}, with a 95\\% interval of $[{n['interval'][0]:.3f},{n['interval'][1]:.3f}]$. A separate analytic coverage grid completes {s['extended_completed']} of {s['extended_requests']} requests. We report analytic and learned effects separately and retain native row selection because earlier learned row policies did not establish a reliable benefit. The results apply to the declared domains and do not establish a speedup for every high-loop scattering integral.
\\end{{abstract}}
""";(REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=f"""Exact identities reduce complete calculation time when the propagator structure admits them. The added partial-fraction rule handles repeated masses, raised powers, and polynomial numerators in vacuum factors. Its tadpole formula and the retained connected-tree derivation also supply explicit analytic values. Direct dispatch avoids algebraic preparation that these identities make unnecessary.

The integrated method completes {q['new_completed']} of 69 reserved requests. Its {q['matched_completed']} matched requests take {q['new_seconds']:.3f} seconds, compared with {q['old_seconds']:.3f} seconds for the preceding application. The separate native comparison with a fixed seed procedure gives ratio {n['ratio']:.3f} and interval $[{n['interval'][0]:.3f},{n['interval'][1]:.3f}]$. These are distinct controls: the first measures the full revision, and the second tests the additional learned choice. {deployment} Earlier equation filtering remains separately supported on its tested workload, while learned row selection is omitted.

The high-loop evidence covers products and connected one-scale trees through thirteen loops. Native generalization is tested within planar and nonplanar two-loop boxes. General coupled multiscale high-loop scattering and globally minimum reduction time remain unestablished. The notes preserve the earlier experiments, unsuccessful choices, and full coverage limits.
""";(REPORT/'paper_conclusion.tex').write_text(conclusion)
 notes=(REPORT/'notes.tex').read_text();begin='% BEGIN CURRENT WORKFLOW UPDATE\n% DIRECT ANALYTIC UPDATE';end='% DIRECT ANALYTIC UPDATE END\n% END CURRENT WORKFLOW UPDATE'
 if begin in notes:
  a=notes.index(begin);b=notes.index(end,a)+len(end);b+=notes[b:b+1]=='\n';notes=notes[:a]+notes[b:]
 block='\\section{Direct analytic evaluation and complete native regions}\nThe following update retains the new method, comparisons, and derivations.\n'+text+'\n'+(REPORT/'focused_derivations.tex').read_text()+'\n'+(REPORT/'focused_trees_appendix.tex').read_text()+'\n'+(REPORT/'direct_appendix.tex').read_text()
 if final:
  initial=read(HERE/'summary.json');iq=initial['all'];inn=initial['native_ml']
  block+=f"\n\\section{{Preceding candidate experiment}}\nBefore the final deployment, the candidate fixed-region application completed {iq['new_completed']} of {iq['requests']} requests. Its {iq['matched_completed']} matched requests took {iq['new_seconds']:.3f} seconds, compared with {iq['old_seconds']:.3f} seconds for the preceding application. The candidate-to-fixed ratio was {inn['ratio']:.3f}. The new selector was disabled by validation. This experiment motivated retaining the preceding native policy when a replacement fails validation; the final native test uses fresh whole batches at a new kinematic point. The candidate exact requests used the same family definitions with the first index one lower than in the final comparison. Its native test used eight batches per graph at profile 22367. The separate 26 exact-domain coverage requests are shared with the final study because their exact routines are unchanged.\n"
  (REPORT/'direct_candidate_data.json').write_text(json.dumps(initial,indent=2)+'\n')
  if (HERE/'import_check.json').exists():
   block+=r'''
\subsection{Interrupted execution and repeat comparison}
The first execution of the final application stopped native calculations before algebra because two modules shared an import name. We preserved those records and corrected the binding without changing the formulas, weights, target batches, or decision rules. A separate check verified all three native controls against the same exact reference. We then repeated the full final comparison from fresh processes. The reported times use that completed repeat, and the interrupted execution is excluded from the scientific timing comparison.
'''
 labels=set(re.findall(r'\\label\{([^}]+)\}',block));refs=set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',block));mapping={x:'notes-direct-'+x for x in labels};mapping.update({'eq:reduction':'eq:generated-integral-reduction','app:lightlike':'notes-light-app:lightlike'})
 assert refs<=set(mapping),refs-set(mapping)
 for old,new in mapping.items():block=block.replace('{'+old+'}','{'+new+'}')
 pos=notes.index('\\bibliographystyle');notes=notes[:pos]+begin+'\n'+block+'\n'+end+'\n'+notes[pos:];(REPORT/'notes.tex').write_text(notes)
 make=REPORT/'Makefile';src=make.read_text()
 if 'report.pdf: direct_results.tex' not in src:src=src.replace('report.pdf: ','report.pdf: direct_results.tex direct_appendix.tex ',1)
 make.write_text(src)
 (REPORT/'direct_data.json').write_text(json.dumps(dict(summary=s,model={k:v for k,v in m.items() if k not in ['trees','failure_guard','minimum','maximum']},checks=checks),indent=2)+'\n')
 if final:
  from s30_deploy_plot import main as plot
 else:
  from s17_plot import main as plot
 plot()
 if not final and not m['enabled']:validation_plot(m)
 print('Current paper, notes, and plots written.',flush=True)
def validation_plot(model):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from s03_cases import cases
 rows=[read(HERE/'validation'/(c['id']+'.json.gz')) for c in cases('validation')]
 fixed=model['fixed'];rows.sort(key=lambda r:statistics.median(x['application_seconds'] for x in r['measurements'][fixed]));names={'dense':'Complete region','wide':'Wide sparse region','order1':'Tight sparse region'}
 fig,ax=plt.subplots(figsize=(6.4,3.1),constrained_layout=True);values=[1.]
 for action,color,marker in zip([a for a in model['actions'] if a!=fixed],['#236b8e','#a55d3a'],['o','s']):
  ratios=[statistics.median(x['application_seconds'] for x in r['measurements'][action])/statistics.median(x['application_seconds'] for x in r['measurements'][fixed]) for r in rows];values+=ratios;ax.scatter(range(1,len(rows)+1),ratios,s=30,color=color,marker=marker,label=names[action])
 ax.axhline(1,color='.4',linestyle='--',linewidth=1,label='Selected fixed region');span=max(.1,max(values)-min(values));ax.set(xlabel='Validation request, ordered by fixed-region time',ylabel='Complete time / fixed-region time',ylim=(min(values)-.12*span,max(values)+.25*span),xlim=(.5,len(rows)+.5));ax.set_xticks(range(1,len(rows)+1));ax.legend(frameon=False,fontsize=8,ncol=3);ax.grid(axis='y',alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);fig.savefig(REPORT/'paper_figures/direct_native.pdf');plt.close(fig)

if __name__=='__main__':main()
