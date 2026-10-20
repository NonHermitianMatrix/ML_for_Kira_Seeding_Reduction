"""Report paired completed reductions, failures, and the separate learned effect."""
from s00_reconstruction_common import *
import random,statistics

def comparison(rows,base='previous',new='integrated'):
 pairs=[r for r in rows if all(r['success'][base]) and all(r['success'][new])]
 a=sum(r['median_seconds'][base] for r in pairs);b=sum(r['median_seconds'][new] for r in pairs)
 interval=None
 if pairs:
  rng=random.Random(28211);ratios=[]
  for _ in range(5000):
   sample=[rng.choice(pairs) for _ in pairs]
   ratios.append(sum(r['median_seconds'][new] for r in sample)/sum(r['median_seconds'][base] for r in sample))
  ratios.sort();interval=[ratios[125],ratios[4874]]
 return dict(requests=len(rows),matched_completed=len(pairs),old_completed=sum(all(r['success'][base]) for r in rows),new_completed=sum(all(r['success'][new]) for r in rows),old_seconds=a,new_seconds=b,ratio=b/a if a else None,interval=interval,slower=sum(r['median_seconds'][new]>r['median_seconds'][base] for r in pairs),old_failed_applications=sum(sum(not ok for ok in r['success'][base]) for r in rows),new_failed_applications=sum(sum(not ok for ok in r['success'][new]) for r in rows),all_attempt_seconds={m:sum(sum(r['times'][m]) for r in rows) for m in [base,new]})

def main():
 protocol=read(HERE/'test_protocol.json.gz')
 for w in [0,1]:assert read(HERE/f'test{w}_complete.json')['protocol_sha256']==sha(HERE/'test_protocol.json.gz')
 rows=[read(HERE/'model_test'/(c['id']+'.json.gz')) for c in protocol['cases']]
 native=[r for r in rows if r['group']=='native'];policy=read(HERE/'trained_model/policy.json')
 choices={};predictions=[];changed=0;used=0
 for r in native:
  a=r['results']['integrated'];f=r['results']['fixed'];action=a.get('reconstruction_action','preceding_dispatch')
  choices[action]=choices.get(action,0)+1
  changed+=action!=f.get('reconstruction_action','preceding_dispatch')
  used+=bool(a.get('reconstruction_decision',{}).get('model_used'))
  predictions.append(a.get('reconstruction_decision_seconds',0.)+a.get('reconstruction_model_loading_seconds',0.))
 summary=dict(complete=True,protocol_sha256=sha(HERE/'test_protocol.json.gz'),all=comparison(rows),native=comparison(native),new_ml=comparison(native,'fixed'),groups={g:comparison([r for r in rows if r['group']==g]) for g in sorted({r['group'] for r in rows})},native_structures={g:comparison([r for r in native if r['topology']==g]) for g in sorted({r['topology'] for r in native})},loop_orders={str(L):comparison([r for r in rows if r['loops']==L]) for L in sorted({r['loops'] for r in rows})},checks=sum(r['checks'] for r in rows),reference_failures=[r['case'] for r in rows if not r['reference_success']],model_enabled=policy['enabled'],changed_actions=changed,model_used_requests=used,choices=choices,median_loading_and_prediction_seconds=statistics.median(predictions),failed_native_attempts={m:sum(sum(r['failed_attempts'][m]) for r in rows) for m in protocol['methods']},reconstruction_fallbacks={m:sum(sum(r['reconstruction_fallbacks'][m]) for r in rows) for m in protocol['methods']},rows=[{k:v for k,v in r.items() if k not in ['results','failed_applications']} for r in rows])
 summary['cumulative']=comparison(rows,'before_formulas')
 summary['analytic_step']=comparison(rows,'before_formulas','previous')
 summary['cumulative_groups']={g:comparison([r for r in rows if r['group']==g],'before_formulas') for g in sorted({r['group'] for r in rows})}
 write(HERE/'summary.json',summary)
 print(json.dumps({k:v for k,v in summary.items() if k not in ['rows','loop_orders','groups','native_structures']}),flush=True)
if __name__=='__main__':main()
