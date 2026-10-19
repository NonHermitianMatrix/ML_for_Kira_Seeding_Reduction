"""Report the complete-cost model gate and validate its separate reserved test."""
from s00_fast_common import *
DEP=HERE/'deployment';REPORT=ROOT/'report'

def main():
 import numpy as np
 assert read(DEP/'complete.json')['complete'];p=read(DEP/'protocol.json');ad=read(DEP/'admission.json')
 assert sha(DEP/'admission.json')==p['admission_sha256'];assert sha(HERE/'trained_model/recurrence.json')==p['model_sha256']
 assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 assert all(sha(HERE/n)==v for n,v in ad['source_sha256'].items())
 old=legacy();h=old.h;rows=[];checks=0;validation_checks=0
 for q in (DEP/'validation').glob('*.json.gz'):
  r=read(q);ref=read(DEP/'validation_references'/(r['case']+'.json.gz'));ok,n=h.compare(r,ref);assert ok and r['independently_verified'];validation_checks+=n
 for c in p['cases']:
  ref=read(DEP/'references'/(c['id']+'.json.gz'));row=read(DEP/'coverage'/(c['id']+'.json'));row['times']={};row['verified']={}
  for m in p['methods']:
   rs=[read(q) for q in sorted((DEP/'model_test').glob(c['id']+'_'+m+'_r*.json.gz'))];assert rs
   for r in rs:
    ok,n=h.compare(r,ref);assert ok==r['independently_verified'];assert not r['success'] or ok;checks+=n
   row['times'][m]=[r['complete_process_and_check_seconds'] for r in rs];row['verified'][m]=len(rs)==3 and all(r['independently_verified'] for r in rs)
  rows.append(row)
 def compare(m,rr):
  rr=[r for r in rr if r['verified']['final'] and r['verified'][m]]
  if not rr:return dict(cases=0)
  x=np.array([r['times']['final'] for r in rr]);y=np.array([r['times'][m] for r in rr]);a=float(np.median(x,axis=1).sum());b=float(np.median(y,axis=1).sum());ix=np.random.RandomState(2963).randint(0,3,(2000,len(rr),3));ii=np.arange(len(rr))[None,:,None];rat=np.median(x[ii,ix],axis=2).sum(1)/np.median(y[ii,ix],axis=2).sum(1)
  return dict(cases=len(rr),final_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,repeat_interval=list(map(float,np.quantile(rat,[.025,.975]))))
 groups={'all':rows,**{k:[r for r in rows if r['scope']==k] for k in sorted({r['scope'] for r in rows})}}
 comp={k:{m:compare(m,rr) for m in ['previous','candidate','fixed_recurrence']} for k,rr in groups.items()}
 s=dict(complete=True,requests=len(rows),rows=rows,comparisons=comp,admission=ad,coefficient_checks=checks,validation_coefficient_checks=validation_checks,completed={m:sum(r['verified'][m] for r in rows) for m in p['methods']},reference_seconds=sum(r['reference_seconds'] for r in rows),protocol_sha256=sha(DEP/'protocol.json'))
 write(DEP/'summary.json',s);(REPORT/'fast_deployment_data.json').write_text(json.dumps(s,indent=2)+'\n')
 enabled=ad['enabled'];decision='enables the recurrence model' if enabled else 'uses the fixed recurrence strategy'
 text=r'''\section{Selecting the final application by complete time}
\label{sec:fast-deployment}
We selected the new tree using recurrence times. A lower kernel cost alone does not establish a lower application cost, so deployment requires a further check on the original validation split. We run the same 56 validation requests in fresh processes, with prediction, exact reduction, and coefficient comparison inside each timer. The two choices use the same fast implementation and retain the same native seed model; they differ only in the recurrence strategy. Three paired repetitions provide each request's median time. We enable the new recurrence model only when its summed median time is at least two percent lower and its paired repetition interval stays below one. The 65 reserved requests do not enter this decision.

'''
 lo,hi=ad['repeat_interval'];text+=f"The complete validation total is {ad['candidate_seconds']:.3f} seconds with the recurrence model and {ad['fixed_recurrence_seconds']:.3f} seconds with the fixed strategy. The ratio is {ad['ratio']:.3f}, with repetition interval $[{lo:.3f},{hi:.3f}]$. The final application therefore {decision}. "
 text+=('The result supports the added recurrence decision under this validation rule. ' if enabled else 'The kernel saving does not meet the complete-time deployment rule, so the trained tree remains a recorded candidate. ')
 text+='The retained sparse-seed model remains active in its validated coupled domain. This decision leaves all exact formulas and coefficient checks unchanged.\n\n'
 text+=r'''A separate twelve-request test follows the frozen decision. It includes six rational polygons, two distinct-triangle products at two and thirteen loops, a nonplanar box, a symbolic bubble, and two thirteen-loop analytic families. Appendix~\ref{app:fast-deployment} specifies their fresh inputs. Table~\ref{tab:fast-deployment} keeps this test separate from the preceding 65-request experiment.
\begin{table}[!htbp]\centering\small
\caption{Separate reserved test of the final complete-cost rule. Times are sums of medians in seconds. ``Candidate'' always enables the recurrence model. ``Fixed recurrence'' retains the native seed model but uses the fixed recurrence strategy.}
\label{tab:fast-deployment}
\begin{tabularx}{\linewidth}{@{}Yrrrrr@{}}\toprule
Collection & $N$ & Final & Candidate & Fixed recurrence & Previous\\\midrule
'''
 for key,name in [('recurrence','Scalar recurrence'),('products','Distinct products'),('learned_native','Nonplanar box'),('symbolic_native','Symbolic bubble'),('finite_formula','Thirteen-loop formulas'),('all','All requests')]:
  rr=groups.get(key,[]);rr=[r for r in rr if all(r['verified'].values())]
  if not rr:continue
  text+=name+f" & {len(rr)}"+''.join(f" & {sum(statistics.median(r['times'][m]) for r in rr):.3f}" for m in ['final','candidate','fixed_recurrence','previous'])+r' \\'+'\n'
 text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
 for m,label in [('previous','the preceding deployed application'),('candidate','the always-enabled recurrence candidate'),('fixed_recurrence','the fixed recurrence strategy')]:
  v=comp['all'][m];lo,hi=v['repeat_interval'];direction='less' if v['ratio']<1 else 'more'
  text+=f"Against {label}, the final method uses {abs(100*(1-v['ratio'])):.1f}\\% {direction} time, with ratio {v['ratio']:.3f} and repetition interval $[{lo:.3f},{hi:.3f}]$. "
  if lo<=1<=hi:text+='This interval includes equal times. '
 text+=f"\n\nThe final method completes {s['completed']['final']} of twelve requests in every repetition. All verified outputs agree with the independent references, with {checks:,} coefficient comparisons in this test and {validation_checks:,} in the full-cost validation. Reference preparation for the twelve requests takes {s['reference_seconds']:.3f} seconds and remains separate. "
 text+='The broad audit in the preceding section belongs to the initial candidate. The final test checks the deployment rule on fresh inputs, while the earlier audit retains its original outcomes and native limits.\n'
 (REPORT/'fast_deployment_results.tex').write_text(text)
 appendix=r'''\section{Inputs for the complete-cost deployment test}
\label{app:fast-deployment}
Use the polygon definitions of Appendix~\ref{app:analytic-inputs} with profile $2917$, $n=3,4,5$, and powers $(3,2,1,\ldots,1)$ or $(1,\ldots,1,2,3)$. The distinct-triangle products contain two or thirteen blocks at profile $2927$, with the mass offsets and target $(2,1,1)$ defined in Appendix~\ref{app:fast-inputs}. The nonplanar box has profile $2939$ and auxiliary powers $(-3,0)$. The symbolic bubble has profile $2941$ and the first extra-power collection of Appendix~\ref{app:analytic-inputs}. The one-mass vacuum and massless propagator families have thirteen loops and profile $2953$.

The full-cost admission uses only the original profile-$2621$ validation inputs. Its cost includes a fresh process, the learned or fixed choice, exact recurrence, output, and comparison with the earlier exact scalar recurrence. The additional reserved references use the same independent native and analytic checks as the main test. We fix all source choices and the admission result before these twelve requests run. The final rule changes no fitted weights. It selects whether the recurrence model earns its cost in the complete application.
'''
 (REPORT/'fast_deployment_appendix.tex').write_text(appendix)
 q=REPORT/'report.tex';z=q.read_text()
 if '\\input{fast_deployment_results}' not in z:z=z.replace('\\input{fast_decomposition_results}','\\input{fast_decomposition_results}\n\\input{fast_deployment_results}')
 if '\\input{fast_deployment_appendix}' not in z:z=z.replace('\\input{fast_decomposition_appendix}','\\input{fast_decomposition_appendix}\n\\input{fast_deployment_appendix}')
 q.write_text(z)
 q=REPORT/'fast_decomposition_results.tex';z=q.read_text().replace('The final comparison tests','The initial fast-implementation comparison tests');q.write_text(z)
 q=REPORT/'fast_decomposition_method.tex';z=q.read_text()
 if 'Complete application validation' not in z:q.write_text(z+'\nComplete application validation also governs deployment of the recurrence model. Section~\\ref{sec:fast-deployment} measures that decision on the original validation split, freezes its outcome, and tests twelve fresh requests.\n')
 for part in ['method','results']:
  z=(REPORT/f'fast_decomposition_{part}.tex').read_text()
  for prefix in ['sec:fast','app:fast','eq:fast','tab:fast','fig:fast','app:analytic','eq:analytic']:z=z.replace(prefix,prefix.replace(':',':notes-'))
  (REPORT/f'notes_fast_decomposition_{part}.tex').write_text(z)
 q=REPORT/'paper_abstract.tex';z=q.read_text().replace('A reserved test contains 65 requests','An initial reserved test contains 65 requests').replace('The combined method completes','The initial candidate completes')
 v=comp['all']['previous'];admission_sentence=('Full-application validation enables the recurrence model. ' if enabled else 'Full-application validation finds no resolved gain from the recurrence model, so the final workflow uses the fixed recurrence strategy and retains learned seed selection. ');z=z.replace('Timings include loading,',admission_sentence+f"A separate twelve-request test gives {v['speedup']:.2f} times the speed of the preceding application, with all {s['completed']['final']} final-method requests verified. Timings include loading,");q.write_text(z)
 q=REPORT/'paper_conclusion.tex';z=q.read_text().replace('The full comparison verifies','The initial fast-implementation comparison verifies')
 z+=f"\nThe final deployment rule {decision}, based on the original validation split. Its separate twelve-request comparison takes {v['final_seconds']:.3f} seconds against {v['control_seconds']:.3f} seconds for the preceding application, a factor of {v['speedup']:.2f}. The retained sparse-seed model remains available. This rule selects methods by complete cost while preserving the initial candidate's measurements and the broader audit limits.\n";q.write_text(z)
 for name in ['results','appendix']:
  z=(REPORT/f'fast_deployment_{name}.tex').read_text()
  for prefix in ['sec:fast','app:fast','tab:fast','app:analytic']:z=z.replace(prefix,prefix.replace(':',':notes-'))
  (REPORT/f'notes_fast_deployment_{name}.tex').write_text(z)
 q=REPORT/'notes.tex';z=q.read_text();add='\\input{notes_fast_deployment_results}\n\\input{notes_fast_deployment_appendix}\n'
 if add not in z:z=z.replace('\\bibliographystyle','% BEGIN CURRENT WORKFLOW UPDATE\n'+add+'% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle',1)
 q.write_text(z)
 q=REPORT/'Makefile';z=q.read_text();z=re.sub(r'^report.pdf:.*$',lambda m:m.group(0)+' fast_deployment_results.tex fast_deployment_appendix.tex' if 'fast_deployment_results.tex' not in m.group(0) else m.group(0),z,flags=re.M);q.write_text(z)
 q=HERE/'README.md';z=q.read_text().replace('s03_fast_runtime.py --case','s12_deploy.py --case').replace('--method learned','--method final').replace('s03_fast_runtime.py combines these stages','s03_fast_runtime.py preserves the initial candidate and combines these stages')
 heading='## Final complete-cost deployment\n';z=z.split(heading)[0]+heading+'\nThe final entry point is s12_deploy.py.\nUse --method final for the deployed workflow.\nUse --method candidate to enable the recurrence tree, or --method fixed_recurrence to disable that tree only.\nThe native seed model remains active in both alternatives.\ns13_application_gate.py tests full application cost on the original 56 validation requests.\ns14_deployment_test.py freezes the decision and tests twelve fresh requests.\ns15_deployment_document.py checks these results and writes the final report section.\n'
 z=z.replace('Use `--method fixed` to disable request-dependent learned decisions in this application.', 'For the initial candidate only, use s03_fast_runtime.py with --method fixed to disable both learned decisions. The final entry point uses the modes listed below.')
 z+=f"The recurrence tree is {'enabled' if enabled else 'disabled'} by full-cost validation. Its validation time ratio is {ad['ratio']:.6f}.\nThe separate final test has a ratio of {v['ratio']:.6f} to the preceding application.\n"
 z+='The initial 65-request experiment and 110-request audit remain unchanged.\nRead deployment/summary.json for the separate final test.\n'
 z+='After s06_train.py, run s13_application_gate.py on the validation split. Run s14_deployment_test.py after admission.json exists and both audit workers finish. Run s11_validate.py last.\n'
 z+='s16_resume_audit.py resumes the unchanged audit after an older result omitted an optional status label. It reuses all recorded times.\nThe independent validation reference limit increased from ten to 120 seconds after one slow Fraction-arithmetic reference. Completed application times remain unchanged.\n'
 if not enabled:z=z.replace('A new tree selects a recurrence strategy for supported one-loop scalar blocks.', 'A trained tree can select a recurrence strategy. Complete-cost validation currently keeps the fixed recurrence strategy.')
 q.write_text(z)
 descriptions={'':'Full-cost validation, admission.json, protocol.json, and the separate final application test.','validation':'Full-process validation times for the original 56 validation requests. These data select the admission rule, not the fitted weights.','validation_references':'Exact recurrence references for validation. These coefficients never enter application decisions.','references':'Independent references for the twelve final reserved requests.','model_test':'Three full-process times per verified final request and method.','coverage':'One record per final reserved request, including incomplete methods.'}
 for name,description in descriptions.items():
  q=DEP/name;q.mkdir(exist_ok=True);(q/'README.md').write_text('# '+('Complete-cost deployment' if not name else name.replace('_',' ').capitalize())+'\n\n'+description+'\n\nRead '+('../README.md' if not name else '../../README.md')+' for the code and controls.\n')
 for name in ['README.md','ML_model_adaptive_reduction/README.md','report/README.md']:
  q=ROOT/name;z=q.read_text().replace('The final entry point is s03_fast_runtime.py in fast_decomposition.','The final entry point is s12_deploy.py in fast_decomposition.');q.write_text(z)
 for q in list(REPORT.glob('*fast_deployment*.tex'))+[REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex']:
  q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 receipt=dict(complete=True,summary_sha256=sha(DEP/'summary.json'),protocol_sha256=sha(DEP/'protocol.json'),admission_sha256=sha(DEP/'admission.json'),coefficient_checks=checks,validation_coefficient_checks=validation_checks)
 write(DEP/'validation.json',receipt);print(json.dumps(dict(complete=True,enabled=enabled,all=comp['all'],checks=checks,validation_checks=validation_checks)),flush=True);return receipt
if __name__=='__main__':main()
