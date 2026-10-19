"""Write the paper, notes, and folder guides from completed frozen measurements."""
from s00_fast_common import *
REPORT=ROOT/'report'

def comparison_sentence(v,control):
 if not v['cases']:return 'No request completes all paired repetitions for this comparison.'
 lo,hi=v['repeat_interval'];direction='less' if v['ratio']<1 else 'more'
 text=f"The combined method uses {abs(v['reduction_percent']):.1f}\\% {direction} time than {control}, with time ratio {v['ratio']:.3f} and repetition interval $[{lo:.3f},{hi:.3f}]$. "
 if lo<=1<=hi:text+='The interval includes equal times. '
 return text

def main():
 s=read(HERE/'summary.json');assert s['complete'];a=s['comparisons'];cov=s['coverage'];model=read(HERE/'trained_model/recurrence.json')
 for n in ['fast_decomposition_method.tex','fast_decomposition_appendix.tex']:(REPORT/n).write_text((HERE/n).read_text())
 text=r'''\section{Complete times and coverage through thirteen loops}
\label{sec:fast-results}
The initial fast-implementation comparison tests the direct finite products, faster exact recurrence, and newly trained recurrence strategy together with the retained sparse-seed model. The preceding deployed application is the main practical control. A matched native control retains the earlier exact formulas and block splitting but uses native Kira decisions for the remaining work. The fast fixed control uses the new exact implementation and fixed choices. Thus the native control already contains acceleration, and its timing is not the time of stock Kira on every target.

The reserved set contains 65 requests, including analytic vacuum and propagator families at every loop count through thirteen, distinct triangle products, rational scalar polygons, symbolic bubbles, and coupled native cases. Appendix~\ref{app:fast-inputs} defines the targets and parameter profiles. Each method starts a fresh process three times per completed request. The timer includes loading, prediction, exact reduction, output, and the independent coefficient check. Prepared master indices and reference calculations remain separate. Table~\ref{tab:fast-results} compares only requests that complete every repetition for both methods.

\begin{table}[!htbp]\centering\small
\caption{Complete application times in the new reserved test. Times are sums of per-request medians in seconds. Each row uses the same matched requests for its three controls when all methods complete; any unequal counts are reported below.}
\label{tab:fast-results}
\begin{tabularx}{\linewidth}{@{}Yrrrrr@{}}\toprule
Collection & $N$ & New learned & Previous & Native & Fast fixed\\\midrule
'''
 groups=[('finite_formula','Vacuum and propagator formulas'),('symbolic_formula','Symbolic one-mass vacua'),('products','Distinct triangle products'),('recurrence','Scalar recurrence'),('learned_native','Nonplanar seed model'),('symbolic_native','Symbolic native inputs'),('native_compatibility','Coupled compatibility'),('all','All matched requests')]
 for k,name in groups:
  v=a[k]['previous'];n=v['cases']
  if not n:continue
  common=set(v['case_ids'])
  for ctrl in ['native','fixed']:common &= set(a[k][ctrl].get('case_ids',[]))
  rr=[r for r in s['rows'] if r['case'] in common]
  if not rr:continue
  times={m:sum(statistics.median(r['times'][m]) for r in rr) for m in ['learned','previous','native','fixed']}
  text+=name+f" & {len(rr)}"+''.join(f" & {times[m]:.3f}" for m in ['learned','previous','native','fixed'])+r' \\'+'\n'
 text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 text+=comparison_sentence(a['all']['previous'],'the preceding deployed application')+comparison_sentence(a['all']['native'],'the already accelerated native control')+'\n\n'
 text+=comparison_sentence(a['all']['fixed'],'the fast fixed control')+'This last comparison isolates request-dependent learned choices after the exact implementation changes. It does not assign the finite-product or arithmetic savings to ML.\n\n'
 text+=f"The combined method completes {s['totals']['learned']['verified']} of 65 requests in all three repetitions. The preceding, native, and fast fixed methods complete {s['totals']['previous']['verified']}, {s['totals']['native']['verified']}, and {s['totals']['fixed']['verified']} requests, respectively. Independent reference preparation takes {s['reference_seconds']:.3f} seconds. "
 text+=f"Across the timed runs, the exact checker performs {sum(t['coefficient_checks'] for t in s['totals'].values()):,} coefficient comparisons. The new method's first-attempt total is {s['totals']['learned']['first_seconds']:.3f} seconds, including {s['totals']['learned']['failed_first_seconds']:.3f} seconds spent on unverified or incomplete first attempts. Failed requests remain in these counts and receive no completed-time speedup.\n\n"
 text+=r'''\subsection{What the new learned decision adds}
The recurrence model selects a strategy before the exact substitutions begin. '''
 text+=f"Validation chooses a depth-{model['selected']['depth']} tree, minimum leaf population {model['selected']['minimum']}, and prediction margin {model['margin']:.2f}. Its fixed alternative selects the last raised index. The measured validation recurrence total changes from {model['fixed_validation_seconds']:.4f} to {model['learned_validation_seconds']:.4f} seconds, including prediction overhead. "
 text+=f"The reserved application test admits the new model on {a['new_model_admitted']['fixed']['cases']} requests and changes the fixed pivot strategy on {a['new_model_changed']['fixed']['cases']} requests. These groups describe observed use, while the complete scalar-recurrence group was specified before testing.\n\n"
 text+='For the nine reserved scalar-recurrence requests, '+comparison_sentence(a['recurrence']['fixed'],'the same fast recurrence with fixed strategy').replace('The combined method','the combined method',1)+'For the eight nonplanar requests, '+comparison_sentence(a['learned_native']['fixed'],'the fixed sparse-seed choice').replace('The combined method','the combined method',1)+'The latter model retains its earlier training. These comparisons separate the new recurrence decision from the retained seed decision.\n\n'
 text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/fast_decomposition.pdf}
\caption{Direct formulas and exact arithmetic reduce complete time, while the fixed control isolates the additional learned choices. Values below one favor the new learned application. Intervals resample the three paired repetitions on the same fixed requests. They do not measure uncertainty over all possible integral families. Formula-only groups use the same exact path in both methods, so their differences measure timing variation.}
\label{fig:fast-time}
\end{figure}

\subsection{Which high-loop requests complete}
The timing set deliberately contains analytically supported families. To expose its limits, a separate 110-request audit includes one-mass and all-mass vacua, massless and massive propagators, scattering ladders, and boxes with bubble chains at each loop count through thirteen. It adds scaleless cases, other scattering structures, and symbolic scales. Each application receives twenty seconds per request. Figure~\ref{fig:fast-coverage} shows the regular loop sequences, and Table~\ref{tab:fast-coverage} includes every audit request.

\begin{table}[!htbp]\centering\small
\caption{Bounded audit at each loop count. ``New'' and ``Previous'' count reported completions within twenty seconds. ``Agree'' counts paired completions with exact coefficient agreement. The audit has different limits and targets from the timing comparison.}
\label{tab:fast-coverage}
\begin{tabular}{@{}rrrrr@{}}\toprule
Loops & Requests & New & Previous & Agree\\\midrule
'''
 for L,row in cov['by_loop'].items():text+=f"{L} & {row['requests']} & {row['methods']['learned']['successes']} & {row['methods']['previous']['successes']} & {row['paired_verified']} \\\\\n"
 t=cov['total'];text+=f"Total & {t['requests']} & {t['methods']['learned']['successes']} & {t['methods']['previous']['successes']} & {t['paired_verified']} \\\\\n"
 text+=r'''\bottomrule\end{tabular}\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/fast_coverage.pdf}
\caption{Completion depends on integral structure as well as loop count. The grid shows the new and preceding applications under the same twenty-second audit limit. A failed entry includes timeouts and unsupported inputs. Additional symbolic and scattering requests appear in the complete counts of Table~\ref{tab:fast-coverage}.}
\label{fig:fast-coverage}
\end{figure}
\FloatBarrier

The six additional completions are scaleless vacuum requests at eight through thirteen loops. Their exact result is zero by the homogeneous IBP identity derived in Eq.~\eqref{eq:fast-scaleless}. The preceding application rejects their native index count before using this general zero rule. These additional completions come from an exact identity and carry no ML speedup claim.

The analytic families and independent products establish high-loop coverage within their derived domains. General coupled scattering, arbitrary numerator powers, singular kinematics, cut integrals, and symbolic indices require further methods or tests. The native 31-index limit also excludes some complete coupled coordinate systems~\cite{Kira3}. Neither prediction nor a shorter failed attempt supplies the missing reduction. The audit therefore records these limits explicitly and does not label its finite collection as all integral types.
'''
 statuses=cov['total']['methods']['learned']['statuses']
 incomplete=cov['total']['requests']-cov['total']['methods']['learned']['successes']
 text=text.replace('The six additional completions',f"The {incomplete} incomplete requests comprise {statuses.get('application_deadline',0)} time limits and {statuses.get('incomplete_block_reduction',0)} inputs above the native index bound.\n\nThe six additional completions")
 (REPORT/'fast_decomposition_results.tex').write_text(text)
 v=a['all']['previous'];nat=a['all']['native'];fixed=a['all']['fixed']
 abstract=r'''\begin{abstract}
We study how to reduce the time needed to decompose loop integrals into master integrals. The method combines direct analytic formulas, independent-loop factorization, exact scalar one-loop recurrences, and learned choices in Kira. A new cost-sensitive tree selects a recurrence strategy, while a retained seed model selects sparse native reductions within its validated domain. The algebra and output checks remain exact. '''
 abstract+=f"A reserved test contains 65 requests, including vacuum and propagator families and independent products through thirteen loops. The combined method completes {s['totals']['learned']['verified']} requests in all three repetitions. Across {v['cases']} matched requests, its summed median time is {v['learned_seconds']:.3f} seconds, compared with {v['control_seconds']:.3f} seconds for the preceding application, a factor of {v['speedup']:.2f}. "
 abstract+=f"The time ratio to the fast fixed control is {fixed['ratio']:.3f}, with repetition interval $[{fixed['repeat_interval'][0]:.3f},{fixed['repeat_interval'][1]:.3f}]$. "
 abstract+=f"A separate bounded audit covers 110 requests at one through thirteen loops; the new application completes {t['methods']['learned']['successes']}, and {t['paired_verified']} paired results agree exactly with the preceding application. "
 abstract+=r'''Timings include loading, prediction, algebra, checks, and recovery. Master-index and reference preparation remain separate. The controls distinguish exact implementation savings from learned gains. General connected high-loop scattering and universal speedup remain outside the demonstrated coverage.
\end{abstract}
'''
 (REPORT/'paper_abstract.tex').write_text(abstract)
 conclusion=r'''\section{Conclusion}
The measured decomposition time decreases when the application uses exact structure before a general equation system. Direct finite products handle the supported vacuum and propagator families, and a combined scalar one-loop recurrence handles raised powers. Independent-loop factorization extends these methods to products with many loops. Learned decisions select recurrence strategies or sparse native seed regions, while exact algebra determines the coefficients.

'''
 conclusion+=comparison_sentence(v,'the preceding application')+comparison_sentence(nat,'the matched native control')+'Both comparisons include the exact implementation changes. '+comparison_sentence(fixed,'the same fast implementation with fixed choices')+'This final control identifies the additional request-dependent learned contribution.\n\n'
 conclusion+='The new recurrence model learns measured kernel costs and must also justify its cost at the application level. '+comparison_sentence(a['recurrence']['fixed'],'the fixed strategy on the nine scalar recurrence requests')+'The retained seed model remains a separate learned contribution on supported coupled inputs. The row model remains omitted because its earlier live test did not resolve a complete-time gain, and the equation model retains its separately measured domain.\n\n'
 conclusion+=f"The full comparison verifies {s['totals']['learned']['verified']} of 65 new-method requests in all repetitions. The separate twenty-second audit completes {t['methods']['learned']['successes']} of 110 requests. These results support analytic families and independent products through thirteen loops, together with the specified lower-loop native reductions. They do not establish complete reduction for every topology, numerator, or kinematic limit. Prepared master indices, training, and independent reference preparation remain separate costs. Further generality requires verified reduction methods for the coupled cases that remain incomplete.\n"
 (REPORT/'paper_conclusion.tex').write_text(conclusion)
 q=REPORT/'report.tex';rt=q.read_text()
 if '\\input{fast_decomposition_method}' not in rt:rt=rt.replace('\\input{analytic_decomposition_method}','\\input{analytic_decomposition_method}\n\\input{fast_decomposition_method}')
 if '\\input{fast_decomposition_results}' not in rt:rt=rt.replace('\\section{Overall interpretation}','\\input{fast_decomposition_results}\n\n\\section{Overall interpretation}')
 if '\\input{fast_decomposition_appendix}' not in rt:rt=rt.replace('\\input{parser_guard_appendix}','\\input{parser_guard_appendix}\n\\input{fast_decomposition_appendix}')
 rt=rt.replace('The latest comparison adds massive scalar one-loop recurrences and independent products through thirteen loops while retaining the existing learned models. It also includes fully symbolic two-point kinematics.','The latest comparison improves the exact arithmetic, trains a recurrence-strategy model, and measures independent products and analytic families through thirteen loops. A separate audit records completion and failure across vacuum, propagator, and scattering sequences at each loop count. It also includes symbolic kinematics.')
 rt=rt.replace('The new analytic comparison also includes two requests with symbolic masses and momentum invariants. Thus the exported coefficients are exact rational functions of $d$.','The analytic comparisons also include symbolic masses and momentum invariants. Thus the exported coefficients are exact rational functions of $d$ and any remaining symbolic scales.')
 rt=rt.replace('The new comparison starts a fresh process','The new comparisons start a fresh process').replace('measurement and includes imports','measurement and include imports')
 if 'The current comparison in Section~\\ref{sec:fast-results} measures' not in rt:rt=rt.replace('The initial analytic-enabled comparison in Section~\\ref{sec:analytic-results} tests', 'The current comparison in Section~\\ref{sec:fast-results} measures the direct formulas, revised exact arithmetic, and learned recurrence strategy against the preceding deployed method. The fixed control separates these exact changes from the request-dependent learned choices. The initial analytic-enabled comparison in Section~\\ref{sec:analytic-results} tests')
 q.write_text(rt)
 for n in ['method','results','appendix']:
  z=(REPORT/f'fast_decomposition_{n}.tex').read_text()
  for prefix in ['sec:fast','app:fast','eq:fast','tab:fast','fig:fast','app:analytic','eq:analytic']:z=z.replace(prefix,prefix.replace(':',':notes-'))
  (REPORT/f'notes_fast_decomposition_{n}.tex').write_text(z)
 q=REPORT/'notes.tex';nt=q.read_text();add=''.join('\\input{notes_fast_decomposition_'+n+'}\n' for n in ['method','results','appendix'])
 if add not in nt:nt=nt.replace('\\bibliographystyle','% BEGIN CURRENT WORKFLOW UPDATE\n'+add+'% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle',1)
 q.write_text(nt)
 (REPORT/'fast_decomposition_data.json').write_text(json.dumps(s,indent=2)+'\n')
 q=REPORT/'Makefile';mt=q.read_text();mt=re.sub(r'^report.pdf:.*$',lambda m:m.group(0)+''.join(' fast_decomposition_'+n+'.tex' for n in ['method','results','appendix']) if 'fast_decomposition_results.tex' not in m.group(0) else m.group(0),mt,flags=re.M);q.write_text(mt)
 q=HERE/'README.md';g=q.read_text().split('The reserved comparison is in progress.')[0].split('## Completed reserved comparison')[0];g+='## Completed reserved comparison\n\n'
 g+=f"The new application verifies {s['totals']['learned']['verified']} of 65 requests in all three repetitions.\nThe separate audit completes {t['methods']['learned']['successes']} of 110 requests within twenty seconds each.\n"
 for group in ['all','recurrence','learned_native']:
  for control,vv in a[group].items():
   if vv['cases']:g+=f"{group}, {control} control: {vv['cases']} matched requests; time ratio {vv['ratio']:.6f}; repetition interval {vv['repeat_interval']}.\n"
 g+='\nRead summary.json for every timing, failure count, and audit outcome.\nRead validation.json for the frozen-evidence and document checks.\nThe report separates exact implementation savings from learned gains.\n';q.write_text(g)
 folders={'training':'Cost records for the recurrence model. These records do not enter reserved tests.','training/training':'112 training requests at profiles 2611 and 2617. Each record includes target powers, four costs, and exact agreement.','training/validation':'56 validation requests at profile 2621. Use these only for model and margin selection.','trained_model':'recurrence.json stores the frozen tree, feature ranges, fixed strategy, and decision margin. selection.json records every validation candidate.','model_test':'Compressed full-process timings and exact checks for the 65 reserved requests. Failed first attempts remain present.','references':'Independent coefficients for the final check. The application never reads this folder to form an answer.','coverage':'First-attempt outcomes for every timing request.','audit':'Complete outcomes for the separate 110-request audit. A timeout means incomplete under the audit limit.','audit_records':'Raw new and preceding application records for the twenty-second audit.','requests':'Temporary request and output files. Jobs remove these files after each run.','logs':'Scheduler logs stay on Hoffman. Structured measurements and this guide are published.'}
 for name,description in folders.items():
  d=HERE/name;d.mkdir(exist_ok=True);(d/'README.md').write_text('# '+name.split('/')[-1].replace('_',' ').capitalize()+'\n\n'+description+'\n\nRead '+('../'*(len(Path(name).parts)))+'README.md for the method and controls.\n')
 for name,link in [('README.md','ML_model_adaptive_reduction/fast_decomposition/README.md'),('ML_model_adaptive_reduction/README.md','fast_decomposition/README.md'),('report/README.md','../ML_model_adaptive_reduction/fast_decomposition/README.md')]:
  q=ROOT/name;z=q.read_text();heading='## Current fast exact and learned decomposition\n'
  if heading not in z:z=heading+'\nUse [the current method guide]('+link+') for the new recurrence model, exact formulas, tests, and limits.\nThe final entry point is s03_fast_runtime.py in fast_decomposition.\nThe paper and notes include the 65-request timing test and the 110-request coverage audit.\nEarlier studies retain their original evidence.\n\n'+z
  q.write_text(z)
 q=PRIOR/'README.md';z=q.read_text();heading='## Superseding fast decomposition study\n'
 if heading not in z:q.write_text(heading+'\nUse ../fast_decomposition/README.md for the current application.\nThis folder preserves the preceding exact recurrence and its measurements.\nIts document receipts identify the earlier paper and notes.\n\n'+z)
 q=REPORT/'paper_figures/README.md';z=q.read_text()
 if 'fast_decomposition.pdf' not in z:q.write_text(z+'\nfast_decomposition.pdf separates the total improvement from the added learned decisions.\nfast_coverage.pdf shows completion by integral structure and loop count under the bounded audit.\n')
 for q in list(REPORT.glob('*fast_decomposition*.tex'))+[REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex']:
  q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 print(json.dumps(dict(documented=True,requests=s['requests'])),flush=True)
if __name__=='__main__':main()
