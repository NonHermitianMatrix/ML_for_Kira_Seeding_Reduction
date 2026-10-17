"""Write the measured seed-policy results and their mathematical definition."""
import json,re,shutil,os,statistics
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[2]/'.tools/cache/kira-cost-plots'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from s00_policy import *

def change(r):return f'{abs(1-r)*100:.1f}\\% '+('less' if r<=1 else 'more')+' time'
def interval(v):return '$['+f'{v[0]:.3f}, {v[1]:.3f}'+']$'
def main():
 d=rt.read(HERE/'summary.json');a=d['adaptive'];i=d['initial'];app=rt.read(HERE/'application/summary.json');report=ROOT/'report'
 integration=rt.read(HERE/'integration_test/summary.json');assert integration['complete'] and integration['all_exact']
 integration_records=[rt.read(p) for p in (HERE/'integration_test').glob('*.json.gz')]
 integration_rows=[dict(case=c,seconds={m:statistics.median(r['process_complete_seconds'] for r in integration_records if r['case']==c and r['method']==m) for m in ['previous','integrated']}) for c in sorted({r['case'] for r in integration_records})]
 integration_data=dict(complete=True,requests=len(integration_records),rows=integration_rows,all_exact=all(r['success'] for r in integration_records))
 inputs.write(HERE/'integration_test/timing_summary.json',integration_data)
 guide=HERE/'integration_test/README.md';s=guide.read_text()
 if 'timing_summary.json' not in s:guide.write_text(s+'`timing_summary.json` gives per-request median process times for both application choices.\nThe report generator computes it from the saved exact checks.\n')
 fitted_rows=[r for r in integration_rows if r['case'].startswith(('double_box_','nonplanar_box_'))]
 integrated_totals={m:sum(r['seconds'][m] for r in fitted_rows) for m in ['previous','integrated']}
 def result(data,control):
  x=data['comparisons']['learned_to_'+control]
  return change(x['ratio'])+', with a paired-repetition ratio interval of '+interval(x['paired_repetition_95_interval'])
 model_rows=[]
 for g,label in [('double_box','Planar box'),('nonplanar_box','Nonplanar box')]:
  f=d['models']['cost_'+g];name={'tree':'Tree','forest':'Random forest','extra':'Extra trees'}[f['kind']];model_rows.append(label+' & '+name+' ('+str(f['depth'])+') & '+str(len(f['training_cases']))+' & '+('Enabled' if f['enabled'] else 'Fixed boundary retained')+r'\\')
 enabled=[label for g,label in [('double_box','planar box'),('nonplanar_box','nonplanar box')] if d['models']['cost_'+g]['enabled']]
 deployment=('Validation enables request-dependent cost prediction for the '+' and '.join(enabled)+'. Other graph choices use their fixed sparse boundary.' if enabled else 'Validation disables both request-dependent cost predictors, so the broader deployment uses one fixed sparse boundary per graph. Its gain is therefore attributed to those selected boundaries. The first evolved-boundary experiment separately measures the learned search result.')
 timing_rows=[]
 for g,label in [('double_box','Planar box'),('nonplanar_box','Nonplanar box'),(None,'All matched')]:
  rows=[r for r in a['rows'] if g is None or r['graph']==g]
  vals=[sum(r['median_seconds'][m] for r in rows) for m in ['native','previous','fixed','learned']]
  timing_rows.append(label+' & '+str(len(rows))+' & '+' & '.join(f'{v:.3f}' for v in vals)+r'\\')
 text=r'''\section{Learning sparse seed regions from reduction time}
\label{sec:seed-geometry}
The batch study leaves little additional saving among its predefined partitions. We therefore change the equations available to Kira more directly. A learned boundary selects individual seeds around the requested numerator powers before equation generation. Kira then applies its usual IBP operators to those seeds. This follows the motivation of sparse target-dependent seeding~\cite{TubeSeeding2026}, while the boundary parameters in this study are fitted through complete reductions with symbolic dimension.

\subsection{The seed model and its training data}
The model describes a surrounding region around each target's numerator-power box. Its width can depend on the seed rank and on how many physical propagators are absent from its sector. It also controls the largest seed rank in each sector. Appendix~\ref{app:seed-geometry} defines these boundaries, derives the distance used by the model, and gives a counting example that explains why a narrow region can avoid many seeds at higher numerator rank.

We first fit the boundary parameters through evolutionary search. Each proposal runs Kira and receives a score from the measured time needed to reach the prescribed masters and pass an exact coefficient check. The score includes unsuccessful attempts and native recovery. Thus the labels describe completed calculations rather than membership in a previously selected equation set. Three training requests per graph start this search; separate validation selects the first fitted boundary. An independent planar-box comparison then tests that boundary on eight new kinematic requests.

The second stage adds twelve training requests per graph and fits models that predict the cost of different seed boundaries. These requests contain single-direction and distributed numerators of ranks two, three, and four. The candidate boundaries include those found by the first search, independent changes to the rank allowance, fixed surrounding widths, and unfiltered Kira. Trees and forests predict the log complete-time ratio of each candidate~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}. Ten validation requests per graph select the model, its decision margin, and a fixed sparse control. The predictor is enabled only when validation gives at least three percent less recorded cost than that fixed control. When validation disables prediction, the deployed policy uses the selected fixed boundary. Table~\ref{tab:seed-geometry-models} gives the selected models. The independent timing tests include the cost of loading and applying them.

\begin{table}[!htbp]\centering\small
\caption{Cost predictors selected before the reserved comparisons. Each graph also has a separately selected fixed sparse control.}
\label{tab:seed-geometry-models}
\begin{tabular}{@{}llll@{}}\toprule
Graph & Predictor (depth) & Training requests & Deployment\\\midrule
MODELS
\bottomrule\end{tabular}\end{table}

DEPLOYMENT_DECISION

\subsection{Independent reductions and controls}
The first evolved planar-box boundary gives INITIAL_NATIVE relative to tuned native Kira. Relative to the fixed surrounding-width control, it gives INITIAL_FIXED. This comparison contains INITIAL_TIMINGS timed reductions, and all successful outputs pass exact checks. The boundary remains fixed throughout this test.

\begin{table}[!htbp]\centering\small
\caption{First independent planar-box comparison. Times are sums of per-request medians over eight requests, with seven repetitions per method. The learned boundary is fitted before this comparison.}
\label{tab:seed-geometry-initial}
\begin{tabular}{@{}lr@{}}\toprule
Method & Complete time (s)\\\midrule
Tuned native Kira & INITIAL_NATIVE_SECONDS\\
Fixed surrounding width & INITIAL_FIXED_SECONDS\\
Evolved seed boundary & INITIAL_LEARNED_SECONDS\\
\bottomrule\end{tabular}\end{table}

The second comparison uses ADAPTIVE_COUNT matched requests from the planar and nonplanar two-loop boxes, with seven repetitions per method. All methods use the same Kira executable, exact preparation, master basis, and native row elimination. The native control disables every learned choice. The fixed sparse control uses one validation-selected boundary per graph, including boundaries discovered during training, and performs no request-dependent cost prediction. The previous application retains the earlier published batch and equation policies. These controls separate the effect of sparse seeding from the added benefit of predicting which boundary to use for a particular target.

The complete selected workflow gives ADAPTIVE_NATIVE relative to tuned native Kira and ADAPTIVE_PREVIOUS relative to the previous application. Relative to the fixed sparse control, it gives ADAPTIVE_FIXED. Table~\ref{tab:seed-geometry-times} reports the measured times for both graphs. The comparison contains ADAPTIVE_TIMINGS timed reductions and CHECKS exact coefficient comparisons. Failed reference requests number FAILED_REFERENCES, and failed timed reductions number FAILED_TRIALS; these remain in the evidence record.

\begin{table}[!htbp]\centering\small
\caption{Sum of per-request median complete times, in seconds. Native uses the tuned outer bounds with all ML disabled. Fixed uses one sparse boundary per graph. Selected uses the frozen deployment policy.}
\label{tab:seed-geometry-times}
\begin{tabular}{@{}lrrrrr@{}}\toprule
Graph & Requests & Native & Previous & Fixed & Selected\\\midrule
TIMINGS
\bottomrule\end{tabular}\end{table}

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/seed_geometry_times.pdf}
\caption{Left: complete-time ratios to tuned native Kira, summed within each graph. Right: the selected-to-fixed-sparse ratio for each reserved request. Labels P and N identify the planar and nonplanar graphs; 1 and 2 identify the two reserved kinematic profiles. Each label gives the number of powered numerator directions and the rank $R$. The dashed lines mark equal time. Values below one indicate a saving. The right panel shows the measured difference from using the fixed sparse rule.}
\label{fig:seed-geometry-times}
\end{figure}
\FloatBarrier

A separate application check starts a fresh process for each request and supplies only the physical definition, target indices, and master basis. It includes imports, model loading, input and output, process exit, and a subsequent exact check. It completes APP_REQUESTS runs over APP_MATCHED matched requests. Its selected total is APP_SELECTED seconds, compared with APP_NATIVE seconds for native choices and APP_FIXED seconds for the fixed sparse control. These requests are a predefined subset of the reserved test, so they check application overhead without adding graph coverage.

The complete integrated application also passes 24 fresh-process checks. These use two of the reserved two-loop requests, one previously tested four-loop native request, and an eight-loop massless banana request. For the two-loop requests, the summed median complete time is INTEGRATED_SELECTED seconds, compared with INTEGRATED_PREVIOUS seconds for the preceding complete application. The other inputs check that the existing native and analytic methods remain available and exact. They do not extend the sparse model's fitted domain.

These results concern numerator ranks two through four, unit positive physical powers, rational kinematic values, symbolic dimension, and supplied bases in two known two-loop structures. The reported production times exclude offline training and construction of the independent reference basis. Some index patterns recur between training and testing. Development probes at other loop orders do not extend the fitted model's validated domain. The application retains its earlier exact methods and native fallback outside this domain. The comparison establishes the measured effects of the new seed policy; it does not establish a universal speedup or a globally optimal reduction path.
'''
 values=dict(MODELS='\n'.join(model_rows),TIMINGS='\n'.join(timing_rows),INITIAL_NATIVE=result(i,'native'),INITIAL_FIXED=result(i,'fixed'),INITIAL_TIMINGS=str(i['timings']),ADAPTIVE_COUNT=str(a['matched']),ADAPTIVE_NATIVE=result(a,'native'),ADAPTIVE_PREVIOUS=result(a,'previous'),ADAPTIVE_FIXED=result(a,'fixed'),ADAPTIVE_TIMINGS=str(a['timings']),CHECKS=str(a['coefficient_checks']),FAILED_REFERENCES=str(len(a['failed_references'])),FAILED_TRIALS=str(len(a['failed_trials'])),APP_REQUESTS=str(app['requests']),APP_MATCHED=str(app['matched']),APP_SELECTED=f"{app['totals']['learned']:.3f}",APP_NATIVE=f"{app['totals']['native']:.3f}",APP_FIXED=f"{app['totals']['fixed']:.3f}")
 values.update(INITIAL_NATIVE_SECONDS=f"{i['totals']['native']:.3f}",INITIAL_FIXED_SECONDS=f"{i['totals']['fixed']:.3f}",INITIAL_LEARNED_SECONDS=f"{i['totals']['learned']:.3f}",DEPLOYMENT_DECISION=deployment,INTEGRATED_SELECTED=f"{integrated_totals['integrated']:.3f}",INTEGRATED_PREVIOUS=f"{integrated_totals['previous']:.3f}")
 for k in sorted(values,key=len,reverse=True):text=text.replace(k,values[k])
 (report/'seed_geometry_results.tex').write_text(text)
 shutil.copyfile(HERE/'seed_geometry_appendix.tex',report/'seed_geometry_appendix.tex')
 fig,axes=plt.subplots(1,2,figsize=(6.3,5.4),constrained_layout=True)
 colors={'fixed':'#3377aa','learned':'#b23a48','previous':'#777777'};labels={'fixed':'Fixed sparse','learned':'Selected','previous':'Previous'}
 for j,(g,label) in enumerate([('double_box','Planar'),('nonplanar_box','Nonplanar')]):
  rows=[r for r in a['rows'] if r['graph']==g];base=sum(r['median_seconds']['native'] for r in rows)
  for k,m in enumerate(['previous','fixed','learned']):
   axes[0].plot(sum(r['median_seconds'][m] for r in rows)/base,j+(k-1)*.16,'o',color=colors[m],label=labels[m] if j==0 else None)
 axes[0].set_yticks([0,1]);axes[0].set_yticklabels(['Planar box','Nonplanar box'],fontsize=9);axes[0].set_xlabel('Complete time /\ntuned native time',fontsize=9);axes[0].legend(frameon=False,fontsize=8)
 xs=[]
 for j,r in enumerate(a['rows']):
  x=r['median_seconds']['learned']/r['median_seconds']['fixed'];xs.append(x);axes[1].plot(x,j,'o',markersize=4,color='#b23a48')
 axes[1].set_yticks(range(len(a['rows'])));axes[1].set_yticklabels([('P' if r['graph']=='double_box' else 'N')+str(int(r['case'].split('_h')[1].split('_')[0])-850)+': '+('one' if 'single' in r['case'] else 'two')+', R='+r['case'][-1] for r in a['rows']],fontsize=8)
 axes[1].invert_yaxis();axes[1].set_xlabel('Selected time /\nfixed sparse time',fontsize=9)
 for ax in axes:
  ax.axvline(1,color='black',linestyle='--',linewidth=.8);ax.grid(axis='x',alpha=.2);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
  lo,hi=ax.get_xlim();ax.set_xlim(max(0,min(lo,1)-.02),max(hi,1)+.02)
 fig.savefig(report/'paper_figures/seed_geometry_times.pdf');plt.close(fig)
 paper=report/'report.tex';s=paper.read_text()
 if '\\input{seed_geometry_results}' not in s:s=s.replace('\\input{batch_policy_results}','\\input{batch_policy_results}\n\\input{seed_geometry_results}',1)
 if '\\input{seed_geometry_appendix}' not in s:s=s.replace('\\input{massless_banana_appendix}','\\input{massless_banana_appendix}\n\\input{seed_geometry_appendix}',1)
 paragraph='The first evolved seed boundary gives '+result(i,'native')+' relative to tuned native Kira on eight planar two-loop requests. Its added saving relative to the fixed surrounding-width control is '+result(i,'fixed')+'. The broader sparse-seed workflow in Section~\\ref{sec:seed-geometry} gives '+result(a,'native')+' relative to tuned native Kira on '+str(a['matched'])+' matched two-loop requests. Its comparison with the fixed sparse control gives '+result(a,'fixed')+'. These results use separate workloads from the earlier equation-filter and batch tests.\n'
 for marker,anchor in [('OVERALL','\\subsection{What the model comparisons establish}'),('CONCLUSION','\\section{Conclusion}')]:
  block='% BEGIN SEED GEOMETRY '+marker+'\n'+paragraph+'% END SEED GEOMETRY '+marker+'\n'
  pattern=r'% BEGIN SEED GEOMETRY '+marker+r'\n.*?% END SEED GEOMETRY '+marker+r'\n'
  if re.search(pattern,s,re.S):s=re.sub(pattern,lambda _:block,s,flags=re.S)
  else:s=s.replace(anchor,anchor+'\n'+block,1)
 abstract='Integration-by-parts reduction expresses Feynman integrals in a master basis. We train seed boundaries and equation filters to reduce the algebraic work performed by Kira, using complete reduction time to assess their benefit. An evolved seed boundary gives '+change(i['comparisons']['learned_to_native']['ratio'])+' than tuned native Kira and '+change(i['comparisons']['learned_to_fixed']['ratio'])+' than a fixed surrounding-width control on eight planar two-loop requests. A broader sparse-seed comparison gives '+change(a['comparisons']['learned_to_native']['ratio'])+' than tuned native Kira on '+str(a['matched'])+' matched planar and nonplanar requests, with '+change(a['comparisons']['learned_to_fixed']['ratio'])+' than the fixed sparse control. Its request-dependent cost predictors are retained only when separate validation supports their use. An earlier equation-filter study gives 4.8\\% less time across 68 matched batches at one through four loops. Learned row selection remains omitted because its tests show no reliable complete-time benefit. These native comparisons use rational kinematics, symbolic dimension, and supplied master bases; their timings include model decisions, equation generation, algebra, exact checks, and recovery. Every successful output matches its exact reference. A separate analytic specialization gives speedups of 21.3--357.8 times for scalar massless banana targets at one through five loops. The experiments establish gains within their stated domains, with separate attribution for learned choices and exact formulas.'
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,count=1,flags=re.S)
 intro='We then train a seed boundary directly from complete Kira times. This model changes which seeds generate identities, and a second model predicts which fitted boundary to use for a target. The comparison includes tuned native Kira, a fixed sparse boundary, and the preceding application. It therefore tests both the benefit of a learned region and the additional value of selecting a region for each request.\n\n'
 if intro not in s:s=s.replace('We first define the notation used in this paper',intro+'We first define the notation used in this paper',1)
 rows='Evolved seed boundary & Eight planar two-loop targets & '+change(i['comparisons']['learned_to_native']['ratio'])+' than tuned native; '+change(i['comparisons']['learned_to_fixed']['ratio'])+' than fixed width'+r'\\'+'\nSparse-seed deployment & '+str(a['matched'])+' planar and nonplanar targets & '+change(a['comparisons']['learned_to_native']['ratio'])+' than tuned native; '+change(a['comparisons']['learned_to_previous']['ratio'])+' than previous'+r'\\'+'\n'
 if '% BEGIN SEED GEOMETRY TABLE' not in s:s=s.replace('% BEGIN BATCH POLICY TABLE','% BEGIN SEED GEOMETRY TABLE\n'+rows+'% END SEED GEOMETRY TABLE\n% BEGIN BATCH POLICY TABLE',1)
 paper.write_text(s)
 notes=report/'notes.tex';s=notes.read_text()
 if '\\input{seed_geometry_results}' not in s:s=s.replace('\\input{batch_policy_results}','\\input{batch_policy_results}\n\\input{seed_geometry_results}',1)
 if '\\input{seed_geometry_appendix}' not in s:s=s.replace('\\input{massless_banana_appendix}','\\input{massless_banana_appendix}\n\\input{seed_geometry_appendix}',1)
 notes.write_text(s)
 checker=report/'s01_check_paper.py';s=checker.read_text();s=s.replace("'massless_banana_appendix.tex']","'massless_banana_appendix.tex','seed_geometry_results.tex','seed_geometry_appendix.tex']");checker.write_text(s)
 make=report/'Makefile';s=make.read_text()
 if 'report.pdf: seed_geometry_results.tex' not in s:s=s.replace('report.pdf:','report.pdf: seed_geometry_results.tex seed_geometry_appendix.tex',1)
 make.write_text(s)
 # Add only missing external bibliography entries to the notes bibliography.
 existing=(report/'references.bib').read_text()+(report/'type_specialist_references.bib').read_text();bib=(report/'paper_references.bib').read_text()
 for key in ['TubeSeeding2026','CART1984','Breiman2001Forest','Geurts2006ExtraTrees']:
  if re.search(r'@\w+\{'+key+r',',existing):continue
  m=re.search(r'@\w+\{'+key+r',.*?(?=\n@|\Z)',bib,re.S);assert m,key
  with (report/'type_specialist_references.bib').open('a') as f:f.write('\n'+m.group(0)+'\n')
 inputs.write(report/'seed_geometry_data.json',dict(initial=i,adaptive=a,application=app,integration=integration_data,models={g:{k:v for k,v in m.items() if k not in ['model','signature']} for g,m in d['models'].items()}))
 print('Seed geometry results written',flush=True)
if __name__=='__main__':main()
