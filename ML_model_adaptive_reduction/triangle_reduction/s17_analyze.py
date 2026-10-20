"""Summarize paired complete-time measurements without selecting on test results."""
from s00_triangle_common import *
import statistics,random

def summarize(rows):
 med={a:sum(statistics.median(r['times'][a]) for r in rows) for a in ['previous','fixed','integrated']}
 rng=random.Random(32003);ratios=[];ml=[]
 for _ in range(3000):
  sample=[rng.choice(rows) for j in rows]
  sums={a:sum(statistics.median(r['times'][a]) for r in sample) for a in med}
  ratios.append(sums['integrated']/sums['previous']);ml.append(sums['integrated']/sums['fixed'])
 def interval(v):v=sorted(v);return [v[int(.025*len(v))],v[int(.975*len(v))]]
 return dict(requests=len(rows),seconds=med,ratio=med['integrated']/med['previous'],interval=interval(ratios),ml_ratio=med['integrated']/med['fixed'],ml_interval=interval(ml))

def main():
 for phase in ['test','batch']:
  assert all(read(HERE/(phase+str(w)+'_complete.json'))['complete'] for w in [0,1])
 p=read(HERE/'test_protocol.json.gz');rows=[read(HERE/'model_test'/(c['id']+'.json.gz')) for c in p['cases']]
 assert all(all(all(v) for v in r['verified'].values()) for r in rows)
 batches=[read(f) for f in sorted((HERE/'batch_test').glob('*.json.gz'))];assert len(batches)==9 and all(r['verified'] for r in batches)
 regression=[read(f) for f in (HERE/'regression').glob('*.json.gz')];assert len(regression)==len(p['regression']) and all(r['success'] for r in regression)
 groups={g:summarize([r for r in rows if r['case']['topology_group']==g]) for g in sorted({r['case']['topology_group'] for r in rows})}
 loops={str(L):summarize([r for r in rows if r['case']['topology_group']=='one_scale_triangle' and len(r['case']['definition']['loop_momenta'])==L]) for L in range(1,14)}
 bulk={a:dict(times=[r['seconds'] for r in batches if r['action']==a]) for a in ['previous','fixed','integrated']}
 for r in bulk.values():r.update(median=statistics.median(r['times']),minimum=min(r['times']),maximum=max(r['times']))
 inner_failures=sum(not a.get('success',False) for row in rows for values in row['results'].values() for result in values for block in result.get('blocks',[]) for a in block['result'].get('attempts',[]))
 inner_failures+=sum(not a.get('success',False) for row in batches for record in row['results'].values() for block in record['result'].get('blocks',[]) for a in block['result'].get('attempts',[]))
 r=dict(complete=True,inner_failed_attempts=inner_failures,guarded_structures=read(HERE/'trained_model/policy.json').get('guarded_structures',[]),protocol_sha256=sha(HERE/'test_protocol.json.gz'),model_sha256=sha(HERE/'trained_model/policy.json'),all=summarize(rows),native=summarize([r for r in rows if r['case']['test_group']=='native']),groups=groups,triangle_loops=loops,batch=bulk,batch_ratio=bulk['integrated']['median']/bulk['previous']['median'],checks=sum(r['checks'] for r in rows)+sum(r['checks'] for r in batches)+sum(r['checks'] for r in regression),separate_applications=len(rows)*9,regression_applications=len(regression),batch_applications=sum(len(r['results']) for r in batches),first_attempt_failures=sum('new_failed_attempt' in q for r in rows for v in r['results'].values() for q in v),new_model_enabled=read(HERE/'trained_model/policy.json')['enabled'])
 write(HERE/'summary.json',r);(ROOT/'report/triangle_summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['groups','triangle_loops','batch']}),flush=True)
if __name__=='__main__':main()
