"""Repeat mixed-worker cost batches before the final fit and reserved tests."""
import json,shutil
from pathlib import Path
import s04_train_test as model
st=model.st
def hosts(c):
 result=set()
 for p in (st.HERE/'training').glob(c['id']+'_*.json.gz'):
  result.update(a['worker_host'] for a in st.read(p)['attempts'])
 return result
def main():
 assert not list((st.HERE/'model_test').glob('*.json.gz')),'Reserved tests must remain unused'
 cases=model.prepare();archive=st.HERE/'development/paired_costs';archive.mkdir(exist_ok=True)
 plan=archive/'plan.json'
 if not plan.exists():
  mixed=[c['id'] for c in cases if c['split']=='training' and len(hosts(c))>1]
  st.write(plan,dict(cases=mixed,reason='Keep every timing comparison within a batch on one compute node before fitting.',reserved_tests_started=False))
  for name in ['candidates.json','freeze.json']:shutil.copy2(st.HERE/'trained_model'/name,archive/('initial_'+name))
  (archive/'training').mkdir(exist_ok=True)
  (archive/'README.md').write_text('# Paired training costs\n\nThe s10_pair_training.py script repeats batches with measurements from more than one worker.\nThe plan.json file lists those batches before repetition.\nThe initial_candidates.json and initial_freeze.json files preserve the earlier fit.\nThe training/ folder preserves the replaced measurements.\nThe completion.json file records the final fit and within-batch worker checks.\nNo reserved test enters this refit.\nSee the [study guide](../../README.md) for inputs, outputs, dependencies, and script order.\n')
  (archive/'training/README.md').write_text('# Replaced training measurements\n\nThese exact reductions used mixed workers within the same cost comparison.\nThe final fit uses newly paired measurements from the main training/ folder.\nSee the [pairing guide](../README.md) and [study guide](../../../README.md).\n')
  for c in cases:
   if c['id'] not in mixed:continue
   for p in (st.HERE/'training').glob(c['id']+'_*.json.gz'):p.rename(archive/'training'/p.name)
  st.write(archive/'archive_complete.json',dict(complete=True,records=len(list((archive/'training').glob('*.json.gz')))))
 else:
  assert (archive/'archive_complete.json').exists(),'Inspect an interrupted archive operation before resuming'
  mixed=json.loads(plan.read_text())['cases']
 selected=[c for c in cases if c['id'] in mixed]
 model.measure(selected,'training',2)
 worker_sets={c['id']:sorted(hosts(c)) for c in cases if c['split']=='training'}
 assert all(len(v)==1 for v in worker_sets.values()),worker_sets
 trained=model.fit(cases);f=model.freeze(cases,trained)
 f['manifest']['s10_pair_training.py']=model.sha(__file__)
 st.write(st.HERE/'trained_model/freeze.json',f)
 st.write(archive/'completion.json',dict(complete=True,repeated_cases=mixed,workers_by_batch=worker_sets,final_freeze_sha256=model.sha(st.HERE/'trained_model/freeze.json')))
 st.emit(stage='paired_fit_complete',repeated_batches=len(mixed),policies={k:dict(model=v['model']['name'],enabled=v['enabled'],control=v['validation_control'],ratio=v['validation']['ratio_to_control']) for k,v in f['policies'].items()})
if __name__=='__main__':main()
