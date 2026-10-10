#!/usr/bin/env python3
import subprocess,sys,time,json,re,os
from pathlib import Path
root=Path('/u/home/r/rushil/ML_for_Kira_Seeding_Reduction')
start=time.perf_counter();events=[]
p=subprocess.Popen(['/usr/bin/stdbuf','-oL','-eL',str(root/'.tools/kira-equation-selection/kira-lazy')]+sys.argv[1:],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
patterns=('*****','Find IBP','Prepare numerical','Prepare Symmetries','Search symmetry','Kira prepares','Number of selected','Triangular form completed','Kira committed','kira2file:','Algebraic reconstruction','Total time:','1 Fermat','Generate equations','length of mandatory','set numerics','One variable')
for line in p.stdout:
 if any(line.startswith(v) for v in patterns) and not line.startswith('Generate equations'):
  events.append({'elapsed':time.perf_counter()-start,'line':line.strip()})
 sys.stdout.write(line)
 sys.stdout.flush()
code=p.wait()
events.append({'elapsed':time.perf_counter()-start,'line':'process_exit'})
Path(os.environ['KIRA_PROFILE_EVENTS']).write_text(json.dumps(events))
sys.exit(code)
