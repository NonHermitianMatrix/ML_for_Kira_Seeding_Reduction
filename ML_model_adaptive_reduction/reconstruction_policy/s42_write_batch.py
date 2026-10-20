"""Document shared application setup and its separately measured effects."""
from s00_reconstruction_common import *
import re

def replace_block(text,tag,body):
 start=f'<!-- BEGIN {tag} -->';end=f'<!-- END {tag} -->'
 block=start+'\n'+body.strip()+'\n'+end
 if start in text:return re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,text,flags=re.S)
 return text.rstrip()+'\n\n'+block+'\n'

def main():
 s=read(HERE/'batch_summary.json')
 assert s['complete'] and not s['failed_applications']
 m=s['methods'];c=s['comparisons']
 b=m['batch']['median_seconds'];a=m['separate']['median_seconds']
 old=m['earlier_separate']['median_seconds'];shared=m['earlier_batch']['median_seconds']
 labels={'earlier_separate':'Earlier method, separate calls','separate':'Current method, separate calls','earlier_batch':'Earlier method, shared call','batch':'Current method, shared call'}
 rows=[]
 for key in ['earlier_separate','separate','earlier_batch','batch']:
  v=m[key];rows.append(f"{labels[key]} & {v['median_seconds']:.3f} & {v['minimum_seconds']:.3f}--{v['maximum_seconds']:.3f} \\\\")
 body=r"""\subsection{Processing a collection together}
\label{sec:batch-application}
The preceding comparison loads the application separately for each request. A further test processes the same 75 requests in one call, so numerical routines, mathematical objects, and learned policies can remain in memory. The shared call also uses one bounded output stream for the collection. Every request still receives its own reduction, and the exact formulas, model weights, algebra settings, and protected bases remain unchanged. The input supplies no reference coefficients.

We compare separate and shared calls for both the earlier and current methods. The earlier method precedes the direct vacuum formulas and reconstruction extension. Each comparison uses three complete repetitions. Two workers run on the same Intel Gold compute node, with one computation thread per application. We alternate method order and reverse the request order in the middle repetition. Time includes loading, all reductions, output, exit, reading the returned data, and cleanup; the separate-call total sums those complete call times. Independent reference comparisons remain outside both timers. These implementation checks reuse the previously verified physical inputs.

\begin{table}[htbp]
\centering\small
\caption{Complete time for the same collection of 75 requests. Each value is the median of three full-collection times. The range contains all three repetitions and is not a confidence interval. Every method completes every request in every repetition.}
\label{tab:batch-application}
\begin{tabular}{lrr}
\toprule
Method & Median (s) & Observed range (s)\\
\midrule
"""+'\n'.join(rows)+r"""
\bottomrule
\end{tabular}
\end{table}

"""+f"""For the current method, shared processing changes complete time from {a:.3f} to {b:.3f} seconds, a ratio of {c['batch_setup']['ratio_of_medians']:.3f}. The matched cumulative comparison changes from {old:.3f} seconds for the earlier separate calls to {b:.3f} seconds for the current shared call. When both methods share their setup, the earlier method takes {shared:.3f} seconds and the current method takes {b:.3f} seconds. This control preserves a comparison of the algebraic changes after both methods receive the same setup benefit. These collection-level medians differ from the sum of per-request medians in Table~\\ref{{tab:reconstruction-times}} and come from a separate timing job. We compare each method with the controls measured in the same experiment.

All {s['applications']} request executions pass {s['coefficient_checks']:,} coefficient comparisons, with zero failed applications. Shared processing preserves every recorded reconstruction choice. This change comes from reuse within a call. The models and verified physical domain remain those of the preceding comparison.
"""
 report=ROOT/'report'
 (report/'batch_application_results.tex').write_text(body)
 paper=(report/'report.tex').read_text()
 if r'\input{batch_application_results}' not in paper:
  assert r'\input{reconstruction_results}' in paper
  paper=paper.replace(r'\input{reconstruction_results}',r'\input{reconstruction_results}'+'\n'+r'\input{batch_application_results}')
 (report/'report.tex').write_text(paper)
 notes_body=body.replace(r'\subsection{Processing a collection together}',r'\section{Processing a collection together}')
 notes_body=notes_body.replace('sec:batch-application','notes-shared-application:method').replace('tab:batch-application','notes-shared-application:times').replace('tab:reconstruction-times','notes-reconstruction:times')
 # Match the actual prefixed label used in the preserved reconstruction notes.
 notes=(report/'notes.tex').read_text()
 matches=re.findall(r'\\label\{([^}]*reconstruction-times)\}',notes)
 assert len(matches)==1,matches
 notes_body=notes_body.replace('notes-reconstruction:times',matches[0])
 notes_body+=r"""

\subsection{Preparation checks}
Two earlier batch-test submissions stopped because the reference checker loaded its dependencies in an order that assumed a native request came first. The first stopped before timing; the second reached the reversed-order reference check and retained a completed forward control. We preserved the interrupted records and repeated the complete comparison after explicitly initializing the checker and checking its analytic path before timing. The reduction application, mathematical methods, model weights, and physical requests remained unchanged. The final timing table uses the complete comparison after this correction.

A subsequent timing audit found that the separate-call timer included reading the returned output and cleanup, while the initial shared-call timer stopped at process exit. We preserved that preliminary comparison, aligned both timing boundaries, and repeated all four methods. The final table uses the aligned timers. The application and mathematical outputs were unchanged.
"""
 (report/'notes_batch_application_results.tex').write_text(notes_body)
 marker='% BATCH APPLICATION UPDATE BEGIN'
 block='% BEGIN CURRENT WORKFLOW UPDATE\n'+marker+'\n'+r'\input{notes_batch_application_results}'+'\n% BATCH APPLICATION UPDATE END\n% END CURRENT WORKFLOW UPDATE\n'
 if marker not in notes:
  assert r'\bibliographystyle{unsrt}' in notes
  notes=notes.replace(r'\bibliographystyle{unsrt}',block+r'\bibliographystyle{unsrt}')
 (report/'notes.tex').write_text(notes)
 for name,paragraph in [
  ('paper_abstract.tex',f' A further shared-call comparison processes the same collection in {b:.3f} seconds, compared with {a:.3f} seconds for separate current calls.'),
  ('paper_conclusion.tex',f'Processing the same collection in one call reduces repeated setup. The current collection time changes from {a:.3f} to {b:.3f} seconds, while the equally prepared earlier method takes {shared:.3f} seconds in one call. Every request passes its independent coefficient comparison. This implementation gain is separate from the learned decisions and applies to the tested collection.')]:
  text=(report/name).read_text()
  text=re.sub(r'\n% BATCH SUMMARY BEGIN.*?% BATCH SUMMARY END\n?', '',text,flags=re.S)
  block='% BATCH SUMMARY BEGIN\n'+paragraph.strip()+'\n% BATCH SUMMARY END'
  if name=='paper_abstract.tex':
   assert 'Separate validation rejects' in text
   text=text.replace('Separate validation rejects','\n'+block+'\nSeparate validation rejects',1)
  else:
   assert '\n\nThe new cost model' in text
   text=text.replace('\n\nThe new cost model','\n\n'+block+'\n\nThe new cost model',1)
  (report/name).write_text(''.join(line.rstrip()+'\n' for line in text.splitlines()).rstrip('\n')+'\n')
 for name in ['paper_abstract.tex','paper_conclusion.tex','reconstruction_results.tex']:
  f=report/name;text=f.read_text()
  for phrase in ['the two latest extensions','the last two extensions','two extensions']:
   text=text.replace(phrase,'the direct vacuum and reconstruction changes')
  f.write_text(text)
 make=(report/'Makefile').read_text()
 if 'report.pdf: batch_application_results.tex' not in make:
  make=make.replace('report.pdf: ','report.pdf: batch_application_results.tex ',1)
 (report/'Makefile').write_text(make)
 guide=f"""Use `s15_deploy.py` for one request. Use `s37_batch.py` for a bounded collection of 1 to 128 requests. The shared call retains loaded routines and policies. It receives no reference answers and computes each requested reduction.

From the project root, run:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/reconstruction_policy/s37_batch.py --cases /path/to/cases.json --output /path/to/new-results.jsonl
```

The input is a JSON list of request objects in the existing application format. Each request needs a distinct `id`. The input must be smaller than 2 MiB. The output path must not exist. Each output line contains `case`, `result`, and the internal request time `seconds`. Read `result.success` for each request. A caught request exception produces a failed result and the next request runs. Native attempt limits remain active. An outer process failure can leave a partial file; check that every input ID has a result. The output is limited to 8 MiB and each line to 2 MiB. Use compute nodes and the same one-thread settings as the test script.

The optional `--method` selects `integrated`, `fixed`, `previous`, or `before_formulas`. The default is `integrated`. These choices match the single-request application. A collection call does not create a new learned model.

The frozen comparison uses the same 75 verified requests, four methods, and three repetitions. It reverses request order in the middle repetition and checks every coefficient against the saved independent references. It is an implementation regression test, not a new held-out physics sample. Current separate calls take {a:.6f} s at the median; the shared call takes {b:.6f} s. The earlier shared call takes {shared:.6f} s. All {s['applications']} executions pass {s['coefficient_checks']} coefficient checks. No reconstruction choices change.

`s38_prepare_batch.py` freezes the inputs, code, weights, binary, and references. `s39_batch_test.py` times and verifies the applications. `s40_batch_test.sh` submits two bounded workers. `s41_analyze_batch.py` computes the summaries. `s42_write_batch.py` updates the documents and guides. `s43_validate_batch.py` verifies the final files. Read `batch_protocol.json.gz`, `batch_summary.json`, and `batch_resource_plan.json` for the protocol, complete results, and storage bounds. The `batch_test` folder contains all timed outputs. Training and all earlier experiments remain unchanged."""
 (HERE/'README.md').write_text(replace_block((HERE/'README.md').read_text(),'SHARED APPLICATION SETUP',guide))
 (HERE/'batch_test/README.md').write_text("""# Shared application test

This folder stores the full comparison of separate calls and one shared call.
Each compressed JSON file identifies the method and repetition. It stores the total elapsed time, every request result, per-request coefficient checks, failures, request order, and worker host.
The protocol and summary are in the parent folder. There are four methods and three repetitions. The earlier methods precede the direct vacuum and reconstruction changes. The current methods use the frozen integrated application.
The same 75 verified requests are used in every method. This checks implementation changes. It does not provide new evidence for unseen integral structures.
Read the total collection timer for speed comparisons. Internal request times in a shared call exclude its first process load. Do not sum those internal times and describe that sum as complete time.
""")
 (HERE/'requests/README.md').write_text("""# Temporary application requests

The comparison writes bounded request and result files here. Each worker uses its own file names and removes its files after reading the results.
Completed scientific records are stored in the test folders. This folder must contain no request or result JSON files when validation and publication run.
""")
 log_guide=HERE/'logs/README.md'
 log_guide.write_text(replace_block(log_guide.read_text() if log_guide.exists() else '# Job logs\n','SHARED APPLICATION TEST','`batch_test.log` records progress of the final shared-call comparison. The complete timed outputs are in `batch_test`. Earlier preparation and timing-boundary attempts are preserved in their named folders with separate READMEs.'))
 for name in ['README.md','ML_model_adaptive_reduction/README.md']:
  f=ROOT/name
  text=f"""The current single-request application remains `ML_model_adaptive_reduction/reconstruction_policy/s15_deploy.py`. Collections can use `s37_batch.py` in the same folder. It keeps routines and policies loaded across requests. The verified 75-request collection takes {b:.3f} s in one call, compared with {a:.3f} s for separate current calls and {shared:.3f} s for an equally prepared earlier shared call. These are medians of three full-collection times. All 900 request executions pass their coefficient checks. See that folder's README and `batch_summary.json` for the scope, commands, and complete results."""
  f.write_text(replace_block(f.read_text(),'SHARED APPLICATION SETUP',text))
 (report/'batch_application_summary.json').write_text(json.dumps(s,indent=2)+'\n')
 print('Shared-call results and guides written',flush=True)

if __name__=='__main__':main()
