"""Summarize completions and paired ratios without hiding slower requests."""
from s00_direct_common import *
from s14_prepare import sha

def comparison(rows,control='previous'):
 matched=[r for r in rows if all(r['success']['integrated']) and all(r['success'][control])];a=sum(r['median_seconds']['integrated'] for r in matched);b=sum(r['median_seconds'][control] for r in matched);ratio=a/b if b else None;rng=random.Random(23603);samples=[]
 if matched:
  for _ in range(4000):
   ids=[rng.randrange(len(matched)) for _ in matched];samples.append(sum(matched[i]['median_seconds']['integrated'] for i in ids)/sum(matched[i]['median_seconds'][control] for i in ids))
  samples.sort()
 return dict(requests=len(rows),matched_completed=len(matched),new_completed=sum(all(r['success']['integrated']) for r in rows),old_completed=sum(all(r['success'][control]) for r in rows),new_seconds=a,old_seconds=b,ratio=ratio,interval=[samples[100],samples[3899]] if samples else None,slower=sum(r['median_seconds']['integrated']>r['median_seconds'][control] for r in matched))

def main():
 p=read(HERE/'protocol.json.gz');assert all(read(HERE/f'test{i}.json')['complete'] for i in [0,1]);rows=[read(HERE/'model_test'/(c['id']+'.json.gz')) for c in p['cases']];extended=[read(HERE/'model_test'/(c['id']+'.json.gz')) for c in p['extended_cases']];native=[r for r in rows if r['group']=='native'];m=read(HERE/'trained_model/policy.json')
 s=dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz'),all=comparison(rows),groups={g:comparison([r for r in rows if r['group']==g]) for g in sorted({r['group'] for r in rows})},native_ml=comparison(native,'fixed'),checks=sum(r['checks'] for r in rows+extended),extended_requests=len(extended),extended_completed=sum(all(r['success']['integrated']) for r in extended),extended_seconds=sum(r['median_seconds']['integrated'] for r in extended),model_enabled=m['enabled'],prediction_seconds=[r['results']['integrated'].get('prediction_seconds') for r in native],changed_native_requests=sum(r['results']['integrated'].get('selected_action')!=m['fixed'] for r in native),failed_applications={method:sum(sum(not v for v in r['success'][method]) for r in native) for method in ['integrated','fixed','previous']},native_failed_attempts={method:sum(sum(r['failed_attempts'][method]) for r in native) for method in ['integrated','fixed','previous']},rows=[{k:v for k,v in r.items() if k not in ['reference','results']} for r in rows+extended])
 write(HERE/'summary.json',s);print(json.dumps({k:v for k,v in s.items() if k not in ['rows','prediction_seconds']}),flush=True)
if __name__=='__main__':main()
