"""Report paired complete time, failures, model use, and finite-sample uncertainty."""
from s00_vac_common import *

def compare(rows,new='integrated',old='previous'):
 pairs=[r for r in rows if all(r['success'][new]) and all(r['success'][old])]
 oldtime=sum(r['median_seconds'][old] for r in pairs);newtime=sum(r['median_seconds'][new] for r in pairs);rng=random.Random(6113);ratios=[]
 if pairs:
  for _ in range(2000):
   sample=[rng.choice(pairs) for _ in pairs];ratios.append(sum(r['median_seconds'][new] for r in sample)/sum(r['median_seconds'][old] for r in sample))
 ratios.sort()
 return dict(requests=len(rows),new_completed=sum(all(r['success'][new]) for r in rows),old_completed=sum(all(r['success'][old]) for r in rows),matched_completed=len(pairs),new_seconds=newtime,old_seconds=oldtime,ratio=newtime/oldtime if oldtime else None,saving_percent=100*(1-newtime/oldtime) if oldtime else None,interval=[ratios[50],ratios[1949]] if ratios else None,slower=sum(r['median_seconds'][new]>r['median_seconds'][old] for r in pairs))

def main():
 p=read(HERE/'protocol.json.gz');assert all(read(HERE/f'test{i}_complete.json')['complete'] for i in [0,1]);rows=[read(HERE/'results'/(c['id']+'.json.gz')) for c in p['cases']]
 groups={g:compare([r for r in rows if r['group']==g]) for g in ['vacuum','native','propagator','triangle']};native=[r for r in rows if r['group']=='native'];ml=compare(native,old='all_fixed')
 actions={};used=0
 for r in native:
  ans=r['results']['integrated'];used+=any(b['result'].get('batch_model_used',False) for b in ans.get('blocks',[]))
  for b in ans.get('blocks',[]):
   a=b['result'].get('batch_action','none');actions[a]=actions.get(a,0)+1
 compact=[{k:v for k,v in r.items() if k!='results'} for r in rows]
 s=dict(complete=True,groups=groups,ml=ml,all=compare(rows),rows=compact,checks=sum(r['checks'] for r in rows),gamma_checks=sum(r['gamma']['checks'] for r in rows),model_requests=used,actions=actions,protocol_sha256=sha(HERE/'protocol.json.gz'),model_sha256=sha(HERE/'trained_model/policy.json'))
 write(HERE/'summary.json',s);print(json.dumps({k:v for k,v in s.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
