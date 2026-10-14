"""Probe smaller seed regions on training examples with exact basis checks."""
import json,os,sys
from pathlib import Path
from s00_pilot import HERE,ROOT,study,save
sys.path.insert(0,str(HERE))
from s02_run import run
def main():
 cases=json.loads((study.HERE/'cases.json').read_text())['cases']
 cases=[c for c in cases if c['split']=='training' and 'point10' in c['id']]
 for c in cases:
  base=[max(sum(max(0,a) for a in t) for t in c['targets']),max(sum(max(0,-a) for a in t) for t in c['targets']),max(sum(max(0,a-1) for a in t) for t in c['targets'])]
  for delta in [(0,0,0),(-1,0,-1),(-1,-1,-1),(0,-1,0)]:
   bounds=[max(0,a+b) for a,b in zip(base,delta)]
   p=HERE/'development'/f'{c["id"]}_bounds_{bounds[0]}_{bounds[1]}_{bounds[2]}.json.gz'
   if p.exists():continue
   study.setup();os.environ['KIRA_EPHEMERAL_DB']='1'
   r=run(c,c['size'],'native',HERE/'unused',timeout=90,margin=0,reference=study.HERE/'references'/(c['id']+'.json.gz'),records=False,archive=False,check_masters=True,scratch_cap=32*1024**2,bounds=bounds)
   save(p,r);print(json.dumps(dict(case=c['id'],bounds=bounds,seconds=r['complete_seconds'],success=r['success'],status=r['status'])),flush=True)
if __name__=='__main__':main()
