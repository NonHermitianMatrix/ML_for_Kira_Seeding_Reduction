"""Train, select on validation cost, and test only a useful frozen policy."""
import subprocess,sys
from s00_probe import HERE,rt,inputs
for name,args in [('s02_train.py',[]),('s03_refine.py',['validate'])]:
 if (HERE/'trained_model/freeze.json').exists():continue
 if name=='s02_train.py' and (HERE/'trained_model/candidates.json').exists():continue
 subprocess.run([sys.executable,str(HERE/name),*args],check=True)
f=rt.read(HERE/'trained_model/freeze.json')
if any(x['option'] is not None for x in f['selection'].values()):
 subprocess.run([sys.executable,str(HERE/'s03_refine.py'),'test'],check=True)
 subprocess.run([sys.executable,str(HERE/'s09_finish.py')],check=True)
else:inputs.write(HERE/'validation_no_gain.json',dict(complete=True,reason='No filter reduced graph-level complete validation time by the prespecified 5 percent.'))
