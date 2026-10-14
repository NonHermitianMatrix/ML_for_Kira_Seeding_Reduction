"""Measure complete-cost alternatives on development cases only."""
import gzip,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'ML_model_equation_selection/scattering_training'))
import s00_scattering_study as study

def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
 assert len(data)<2*1024**2
 tmp=p.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(p)
 assert sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())<40*1024**2

def main():
 cases=json.loads((study.HERE/'cases.json').read_text())['cases']
 cases=[c for c in cases if c['split']=='training' and 'point10' in c['id']]
 configs=[dict(name='native',ordering=1,ephemeral=False,task='native',threshold=.01)]
 configs += [dict(name=f'order{o}',ordering=o,ephemeral=True,task='native',threshold=.01) for o in [1,2,3,4,5,6,7,8]]
 configs += [dict(name=f'equation{t}',ordering=1,ephemeral=True,task='equation',threshold=t) for t in [.1,.3,.5]]
 for c in cases:
  ref=study.HERE/'references'/(c['id']+'.json.gz')
  for cfg in configs:
   p=HERE/'development'/f'{c["id"]}_{cfg["name"]}.json.gz'
   if p.exists():continue
   os.environ['KIRA_EPHEMERAL_DB']='1' if cfg['ephemeral'] else '0'
   study.setup('off' if cfg['task']=='native' else 'learned',study.model_path(c,'equation'),cfg['threshold'])
   r=study.run(c,c['size'],'native',HERE/'unused',timeout=90,margin=0,reference=ref,records=False,archive=False,check_masters=True,scratch_cap=32*1024**2,ordering=cfg['ordering'])
   r['configuration']=cfg;save(p,r)
   print(json.dumps(dict(case=c['id'],config=cfg['name'],seconds=r['complete_seconds'],success=r['success'],status=r['status'])),flush=True)
if __name__=='__main__':main()
