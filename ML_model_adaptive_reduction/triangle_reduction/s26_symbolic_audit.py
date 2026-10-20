"""Audit all fitted and selected action records against independent symbolic algebra."""
from s00_triangle_common import *
from s04_triangle_measure import measured,compare

def main(w):
 assert os.environ.get('JOB_ID');cfg=read(HERE/'learning_protocol.json');paths=[]
 for phase in ['training','validation']:paths.extend(sorted((HERE/phase).glob('*.json.gz')))
 out=[]
 for path in paths[w::2]:
  row=read(path);c=row['case'];dest=HERE/'symbolic_references'/(c['id']+'.json.gz')
  if dest.exists():record=read(dest);ref=record['result']
  else:
   ref,t=measured(c,'symbolic_prior',w);record=dict(case=c,result=ref,seconds=t);write(dest,record)
  assert ref.get('success'),c['id']
  actions=['baseline'] if c['topology_group'] in cfg.get('guarded_structures',[]) else list(row['actions'])
  checks=[]
  for a in actions:
   for i,r in enumerate(row['actions'][a]['records']):
    ok,n=compare(c,r['result'],ref);checks.append(dict(action=a,repetition=i,verified=ok,checks=n))
  rec=dict(case=c['id'],source=path.name,checks=checks,verified=all(r['verified'] for r in checks));write(HERE/'symbolic_audit'/(c['id']+'.json'),rec);out.append(rec)
  print('symbolic',c['id'],rec['verified'],flush=True);assert rec['verified'],c['id']
 write(HERE/('symbolic_audit'+str(w)+'.json'),dict(complete=True,records=out))
if __name__=='__main__':main(int(sys.argv[1]))
