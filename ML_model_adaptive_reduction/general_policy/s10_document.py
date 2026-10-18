"""Write the completed shared-model results into the concise paper and notes."""
from s00_common import *
import re

def pct(r):return f'{100*(1-r):.1f}'
def main():
 s=READ(HERE/'summary.json');m=READ(HERE/'refit/trained_model/freeze.json');overall=s['overall'];held=s['held_out'];known=s['known'];assert overall['cases']
 times=overall['summed_median_seconds'];ratios=overall['ratios'];ci=overall['intervals'];held_text=''
 if held['cases']:
  hr=held['ratios'];hi=held['intervals']
  held_text=f"The {held['cases']} matched requests from excluded families or higher orders give a learned-to-native ratio of {hr['native']:.3f}, with repeat interval [{hi['native'][0]:.3f},{hi['native'][1]:.3f}], and a learned-to-fixed ratio of {hr['fixed']:.3f}, with interval [{hi['fixed'][0]:.3f},{hi['fixed'][1]:.3f}]. Their physical groups were excluded from both fitting and model selection."
 counts=s['counts'];failed=counts.get('reference_failed',0)+counts.get('independent_check_failed',0)
 selection=m['selection'];kind=m['model']['kind'];filename=selection['file']
 if kind=='mlp':
  width=len(m['model']['bias'][0]);model_name=f'a neural network with two {width}-component hidden layers';parameter_count=sum(len(row) for a in m['model']['weights'] for row in a)+sum(len(a) for a in m['model']['bias'])
 elif kind=='ridge':model_name='a regularized linear cost model';parameter_count=sum(map(len,m['model']['coef']))+len(m['model']['intercept'])
 else:
  label={'tree':'decision tree','forest':'random forest','extra':'forest with randomized splits'}[filename.split('_')[0]]
  model_name='a '+label+' for cost prediction';parameter_count=sum(len(t['left']) for t in m['model']['trees'])
 output=r'''\subsection{Reserved results and loop coverage}
\label{sec:general-results}
'''
 output+=f"The corrected shared model completes {overall['cases']} matched nontrivial requests from the 110-request grid. The coverage record contains {counts.get('reference_failed',0)} failed reference calculations, {counts.get('independent_check_failed',0)} failed enlarged-region checks, {counts.get('method_failed',0)} incomplete method comparisons, and {counts.get('unsupported_native_index_count',0)} inputs above the native coordinate limit. Identity-only batches number {counts.get('identity_only',0)}. The matched outputs pass {s['coefficient_checks']:,} coefficient comparisons. Table~\\ref{{tab:general-coverage}} retains every loop order and outcome.\n\n"
 output+=f"Complete supplied-basis time, summed over request medians, is {times['native']:.3f} seconds for native choices, {times['fixed']:.3f} seconds for the common fixed setting, {times['learned']:.3f} seconds for the shared model, and {times['previous']:.3f} seconds for the preceding application. The learned-to-native ratio is {ratios['native']:.3f}, with repeat interval [{ci['native'][0]:.3f},{ci['native'][1]:.3f}]. The learned-to-fixed ratio is {ratios['fixed']:.3f}, with interval [{ci['fixed'][0]:.3f},{ci['fixed'][1]:.3f}]. Relative to the preceding application, the ratio is {ratios['previous']:.3f}, with interval [{ci['previous'][0]:.3f},{ci['previous'][1]:.3f}]. All ratios include inference, checking, and recovery.\n\n"
 output+=held_text+'\n\n'
 output+=r'''\begin{table}[!htbp]\centering\small
\caption{The shared model across physical classes. Ratios use sums of median times on each matched set. Values below one mean less complete time. A class can contain both training-domain and held-out loop orders.}
\label{tab:general-classes}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Physical class & Matched & Model/native & Model/fixed\\\midrule
'''
 names={'vacuum_one_mass':'One-mass vacuum','vacuum_all_mass':'Distinct-mass vacuum','propagator_massless':'Massless two-point','propagator_massive':'Massive two-point','ladder':'Four-point ladder','bubble_box':'Box with bubbles','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Box with a virtual leg'}
 for group,g in s['by_family_class'].items():
  output+=f"{names.get(group,group.replace('_',' '))} & {g['cases']} & {g['ratios']['native']:.3f} & {g['ratios']['fixed']:.3f}\\\\\n"
 output+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 output+=f"The model changes the initial action from native bounds on {overall['changed_native']} matched requests and from the fixed control on {overall['changed_fixed']}. Thus the comparison records actual action changes as well as complete time. Reference discovery across the requested grid takes {s['discovery_seconds']:.1f} seconds and the independent checks take {s['independent_check_seconds']:.1f} seconds, including unsuccessful attempts. These costs precede the matched supplied-basis timings. The new fit takes {m['fitting_seconds']:.1f} seconds and reuses the existing cost labels; this fitting time does not include the earlier cost of generating those labels.\n\n"
 output+=r'''\begin{table}[!htbp]\centering\small
\caption{Every requested loop order in the corrected-model test. ``Reference'' includes failed initial or enlarged-region reductions. ``Method'' means an incomplete matched comparison. A dash means that no complete ratio is available. The last column compares the shared model with native choices on matched nontrivial requests.}
\label{tab:general-coverage}
\begin{tabular}{@{}rrrrrrr@{}}\toprule
Loops & Requests & Matched & Reference & Method & Unsupported & Ratio\\\midrule
'''
 for L in range(1,13):
  g=s['by_loop'][str(L)];cc=g['counts'];r=g['timing'];ratio=f"{r['ratios']['native']:.3f}" if r['cases'] else '---'
  output+=f"{L} & {g['requested']} & {r['cases']} & {cc.get('reference_failed',0)+cc.get('independent_check_failed',0)} & {cc.get('method_failed',0)} & {cc.get('unsupported_native_index_count',0)} & {ratio}\\\\\n"
 output+=r'''\bottomrule\end{tabular}\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/general_policy_times.pdf}
\caption{Complete time of the corrected shared model, separated into training domains and physical holdouts. Both controls use the same exact implementation. The fixed control has one setting for all requests. The line at one marks equal time, and the intervals describe paired repeat variation.}
\label{fig:general-times}
\end{figure}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/general_policy_coverage.pdf}
\caption{The loop range extends through twelve, while native completion has a smaller measured range. Predictions for unsupported inputs do not count as reductions. Failed reference checks also prevent a timing claim.}
\label{fig:general-coverage}
\end{figure}
\FloatBarrier
'''
 output+="The family holdouts test transfer within this finite set of denominator structures, target powers, and rational parameter values. They do not establish performance for arbitrary graph routings, large target ranks, general symbolic kinematics, cuts, or unbounded loop order. The same physical definitions have also been used in earlier project development, although the excluded groups supply no labels or model-selection costs to this new fit. The high-loop failures and native input limits therefore remain part of the result.\n"
 write(ROOT/'report/general_policy_model_description.json',dict(name=model_name,parameters=parameter_count,selection=selection,fit_seconds=m['fitting_seconds']))
 (ROOT/'report/general_policy_results.tex').write_text(output)
 abstract=r'\begin{abstract}'+'\n'
 abstract+='Integration-by-parts reduction expresses Feynman integrals in a master basis~\\cite{KiraOriginal}. We train models to select seeds and equations before Kira performs exact algebra, and compare their complete reduction time with matched controls. On separate known-graph workloads, sparse seeding uses 3.6\\% less time than a tuned fixed sparse setting, while an equation filter uses 6.7\\% less time on new target-index batches. Learned row selection gives no reliable saving and is omitted from the retained method. '
 abstract+=f"To test transfer, we train one structural cost model while excluding whole families and all loop orders above three from fitting and model selection. A fresh grid defines 110 requests through twelve loops, of which {overall['cases']} give matched nontrivial native reductions. Their learned-to-native time ratio is {ratios['native']:.3f}, and their learned-to-fixed ratio is {ratios['fixed']:.3f}. "
 if held['cases']:abstract+=f"The {held['cases']} matched physical holdouts give a learned-to-native ratio of {held['ratios']['native']:.3f}. "
 abstract+='Timings include prediction, equation generation, exact algebra, checks, and recovery, with master discovery reported separately. Failed references and unsupported inputs remain explicit. The calculations keep the dimension symbolic and otherwise use rational kinematics. These results measure the supported domain of the learned method; they do not establish a speedup for every integral or loop order.\n'+r'\end{abstract}'+'\n'
 (ROOT/'report/paper_abstract.tex').write_text(abstract)
 con=r'\section{Conclusion}'+'\n'
 con+='This study measures learned decisions through complete Kira reduction time. The local seed and equation comparisons support their use within the tested domains, while the row model adds no reliable saving. The retained method therefore keeps native elimination rows and places learned decisions before work that they can avoid.\n\n'
 con+=f"The shared structural model extends the comparison beyond family-specific choices. It learns from {m['training_count']} cost-labelled requests, uses {m['validation_count']} separate validation requests, and is tested on a new 110-request grid. The {overall['cases']} matched nontrivial reductions give time ratios {ratios['native']:.3f} against native choices and {ratios['fixed']:.3f} against the common fixed setting. "
 if held['cases']:con+=f"The {held['cases']} matched requests from excluded physical groups give ratios {held['ratios']['native']:.3f} and {held['ratios']['fixed']:.3f}, respectively. "
 con+='The timing intervals and coverage table determine the scope of these measurements.\n\nThe remaining limitation is native coverage. Defining and scoring an input through twelve loops does not show that its full IBP reduction completes. Unsupported coordinates, failed reference calculations, general symbolic kinematics, and more varied graph structures require further verified comparisons. Exact scalar formulas and reuse can supply separate savings under their assumptions, and the notes retain those results without attributing them to ML.\n'
 (ROOT/'report/paper_conclusion.tex').write_text(con)
 paper=ROOT/'report/report.tex';text=paper.read_text()
 text=re.sub(r'Training selects a neural network with two 48-component hidden layers and a margin of 0\.12\.',f"Training selects {model_name} and a margin of {selection['margin']:.2f}.",text)
 if kind=='mlp' and 'fitted weights and biases' not in text:
  text=text.replace('The runtime evaluates the saved weights directly',f'The network has {parameter_count:,} fitted weights and biases. The runtime evaluates the saved weights directly')
 paper.write_text(text)
 appendix=ROOT/'report/paper_derivations.tex';text=appendix.read_text()
 if kind=='mlp':
  text=text.replace('Both hidden vectors have 48 components',f'Both hidden vectors have {width} components')
  text=text.replace('The selected candidate is the 48-component network, with truncated numerator expansion as anchor and margin 0.12.',f"The selected candidate is the {width}-component network, with action {selection['anchor']} from Table~\\ref{{tab:shared-actions}} (numbered from zero) as anchor and margin {selection['margin']:.2f}.")
 else:
  text=text.replace('The selected network standardizes','Each neural candidate standardizes').replace('Both hidden vectors have 48 components','For the larger candidate, both hidden vectors have 48 components')
  text=text.replace('The selected candidate is the 48-component network, with truncated numerator expansion as anchor and margin 0.12.',f"The selected candidate is {model_name}, with action {selection['anchor']} from Table~\\ref{{tab:shared-actions}} (numbered from zero) as anchor and margin {selection['margin']:.2f}.")
 text=text.replace(r'Let $N_{cy}$ be the native number of records of class $y\in\{0,1\}$ in batch $c$, $N_c=N_{c0}+N_{c1}$, and $n_{cy}=\min(2000,N_{cy})$ the number sampled without replacement.',r'Let $N_{cy}$ be the native number of records of class $y\in\{0,1\}$ in batch $c$. The total number of records is $N_c=N_{c0}+N_{c1}$. We sample $n_{cy}=\min(2000,N_{cy})$ records from each class without replacement.')
 appendix.write_text(text)
 notes=ROOT/'report/notes.tex';text=notes.read_text();start=text.index('\\paragraph{Current');end=text.index('% END CURRENT WORKFLOW UPDATE',start)
 text=text[:start]+f"\\paragraph{{Current shared-model comparison.}} Section~\\ref{{sec:general-results}} tests a model without family-name inputs. It gives {overall['cases']} matched native reductions from 110 defined requests through twelve loops, with learned-to-native ratio {ratios['native']:.3f} and learned-to-fixed ratio {ratios['fixed']:.3f}. The preceding family-specific studies and exact methods remain below. Their workloads and controls differ, so their speedups cannot be multiplied.\n"+text[end:];notes.write_text(text)
 initial=s['initial_trial'];hist=ROOT/'report/general_policy_initial_notes.tex'
 hist.write_text(r'\section{Initial shared-model trial and corrected fitting}'+'\n'+f"The first shared-model trial uses profile 1201 and records {initial['overall']['cases']} matched requests. Its learned-to-native ratio is {initial['overall']['ratios']['native']:.3f}. During an audit of the installed training implementation, we found that the multi-output objective averaged across outputs while its gradient summed them. We changed the objective to the output sum, checked all {s['gradient_check']['components']} components of a small-network gradient by finite differences, and refitted using the same original training and validation data. The maximum absolute discrepancy in that check is {s['gradient_check']['max_absolute_error']:.2g}. No reserved label enters refitting or model selection. The corrected model is tested on fresh profile 1213, and both trials remain in the evidence record.\n")
 text=notes.read_text()
 if '\\input{general_policy_initial_notes}' not in text:text=text.replace('\\input{general_policy_results}', '\\input{general_policy_results}\n\\input{general_policy_initial_notes}')
 notes.write_text(text)
 print('DOCUMENTED',model_name,overall['cases'],flush=True)
if __name__=='__main__':main()
