"""Write measured physics and ML results into both maintained documents."""
import re,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from s00_engine import *

def change(r):return f'{abs(1-r)*100:.1f}\\% '+('less' if r<=1 else 'more')+' time'
def result(c):
 lo,hi=c['paired_repetition_95_interval'];return change(c['ratio'])+f', with time-ratio interval $[{lo:.3f},{hi:.3f}]$'
def replace(s,key,body,anchor):
 block='% BEGIN '+key+'\n'+body+'\n% END '+key+'\n';pat=r'% BEGIN '+re.escape(key)+r'\n.*?% END '+re.escape(key)+r'\n'
 return re.sub(pat,lambda _:block,s,flags=re.S) if re.search(pat,s,re.S) else s.replace(anchor,anchor+'\n'+block,1)

def main():
 d=rt.read(HERE/'summary.json');assert d['complete'] and d['all_exact'];report=ROOT/'report';app=d['application']
 models=[];validation_outcomes=[]
 for g,label in [('double_box','Planar'),('nonplanar_box','Nonplanar')]:
  m=d['models'][g];description={'tree':'Regression tree','extra':'48 extremely randomized trees','forest':'48 random-forest trees'}[m['kind']]
  decision='Previous application retained' if not m['deploy'] else 'Cost prediction enabled' if m['enabled'] else 'Fixed configuration retained'
  validation_outcomes.append('The '+label.lower()+' replacement gives '+change(m['previous_validation_ratio'])+' than the preceding application on validation.')
  models.append(label+' & '+description+f", maximum depth {m['depth']} & "+decision+r'\\')
 rows=[]
 for g,label in [('double_box','Planar'),('nonplanar_box','Nonplanar'),(None,'Total')]:
  t=d['by_graph'][g]['totals'] if g else d['totals'];rows.append(label+' & '+' & '.join(f'{t[m]:.3f}' for m in ['native','previous','fixed','learned'])+r'\\')
 a=d['comparisons'];b=app['comparisons']
 attribution=[]
 for g,label in [('double_box','planar'),('nonplanar_box','nonplanar')]:
  m=d['models'][g]
  if m['deploy'] and m['enabled']:
   attribution.append('For the '+label+' graph, where the new prediction is enabled, the selected-to-fixed comparison gives '+result(d['by_graph'][g]['comparisons']['learned_to_fixed'])+'. Both methods use the same candidate configurations, exact implementation, and recovery rule, so this comparison isolates request-dependent model selection.')
  elif not m['deploy']:
   attribution.append('For the '+label+' graph, validation retains the preceding application. Its difference from the new fixed control includes the configuration choice and timing variation; it supplies no evidence of a gain from the new predictor.')
  else:attribution.append('For the '+label+' graph, validation retains a fixed configuration. Its saving comes from that fixed choice.')
 if all(not m['deploy'] for m in d['models'].values()):
  attribution=['The selected-to-fixed differences include configuration choices inherited from the preceding application. These comparisons therefore assess complete configurations and provide no evidence of a gain from the new predictors.']
 template=r'''\section{Joint seed choices and exact scale reuse}
\label{sec:joint-policy}
The preceding study reduces unnecessary equation generation, but some sparse choices still require a repeated calculation. To reduce this cost, we train new policies that select a seed boundary and Kira configuration together, then compare them with the preceding ML application. Validation retains the preceding application for both graphs because neither replacement clears the required improvement threshold. We add an exact scaling relation that reuses a completed reduction at a different overall momentum scale. The retained ML application performs the first reduction, and the exact identity can remove later reductions with matching dimensionless kinematics.

\subsection{Learning a complete reduction configuration}
The candidate configurations combine sparse boundaries with Kira's integral-ordering and internal propagator-permutation options~\cite{Kira2,Kira3}. The model chooses a configuration before equation generation. Kira then uses its native elimination procedure, and the earlier learned row policy remains omitted. Development reductions determine the candidate set, while separate training reductions supply the complete time of each candidate, including failed attempts and recovery. This follows the same cost-based principle as the preceding seed-boundary study; sparse seed searches also motivate the work in Ref.~\cite{TubeSeeding2026}.

We compare regression trees, random forests, and extremely randomized trees~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}. Each predicts candidate log-time ratios from 68 features describing the integral family and target powers. Validation selects the model, its decision margin, and a fixed configuration for each graph. The model is enabled only when validation gives at least 2\% less time than the fixed choice, and the new deployment must also improve on the preceding application by at least 2\%. Otherwise the preceding application remains in use. VALIDATIONOUTCOMES Both improvements fall below the predefined threshold, so the following tests retain the preceding ML decisions. Appendix~\ref{app:joint-policy} specifies the candidates, inputs, training objective, and exact target definitions.

\begin{table}[!htbp]\centering\small
\caption{Models selected before testing. The deployment condition uses validation times only.}
\label{tab:joint-models}
\begin{tabular}{@{}p{0.13\linewidth}p{0.41\linewidth}p{0.38\linewidth}@{}}\toprule
Graph & Selected fitted model & Deployment\\\midrule
MODELROWS
\bottomrule\end{tabular}\end{table}

\subsection{First-request time on separate test inputs}
The test contains 24 requests from the same two massless two-loop graph structures, at new rational kinematic profiles. Targets have unit positive physical powers and numerator ranks two through four, with either one or two powered auxiliary entries. Each graph has twelve training, twelve validation, and twelve test requests. Some target index patterns recur between the splits. Five repetitions rotate the four methods on the same worker for each request, using one Kira thread. The main test performs no result reuse.

The native control disables all ML and uses the tuned outer seed bounds. The fixed control uses one validation-selected seed and ordering configuration per graph, with no prediction or model loading. The previous control uses the preceding complete application. The selected method wraps that same application with the new input checks and optional reuse interface. Since validation disabled both replacements, its first-request comparison with the previous control measures this added interface and timing variation. All methods receive the same master basis, and the timer includes input preparation, configuration selection, equation generation, exact algebra, coefficient checks, and every retry. Master discovery and offline model training precede these production timings.

Table~\ref{tab:joint-times} gives the sum of per-request medians. Relative to the preceding application, the selected method gives PREVIOUSRESULT. Relative to tuned native Kira, it gives NATIVERESULT. Its comparison with the fixed control gives FIXEDRESULT. These intervals use paired resampling of the five repetitions on the fixed test workload. They describe timing variation and do not establish performance for unseen graph structures. All MAINTIMINGS timed reductions pass CHECKS exact coefficient comparisons. The retained data include individual slower requests and all failed first attempts.

Across the five repetitions, the preceding application makes PREVIOUSRETRIES additional reduction attempts, the fixed control makes FIXEDRETRIES, and the selected method makes SELECTEDRETRIES. These counts identify repeated algebra caused by an insufficient first choice; their costs are already included in the reported times.

ATTRIBUTION

\begin{table}[!htbp]\centering\small
\caption{Complete first-request times, in seconds, summed over per-request medians. There are twelve reserved requests per graph.}
\label{tab:joint-times}
\begin{tabular}{@{}lrrrr@{}}\toprule
Graph & Tuned native & Previous & Fixed & Selected\\\midrule
TIMINGROWS
\bottomrule\end{tabular}\end{table}

\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/joint_policy_times.pdf}
\caption{Left: the selected-to-previous complete-time ratio for each reserved request, including slower cases. P and N identify the planar and nonplanar graphs, 1 and 2 identify the two kinematic profiles, and the labels give the numerator pattern and rank. Right: aggregate time for the four scale sequences, normalized to the preceding application without reuse. Every sequence includes its first Kira reduction. Dashed lines mark equal time. The panels have separate workloads and their ratios cannot be multiplied.}
\label{fig:joint-times}
\end{figure}
\FloatBarrier

\subsection{Exact reuse when only the overall scale changes}
For a massless family with homogeneous quadratic inverse propagators, a common positive change of all external scalar products gives an exact relation between reduction coefficients. If $\boldsymbol b_m$ is the index vector of master $m$, define $\nu(\boldsymbol a)=\sum_i a_i$. Then
\begin{equation}
 r_{\boldsymbol a m}(\lambda\boldsymbol x,d)
 =\lambda^{\nu(\boldsymbol b_m)-\nu(\boldsymbol a)}
  r_{\boldsymbol a m}(\boldsymbol x,d),\qquad\lambda>0.
 \label{eq:joint-scale-rule}
\end{equation}
Appendix~\ref{app:joint-policy} derives this identity by scaling the integration momenta. Its exponent is an integer, and a rational scale therefore gives an exact rational multiplier. The application checks the graph, target indices, supplied basis, and every dimensionless kinematic ratio before reusing an earlier result. Changed ratios, masses, or symbolic kinematic values continue through the reduction application. Reuse supplies no benefit before a matching exact result exists.

We test four predefined rank-four requests, two from each graph, in sequences with scale factors $1$, $3/2$, and $2$. Each sequence starts a fresh process and includes the initial Kira reduction, imports, model loading, input and output, exact transformation, and the subsequent independent coefficient checks. Three repetitions and four methods give APPSEQUENCES measured sequences containing APPREQUESTS requests. Independent native reductions at every scale supply the checks; their coefficients never enter the application inputs.

We sum the median sequence times over the four base requests. Under this measure, the selected policy with scale reuse uses APPSELECTED seconds, compared with APPPREVIOUS seconds for the preceding application without reuse and APPLEARNED seconds for the selected policy without reuse. The resulting change relative to the preceding application is APPPREVIOUSRESULT, while reuse alone changes the selected policy's time by APPREUSERESULT. A fixed configuration with the same exact reuse uses APPFIXED seconds; the selected-to-fixed-reuse comparison gives APPFIXEDRESULT. All transformed outputs pass exact checks. These sequence results measure the benefit of repeated dimensionless kinematics, and remain separate from the first-request model comparison.

The deployed application combines the retained ML application with this exact reuse and retains the existing analytic and native paths outside its fitted domain. Eight further fresh-process checks reproduce the earlier four-loop native and eight-loop analytic results. These checks preserve existing behavior and do not extend the new model's fitted range. The new timing evidence covers known two-loop boxes, rational kinematics, symbolic dimension, and supplied bases. It does not establish a fastest possible strategy for arbitrary integrals or unrestricted loop order.
'''
 vals=dict(VALIDATIONOUTCOMES=' '.join(validation_outcomes),ATTRIBUTION='\n\n'.join(attribution),MODELROWS='\n'.join(models),TIMINGROWS='\n'.join(rows),PREVIOUSRESULT=result(a['learned_to_previous']),NATIVERESULT=result(a['learned_to_native']),FIXEDRESULT=result(a['learned_to_fixed']),MAINTIMINGS=str(d['timings']),CHECKS=str(d['coefficient_checks']),APPSEQUENCES=str(app['sequences']),APPREQUESTS=str(app['requests']),APPSELECTED=f"{app['totals']['learned_reuse']:.3f}",APPPREVIOUS=f"{app['totals']['previous']:.3f}",APPLEARNED=f"{app['totals']['learned']:.3f}",APPFIXED=f"{app['totals']['fixed_reuse']:.3f}",APPPREVIOUSRESULT=result(b['learned_reuse_to_previous']),APPREUSERESULT=result(b['learned_reuse_to_learned']),APPFIXEDRESULT=result(b['learned_reuse_to_fixed_reuse']))
 vals.update(PREVIOUSRETRIES=str(d['additional_attempts']['previous']),FIXEDRETRIES=str(d['additional_attempts']['fixed']),SELECTEDRETRIES=str(d['additional_attempts']['learned']))
 for key in sorted(vals,key=len,reverse=True):template=template.replace(key,vals[key])
 (report/'joint_policy_results.tex').write_text(template)
 shutil.copyfile(HERE/'joint_policy_appendix.tex',report/'joint_policy_appendix.tex')
 plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(1,2,figsize=(6.4,5.9),gridspec_kw={'width_ratios':[1.1,1]},constrained_layout=True)
 values=[];labels=[]
 for i,row in enumerate(d['rows']):
  ratio=row['median_seconds']['learned']/row['median_seconds']['previous'];values.append(ratio)
  suffix=row['case'].split('_h')[1];profile,shape=suffix.split('_')
  label=('P' if row['graph']=='double_box' else 'N')+str(int(profile)-930)+': '+('one' if 'single' in shape else 'two')+', R='+shape[-1];labels.append(label)
  axes[0].plot(ratio,i,'o',color='#245c8a' if row['graph']=='double_box' else '#b04632',markersize=4)
 axes[0].set_yticks(range(len(labels)));axes[0].set_yticklabels(labels,fontsize=7.5);axes[0].invert_yaxis();axes[0].set_xlabel('Selected time / previous time')
 axes[0].set_xlim(max(0,min(values+[1])-.04),max(values+[1])+.04)
 colors=['#555555','#245c8a','#b18b35','#b04632']
 names=['Previous, no reuse','Selected, no reuse','Fixed + reuse','Selected + reuse']
 for i,method in enumerate(['previous','learned','fixed_reuse','learned_reuse']):
  v=app['totals'][method]/app['totals']['previous'];axes[1].plot(v,i,'o',color=colors[i],markersize=6);axes[1].text(v+.025,i,f'{v:.3f}',va='center',fontsize=8)
 axes[1].set_yticks(range(4));axes[1].set_yticklabels(names,fontsize=8);axes[1].invert_yaxis();axes[1].set_ylim(3.8,-.8);axes[1].set_xlabel('Sequence time / previous time')
 hi=max(app['totals'][m]/app['totals']['previous'] for m in app['totals']);axes[1].set_xlim(0,max(1,hi)+.2)
 axes[0].set_title('First requests: retained ML',fontsize=9);axes[1].set_title('Scale reuse includes first solve',fontsize=9)
 for ax in axes:ax.axvline(1,color='black',ls='--',lw=.8);ax.grid(axis='x',alpha=.2)
 fig.savefig(report/'paper_figures/joint_policy_times.pdf');plt.close(fig)
 paper=report/'report.tex';s=paper.read_text()
 if '\\input{joint_policy_results}' not in s:s=s.replace('\\input{seed_geometry_results}','\\input{seed_geometry_results}\n\\input{joint_policy_results}',1)
 if '\\input{joint_policy_appendix}' not in s:s=s.replace('\\input{seed_geometry_appendix}','\\input{seed_geometry_appendix}\n\\input{joint_policy_appendix}',1)
 intro='The final study tests joint choices of seed boundaries and Kira settings using complete reduction time, including retries. Neither new predictor improves enough to replace the preceding ML application. We retain that application and add exact reuse when all invariants change by the same positive factor. Separate tests measure first-request time and sequence time with the initial reduction included.\n'
 s=replace(s,'JOINT POLICY INTRO',intro,'It therefore tests both the benefit of a learned region and the additional value of selecting a region for each request.')
 paragraph='Section~\\ref{sec:joint-policy} retains the preceding ML application because neither new joint predictor clears the 2\\% validation threshold. On 24 first requests, the retained application with the new interface gives '+result(a['learned_to_previous'])+' relative to its preceding interface. This difference supplies no evidence of a gain from the new predictors. The separate scale sequences give '+change(b['learned_reuse_to_previous']['ratio'])+' than the preceding application without reuse, including the initial Kira solve. This additional saving comes from the derived scale identity, while the first reduction still uses the preceding ML decisions.'
 s=replace(s,'JOINT POLICY OVERALL',paragraph,'\\subsection{What the model comparisons establish}')
 s=replace(s,'JOINT POLICY CONCLUSION',paragraph,'\\section{Conclusion}')
 table='Retained ML, new interface & 24 first requests; two-loop boxes & '+change(a['learned_to_previous']['ratio'])+' than previous; '+change(a['learned_to_fixed']['ratio'])+' than fixed'+r'\\'+'\nScale reuse with ML & Four three-scale sequences & '+change(b['learned_reuse_to_previous']['ratio'])+' than previous, including first solve'+r'\\'
 s=replace(s,'JOINT POLICY TABLE',table,'% END SEED GEOMETRY TABLE')
 abstract='Integration-by-parts reduction expresses Feynman integrals in a master basis. We train models to select seeds and equations before Kira performs the exact algebra, using complete reduction time as the cost. We also test new models that jointly select seed boundaries and Kira settings. Validation retains the preceding ML application for both tested graphs because the replacements do not reach the required 2\\% improvement. On 24 reserved planar and nonplanar two-loop requests, the retained workflow gives '+change(a['learned_to_native']['ratio'])+' than tuned native Kira. A derived scale identity reuses completed reductions when all invariants change by a common positive factor. Four three-scale sequences give '+change(b['learned_reuse_to_previous']['ratio'])+' than the preceding application without reuse, with the first reduction included. All timed outputs pass exact coefficient checks. These tests use rational kinematics, symbolic dimension, and supplied master bases; timings include decisions, algebra, checks, and retries. Earlier equation-filter tests give 4.8\\% less time on 68 matched batches at one through four loops. Learned row selection remains omitted because its tests show no reliable gain. We report learned and exact-method gains separately within their tested physical domains.'
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',s,count=1,flags=re.S);paper.write_text(s)
 notes=report/'notes.tex';s=notes.read_text()
 current='\\paragraph{Current measured method.} '+paragraph+' All 480 first-request reductions and 144 requests in the scale sequences pass exact coefficient checks. The tests use the two known massless two-loop box graphs at rational kinematics, with symbolic dimension and supplied masters.'
 s=re.sub(r'% BEGIN CURRENT WORKFLOW UPDATE\n.*?% END CURRENT WORKFLOW UPDATE\n',lambda _:'% BEGIN CURRENT WORKFLOW UPDATE\n'+current+'\n% END CURRENT WORKFLOW UPDATE\n',s,count=1,flags=re.S)
 s=s.replace('The latest comparison keeps every trained model fixed and reduces exact preparation around its decisions.','The preparation comparison keeps every trained model fixed and reduces exact preparation around its decisions.')
 if '\\input{joint_policy_results}' not in s:s=s.replace('\\input{seed_geometry_results}','\\input{seed_geometry_results}\n\\input{joint_policy_results}',1)
 if '\\input{joint_policy_appendix}' not in s:s=s.replace('\\input{seed_geometry_appendix}','\\input{seed_geometry_appendix}\n\\input{joint_policy_appendix}',1)
 notes.write_text(s)
 checker=report/'s01_check_paper.py';s=checker.read_text()
 if "'joint_policy_results.tex'" not in s:s=s.replace("'seed_geometry_appendix.tex']","'seed_geometry_appendix.tex','joint_policy_results.tex','joint_policy_appendix.tex']",1)
 checker.write_text(s)
 make=report/'Makefile';s=make.read_text()
 if 'report.pdf: joint_policy_results.tex' not in s:s=s.replace('report.pdf:','report.pdf: joint_policy_results.tex joint_policy_appendix.tex',1)
 make.write_text(s);save(report/'joint_policy_data.json',d)
 print('Both documents updated from measured evidence.',flush=True)

if __name__=='__main__':main()
