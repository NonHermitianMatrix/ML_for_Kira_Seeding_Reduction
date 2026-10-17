"""Validate all new records and create human-readable folder guides."""
import hashlib,json,subprocess
from s00_protocol import HERE,ROOT,read,write,sha

def main():
 protocol=read(HERE/'protocol.json');summary=read(HERE/'summary.json')
 assert summary['complete'] and summary['analytic_all_exact']
 assert len(summary['coverage'])==len(protocol['cases'])==84
 assert len(summary['analytic_rows'])==24
 assert {r['loops'] for r in summary['analytic_rows']}==set(range(1,13))
 for c in summary['native_rows']:
  for m in protocol['methods']:
   for i in range(3):
    r=read(HERE/'model_test'/f'{c["id"]}_{m}_{i}.json.gz');assert r['success'] and r['reference_checked']
 extra=read(HERE/'additional_tests_freeze.json')
 assert extra['protocol_sha256']==sha(HERE/'protocol.json')
 for n,h in extra['sources'].items():assert sha(HERE/n)==h,n
 for n,h in protocol['models'].items():assert sha(ROOT/n)==h,n
 for n,h in protocol['sources'].items():assert sha(ROOT/n)==h,n
 # Verify every deployed model file against the publication that preceded this test.
 folders=['ML_model_equation_selection/bound_refinement/trained_model','ML_model_seed_selection/cost_geometry/trained_model','ML_model_seed_selection/joint_policy/trained_model','ML_model_adaptive_reduction/batch_policy/trained_model','ML_model_adaptive_reduction/learned_seed_bounds/trained_model','ML_model_adaptive_reduction/batch_policy/fixed_inputs.json']
 entries=subprocess.check_output(['git','ls-tree','-r','-z','1163e1bee6430d8f23115e8f69ca539bdbb6babb','--',*folders],cwd=ROOT).split(b'\0');published={}
 for item in entries:
  if not item:continue
  meta,name=item.split(b'\t',1);mode,kind,oid=meta.split()
  if kind!=b'blob':continue
  raw=(ROOT/name.decode()).read_bytes();actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  assert actual==oid.decode(),name.decode();published[name.decode()]=actual
 write(HERE/'published_model_audit.json',dict(passed=True,files=published,comparison='Published model contents before this test'))
 details={
 'references':'Independent native Kira reductions and checks. Each file records exact coefficients, discovered masters, resource outcomes, and elapsed time. Failed references remain here. s02_study.py creates these files.',
 'coverage':'One outcome per requested native family. Unsupported index counts have no timed reduction. s02_study.py writes these records.',
 'model_test':'Repeated native, previous, and selected application results. Each file contains exact-check status and complete process time. s02_study.py creates these files. Failed methods stop further repetitions.',
 'analytic':'Physical inputs, independently constructed recurrence references, and measured applications through twelve loops. s04_analytic.py creates these files. These are exact scalar banana tests, not general native high-loop reductions.',
 'scale':'Independent references at each scale and complete sequence results. s05_scale.py creates these files. Reuse can act only on the graph signatures supported before this test.',
 'requests':'Temporary inputs for one measured process. s02_study.py removes each temporary input after recording the result. This folder should contain only this guide when all jobs finish.',
 'logs':'Cluster output for these tests. Logs are bounded operational records and stay outside Git. The summary and coverage files retain scientific outcomes.'}
 for name,text in details.items():
  d=HERE/name;d.mkdir(exist_ok=True);(d/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+text+'\n\nRead the parent README for inputs, limits, and execution order.\n')
 assert not list((HERE/'requests').glob('*.json'))
 for d in HERE.rglob('*'):
  if d.is_dir() and d.name!='__pycache__' and not (d/'README.md').exists():
   (d/'README.md').write_text('# Supporting files\n\nRead the parent README for the producing script, inputs, outputs, and limits.\n')
 p=HERE/'README.md';text=p.read_text().split('\nCompleted scripts:')[0];text+='\nCompleted scripts: `s04_analytic.py` checks the scalar recurrence. `s05_scale.py` tests scale sequences. `s06_analyze.py` makes summaries and the figure. `s07_document.py` writes the new report sections. `s08_finish.py` checks the results and writes folder guides. `s09_complete.py` runs analysis, builds both PDFs, and checks the documents after the measurements finish.\n\n'
 text+='Native coverage: '+json.dumps(summary['coverage_counts'],sort_keys=True)+'. The matched nontrivial set has '+str(summary['native']['cases'])+' cases. All 24 analytic batches pass. See `summary.json` for measured times and the full failure list.\n';p.write_text(text)
 validation=dict(complete=True,models_unchanged=True,all_matched_results_exact=True,analytic_batches=24,native_requests=84,summary_sha256=sha(HERE/'summary.json'),source_sha256={p.name:sha(p) for p in HERE.glob('s0*')},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},study_allocated_bytes=int(subprocess.check_output(['du','-sk',str(HERE)]).split()[0])*1024)
 assert validation['study_allocated_bytes']<12*1024**2
 write(HERE/'validation.json',validation);write(ROOT/'report/extended_coverage_validation.json',validation)
 print(json.dumps(validation),flush=True)
if __name__=='__main__':main()
