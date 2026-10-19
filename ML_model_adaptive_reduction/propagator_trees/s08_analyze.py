"""Report matched completed reductions separately from deadlines and unsupported inputs."""
from s00_prop_common import *
import random,collections

def aggregate(rows,new='integrated',old='previous'):
    paired=[r for r in rows if all(r['success'][new]) and all(r['success'][old])]
    a=sum(r['median_seconds'][new] for r in paired);b=sum(r['median_seconds'][old] for r in paired)
    ratios=[];rng=random.Random(5051)
    if paired:
        for _ in range(2000):
            sample=[rng.choice(paired) for r in paired]
            ratios.append(sum(r['median_seconds'][new] for r in sample)/sum(r['median_seconds'][old] for r in sample))
        ratios.sort()
    return dict(requests=len(rows),matched_completed=len(paired),new_completed=sum(all(r['success'][new]) for r in rows),old_completed=sum(all(r['success'][old]) for r in rows),new_seconds=a,old_seconds=b,ratio=a/b if b else None,saving_percent=100*(1-a/b) if b else None,interval=[ratios[49],ratios[1949]] if ratios else [],slower=sum(r['median_seconds'][new]>r['median_seconds'][old] for r in paired),new_all_seconds=sum(r['median_seconds'][new] for r in rows),old_all_seconds=sum(r['median_seconds'][old] for r in rows),old_status_counts=dict(collections.Counter(s for r in rows for s in r['statuses'][old])))
def main():
    p=read(HERE/'protocol.json.gz');assert all(read(HERE/f'worker{w}_complete.json')['complete'] for w in [0,1])
    rows=[read(HERE/'results'/(c['id']+'.json.gz')) for c in p['cases']]
    s=dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz'),groups={g:aggregate([r for r in rows if r['group']==g]) for g in ['propagator','triangle','native']},all=aggregate(rows),ml=aggregate([r for r in rows if r['group']=='native'],'integrated','all_fixed'),checks=sum(r['checks'] for r in rows),gamma_checks=sum(r['gamma']['checks'] for r in rows),rows=[{k:v for k,v in r.items() if k!='results'} for r in rows])
    write(HERE/'summary.json',s);print(json.dumps({k:v for k,v in s.items() if k!='rows'}))
if __name__=='__main__':main()
