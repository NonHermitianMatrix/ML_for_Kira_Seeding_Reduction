"""Report the separate parser-guard test and validate the final application."""
from s01_common import *
import statistics,subprocess,re
DEP=HERE/'deployment';REPORT=ROOT/'report'

def main():
 import numpy as np
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for i in range(2):assert READ(DEP/f'test_{i}_complete.json')['complete']
 p=READ(DEP/'protocol.json');assert READ(DEP/'admission.json')['enabled']
 assert all(sha(HERE/n)==v for n,v in p['runtime_sources'].items())
 assert sha(HERE/'basis_registry.json')==p['basis_sha256']
 assert sha(HERE/'test_protocol.json')==p['initial_protocol_sha256']
 rows=[];checks=0;totals={m:dict(first_seconds=0.,all_seconds=0.,verified=0,native_calls=0,failed_native_calls=0) for m in p['methods']}
 for c in p['cases']:
  row=READ(DEP/'coverage'/(c['id']+'.json'));row['times']={};ref=READ(DEP/'references'/(c['id']+'.json.gz'));assert ref['success']
  for m in p['methods']:
   records=[READ(DEP/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')) for rep in range(3)]
   for r in records:
    ok,n=h.compare(r,ref);assert ok and r['independently_verified'];checks+=n
   times=[r['complete_process_and_check_seconds'] for r in records];row['times'][m]=times
   totals[m]['first_seconds']+=times[0];totals[m]['all_seconds']+=sum(times);totals[m]['verified']+=1
   attempts=[a for r in records for b in r.get('blocks',[]) if not b.get('reused') for a in b['result'].get('attempts',[]) if a.get('native_called',True)]
   totals[m]['native_calls']+=len(attempts);totals[m]['failed_native_calls']+=sum(not a['success'] for a in attempts)
  rows.append(row)
 def comparison(rs,m):
  x=np.array([r['times']['learned'] for r in rs]);y=np.array([r['times'][m] for r in rs]);a=float(np.median(x,axis=1).sum());b=float(np.median(y,axis=1).sum())
  ix=np.random.RandomState(2539).randint(0,3,(2000,len(rs),3));ii=np.arange(len(rs))[None,:,None];rat=np.median(x[ii,ix],axis=2).sum(1)/np.median(y[ii,ix],axis=2).sum(1)
  return dict(cases=len(rs),learned_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,reduction_percent=100*(1-a/b),repeat_interval=list(map(float,np.quantile(rat,[.025,.975]))))
 groups={'all':rows,'symbolic':[r for r in rows if r['scope']=='symbolic_guard'],'compatibility':[r for r in rows if r['scope']=='guard_compatibility']}
 comparisons={g:{m:comparison(rs,m) for m in ['all_analytic','native','fixed']} for g,rs in groups.items()}
 s=dict(complete=True,requests=len(rows),rows=rows,totals=totals,comparisons=comparisons,coefficient_checks=checks,protocol_sha256=sha(DEP/'protocol.json'),admission_sha256=sha(DEP/'admission.json'),reference_seconds=sum(r['reference_seconds'] for r in rows))
 assert len(rows)==9
 write(DEP/'summary.json',s);(REPORT/'parser_guard_data.json').write_text(json.dumps(s,indent=2)+'\n')
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,ax=plt.subplots(figsize=(7.3,2.8));values=[]
 for i,(g,name) in enumerate([('symbolic','Four symbolic requests'),('compatibility','Five compatibility requests'),('all','All nine requests')]):
  q=comparisons[g]['all_analytic'];v=q['ratio'];lo,hi=q['repeat_interval'];values += [lo,hi]
  ax.plot([lo,hi],[i,i],color='#146b7d',lw=2);ax.scatter(v,i,color='#146b7d',s=30);ax.text(hi+.025,i,f'{v:.3f}',va='center',fontsize=9)
 ax.set_yticks(range(3));ax.set_yticklabels(['Four symbolic requests','Five compatibility requests','All nine requests']);ax.invert_yaxis();ax.axvline(1,color='black',ls='--',lw=1)
 ax.set_xlim(max(0,min(values)-.06),max([1]+values)+.15);ax.set_xlabel('Final time / initial analytic-enabled time');ax.set_title('Choosing the cheaper path reduces the measured cost')
 fig.tight_layout();fig.savefig(REPORT/'paper_figures/parser_guard.pdf',bbox_inches='tight');plt.close(fig)
 # Preserve the first experiment and identify its two symbolic regressions.
 initial=READ(HERE/'summary.json');symbols=[r for r in initial['rows'] if 'symbolic' in r['case']]
 assert len(symbols)==2
 slow=sorted([statistics.median(r['times']['learned'])/statistics.median(r['times']['native']) for r in symbols])
 intro=f"\nThe two fully symbolic requests expose a cost hidden by the collection average: their analytic-enabled medians are {slow[0]:.2f} and {slow[1]:.2f} times the matched native medians. Each fresh process loads and uses symbolic algebra before it returns the recurrence result. These measurements compare full paths and do not isolate import time. Section~\\ref{{sec:parser-guard}} tests a separate deployment rule that avoids this setup. The original 41-request measurements remain unchanged.\n"
 for name,prefix in [('analytic_decomposition_results.tex',''),('notes_analytic_decomposition_results.tex','notes-')]:
  q=REPORT/name;t=q.read_text().replace('The latest comparison measures','The initial analytic-enabled comparison measures')
  if 'The two fully symbolic requests expose' not in t:t+=intro.replace('sec:parser-guard','sec:'+prefix+'parser-guard')
  q.write_text(t)
 v=comparisons['all']['all_analytic'];sy=comparisons['symbolic']['all_analytic'];co=comparisons['compatibility']['all_analytic'];dev=READ(DEP/'admission.json')
 text=r'''\section{Using native reduction when symbolic algebra costs more}
\label{sec:parser-guard}
The symbolic regressions motivate a narrower use of the new recurrence. Before entering it, the final application checks whether all masses and scalar products are direct rational values. If an input requires symbolic parsing, the application keeps the older exact formulas where they apply and otherwise uses Kira. This rule leaves the learned models and the existing native settings unchanged. It controls the cost of the new analytic stage; it does not estimate a reduction coefficient.

Two development requests use the massive symbolic two-point family with powers $(4,1)$ and $(1,4)$. We enable the rule only when it reduces their summed median time by at least five percent. The reserved comparison then uses powers $(3,2)$ and $(2,3)$, two independent products containing those blocks at loop orders two and thirteen, and five compatibility requests. Appendix~\ref{app:parser-guard} specifies these inputs. Each method runs three times in a fresh process, and all four methods pass every exact coefficient comparison.

\begin{table}[!htbp]\centering\small
\caption{Separate validation of the final input rule. Times are sums of per-request medians in seconds. The initial analytic variant has the new recurrence but lacks the input rule. Native and fixed controls retain the same prepared master indices and factorization.}
\label{tab:parser-guard}
\begin{tabular}{@{}lrrrrr@{}}\toprule
Collection & $N$ & Final & Initial analytic & Native & Fixed\\\midrule
'''
 for g,label in [('symbolic','Symbolic inputs'),('compatibility','Compatibility'),('all','All requests')]:
  q=comparisons[g];a=q['all_analytic'];text+=f"{label} & {a['cases']} & {a['learned_seconds']:.3f} & {a['control_seconds']:.3f} & {q['native']['control_seconds']:.3f} & {q['fixed']['control_seconds']:.3f} \\\\\n"
 text+=r'''\bottomrule\end{tabular}\end{table}
'''
 for q,label in [(sy,'the four symbolic requests'),(co,'the five compatibility requests'),(v,'all nine requests')]:
  lo,hi=q['repeat_interval'];direction='less' if q['ratio']<1 else 'more'
  text+=f"\nFor {label}, the final method uses {abs(q['reduction_percent']):.1f}\\% {direction} time than the initial analytic variant. Its time ratio is {q['ratio']:.3f}, with repetition interval $[{lo:.3f},{hi:.3f}]$. "
  if lo<=1<=hi:text+='The interval includes equal times. '
  text+='\n'
 q=comparisons['all']['native'];lo,hi=q['repeat_interval']
 text+=f"\nAcross all nine requests, the final method uses {q['reduction_percent']:.1f}\\% less time than the matched native control, with time ratio {q['ratio']:.3f} and repetition interval $[{lo:.3f},{hi:.3f}]$. "
 q=comparisons['all']['fixed'];lo,hi=q['repeat_interval']
 text+=f"Against the fixed control, the ratio is {q['ratio']:.3f}, with interval $[{lo:.3f},{hi:.3f}]$. This interval includes equal times, so this follow-up does not establish an additional learned saving. The symbolic subset uses the same native branch in both final and native methods; its small timing difference also has an interval that includes one.\n"
 text+=f"\nAll {len(rows)} requests complete in every repetition, giving {len(rows)*len(p['methods'])*3} timed reductions and {checks:,} exact coefficient comparisons. Independent reference preparation takes {s['reference_seconds']:.3f} seconds and remains separate. The first-attempt total for the final method is {totals['learned']['first_seconds']:.3f} seconds; this total includes every requested input.\n"
 text+=r'''
\begin{figure}[!htbp]\centering
\includegraphics[width=.9\linewidth]{paper_figures/parser_guard.pdf}
\caption{The input rule bypasses symbolic recurrence work where native reduction is cheaper. Values below one favor the final rule. Intervals resample three repetitions on these fixed inputs. Compatibility requests check that other application branches remain available.}
\label{fig:parser-guard}
\end{figure}

The final rule uses native Kira for the four symbolic requests, so their saving relative to the initial analytic variant is an integration improvement. This test compares complete paths and does not separately measure parsing, import, and symbolic arithmetic costs. It is not an additional ML contribution. The earlier 41-request experiment and this nine-request test use different targets and remain separate comparisons. We do not combine their times into a new overall speedup or claim that every symbolic family benefits from this rule.
'''
 (REPORT/'parser_guard_results.tex').write_text(text)
 appendix=r'''\section{Inputs and admission rule for the final application}
\label{app:parser-guard}
Use the symbolic two-point denominators $D_1=\ell^2-\mu_1+i0$ and $D_2=(\ell-p)^2-\mu_2+i0$, with independent variables $\mu_1$, $\mu_2$, and $s=p^2$. Development uses one target per request, with powers $(4,1)$ or $(1,4)$. Testing uses $(3,2)$ and $(2,3)$, one product of two identical $(3,2)$ blocks, and one product of thirteen identical $(2,3)$ blocks. As in the main comparison, identical blocks share work within each request and the product expansion stays factored.

The compatibility inputs comprise two-, four-, and five-denominator rational polygons at profile $2521$ and extra power three, using Appendix~\ref{app:analytic-inputs}. They also include a nonplanar box at profile $2527$ with target $(1,1,1,1,1,1,1,-3,0)$ and the one-mass thirteen-loop vacuum at profile $2531$, with two extra powers on its first physical denominator. Their family definitions follow Appendices~\ref{app:hybrid-experts} and~\ref{app:families-new}. Every input uses the previously prepared master indices; the test does not add entries to that registry.

The input rule accepts direct integer or rational mass and scalar-product values for the new recurrence. Expressions that require a symbolic parser use the existing exact or native path, even if an expression could simplify to a rational number. This conservative implementation avoids a symbolic startup cost merely to decide which method to use. Three rotated repetitions compare the final learned application, its fixed counterpart, matched native settings, and the initial analytic-enabled application. Exact comparison with an independent reference follows every run and remains inside its timer.
'''
 (REPORT/'parser_guard_appendix.tex').write_text(appendix)
 for name in ['analytic_decomposition_appendix.tex','notes_analytic_decomposition_appendix.tex']:
  q=REPORT/name;t=q.read_text().replace('an unsupported numerator or cut, or an exceeded analytic work limit','an unsupported numerator, or an exceeded analytic work limit')
  if 'The existing application interface rejects cut propagators' not in t:t=t.replace('This check preserves a common output basis','The existing application interface rejects cut propagators and symbolic indices before this stage. This check preserves a common output basis')
  q.write_text(t)
 method=REPORT/'analytic_decomposition_method.tex';t=method.read_text()
 if 'The final input rule' not in t:method.write_text(t+'\nThe final input rule limits the new recurrence to direct rational kinematics. Symbolic inputs retain the earlier exact formulas or native Kira path, as tested in Section~\\ref{sec:parser-guard}. The symbolic recurrence remains mathematically valid, but its fresh-process setup cost exceeded the native cost in the measured examples.\n')
 for name in ['report.tex','notes.tex']:
  q=REPORT/name;t=q.read_text()
  if name=='report.tex':
   t=t.replace('The current combined comparison in Section~\\ref{sec:analytic-results}', 'The initial analytic-enabled comparison in Section~\\ref{sec:analytic-results}')
   t=t.replace('\\input{analytic_decomposition_results}\n','\\input{analytic_decomposition_results}\n\\input{parser_guard_results}\n') if '\\input{parser_guard_results}' not in t else t
   t=t.replace('\\input{analytic_decomposition_appendix}\n','\\input{analytic_decomposition_appendix}\n\\input{parser_guard_appendix}\n') if '\\input{parser_guard_appendix}' not in t else t
  elif '\\input{notes_parser_guard_results}' not in t:t=t.replace('\\input{notes_analytic_decomposition_appendix}\n','\\input{notes_analytic_decomposition_appendix}\n\\input{notes_parser_guard_results}\n\\input{notes_parser_guard_appendix}\n')
  q.write_text(t)
 for source,target in [('parser_guard_results.tex','notes_parser_guard_results.tex'),('parser_guard_appendix.tex','notes_parser_guard_appendix.tex')]:
  t=(REPORT/source).read_text()
  for a in ['sec:parser-guard','app:parser-guard','tab:parser-guard','fig:parser-guard','app:analytic-inputs']:t=t.replace(a,a.replace(':',':notes-'))
  (REPORT/target).write_text(t)
 q=REPORT/'paper_abstract.tex';t=q.read_text().replace('The new 41-request test','An initial 41-request test')
 addition=f"Two symbolic requests were slower, so the final application uses native reduction when the new recurrence would require symbolic setup. A separate nine-request test verifies this rule and measures {sy['reduction_percent']:.1f}\\% less time on four symbolic requests relative to the initial analytic variant. "
 if 'Two symbolic requests were slower' not in t:t=t.replace('The models remain unchanged,',addition+'The models remain unchanged,')
 q.write_text(t)
 q=REPORT/'paper_conclusion.tex';t=q.read_text().replace('The new comparison completes','The initial analytic-enabled comparison completes')
 if 'The final input rule avoids' not in t:t+=f"\nThe final input rule avoids the more expensive symbolic-recurrence path exposed by two initial regressions. It completes all nine follow-up requests and uses {sy['reduction_percent']:.1f}\\% less time on their four symbolic inputs than the initial analytic variant. This separate result supports choosing exact and native methods by measured total cost, while preserving the earlier ML comparison and its limits.\n"
 q.write_text(t)
 guide=(HERE/'README.md').read_text().replace('s02_runtime.py --case','s10_runtime.py --case').replace('s02_runtime.py is the application entry point.','s02_runtime.py preserves the initial analytic-enabled application.').replace('A singular required matrix, active numerator, cut propagator, or missing master index returns the request to Kira.','A singular required matrix, active numerator, or missing master index returns the request to the existing application. Its interface rejects cut propagators and symbolic indices before reduction.')
 marker='## Final input rule\n'
 guide=guide.split(marker)[0]+marker+'''
The final entry point is s10_runtime.py. It uses the new recurrence for direct rational kinematics.
It keeps the older exact formulas or Kira when the input needs symbolic parsing.
s02_runtime.py preserves the initial analytic-enabled experiment.
s11_guard_test.py checks two development inputs, freezes the rule, and tests nine different requests.
s12_guard_document.py checks these results, writes the paper and notes, and rebuilds both PDFs.
The rule changes no model weights. It addresses the two symbolic regressions in the initial 41-request test.
The final nine-request test is a separate comparison. Do not add its times to the initial test.
Cut propagators and symbolic indices are outside the existing application interface.

'''
 guide+=f"The final rule passes all nine reserved requests. Its time ratio on the four symbolic requests is {sy['ratio']:.6f} against the initial analytic variant.\n"
 (HERE/'README.md').write_text(guide)
 for folder,description in {'':'Development and reserved tests of the final input rule. admission.json records the development decision. protocol.json freezes the sources and prepared basis. summary.json records every reserved request and its costs.','development':'Two symbolic target powers used to choose the rule. These timings do not enter reserved results.','development_references':'Independent exact references for the two development requests.','references':'Independent exact references for the nine reserved requests. The application never reads these coefficients.','model_test':'Three timed records per request and method. Every run includes exact coefficient checking.','coverage':'One outcome for each reserved request. Read ../summary.json for the paired times.'}.items():
  q=DEP/folder;q.mkdir(exist_ok=True);(q/'README.md').write_text('# '+('Final input rule' if not folder else folder.replace('_',' ').capitalize())+'\n\n'+description+'\n\nRead '+('../README.md' if not folder else '../../README.md')+' for the method and resource limits.\n')
 for name in ['README.md','ML_model_adaptive_reduction/README.md','report/README.md']:
  q=ROOT/name;t=q.read_text();line='The final application uses the recurrence for direct rational kinematics and keeps native Kira or earlier exact formulas for symbolic inputs.\n'
  if line not in t:q.write_text(t.replace('Read [the method guide]',line+'Read [the method guide]',1))
 q=REPORT/'paper_figures/README.md';t=q.read_text()
 if 'parser_guard.pdf' not in t:q.write_text(t+'\nparser_guard.pdf shows the separate cost reduction from avoiding symbolic setup. It uses the nine-request deployment test.\n')
 q=REPORT/'Makefile';t=q.read_text();t=re.sub(r'^report.pdf:.*$',lambda m:m.group(0)+' parser_guard_results.tex parser_guard_appendix.tex' if 'parser_guard_results.tex' not in m.group(0) else m.group(0),t,flags=re.M);q.write_text(t)
 q=REPORT/'s01_check_paper.py';t=q.read_text();marker='    result=dict(general_model_test_complete=True'
 block="""    guard=json.loads((HERE/'parser_guard_data.json').read_text())
    assert guard['complete'] and guard['requests']==len(guard['rows'])==9
    assert 'sec:parser-guard' in labels and 'app:parser-guard' in labels
    for group in guard['comparisons'].values():
        for value in group.values():
            assert abs(value['ratio']-value['learned_seconds']/value['control_seconds'])<1e-12
    p=HERE.parent/'ML_model_adaptive_reduction/analytic_decomposition/deployment/summary.json'
    if p.exists():assert json.loads(p.read_text())==guard
"""
 if "guard=json.loads((HERE/'parser_guard_data.json')" not in t:q.write_text(t.replace(marker,block+marker))
 q=REPORT/'paper_derivations.tex';t=q.read_text()
 t=t.replace(r"The latter is the defined distance $\min_{\boldsymbol a\in\mathcal T}\sum_i|\sigma_i-a_i|$.",r"The latter is the defined distance"+'\n'+r"\[\min_{\boldsymbol a\in\mathcal T}\sum_i|\sigma_i-a_i|.\]"+'\n')
 q.write_text(t)
 # Normalize only current editorial fragments, preserving the original notes.
 for q in REPORT.glob('*.tex'):
  if q.name.startswith(('analytic_decomposition_','notes_analytic_decomposition_','parser_guard_','notes_parser_guard_')) or q.name in ['paper_abstract.tex','paper_conclusion.tex']:
   q.write_text(''.join(line.rstrip()+'\n' for line in q.read_text().splitlines()).rstrip('\n')+'\n')
 subprocess.run(['make','-C',str(REPORT),'all'],check=True)
 subprocess.run([sys.executable,str(REPORT/'s01_check_paper.py')],check=True)
 v=READ(HERE/'validation.json')
 if not (HERE/'initial_validation.json').exists():write(HERE/'initial_validation.json',v)
 old=READ(HERE/'test_protocol.json');assert all(sha(HERE/n)==v for n,v in old['runtime_sources'].items())
 assert sha(PREVIOUS/'trained_model/freeze.json')==old['prior_model_sha256'];assert sha(PREVIOUS/'trained_model/expert.json')==old['prior_expert_sha256']
 receipt=dict(complete=True,coefficient_checks=checks,summary_sha256=sha(DEP/'summary.json'),protocol_sha256=sha(DEP/'protocol.json'),admission_sha256=sha(DEP/'admission.json'),sources_unchanged=True,basis_unchanged=True)
 write(DEP/'validation.json',receipt)
 v.update(final_entry_point='s10_runtime.py',guard_validation=receipt,source_sha256={q.name:sha(q) for q in HERE.glob('s*.py')},pdf_sha256={n:sha(REPORT/(n+'.pdf')) for n in ['report','notes']})
 write(HERE/'validation.json',v);(REPORT/'analytic_decomposition_validation.json').write_text(json.dumps(v,indent=2)+'\n')
 print(json.dumps(dict(complete=True,comparisons=comparisons,checks=checks,pdfs=v['pdf_sha256'])),flush=True)

if __name__=='__main__':main()
