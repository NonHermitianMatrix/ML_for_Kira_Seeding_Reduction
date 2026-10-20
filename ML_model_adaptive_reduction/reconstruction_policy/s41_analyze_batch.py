"""Summarize complete collection time without multiplying earlier speed ratios."""
from s00_reconstruction_common import *
import statistics

def main():
 p=read(HERE/'batch_protocol.json.gz')
 for worker in [0,1]:
  done=read(HERE/f'batch{worker}_complete.json')
  assert done['complete'] and done['protocol_sha256']==sha(HERE/'batch_protocol.json.gz')
 assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items())
 rows={};checks=0;failed=[];changed=[]
 inner_failures={m:0 for m in p['methods']}
 fallbacks={m:0 for m in p['methods']}
 for rep in range(p['repetitions']):
  for method in p['methods']:
   r=read(HERE/'batch_test'/f'{rep}_{method}.json.gz')
   assert r['repetition']==rep and r['method']==method
   assert r['verification_complete']
   assert set(r['results'])=={c['id'] for c in p['cases']}
   checks+=r['checks'];failed.extend((rep,method,c) for c in r['failed'])
   for item in r['results'].values():
    result=item['result']
    for attempt_result in [result,result.get('reconstruction_failed_attempt',{})]:
     inner_failures[method]+=sum(not a.get('success',False) for b in attempt_result.get('blocks',[]) for a in b['result'].get('attempts',[]))
    fallbacks[method]+=bool(result.get('reconstruction_fallback',False))
   rows[rep,method]=r
  for c in p['cases']:
   a=rows[rep,'separate']['results'][c['id']]['result']
   b=rows[rep,'batch']['results'][c['id']]['result']
   if a.get('reconstruction_action')!=b.get('reconstruction_action'):
    changed.append((rep,c['id']))
 times={m:[rows[rep,m]['total_seconds'] for rep in range(p['repetitions'])] for m in p['methods']}
 stats={m:dict(seconds=v,median_seconds=statistics.median(v),minimum_seconds=min(v),maximum_seconds=max(v),sum_seconds=sum(v)) for m,v in times.items()}
 for method in ['earlier_batch','batch']:
  stats[method]['included_parent_output_seconds']=[rows[rep,method]['total_seconds']-rows[rep,method]['process']['process_seconds'] for rep in range(p['repetitions'])]
  assert all(x>=0 for x in stats[method]['included_parent_output_seconds'])
 comparisons={}
 for name,base,new in [('batch_setup','separate','batch'),('cumulative','earlier_separate','batch'),('shared_process_algebra','earlier_batch','batch'),('earlier_batch_setup','earlier_separate','earlier_batch')]:
  ratios=[times[new][r]/times[base][r] for r in range(p['repetitions'])]
  comparisons[name]=dict(baseline=base,new=new,ratio_of_medians=stats[new]['median_seconds']/stats[base]['median_seconds'],paired_repetition_ratios=ratios)
 result=dict(complete=True,requests=len(p['cases']),repetitions=p['repetitions'],
  applications=len(p['cases'])*p['repetitions']*len(p['methods']),
  coefficient_checks=checks,failed_applications=failed,changed_reconstruction_actions=changed,
  recorded_inner_failures=inner_failures,reconstruction_fallbacks=fallbacks,
  methods=stats,comparisons=comparisons,protocol_sha256=sha(HERE/'batch_protocol.json.gz'),
  worker_hosts=sorted({r['host'] for r in rows.values()}),
  scope=p['purpose'],estimator='Median complete collection time; ranges span three full repetitions, not confidence intervals.')
 assert not failed and not changed
 write(HERE/'batch_summary.json',result)
 print(json.dumps(result),flush=True)

if __name__=='__main__':main()
