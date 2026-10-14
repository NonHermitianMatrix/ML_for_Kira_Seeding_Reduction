"""Select development candidates, train, freeze, test, and check the public route."""
import json,sys
import s04_train as model
import s05_test as test
import s06_analyze as analyze
import s08_public_checks as public
w=model.w
def main():
 development=json.loads((w.HERE/'development_cases.json').read_text());choices=[];selected={'previous'}
 for c in development['cases']:
  costs={cfg:w.read(w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz')['complete_seconds'] for cfg in development['configurations']}
  best=min(costs,key=costs.__getitem__);ratio=costs[best]/costs['previous']
  if ratio<=.9:selected.add(best)
  choices.append(dict(case=c['id'],best=best,ratio_to_previous=ratio,costs=costs))
 configs=[cfg for cfg in development['configurations'] if cfg in selected]
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
