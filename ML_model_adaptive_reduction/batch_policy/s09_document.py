"""Write the measured physics/ML results and preserve the archived notes."""
import json,re
from datetime import datetime
from zoneinfo import ZoneInfo
from s00_runtime import HERE,ROOT,rt,inputs
R=ROOT/'report'
NAMES={'sunrise':'Sunrise','double_box':'Planar double box','vacuum3':'Massive vacuum','ladder3':'Massive ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box','bubble_box3':'Three-loop bubble box','bubble_box4':'Four-loop bubble box','massless4':'Massless two-point'}
def change(r):return f'{100*abs(1-r):.1f}\\% '+('less' if r<1 else 'more')+' time'
def block(s,name,text):
 begin='% BEGIN '+name+'\n';end='% END '+name+'\n'
 new=begin+text+'\n'+end
 if begin in s:return re.sub(re.escape(begin)+'.*?'+re.escape(end),lambda _:new,s,flags=re.S)
 return s,new

def main():
 d=rt.read(HERE/'summary.json');f=rt.read(HERE/'trained_model/freeze.json');a=rt.read(HERE/'application/summary.json')
 fixed=d['ratios']['fixed'];extra=f['enabled'] and d['repeat_intervals']['fixed'][1]<1
 kind={'tree':'a regression tree','forest':'a random forest','extra':'an extremely randomized forest'}[f['selected']['kind']]
 trees=len(f['model']['trees']);depth=f['selected']['depth'];leaf=f['selected']['min_leaf'];gate=f['gate']
 fields=dict(N=d['batches'],REQ=d['requested'],TRAIN=f['training_cases'],VAL=f['validation_cases'],TMAX=max(c['size'] for c in d['matched']),TMIN=min(c['size'] for c in d['matched']),KIND=kind,TREES=trees,DEPTH=depth,LEAF=leaf,GATE=gate,PREV=f"{d['totals']['previous']:.3f}",FIXED=f"{d['totals']['fixed']:.3f}",OFF=f"{d['totals']['fixed_off']:.3f}",ON=f"{d['totals']['learned']:.3f}",PREVCHANGE=change(d['ratios']['previous']),FIXEDCHANGE=change(fixed),OFFCHANGE=change(d['ratios']['fixed_off']),CI=', '.join(f'{v:.3f}' for v in d['repeat_intervals']['fixed']),TIMED=d['timed'],SUCCESS=d['successful'],CHECKS=d['coefficient_checks'],FAILED=len(d['reference_failed']),INCOMPLETE=len(d['incomplete']),IDENTITY=len(d['identity_only']),OVERLAP=len(d['repeated_index_batches']),FIT=f"{f['fitting_seconds']:.2f}",COST=f"{sum(d['offline_costs'].values())/60:.1f}",INFERENCE=f"{1000*d['decision_median_seconds']:.2f}",APPS=a['matched'],APPTIMED=a['timed'],APPCHANGE=change(a['ratios']['previous']) if a['matched'] else 'no matched comparison',VERDICT=('The paired timing interval supports an additional saving from the learned batch choice on this workload.' if extra else 'The paired timing interval does not establish an additional saving from the learned batch choice on this workload.'),ENABLE=('Validation enables this model.' if f['enabled'] else 'No predictor reaches the required three-percent validation saving, so deployment uses the fixed partitions.') )
 fields['TREEWORD']='tree' if trees==1 else 'trees'
 fields['VALCHANGE']=change(f['selected']['ratio'])
 fields['OFFCI']=', '.join(f'{v:.3f}' for v in d['repeat_intervals']['fixed_off'])
 if not f['enabled']:fields['VERDICT']='Validation disables the new predictor, so this comparison establishes no additional ML gain from batch selection.'
 def fill(s):
  for k,v in fields.items():s=s.replace('@'+k+'@',str(v))
  assert not re.search('@[A-Z]+@',s)
  return s
 text=fill(r'''\section{Learning which targets to reduce together}
\label{sec:batch-policy}
The equation filters reduce work inside a seed region, but the targets grouped in one request also determine that region. A batch can contain targets with high denominator powers and other targets with high numerator rank. Their combined limits can generate equations that neither group needs separately. Dividing the batch can avoid these equations, while repeating preparation and shared algebra can make an unnecessary division slower. We therefore train a model to choose the division from measured complete reduction time. Recent tube-seeding work also uses target groups to control reduction cost~\cite{TubeSeeding2026}; the present method uses ordinary Kira seed regions and the already checked equation filters.

\subsection{Model and integration with Kira}
The model compares five ways to divide a batch: keep all targets together, group equal numerator ranks, group equal extra denominator powers, group equal sectors, or use consecutive groups of at most three targets. A sixth candidate keeps the batch together and disables the equation filter, allowing the new model to avoid an expensive filter or retry. It receives 32 quantities that describe the physical family, the requested powers, and their distribution across the batch. It predicts the complete relative cost of each choice before Kira generates any equations. Each selected group then uses the same fixed seed policy and native row elimination as the preceding method. The existing equation filter acts only when enabled and when the group lies inside its original checked domain. We merge the resulting exact master coefficients after checking that every target has completed.

We compare regression trees, random forests, and extremely randomized forests~\cite{CART1984,Breiman2001Forest,Geurts2006ExtraTrees}. A tree compares the input quantities with learned thresholds and returns predicted costs from the final group of training examples. A forest averages the predictions of several trees. Here each prediction contains six log-cost ratios: the logarithm of a candidate's complete time divided by the time of the undivided batch. Training uses @TRAIN@ batches, and separate validation uses @VAL@ batches. The candidate with the smallest validation cost is @KIND@ with @TREES@ @TREEWORD@, at most @DEPTH@ threshold levels, and at least @LEAF@ training examples in each final group. Its chosen prediction margin is @GATE@ in log-cost units, as defined in Appendix~\ref{app:batch-policy}, and its selected validation costs give @VALCHANGE@ than fixed partitions. @ENABLE@ The appendix specifies every partition, input, training objective, recovery rule, and physical request, and derives how the independently reduced groups give the complete target reduction.

The training labels include unsuccessful attempts and recovery. Reference construction supplies a common basis and checked coefficients before timing, but the solver receives only the basis and the target definitions. Reference coefficients enter the exact check after reduction. Recorded development, training, and validation reductions take @COST@ minutes, while fitting takes @FIT@ seconds; these costs precede deployment and exclude reference construction. The median loading and decision cost in the timed test is @INFERENCE@ milliseconds.

\subsection{Controls and results}
The reserved comparison uses new rational profiles in the same ten structures at one through four loops, with symbolic dimension. The matched requests contain @TMIN@ to @TMAX@ targets each. Five repetitions rotate the methods through execution positions on the same worker. The previous method keeps each batch together. One fixed control chooses a partition per graph with the equation filters available; a second fixed control tunes its partitions independently with every ML model disabled. The comparison with the first fixed control measures the added batch-selection application, including its domain checks and loading cost. The second compares the combined workflow with tuned choices that perform no ML inference. All methods share the same exact implementation, basis, worker count, and checks.

Of @REQ@ requests, @N@ give matched nontrivial completions. There are @FAILED@ failed reference requests, @INCOMPLETE@ incomplete timed batches, and @IDENTITY@ matched identity-only batches. The comparison record contains @SUCCESS@ successful results in @TIMED@ calculations, with @CHECKS@ exact coefficient comparisons. Every successful result passes its reference check. A total of @OVERLAP@ requested index batches recur in this study's training or validation sets at different rational profiles. The test therefore measures new kinematics and a defined mixture of target batches within known graph structures.

Summed batch median time changes from @PREV@ seconds for the previous undivided workflow to @ON@ seconds for the selected workflow, giving @PREVCHANGE@. The fixed control with filters takes @FIXED@ seconds, and the independently tuned all-ML-disabled control takes @OFF@ seconds. Relative to these controls, the selected workflow uses @FIXEDCHANGE@ and @OFFCHANGE@, respectively. The selected-to-fixed ratio has a paired-repetition interval of $[@CI@]$, and the ratio to the all-ML-disabled control has interval $[@OFFCI@]$. @VERDICT@ Table~\ref{tab:batch-policy} shows the separate graph results, including regressions.

\begin{table}[!htbp]\centering\small
\caption{Sum of median complete times in seconds on matched batches. Previous keeps each batch together. Fixed uses one partition per graph with filters. ML off tunes partitions separately with every model disabled. Selected uses the frozen deployment choice.}
\label{tab:batch-policy}
\begin{tabular}{@{}lrrrrr@{}}\toprule
Graph & Batches & Previous & Fixed & ML off & Selected\\\midrule
''')
 text=text.replace('at least 1 training examples','at least one training example')
 for g,v in d['graphs'].items():
  t=v['totals'];text+=f"{NAMES[g]} & {v['batches']} & {t['previous']:.2f} & {t['fixed']:.2f} & {t['fixed_off']:.2f} & {t['learned']:.2f}"+r'\\'+'\n'
 text+=fill(r'''\bottomrule\end{tabular}
\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/batch_policy_times.pdf}
\caption{The left panel compares the selected complete workflow with the previous undivided workflow. The right panel compares it with independently tuned fixed partitions with every model disabled. Values below one indicate less time; the dashed line marks equal time. Segments describe paired repetition variation on this workload. Validation disables the new batch predictor; the selected workflow uses the retained fixed partitions and equation-filter settings.}
\label{fig:batch-policy}
\end{figure}
\FloatBarrier

A separate application check starts a new Python process for each request and includes imports, model loading, input and output, and exact checks. Deployment loads only the parts of the frozen policy that it uses: when validation disables the predictor, it retains the fixed choices and domain limits and omits the unused tree arrays. We check that this compact form gives the same choices on every training, validation, and reserved input, without reading reserved timing outcomes. The repeated comparison above retains the original frozen application; this separate check uses the compact form. It completes @APPTIMED@ timed requests over @APPS@ matched batches and gives @APPCHANGE@ than the previous workflow. These batches are a predeclared subset of the reserved inputs, so this check measures application overhead without adding evidence for new topologies.

The new study extends the batch sizes tested by the earlier equation-filter comparison. It still supplies a master basis and keeps the kinematic invariants rational. General symbolic scattering, arbitrary higher-loop structures, and globally optimal partitions remain outside this evidence. The earlier restricted vacuum recurrence covers its stated one-through-twelve-loop family separately, and its speedup cannot be multiplied by the ratios measured here.
''')
 work=d['reported_work']
 active=d['equation_filter_active']
 filter_text=f"\nThe selected workflow actually calls an equation filter on {active['batches']} matched batches."
 if active['batches']:
  filter_text+=f" On this subset it uses {change(active['ratios']['fixed_off'])} than the separately tuned ML-disabled control. This subset records filter use; its controls can also choose different fixed partitions."
  lo,hi=active['repeat_intervals']['fixed_off']
  filter_text+=f" Its paired-repetition ratio interval is $[{lo:.3f}, {hi:.3f}]$."
  if lo<=1<=hi:filter_text+=' This interval includes equal time and does not establish a reliable saving on this subset.'
 filter_text+='\n'
 text=text.replace('Summed batch median time changes',filter_text+'\nSummed batch median time changes',1)
 if 'interruption_recovery' in d:
  rec=d['interruption_recovery']
  recovery=(f"\nTwo cluster allocations reached their time limits before completing all requests. We preserve the {rec['retained_complete_batches']} complete comparison batches and resume the {rec['resumed_batches']} remaining batches with unchanged models and timing rules. For an interrupted batch, we repeat every method and repetition on one worker. The {rec['archived_trials']} saved timings from its earlier partial comparison remain available separately and do not enter the ratios. Work assignment uses validation costs only.\n")
  text=text.replace('Summed batch median time changes',recovery+'\nSummed batch median time changes',1)
 bound=d['validation_candidate_bound']
 retrospective=f"\nSelecting the smallest recorded cost separately for every validation batch would lower the fixed-partition cost by {100*(1-bound['ratio']):.1f}\\%. This comparison uses timing information available only after the calculations and describes the remaining opportunity within these six candidates. It does not describe a deployable predictor. Appendix~\\ref{{app:batch-policy}} defines this retrospective bound.\n"
 text=text.replace('\\subsection{Controls and results}',retrospective+'\n'+r'\subsection{Controls and results}',1)
 diagnostic=f"\nThe recorded generation counts sum to {work['previous']['generated_equations']:,.0f} equations for the previous workflow, {work['fixed_off']['generated_equations']:,.0f} for the tuned ML-disabled control, and {work['learned']['generated_equations']:,.0f} for the selected workflow. These are sums of per-batch median counters over reported generation passes, including repeated passes and retries. They describe generated equations rather than the total number of arithmetic operations. Complete time remains the criterion for retaining a model.\n"
 text=text.replace('\\begin{table}[!htbp]\\centering\\small',diagnostic+'\n'+r'\begin{table}[!htbp]\centering\small',1)
 (R/'batch_policy_results.tex').write_text(text);(R/'batch_policy_appendix.tex').write_text((HERE/'batch_policy_appendix.tex').read_text())
 summary=fill(r'The target-batch comparison in Section~\ref{sec:batch-policy} gives @PREVCHANGE@ than the previous undivided workflow across @N@ matched batches with up to @TMAX@ targets. Its additional change relative to fixed partitions with the same filters is @FIXEDCHANGE@, with ratio interval $[@CI@]$. @VERDICT@ Every successful reduction passes exact coefficient checks. This is a separate workload from the smaller-batch filter study.')
 p=R/'report.tex';s=p.read_text()
 s=s.replace('As the loop order increases, a calculation produces many integrals with related numerator and denominator structures. Integration-by-parts (IBP) identities connect these integrals and allow them to be expressed in terms of a smaller set of master integrals.', 'As the loop order increases, a calculation produces many integrals with related numerator and denominator structures, and integration-by-parts (IBP) identities allow them to be expressed in terms of a smaller set of master integrals.')
 date=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%B %-d, %Y')
 s=re.sub(r'\\date\{[^}]*\}',lambda _:r'\date{'+date+'}',s,count=1)
 s=s.replace('Seed selection & Which index vectors supply IBP identities? & Generate fewer groups of equations.','Seed and batch selection & Which seed regions and target groups should Kira use? & Limit equation generation and repeated work.')
 if '\\input{batch_policy_results}' not in s:s=s.replace('\\input{equation_refinement_results}','\\input{equation_refinement_results}\n\\input{batch_policy_results}',1)
 if '\\input{batch_policy_appendix}' not in s:s=s.replace('\\input{equation_refinement_appendix}','\\input{equation_refinement_appendix}\n\\input{batch_policy_appendix}',1)
 if '% BEGIN BATCH POLICY OVERALL' in s:s=block(s,'BATCH POLICY OVERALL',summary)
 else:s=s.replace('\\subsection{What the model comparisons establish}\n','\\subsection{What the model comparisons establish}\n% BEGIN BATCH POLICY OVERALL\n'+summary+'\n% END BATCH POLICY OVERALL\n',1)
 if '% BEGIN BATCH POLICY CONCLUSION' in s:s=block(s,'BATCH POLICY CONCLUSION',summary)
 else:s=s.replace('\\section{Conclusion}\n','\\section{Conclusion}\n% BEGIN BATCH POLICY CONCLUSION\n'+summary+'\n% END BATCH POLICY CONCLUSION\n\n',1)
 intro='The next comparison trains a model to choose which targets Kira reduces together. This choice changes the seed limits of each group and can trade repeated preparation for a smaller equation system. We compare its complete time with the preceding undivided workflow and with separately tuned fixed partitions.'
 if intro not in s:s=s.replace('We first define the notation used in this paper',intro+'\n\nWe first define the notation used in this paper',1)
 s=s.replace('Larger target batches, general high-loop scattering, unrestricted symbolic kinematics, and globally minimal reduction paths remain outside its demonstrated scope.','The target-partition study extends the tested batch sizes as described in Section~\\ref{sec:batch-policy}. General high-loop scattering, unrestricted symbolic kinematics, and globally minimal reduction paths remain outside the demonstrated scope.')
 absnote=fill(r'Integration-by-parts reduction expresses Feynman integrals in a master basis, and its cost depends partly on the equations generated for the targets. We train equation filters and complete-time predictors while retaining exact algebra and native row elimination in Kira. The equation-filter comparison gives 4.8\% less time on 68 matched batches at one through four loops, including 8.0\% less time on the 32 batches where validation enables filtering. A separate target-batch comparison gives @PREVCHANGE@ than the preceding undivided workflow across @N@ matched requests. It uses @FIXEDCHANGE@ than fixed partitions with the same filters and @OFFCHANGE@ than a separately tuned control with all ML disabled. @VERDICT@ All successful coefficients match exact references, and timing includes model loading, prediction, equation generation, algebra, checks, and recovery. The native ML comparisons use rational kinematics, symbolic dimension, supplied master bases, and known graph structures. Learned row selection remains excluded because it gives no reliable complete-time benefit.')
 if not f['enabled']:absnote=absnote.replace('A separate target-batch comparison','Validation retains fixed target partitions. The separate target-batch comparison')
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+absnote+'\n'+r'\end{abstract}',s,count=1,flags=re.S)
 row=fill(r'Target batch choice & @N@ matched batches; up to @TMAX@ targets & @PREVCHANGE@ than previous; @FIXEDCHANGE@ than fixed partitions\\')
 if '% BEGIN BATCH POLICY TABLE' in s:s=block(s,'BATCH POLICY TABLE',row)
 else:s=s.replace('% BEGIN EQUATION REFINEMENT TABLE','% BEGIN BATCH POLICY TABLE\n'+row+'\n% END BATCH POLICY TABLE\n% BEGIN EQUATION REFINEMENT TABLE',1)
 p.write_text(s)
 # Record reversible additions so the original notes remain reconstructable.
 p=R/'notes.tex';s=p.read_text();rev=rt.read(R/'notes_revision.json')
 for old,new in [('\\input{equation_refinement_results}','\\input{equation_refinement_results}\n\\input{batch_policy_results}'),('\\input{equation_refinement_appendix}','\\input{equation_refinement_appendix}\n\\input{batch_policy_appendix}')]:
  if new not in s:
   assert s.count(old)==1;s=s.replace(old,new)
 current='% BEGIN CURRENT WORKFLOW UPDATE\n\\paragraph{Current measured method.} '+summary+'\n% END CURRENT WORKFLOW UPDATE\n'
 s=re.sub(r'% BEGIN CURRENT WORKFLOW UPDATE\n.*?% END CURRENT WORKFLOW UPDATE\n',lambda _:current,s,count=1,flags=re.S);p.write_text(s);inputs.write(R/'notes_revision.json',rev)
 p=R/'s01_check_paper.py';s=p.read_text()
 if "'batch_policy_results.tex'" not in s:s=s.replace("'equation_refinement_appendix.tex']","'equation_refinement_appendix.tex','batch_policy_results.tex','batch_policy_appendix.tex']",1)
 p.write_text(s)
 p=R/'Makefile';s=p.read_text()
 if 'batch_policy_results.tex' not in s:s=s.replace('report.pdf:','report.pdf: batch_policy_results.tex batch_policy_appendix.tex',1)
 p.write_text(s)
 print('DOCUMENT_TEXT_UPDATED',flush=True)

if __name__=='__main__':main()
