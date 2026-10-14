"""Audit exact records, split separation, resource bounds, and folder guides."""
import collections,json
import s05_fit as model
w=model.w
def main():
 f=json.loads((w.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 p=json.loads((w.HERE/'protocol.json').read_text());s=json.loads((w.HERE/'model_test/summary.json').read_text());public=json.loads((w.HERE/'model_test/public_checks.json').read_text())
 if (w.HERE/'test_writer.json').exists():
  writer=json.loads((w.HERE/'test_writer.json').read_text())
  assert writer['source_sha256']==model.sha(w.HERE/'s14_test.py') and writer['freeze_sha256']==model.sha(w.HERE/'trained_model/freeze.json')
 assert s['complete'] and s['all_exact'] and public['complete'] and public['all_exact']
 assert s['freeze_sha256']==model.sha(w.HERE/'trained_model/freeze.json')
 worker=json.loads((w.HERE/'model_test/worker_checks.json').read_text())
 assert worker['allocated_cores']==2
 assert worker['complete'] and worker['all_exact'] and worker['applications']==7 and worker['requests_in_one_worker']
 assert worker['source_sha256']==model.sha(w.HERE/'s15_worker.py') and worker['checker_sha256']==model.sha(w.HERE/'s16_worker_checks.py')
 assert worker['freeze_sha256']==model.sha(w.HERE/'trained_model/freeze.json')
 groups={split:{c['group'] for c in p['cases'] if c['split']==split} for split in ['training','validation','reserved']}
 assert all(not groups[a]&groups[b] for a,b in [('training','validation'),('training','reserved'),('validation','reserved')])
 retained_choices={'previous'}
 for policy in f['policies'].values():
  control=policy['validation_control'];retained_choices.add(control)
  if policy['enabled']:
   assert policy['model']['type']=='tree'
   for node in policy['model']['nodes']:
    if node['feature']>=0:continue
    scores=node['value'];j=min(range(len(scores)),key=scores.__getitem__)
    retained_choices.add(f['configurations'][j] if scores[j]<scores[f['configurations'].index(control)]-policy['gate'] else control)
 assert retained_choices<={'previous','threads2'}
 counts=collections.Counter();seen=set()
 for c in p['cases']:
  key=(c['group'],tuple(map(tuple,c['targets'])));assert key not in seen;seen.add(key)
  if c['split']=='reserved':continue
  hosts=set()
  for cfg in p['configurations']:
   for rep in range(p[c['split']+'_repetitions']):
    r=w.read(w.HERE/c['split']/f'{c["id"]}_{cfg}_{rep}.json.gz');assert r['success'] and r['reference_checked'] and r['basis_admitted']
    counts[c['split']]+=1
    for a in r['attempts']:
     hosts.add(a['worker_host']);minimum=max(bin(x).count('1') for x in a['input']['config']['integralfamilies'][0]['top_level_sectors']);assert a['seed_bounds'][0]>=minimum
  assert len(hosts)==1,(c['id'],hosts)
 applied=0
 for folder in ['development','training','validation','model_test']:
  for path in (w.HERE/folder).glob('*.json.gz'):
   r=w.read(path);cfg=r.get('configuration','previous')
   if cfg not in ['threads2','threads4']:continue
   threads=int(cfg[-1])
   for attempt in r['attempts']:
    if attempt.get('driver_sha256')!=model.sha(w.HERE/'s02_native_runner.py'):continue
    assert attempt['worker_threads']==threads
    applied+=1
 for c in p['cases']:
  if c['split']!='reserved':continue
  selected,_=model.select(f,c)
  for rep in range(5):
   r=w.read(w.HERE/'model_test'/f"{c['id']}_selected_{rep}.json.gz")
   assert r['configuration']==selected
 assert counts['training']==216 and counts['validation']==162
 assert applied>0
 assert s['workflows']==900 and s['applications']==36 and len(public['cases'])==7
 assert all(c['success'] for c in public['cases'])
 descriptions={
  'development':'Development records compare one, two, and four Kira workers on profile 91. The records include exact coefficients, attempt costs, failures, and resource peaks. All three predefined choices enter training. Run `../s04_probe.py` to produce them. Read them with `../s01_study.py`.',
  'references':'These are independent expanded-seed reductions for each input batch. They supply a prescribed master basis and final check coefficients. The policy does not receive the coefficients. The `reference` function in `../s01_study.py` makes each record.',
  'training':'These records use profiles 92 and 93. Each candidate has two measurements per batch. The complete-time ratios form training labels. Run `../s09_pipeline.py --train-only` to make them.',
  'validation':'These records use profile 94. Each candidate has three measurements per batch. Validation selects the control, predictor, and decision margin before reserved tests. Run `../s05_fit.py` to make them.',
  'trained_model':'The `candidates.json` file stores all seventy fitted predictors. The `freeze.json` file stores the selected policies, controls, domain guards, and source checks. Run `../s05_fit.py` to fit and freeze. Run `../s07_reduce.py` to apply the frozen route. Do not refit after reserved tests.',
  'model_test':'These records use profiles 95 and 96. Five repetitions compare native, previous, always-four-worker, fixed, and selected routes. Application records supply no target coefficients to the reduction. Public inputs include the case and master basis. Seven further checks use one persistent worker. `../s15_worker.py` serves requests and `../s16_worker_checks.py` checks it. The summary and public checks report exact comparisons. Run `../s06_test.py`, `../s08_analyze.py`, and `../s10_public_checks.py` in that order.',
  'logs':'These text files contain scheduler output and progress messages. Use `../s03_job.sh` to submit jobs. Full scientific records are in the other study folders. Do not use log timing as a replacement for the saved complete-time records.'}
 for name,text in descriptions.items():
  q=w.HERE/name;q.mkdir(exist_ok=True);(q/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+text+'\n\nSee the [study guide](../README.md) for inputs, commands, dependencies, and limits. Data stay on Hoffman and GitHub.\n')
 storage=sum(q.stat().st_blocks*512 for q in w.HERE.rglob('*') if q.is_file());assert storage<w.CAP
 plan=json.loads((w.HERE/'resource_plan.json').read_text());assert plan['combined_upper_bytes']<10000000000
 out=dict(complete=True,all_exact=True,training_records=counts['training'],validation_records=counts['validation'],timed_test_workflows=900,basis_only_applications=36,public_applications=7,persistent_worker_applications=7,
  tested_coefficient_entries=s['coefficient_entries_checked'],application_coefficient_checks=s['application_coefficient_checks']+sum(c['coefficient_checks'] for c in public['cases'])+sum(c['coefficient_checks'] for c in worker['cases']),
  fitted_candidates=70,trained_graph_types=7,enabled_models=[k for k,v in f['policies'].items() if v['enabled']],
  source_checks=True,retained_max_workers=2,persistent_worker_allocated_cores=2,worker_settings_checked=applied,separate_parameter_groups=True,duplicate_batches_removed=True,within_batch_worker_pairing=True,
  saved_bytes=storage,retained_cap_bytes=w.CAP,combined_upper_bytes=plan['combined_upper_bytes'],freeze_sha256=model.sha(w.HERE/'trained_model/freeze.json'),summary_sha256=model.sha(w.HERE/'model_test/summary.json'))
 w.write(w.HERE/'evidence_validation.json',out);w.write(w.ROOT/'report/thread_policy_validation.json',out);w.emit(**out)
if __name__=='__main__':main()
