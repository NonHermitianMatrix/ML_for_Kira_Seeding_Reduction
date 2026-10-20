"""Write a focused physics paper from the frozen complete-time evidence."""
from s00_light_common import *
import re
REPORT=ROOT/'report'

def main():
 s=read(HERE/'summary.json');p=read(HERE/'protocol.json.gz');m=read(HERE/'trained_model/policy.json');checks=read(HERE/'checks.json');extended=read(HERE/'symbolic_checks.json')
 compare=load('lightlike_document_compare',PRIOR/'s12_analyze.py').compare
 exact_rows=[r for r in s['rows'] if r['group'] in ['lightlike','symbolic','products','embedded']];exact=compare(exact_rows)
 native=s['native_ml'];groups=s['groups']
 audit=dict(changed_native_requests=0,prediction_seconds=[],last_repetition_attempts={method:dict(attempts=0,failed=0,outputs_without_attempt_records=0) for method in ['integrated','all_fixed','previous']})
 for row in s['rows']:
  if row['group']!='native':continue
  records=read(HERE/'model_test'/(row['case']+'.json.gz'))['results']
  r=records['integrated'];audit['changed_native_requests']+=r.get('selected_native_action') not in [None,m['fixed']]
  if r.get('prediction_seconds') is not None:audit['prediction_seconds'].append(r['prediction_seconds'])
  for method,rr in records.items():
   aa=[a for b in rr.get('blocks',[]) for a in b['result'].get('attempts',[])];z=audit['last_repetition_attempts'][method];z['attempts']+=len(aa);z['failed']+=sum(not a.get('success',False) for a in aa);z['outputs_without_attempt_records']+=not bool(aa)
 audit['median_prediction_seconds']=statistics.median(audit['prediction_seconds']) if audit['prediction_seconds'] else None
 write(HERE/'model_application_audit.json',audit)
 REPORT.mkdir(exist_ok=True)
 original=REPORT/'paper_before_lightlike.tex'
 if not original.exists():original.write_bytes((REPORT/'report.tex').read_bytes())
 (REPORT/'report.tex').write_text((HERE/'focused_main.tex').read_text())
 for n in ['focused_derivations.tex','focused_tensor_appendix.tex','focused_trees_appendix.tex','lightlike_appendix.tex']:(REPORT/n).write_bytes((HERE/n).read_bytes())
 text=r'''\section{Measured results}
\label{sec:results}
The following numbers are measurements of this study. The new test holds the exact identities and the selected model fixed. Table~\ref{tab:light-results} separates the physical groups and retains incomplete controls. A completed request must agree with its reference in every repetition.
\begin{table}[!htbp]\centering\small
\caption{Complete application times against the preceding application. Done gives preceding/new completions; times sum request medians on the matched completed subset only. A dash means no matched pair.}
\label{tab:light-results}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Requests & Done & Paired & Preceding (s) & New (s)\\\midrule
'''
 titles={'lightlike':'Zero-invariant tensor bubbles','symbolic':'Symbolic scalar masses','products':'Independent products, 2--13 loops','embedded':'Larger sectors with a zero-invariant sub-sector','ordinary_tensor':'Ordinary one-loop tensors','vacuum':'Connected vacuum checks','native':'Native two-loop box batches'}
 for g in ['lightlike','symbolic','products','embedded','ordinary_tensor','vacuum','native']:
  q=groups[g];old=f"{q['old_seconds']:.3f}" if q['matched_completed'] else '---';new=f"{q['new_seconds']:.3f}" if q['matched_completed'] else '---'
  text+=f"{titles[g]} & {q['old_completed']}/{q['new_completed']} & {q['matched_completed']} & {old} & {new}"+r' \\'+'\n'
 q=s['all'];text+=f"All {q['requests']} requests & {q['old_completed']}/{q['new_completed']} & {q['matched_completed']} & {q['old_seconds']:.3f} & {q['new_seconds']:.3f}"+r' \\\bottomrule\end{tabularx}\end{table}'+'\n\n'
 text+=f"The new application completes {q['new_completed']} of {q['requests']} requests, compared with {q['old_completed']} for the preceding application. The comparison contains {s['checks']:,} exact coefficient checks across the timed outputs. There are {s['reference_failures']} requests without a successful external reference. On the {q['matched_completed']} matched requests, summed median time changes from {q['old_seconds']:.3f} to {q['new_seconds']:.3f} seconds, a time ratio of {q['ratio']:.3f}, or {100*(1-q['ratio']):.1f}\\% less time. This decrease is incremental relative to the preceding implementation on the same new requests. It is not a comparison with unmodified Kira, and percentages from earlier workloads cannot be added to it. The new application is slower on {q['slower']} matched requests. These totals describe this finite collection and include native requests where the exact extension does not apply.\n\n"
 text+=r'\subsection{Exact identities and their integration}'+'\n'
 text+=f"The new exact domains comprise {exact['requests']} requests: zero-invariant tensor bubbles, symbolic scalar masses, independent products, and embedded sub-sectors. The new method completes {exact['new_completed']} and the preceding method completes {exact['old_completed']}. Their {exact['matched_completed']} matched requests take {exact['old_seconds']:.3f} and {exact['new_seconds']:.3f} seconds, respectively. The exact rules supply the change in this comparison; no learned action is required for these recognized inputs.\n\n"
 text+=f"Development verifies the seven direct-formula cases against Kira, checks signed IBP residuals, and compares {extended['substitution_checks']} symbolic-mass coefficients after rational substitutions. The larger-sector development check compares {extended['embedded_native_coefficient_checks']} coefficients with Kira. In the reserved test, {groups['embedded']['new_completed']} of the three embedded-sector requests complete. This checks that a formula used inside a recurrence produces the same physical reduction as native elimination.\n\n"
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/lightlike_exact.pdf}
\caption{Exact-extension results. The left panel compares completion counts, including failures. The right panel shows paired request times on logarithmic axes; points below the equal-time line favor the new method. Only completed, verified pairs appear in the time panel.}
\label{fig:light-exact}
\end{figure}
'''
 text+=r'\subsection{The added native ML choice}'+'\n'
 text+=f"Validation selects {m['selection']['count']} cost {'tree' if m['selection']['count']==1 else 'trees'} with maximum depth {m['selection']['depth']}, minimum leaf population {m['selection']['minimum']}, a saving margin of {100*m['margin']:.0f}\\%, and a failure score threshold of {m['failure_threshold']:.2f}. It {'enables' if m['enabled'] else 'disables'} the new model. The selected validation cost, including the prediction allowance and any failure penalties, is {m['selection']['cost']:.3f} seconds; the fixed choice gives {m['fixed_validation_seconds']:.3f} seconds. The selected fixed region is {m['fixed'].replace('sparse_','')}. These values determine deployment before the reserved test.\n\n"
 text+=f"In the 24 reserved native batches, the integrated method uses the new model on {s['native_model_used']} requests in the final repetition. Against the fixed-choice application, it completes {native['new_completed']} requests while the control completes {native['old_completed']}. The {native['matched_completed']} matched batches take {native['old_seconds']:.3f} seconds with the fixed choice and {native['new_seconds']:.3f} seconds with the integrated choice. The ratio is {native['ratio']:.3f}, with a central 95\\% request-resampling interval of $[{native['interval'][0]:.3f},{native['interval'][1]:.3f}]$. It is slower on {native['slower']} matched batches. "
 if native['interval'][1]<1:text+='This comparison supports an additional learned saving on these batches. '
 elif native['interval'][0]>1:text+='This comparison shows an increase over the fixed choice. '
 else:text+='The interval includes equal time, so this sample does not resolve a consistent additional saving. '
 text+='The exact formulas and native reduction interface are shared by these two controls. The learned failure check redirects predicted risky actions and inputs outside the new feature range to the verified fixed choice.\n\n'
 text+=f"Across the 72 native applications per method, the integrated method has {s['native_failed_applications']['integrated']} unverified applications, the fixed control has {s['native_failed_applications']['all_fixed']}, and the preceding application has {s['native_failed_applications']['previous']}. In the final repetition, the recorded rejection counts are {s['native_failure_gates']['predicted_failure_risk']} for predicted failure risk and {s['native_failure_gates']['outside_training_range']} for inputs outside the training feature range. These checks occur before the selected native reduction. The measured failure counts, rather than a zero predicted risk, determine whether failures were avoided in this test.\n\n"
 text+=f"The learned policy changes the fixed action on {audit['changed_native_requests']} of the 24 native requests in the final repetition. Its median measured loading and decision time is {1000*audit['median_prediction_seconds']:.3f} milliseconds. The saved final-repetition outputs give failed inner-attempt counts of {audit['last_repetition_attempts']['integrated']['failed']} for the integrated method, {audit['last_repetition_attempts']['all_fixed']['failed']} for the fixed control, and {audit['last_repetition_attempts']['previous']['failed']} for the preceding method. Interrupted outputs can lack inner-attempt records and remain in the separate application-failure counts. Inner attempts from the first two repetitions are not retained, so these inner-attempt counts refer only to the last repetition.\n\n"
 n=groups['native'];text+=f"Against the preceding native application, the {n['matched_completed']} matched batches change from {n['old_seconds']:.3f} to {n['new_seconds']:.3f} seconds. This comparison measures the change in the deployed policy, while the fixed control measures learned selection against one preselected region. Neither comparison measures a new elimination-row policy.\n\n"
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=.96\linewidth]{paper_figures/lightlike_native.pdf}
\caption{The native learned-choice comparison holds exact formulas and the native reduction interface fixed. Each point divides a request's integrated median time by its fixed-choice median. The horizontal line marks equal time. The aggregate ratio and its request-resampling interval appear separately; individual points show the observed variation across batches.}
\label{fig:light-native}
\end{figure}
'''
 text+=r'''\subsection{The other learned interventions}
Table~\ref{tab:retained-results} retains the main earlier controls needed to interpret the method. They use different workloads and cannot be multiplied into a cumulative speed factor. The equation-filter result supports that intervention on its tested domain, while the row results motivate its omission. The current combined experiment keeps equation filtering off and does not claim a joint seed-plus-equation gain.
\begin{table}[!htbp]\centering\small
\caption{Earlier measurements from this study, retained as separate evidence. A ratio below one means less time. Their full input definitions and measurements remain in the notes.}
\label{tab:retained-results}
\begin{tabularx}{\linewidth}{@{}YYr@{}}\toprule
Intervention & Control and workload & Time ratio\\\midrule
Earlier native seed model & Fixed region, 32 box batches: 156.383 to 150.663 s & 0.963\\
Equation selection & Native filter, 24 new-index batches: 72.295 to 67.478 s & 0.933\\
Original learned row model & Native row choices, 84 trials & 1.305\\
Compiled row-cost policy & Native row choices; geometric mean & 0.982\\\bottomrule
\end{tabularx}
\end{table}
The earlier seed comparison has interval $[0.937,0.984]$, and the equation comparison has interval $[0.928,0.940]$. The compiled row policy has interval $[0.959,1.003]$, which includes equal time. These intervals use the resampling procedure recorded for each original study. The native row algorithm remains in the retained workflow.

\subsection{Scope of the result}
The new exact identities cover their stated masses, powers, and kinematics, and the reserved comparison tests concrete instances of those identities. The independent products reach thirteen loops by factorization, while the connected vacuum checks use a one-scale tree. General coupled multiscale scattering at every loop order remains outside this evidence. The native build also has a finite integral-coordinate limit, documented in the notes; a loop count alone does not determine whether an arbitrary family can be reduced.

The learned test uses two graph types already represented during training, with new whole target batches and kinematic points. It does not establish transfer to every topology. The application keeps exact algebra and bounded recovery for supported native inputs, but neither a finite training search nor the present timings prove globally minimal reduction time. The practical result is a tested extension of the exact domain together with a separately measured policy for the remaining native work.
\FloatBarrier
'''
 (REPORT/'lightlike_results.tex').write_text(text)
 abstract=f"""\\begin{{abstract}}
We study the time required to decompose Feynman integrals into master integrals using Kira, exact analytic identities, and machine learning. The method applies recognized exact reductions before native elimination and uses measured-cost models to select seed regions for supported remaining requests. We extend the exact stage to zero-invariant two-point sectors with polynomial numerators and unequal, equal, or zero masses, including their occurrence inside larger one-loop reductions. Scalar formulas also retain symbolic masses. A frozen comparison contains 68 requests, including independent products through thirteen loops and 24 native two-loop box batches. The integrated method completes {q['new_completed']} requests and the preceding application completes {q['old_completed']}; their {q['matched_completed']} matched requests take {q['new_seconds']:.3f} and {q['old_seconds']:.3f} seconds, respectively. On {native['matched_completed']} matched native batches, learned selection takes {native['ratio']:.3f} times the fixed-choice cost, with a 95\\% interval of $[{native['interval'][0]:.3f},{native['interval'][1]:.3f}]$. We report exact and learned effects separately and omit learned row selection because its earlier tests did not establish a reliable benefit. The results apply to the defined integral domains and do not establish a universal high-loop speedup.
\\end{{abstract}}
"""
 (REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=f"""The measured method reduces decomposition time by applying exact identities where their structural conditions hold and reserving learned choices for the remaining native work. The new zero-invariant formula removes a singular-Gram obstruction in two-point sectors and applies to intermediate sub-sectors as well as complete bubble requests. Its derivation gives rational coefficients of tadpole masters, with separate equal-mass and zero-mass treatments. Independent products and previously derived one-scale tree formulas supply the stated high-loop domains.

The complete application finishes {q['new_completed']} of 68 reserved requests. On {q['matched_completed']} matched requests, its total of median times is {q['new_seconds']:.3f} seconds, compared with {q['old_seconds']:.3f} seconds for the preceding application. The native comparison with a fixed seed region gives ratio {native['ratio']:.3f} and interval $[{native['interval'][0]:.3f},{native['interval'][1]:.3f}]$. These controls separate the exact extension from the added learned choice. Earlier equation-filter measurements support its separate use, while the retained application omits learned row selection.

The tested domains determine the conclusion. Exact formulas require their stated propagator structure, and the new native model is tested on new batches within two known graph types. General coupled high-loop scattering, unrestricted symbolic kinematics, and globally fastest reduction paths remain unestablished. The notes preserve the failures and earlier comparisons so that completion and timing limits remain part of the result.
"""
 (REPORT/'paper_conclusion.tex').write_text(conclusion)
 # Preserve all prior studies; the new notes block adds only the current evidence.
 notes=(REPORT/'notes.tex').read_text();marker='LIGHTLIKE EXACT AND ML UPDATE';begin='% BEGIN CURRENT WORKFLOW UPDATE\n% '+marker;end='% '+marker+' END\n% END CURRENT WORKFLOW UPDATE'
 if begin in notes:
  stop=notes.index(end)+len(end)
  if notes[stop:stop+1]=='\n':stop+=1
  notes=notes[:notes.index(begin)]+notes[stop:]
 details=(HERE/'focused_derivations.tex').read_text().split('\\section{Measured-cost learning}',1)[1]
 blocks=[text,'\\section{Measured-cost learning}'+details,(HERE/'lightlike_appendix.tex').read_text()]
 blocks=['\\section{Focused exact and learned decomposition update}\nThe main paper now follows the physics method and its current measurements. Earlier experiments remain in these notes.\n']+blocks
 block='\n'.join(blocks)
 # The earlier notes already define the original integral and tensor labels.
 labels=set(re.findall(r'\\label\{([^}]+)\}',block));refs=set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',block))
 for label in labels|refs:block=block.replace('{'+label+'}','{notes-light-'+label+'}' if label in labels else '{'+{'eq:integral':'eq:general-integral','app:tensor-reduction':'app:notes-tensor-reduction','app:trees':'app:notes-vac-ml'}[label]+'}')
 pos=notes.index('\\bibliographystyle')
 notes=notes[:pos]+begin+'\n'+block+'\n'+end+'\n'+notes[pos:]
 (REPORT/'notes.tex').write_text(notes)
 # Keep main-paper citation/reference checks strict, and audit old measurements in retained sources.
 check=REPORT/'s01_check_paper.py';src=check.read_text()
 if 'retained_labels=' not in src:
  line="    labels=re.findall(r'\\\\label\\{([^}]+)\\}',source)"
  assert line in src
  src=src.replace(line,line+"\n    retained_labels=set(labels) | {x for p in HERE.glob('*.tex') for x in re.findall(r'\\\\label\\{([^}]+)\\}',p.read_text())}")
  lines=src.splitlines()
  for i,line in enumerate(lines):
   if i>160 and ' in labels' in line:lines[i]=line.replace(' in labels',' in retained_labels')
  check.write_text('\n'.join(lines)+'\n')
 make=REPORT/'Makefile';src=make.read_text();src=src if 'report.pdf: focused_derivations.tex' in src else src.replace('report.pdf: ','report.pdf: focused_derivations.tex focused_tensor_appendix.tex focused_trees_appendix.tex lightlike_results.tex lightlike_appendix.tex ',1);make.write_text(src)
 data=dict(summary=s,application_audit=audit,model={k:v for k,v in m.items() if k not in ['trees','failure_guard','minimum','maximum']},checks=checks,extended_checks={k:v for k,v in extended.items() if k!='records'},exact=exact)
 (REPORT/'lightlike_data.json').write_text(json.dumps(data,indent=2)+'\n')
 plot(s,exact_rows)
 print('Focused paper, notes, and figures written.',flush=True)

def plot(s,rows):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 groups=['lightlike','symbolic','products','embedded'];names=['Tensor bubbles','Symbolic masses','Products, 2–13 loops','Embedded sectors']
 fig,axs=plt.subplots(1,2,figsize=(6.4,3.5),constrained_layout=True)
 y=list(range(4));axs[0].barh([i-.18 for i in y],[s['groups'][g]['old_completed'] for g in groups],height=.34,color='#a55d3a',label='Preceding');axs[0].barh([i+.18 for i in y],[s['groups'][g]['new_completed'] for g in groups],height=.34,color='#236b8e',label='New exact stage');axs[0].set_yticks(y);axs[0].set_yticklabels(names);axs[0].invert_yaxis();axs[0].set(xlabel='Completed and verified requests',xlim=(0,21));axs[0].legend(frameon=False,fontsize=8)
 colors=['#236b8e','#9261a3','#398563','#c08031'];values=[]
 for g,name,col,mark in zip(groups,names,colors,['o','s','^','D']):
  rr=[r for r in rows if r['group']==g and all(r['success']['integrated']) and all(r['success']['previous'])];xx=[r['median_seconds']['previous'] for r in rr];yy=[r['median_seconds']['integrated'] for r in rr];values+=xx+yy
  if rr:axs[1].scatter(xx,yy,s=25,label=name,color=col,alpha=.8,marker=mark)
 if values:
  lo=min(values)*.75;hi=max(values)*1.4;axs[1].plot([lo,hi],[lo,hi],color='.5',linestyle='--',linewidth=1);axs[1].set(xscale='log',yscale='log',xlim=(lo,hi),ylim=(lo,hi))
 axs[1].set(xlabel='Preceding complete time (s)',ylabel='New complete time (s)');axs[1].legend(frameon=False,fontsize=7,loc='upper left')
 for ax in axs:ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(alpha=.15)
 fig.savefig(REPORT/'paper_figures/lightlike_exact.pdf');plt.close(fig)
 rr=[r for r in s['rows'] if r['group']=='native' and all(r['success']['integrated']) and all(r['success']['all_fixed'])];rr.sort(key=lambda r:r['median_seconds']['all_fixed']);q=s['native_ml'];ratios=[r['median_seconds']['integrated']/r['median_seconds']['all_fixed'] for r in rr]
 fig,ax=plt.subplots(figsize=(6.4,3.1),constrained_layout=True)
 for non,name,col in [(False,'Planar','#236b8e'),(True,'Nonplanar','#a55d3a')]:
  ids=[i for i,r in enumerate(rr) if ('nonplanar' in r['case'])==non];ax.scatter([i+1 for i in ids],[ratios[i] for i in ids],color=col,label=name,s=30,marker='s' if non else 'o')
 x=len(rr)+2;ax.errorbar([x],[q['ratio']],yerr=[[q['ratio']-q['interval'][0]],[q['interval'][1]-q['ratio']]],fmt='D',color='black',capsize=4,label='Aggregate and 95% interval');ax.axhline(1,color='.4',linestyle='--',linewidth=1)
 values=ratios+q['interval']+[1];span=max(.08,max(values)-min(values));ax.set(xlabel='Request, ordered by fixed-choice time; aggregate at right',ylabel='Integrated / fixed complete time',ylim=(min(values)-.15*span,max(values)+.25*span),xlim=(0,x+1));ax.legend(frameon=False,fontsize=8,ncol=3);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(axis='y',alpha=.2);fig.savefig(REPORT/'paper_figures/lightlike_native.pdf');plt.close(fig)
if __name__=='__main__':main()
