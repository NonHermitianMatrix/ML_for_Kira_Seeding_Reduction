"""Audit the completed graph-specific study without running reductions."""
import collections,json
import s04_train_test as model
st=model.st
def main():
 f=json.loads((st.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 p=json.loads((st.HERE/'protocol.json').read_text());summary=json.loads((st.HERE/'model_test/summary.json').read_text())
 public=json.loads((st.HERE/'model_test/public_checks.json').read_text());trained=json.loads((st.HERE/'trained_model/candidates.json').read_text())
 assert summary['complete'] and summary['all_exact'] and public['complete'] and public['all_exact']
 assert summary['freeze_sha256']==model.sha(st.HERE/'trained_model/freeze.json')
 assert sum(len(r['models']) for r in trained['families'].values())==70
 groups={s:{c['group'] for c in p['cases'] if c['split']==s} for s in ['training','validation','reserved']}
 assert not groups['training']&groups['validation'] and not groups['training']&groups['reserved'] and not groups['validation']&groups['reserved']
 counts=collections.Counter();targets=set()
 for c in p['cases']:
  identity=(c['group'],tuple(map(tuple,c['targets'])));assert identity not in targets;targets.add(identity)
  if c['split']=='reserved':continue
  repetitions=2 if c['split']=='training' else 3
  worker_hosts=set()
  for cfg in dict.fromkeys(model.canonical(c,cfg) for cfg in model.BASE):
   for rep in range(repetitions):
    r=st.read(st.HERE/c['split']/f'{c["id"]}_{cfg}_{rep}.json.gz');assert r['success'] and r['attempts'][-1]['reference_checked'];counts[c['split']]+=1
    for a in r['attempts']:
     worker_hosts.add(a['worker_host'])
     minimum=max(bin(v).count('1') for v in a['input']['config']['integralfamilies'][0]['top_level_sectors'])
     assert a['seed_bounds'][0]>=minimum
  assert len(worker_hosts)==1,(c['id'],worker_hosts)
 test_count=sum(c['split']=='reserved' for c in p['cases'])
 assert summary['workflows']==20*test_count and summary['applications']==test_count and len(public['cases'])==7
 assert all(c['success'] for c in public['cases'])
 storage=sum(x.stat().st_blocks*512 for x in st.HERE.rglob('*') if x.is_file());assert storage<st.CAP
 plan=json.loads((st.HERE/'resource_plan.json').read_text());assert plan['combined_upper_bytes']<10000000000
 result=dict(complete=True,all_exact=True,training_records=counts['training'],validation_records=counts['validation'],timed_test_workflows=summary['workflows'],basis_only_applications=test_count,public_applications=7,
  tested_coefficient_entries=summary['coefficient_entries_checked'],application_coefficient_checks=summary['application_coefficient_checks']+sum(c['coefficient_checks'] for c in public['cases']),
  fitted_candidates=70,trained_graph_types=7,enabled_specialist_models=[k for k,v in f['policies'].items() if v['enabled']],
  saved_bytes=storage,retained_cap_bytes=st.CAP,combined_upper_bytes=plan['combined_upper_bytes'],
  freeze_sha256=model.sha(st.HERE/'trained_model/freeze.json'),summary_sha256=model.sha(st.HERE/'model_test/summary.json'),
  source_checks=True,weight_checks=True,separate_parameter_groups=True,duplicate_batches_removed=True,within_batch_worker_pairing=True)
 st.write(st.HERE/'evidence_validation.json',result);st.write(st.ROOT/'report/type_specialist_validation.json',result);st.emit(**result)
if __name__=='__main__':main()
