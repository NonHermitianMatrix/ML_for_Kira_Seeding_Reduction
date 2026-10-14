"""Select development candidates, train, freeze, test, and check the public route."""
import json,sys
import s05_fit as model
import s06_test as test
import s08_analyze as analyze
import s10_public_checks as public
w=model.w
def main():
 development=json.loads((w.HERE/'development_cases.json').read_text());choices=[];selected={'previous'}
 # Test each batch's best single-axis choices together before selecting candidates.
 joint=[]
 for c in development['cases']:
  costs={cfg:w.read(w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz')['complete_seconds'] for cfg in development['configurations']}
  order=min([f'o{i}p1' for i in range(2,9)],key=costs.__getitem__).split('p')[0]
  perm=min([f'o1p{i}' for i in range(2,5)],key=costs.__getitem__).split('p')[1]
  cfg=order+'p'+perm;path=w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz'
  if not path.exists():
   ref=w.reference(c);r=w.workflow(c,w.read(ref)['masters'],cfg,ref);w.save(path,r)
   w.emit(stage='joint_development',case=c['id'],configuration=cfg,seconds=r['complete_seconds'],success=r['success']);assert r['success']
  joint.append(dict(case=c['id'],configuration=cfg))
 configurations=development['configurations']+sorted({v['configuration'] for v in joint})
 w.write(w.HERE/'joint_development.json',dict(choices=joint,rule='For each batch, combine the fastest nondefault integral order and fastest nondefault propagator scheme. This is development-only.'))

 for c in development['cases']:
  costs={cfg:w.read(w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz')['complete_seconds'] for cfg in configurations if (w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz').exists()}
  best=min(costs,key=costs.__getitem__);ratio=costs[best]/costs['previous']
  if ratio<=.9:selected.add(best)
  choices.append(dict(case=c['id'],best=best,ratio_to_previous=ratio,costs=costs))
 configs=[cfg for cfg in configurations if cfg in selected]
 assert len(configs)>1,'No development improvement; retain the prior route and inspect the probes'
 decision=dict(configurations=configs,choices=choices,rule='Include the previous route and each development-case winner with at least ten percent lower complete time. Development is separate from training, validation, and reserved tests.')
 path=w.HERE/'candidate_selection.json'
 if path.exists():assert json.loads(path.read_text())==decision
 else:w.write(path,decision)
 w.emit(stage='candidate_selection',configurations=configs)
 if not (w.HERE/'trained_model/freeze.json').exists():
  sys.argv=[__file__,'--configurations',*configs];model.main()
 test.main();analyze.main();public.main()
 w.emit(stage='pipeline_complete')
if __name__=='__main__':main()
