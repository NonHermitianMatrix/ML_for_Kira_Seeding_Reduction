"""Write the current method, measured results, and connected conclusions."""
from s00_batch_common import *
from collections import Counter
REPORT=ROOT/'report'

def main():
 s=read(HERE/'summary.json');p=read(HERE/'protocol.json');m=read(HERE/'trained_model/initial_policy.json');a=s['admission'];basis=read(HERE/'basis_validation.json')
 assert s['complete'] and s['protocol_sha256']==sha(HERE/'protocol.json')
 names={'double_box':'Planar box batches','nonplanar_box':'Nonplanar box batches','native_batch_new_indices':'New index batches','native_all':'All native box batches','triangle_products':'Triangle products, one to thirteen loops','exact_triangle':'Triangle with symbolic scale','compatibility':'Compatibility requests','all':'All matched requests'}
 order=['double_box','nonplanar_box','native_batch_new_indices','triangle_products','exact_triangle','compatibility','all']
 method=r'''\section{Exact triangle reduction and learned target grouping}
\label{sec:analytic-batch-method}
Some integral structures admit a direct reduction formula. We use such a formula before asking a learned model to choose the remaining native work. The new exact case is a massless one-loop triangle with two lightlike external momenta and one nonzero invariant. Its denominator powers can include a polynomial numerator. Its singular invariant matrix prevents use of the preceding inverse-matrix recurrence in the full triangle sector. Appendix~\ref{app:analytic-batch} derives the coefficient of a single off-shell bubble master from Feynman parameters and expresses it through finite products. This avoids equation generation and elimination for that block. Factorization then applies the formula independently to products of these blocks. The tests through thirteen loops concern these independent products; they do not establish a formula for a general connected thirteen-loop scattering graph.

For the coupled two-loop boxes, several requested integrals often need overlapping equations. We therefore train a model to select how Kira shares the reduction work. The five choices are the preceding application, a common reduction with either of two sparse seed regions, separate reductions for groups of equal numerator rank, and separate reductions for each target. Numerator rank is the sum of the absolute values of negative indices. Each choice uses the same target integrals and checked master basis. Exact algebra determines the coefficients, and an incomplete restricted reduction invokes the existing recovery procedure.

The model uses seventeen numerical features of the denominators and target indices. These include target count, numerator ranks, distances between numerator indices, and how propagators depend on the loop momenta. It predicts the complete cost of each choice. A cost-sensitive tree selects splits that reduce the sum of measured action costs, and bootstrap ensembles provide an additional candidate model~\cite{CART1984,Breiman1996Bagging}. Appendix~\ref{app:analytic-batch} derives the training objective and states all candidate settings. Reference coefficients enter only the independent result checks.

We collect 32 training requests and sixteen separate validation requests from planar and nonplanar massless boxes. Their indices have unit positive propagator powers and numerator ranks one through four. We select the model using validation costs, then test its full application cost against the best fixed action at a fresh validation profile. This second check includes loading, prediction, exact reduction, and verification. The model enters deployment only if it saves at least two percent, completes every validation check, and has a request-resampling interval below equal time. The reserved requests remain unused during both decisions.

During development, repeated basis discovery caused avoidable failures on some planar batches. We add a separately checked registry containing only master indices. Two native reductions with different integral orderings must reproduce each other and the development coefficients. The same-basis control receives this registry too, so it separates basis preparation from the new triangle formula and learned grouping. The unmodified preceding application supplies a further practical control. We report basis preparation and benchmark-reference preparation separately from the supplied-basis application timer.
'''
 (REPORT/'analytic_batch_method.tex').write_text(method)
 results=r'''\section{Complete-time results for exact triangles and target batches}
\label{sec:analytic-batch-results}
The reserved comparison contains forty native two-loop box requests, thirteen independent triangle products, one triangle with a symbolic scale, and four compatibility requests. Thirty-two box requests use fresh kinematics with the original index patterns, while eight use new index batches. The compatibility requests retain the earlier vacuum, propagator, and ladder definitions. Appendix~\ref{app:analytic-batch} specifies every collection and the separation between training, validation, and testing.

Each measurement starts a fresh application process and includes loading, model use, exact reduction, retries, output, and the independent coefficient comparison. Three repetitions rotate method order on each request's worker. A first unverified result remains recorded and stops further repetitions for that method and request. Completed-time ratios include only requests verified by both compared methods; the separate completion table retains all requests.

'''
 env=s['test_environment']['0'];cpu=env['cpu'].replace('_',r'\_')
 results+=f"The reserved measurements use two single-core workers on the same {cpu} compute node. We fix that hardware assignment before the reserved tests. The full application validation uses a fresh profile on the same hardware. We preserve an interrupted heterogeneous-worker comparison in the notes; those trials do not determine admission. Each request compares every method on the same worker. The cluster allocation shares the node with other work, and the reported repetition intervals describe variation under those conditions.\n\n"
 selected=m['selection'];decision='enables the new batch model' if a['enabled'] else 'keeps the fixed batch action'
 results+=f"Training selects {selected['trees']} tree{'s' if selected['trees']!=1 else ''} with maximum depth {selected['depth']} and minimum leaf population {selected['minimum']}. The full application validation takes {a['learned_seconds']:.3f} seconds with the selected policy and {a['fixed_seconds']:.3f} seconds with the fixed action. Its time ratio is {a['time_ratio']:.3f}, with request-resampling interval $[{a['request_bootstrap_interval'][0]:.3f},{a['request_bootstrap_interval'][1]:.3f}]$. The deployment rule therefore {decision}. "
 results+=('The separate reserved comparisons below measure the added learned choice after this decision.\n\n' if a['enabled'] else 'The trained candidate and its measurements remain available, while deployment uses the cheaper validated choice. The retained native sparse-seed model remains active in its previously validated domain.\n\n')
 fixed_names={'prior':'preceding application','sparse_wide':'wider shared sparse region','sparse_tight':'tighter shared sparse region','rank_groups':'equal-rank grouping','single_targets':'separate-target reduction'}
 count=sum(r['methods']['learned']['batch_model_used'] for r in s['rows'])
 results+=f"The selected fixed action is the {fixed_names[m['fixed']]}. The tree changes that action only when its predicted saving exceeds {100*m['margin']:.0f}\\% of the fixed cost plus 0.002 seconds. It changes the fixed action on {selected['changes']} model-selection requests and makes a prediction on {count} reserved requests within its input ranges. Exact formulas and the preceding application handle the remaining structures or inputs outside those ranges.\n\n"
 decisions=Counter(action for r in s['rows'] if r['methods']['learned']['batch_model_used'] for action in r['methods']['learned']['actions'] if action is not None)
 if decisions:
  descriptions=[f"the {fixed_names[action]} on {number} requests" for action,number in sorted(decisions.items())]
  choices=(', '.join(descriptions[:-1])+' and '+descriptions[-1]) if len(descriptions)>1 else descriptions[0]
  results+='Within those reserved predictions, the model selects '+choices+'. These observed choices show which alternatives contribute to the deployed result.\n\n'
 results+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete-time comparison with the preceding application supplied with the same checked master indices. Times are sums of request medians in seconds. Each row uses only pairs that pass all three repetitions. A ratio below one means less time.}
\label{tab:analytic-batch-times}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Collection & Pairs & New & Same-basis control & Ratio\\\midrule
'''
 for g in order:
  r=s['comparisons'][g]['previous_prepared']
  if r['matched']:results+=names[g]+f" & {r['matched']} & {r['learned_seconds']:.3f} & {r['control_seconds']:.3f} & {r['ratio']:.3f}"+r' \\'+'\n'
 results+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 v=s['comparisons']['all']['previous_prepared'];raw=s['comparisons']['all']['previous'];fixed=s['comparisons']['all']['fixed'];off=s['comparisons']['all']['all_fixed']
 def sentence(r,label):
  if not r['matched']:return 'No fully verified matched pair supports a time ratio against '+label+'. '
  direction='less' if r['ratio']<1 else 'more';lo,hi=r['repetition_interval']
  return f"Against {label}, the final method uses {abs(r['saving_percent']):.1f}\\% {direction} time on {r['matched']} matched requests. The ratio is {r['ratio']:.3f}, with repetition interval $[{lo:.3f},{hi:.3f}]$. "+('The interval includes equal time. ' if lo<=1<=hi else '')
 results+=sentence(v,'the preceding method with the same basis')+f"The new method is slower on {v['slower_requests']} of those individual requests; the largest individual time ratio is {v['largest_request_ratio']:.3f}. These per-request outcomes remain visible in the full result record.\n\n"
 results+=sentence(raw,'the unmodified preceding application')+'The matched populations can differ because failed requests remain outside a completed-time ratio. Their totals therefore cannot be subtracted to assign a basis-preparation saving.\n\n'
 results+=r'''\begin{table}[!htbp]\centering\small
\caption{Added effect of the new batch decision on native requests. The fixed control has the same exact methods and basis, with the new model disabled. Both methods retain the preceding sparse expert where its action calls for it. These are original measurements of this study.}
\label{tab:analytic-batch-ml}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Collection & Pairs & Final time & Fixed time & Ratio\\\midrule
'''
 for g in order[:3]+['native_all']:
  r=s['comparisons'][g]['fixed']
  if r['matched']:results+=names[g]+f" & {r['matched']} & {r['learned_seconds']:.3f} & {r['control_seconds']:.3f} & {r['ratio']:.3f}"+r' \\'+'\n'
 results+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 native_fixed=s['comparisons']['native_all']['fixed']
 results+=sentence(native_fixed,'the fixed batch action over the forty native box requests')+'This subtotal isolates the added model on the native workload. The full-workflow comparisons below also retain exact and compatibility requests.\n\n'
 results+=f"The learned choice takes more time on {native_fixed['slower_requests']} individual native requests, with a largest request ratio of {native_fixed['largest_request_ratio']:.3f}. Its aggregate saving therefore does not imply a saving for each input. The recorded native elimination counters total {int(native_fixed['learned_native_operations']):,} operations for the learned choice and {int(native_fixed['control_native_operations']):,} for the fixed action. These counters cover the instrumented native algebra; they exclude loading, symbolic checks, and direct-formula arithmetic. The complete timer includes those costs.\n\n"
 results+=sentence(fixed,'the same workflow with a fixed batch action')+sentence(off,'the same workflow with both learned choices disabled')+'The second control changes the earlier seed choice as well, so its difference measures the combined learned decisions.\n\n'
 results+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/analytic_batch.pdf}
\caption{The upper panel measures the combined analytic and learned changes with matched basis preparation. Its logarithmic axis accommodates the exact-triangle saving and the smaller native changes. The lower panel isolates the new batch choice within the native test groups. Horizontal intervals describe paired repetition variation. The line at one indicates equal time; completion counts appear separately in Table~\ref{tab:analytic-batch-completion}.}
\label{fig:analytic-batch}
\end{figure}
\begin{table}[!htbp]\centering\small
\caption{Completion and first-pass cost over all 58 reserved requests. A verified request must pass all three repetitions. First-pass time sums the first measured application and check cost for every request, including failed work. The paired completed-time ratios appear in Table~\ref{tab:analytic-batch-times}.}
\label{tab:analytic-batch-completion}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Method & Verified & First unverified & First-pass seconds\\\midrule
'''
 for k,label in [('learned','Final method'),('fixed','Fixed batch action'),('all_fixed','Both learned choices disabled'),('previous_prepared','Preceding method, same basis'),('previous','Unmodified preceding application')]:
  results+=label+f" & {s['totals'][k]['verified']} & {s['first_unverified'][k]} & {s['totals'][k]['first_pass_seconds']:.3f}"+r' \\'+'\n'
 results+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 checks=sum(r['checks'] for r in basis['cases'])
 results+=f"The reserved test contains {s['timed_records']:,} measured outcomes and {s['coefficient_checks']:,} successful coefficient comparisons. The added basis preparation takes {basis['preparation_seconds']:.3f} seconds and supplies {checks} coefficient checks across five development requests. Independent reference preparation for the reserved set takes {s['reference_seconds']:.3f} seconds. These one-time and benchmark costs remain separate from the supplied-basis totals. The stored master indices contain no solved target coefficients.\n\n"
 offline=s['offline_costs'];total=sum(offline[k]['summed_measured_seconds'] for k in ['training','validation','application_validation'])
 results+=f"Training-data collection, model selection data, and full-cost admission use {total:.3f} seconds of summed measured application time. Their independent references add {offline['reference_seconds']:.3f} seconds. "
 if offline['fit_job_wall_seconds'] is not None:results+=f"Model fitting, including its initialization, takes {offline['fit_job_wall_seconds']:.3f} seconds. "
 results+='These are separate one-time learning costs. The reserved reduction times measure use of the prepared method and do not imply that training has already paid for itself in a single calculation. Summed process times also differ from elapsed collection time when two workers run concurrently.\n\n'
 results+='The triangle identity has an explicit analytic domain and independent native checks. The learned model has a narrower measured domain: two massless two-loop box structures with rational kinematics and symbolic dimension. The new index batches test transfer within those structures. General connected higher-loop scattering and all integral types remain outside this evidence. A finite candidate search also cannot prove that the selected workflow has the smallest possible runtime.\n\\FloatBarrier\n'
 (REPORT/'analytic_batch_results.tex').write_text(results)
 (REPORT/'analytic_batch_appendix.tex').write_bytes((HERE/'analytic_batch_appendix.tex').read_bytes())
 (REPORT/'analytic_batch_data.json').write_text(json.dumps(s,indent=2)+'\n')
 q=REPORT/'report.tex';z=q.read_text()
 if '\\input{analytic_batch_method}' not in z:z=z.replace('\\section{Training and comparison design}','\\input{analytic_batch_method}\n\n\\section{Training and comparison design}')
 if '\\input{analytic_batch_results}' not in z:z=z.replace('\\section{Overall interpretation}','\\input{analytic_batch_results}\n\n\\section{Overall interpretation}')
 if '\\input{analytic_batch_appendix}' not in z:z=z.replace('\\input{fast_deployment_appendix}','\\input{fast_deployment_appendix}\n\\input{analytic_batch_appendix}')
 z=z.replace('The latest comparison improves the exact arithmetic, trains a recurrence-strategy model, and measures independent products and analytic families through thirteen loops.', 'The latest comparison adds a derived triangle formula and trains a complete-cost model to choose shared native reductions. It tests new two-loop target batches, symbolic triangle kinematics, and independent products through thirteen loops.')
 old_marker='The current comparison in Section~\\ref{sec:fast-results}'
 current_marker='The latest comparison in Section~\\ref{sec:analytic-batch-results}'
 start=z.index(old_marker if old_marker in z else current_marker)
 end=z.index('\n\nThe direct local comparisons',start)
 z=z[:start]+r'''The latest comparison in Section~\ref{sec:analytic-batch-results} separates three changes: a checked master-index registry, an exact triangle formula, and a learned choice of target grouping and sparse seed region. The same-basis control isolates the latter two changes. The fixed-action control then measures the added batch model under the same exact implementation, while the control with both learned choices disabled measures its combination with the retained sparse expert. The preceding formula and recurrence experiments remain separate comparisons with their original inputs and controls.'''+z[end:]
 q.write_text(z)
 abstract=r'''\begin{abstract}
We study how exact analytic methods and machine learning can reduce the time needed to decompose loop integrals into master integrals with Kira. The workflow first applies supported analytic identities and independent-loop factorization, then selects the native reduction work that remains. We derive a finite-product reduction for a one-scale massless triangle, including polynomial numerators, and train a cost-sensitive model to choose shared target reductions and sparse seed regions. Training uses complete measured time, including model loading, exact algebra, checks, and recovery. Separate controls distinguish the new learned decision from exact formulas and prior basis preparation. '''
 abstract+=f"The reserved test contains 58 requests: forty two-loop scattering batches, thirteen independent triangle products through thirteen loops, one symbolic triangle, and four compatibility requests. The final method verifies {s['totals']['learned']['verified']} requests in all three repetitions. On {v['matched']} matched requests, it uses {v['learned_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for the preceding application with the same master indices, a speed factor of {v['speedup']:.2f}. "
 abstract+=('Full-cost validation enables the new batch model. ' if a['enabled'] else 'Full-cost validation keeps the fixed batch action and preserves the previously validated sparse expert. ')
 abstract+=f"On the forty native box requests, the added learned choice has time ratio {native_fixed['ratio']:.3f} against the same workflow with a fixed batch action. "
 abstract+=r'''Learned row selection remains omitted because its measured improvement is unresolved. The triangle result follows an explicit analytic identity, while learned gains apply to the stated native test domain. These finite tests do not establish a universal speedup for arbitrary connected high-loop integrals.
\end{abstract}
'''
 (REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
The reduction workflow can save time by removing exact work before selecting the remaining algebra. The triangle formula replaces equation generation and elimination within its stated one-scale domain. Independent-loop factorization extends that result to products through thirteen loops. For coupled two-loop boxes, the new model learns whether targets should share a reduction and which sparse seed region should supply the equations. Complete application cost determines whether the learned choice enters deployment.

'''
 conclusion+=f"The latest method verifies {s['totals']['learned']['verified']} of 58 reserved requests in every repetition. Its matched total is {v['learned_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for the same-basis preceding application, or {v['speedup']:.2f} times the speed. "+sentence(fixed,'the fixed batch action')+'\n\n'
 conclusion+=sentence(native_fixed,'the fixed action on the forty native box requests')+'This comparison holds the exact methods and prepared basis constant.\n\n'
 conclusion+=r'''These controls keep the sources of improvement separate. A prepared master-index set avoids repeated discovery, exact formulas avoid whole reductions, and learned choices alter the work left for native Kira. The earlier seed and equation models retain their separate measured gains. Learned row selection remains excluded because its later timing interval includes equal time.

The current result covers an explicit analytic triangle family, independent products, and two learned native graph structures. It does not demonstrate arbitrary connected thirteen-loop scattering. Every failed or unsupported request remains part of the coverage record. Further claims require new physical families, separate training or validation where needed, and complete-time comparisons with equally prepared controls.
'''
 (REPORT/'paper_conclusion.tex').write_text(conclusion)
 # Give notes their own labels, preserving all earlier material.
 for name in ['method','results','appendix']:
  text=(REPORT/f'analytic_batch_{name}.tex').read_text()
  for prefix in ['sec:analytic-batch','app:analytic-batch','eq:batch','tab:analytic-batch','fig:analytic-batch','app:fast-method','eq:analytic']:text=text.replace(prefix,prefix.replace(':',':notes-'))
  (REPORT/f'notes_analytic_batch_{name}.tex').write_text(text)
 interrupted=s['interrupted_validation'];q=REPORT/'notes_analytic_batch_results.tex'
 q.write_text(q.read_text()+r'\subsection{Preserved validation before the hardware assignment}'+'\n'+f"The initial full application validation used profile $3037$ on two different cluster nodes. It recorded {interrupted['records']} completed measurements with exact agreement before the slower worker was stopped. Their summed measured time is {interrupted['completed_measured_seconds']:.3f} seconds. The runtime and measurement sources, completed records, and interrupted inputs remain preserved. These measurements do not enter the admission decision. We retain the selected tree and its weights, then use the fresh profile $3041$ on the fixed reserved-test node for the completed validation. This change precedes all reserved testing and changes no target reduction formula.\n")
 q=REPORT/'notes.tex';z=q.read_text();addition=''.join('\\input{notes_analytic_batch_'+n+'}\n' for n in ['method','results','appendix'])
 if addition not in z:z=z.replace('\\bibliographystyle','% BEGIN CURRENT WORKFLOW UPDATE\n'+addition+'% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle',1)
 q.write_text(z)
 q=REPORT/'Makefile';z=q.read_text();z=re.sub(r'^report.pdf:.*$',lambda m:m.group(0)+' analytic_batch_method.tex analytic_batch_results.tex analytic_batch_appendix.tex' if 'analytic_batch_results.tex' not in m.group(0) else m.group(0),z,flags=re.M);q.write_text(z)
 for q in [REPORT/'report.tex',REPORT/'notes.tex',REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex',*REPORT.glob('*analytic_batch*.tex')]:q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 print(json.dumps(dict(report_written=True,complete_checks=s['coefficient_checks'])),flush=True)
if __name__=='__main__':main()
