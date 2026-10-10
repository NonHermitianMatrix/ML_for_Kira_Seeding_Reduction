import sys,os,json,gzip,time,resource
from pathlib import Path
root=Path.cwd();out=root/'.tools/bottleneck-audit';sys.path.insert(0,str(root/'ML_model_equation_selection'))
from s04_experiment import setup,cases,reference
from s03_profile_run import run
os.environ['KIRA_EQ_RUNTIME_BINARY']=str(out/'s00_timestamp.py')
setup();os.environ.update(KIRA_EQ_MODE='off',KIRA_EQ_COLLECT='0')
selected=[(c,n) for c,n in cases('testing') if (c['id'],n) in [('equation_test_00_sunrise',21),('equation_test_02_double_box',128),('equation_test_06_ladder3',128),('equation_test_07_ladder3',128)]]
for rep in range(3):
 for c,n in selected[::1 if rep%2==0 else -1]:
  name=f"{c['id']}_n{n}_r{rep}";p=out/(name+'.json.gz')
  os.environ['KIRA_PROFILE_EVENTS']=str(out/(name+'_events.json'))
  ref=reference(c,n)
  r=run(c,n,'native',p,timeout=90,margin=0,reference=ref,records=False,archive=False,check_masters=True,scratch_cap=8*1024**2)
  with gzip.open(p,'wt') as f:json.dump(r,f)
  assert r['success'],(name,r['status'])
  print(json.dumps({'case':name,'complete_seconds':r['complete_seconds'],'success':r['success']}),flush=True)
  assert sum(p.stat().st_size for p in out.iterdir() if p.is_file())<8*1024**2
(out/'completed.json').write_text(json.dumps({'count':len(selected)*3,'success':True,'scope':'diagnostic timestamps; native equations and exact reference checks; no model changes'}))
