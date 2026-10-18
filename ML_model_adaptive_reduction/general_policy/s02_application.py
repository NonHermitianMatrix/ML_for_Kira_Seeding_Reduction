"""Apply one shared model to valid family definitions, with exact fallback."""
from s00_common import *
import contextlib,struct

def predict(m,x):
 if m['kind'] in ['ridge','mlp']:
  v=[(a-b)/s for a,b,s in zip(x,m['mean'],m['scale'])]
  if m['kind']=='ridge':return [b+sum(a*w for a,w in zip(v,row)) for b,row in zip(m['intercept'],m['coef'])]
  for k,(w,b) in enumerate(zip(m['weights'],m['bias'])):
   v=[b[j]+sum(v[i]*w[i][j] for i in range(len(v))) for j in range(len(b))]
   if k<len(m['weights'])-1:v=[max(0.,a) for a in v]
  return v
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x];out=[0.]*len(ACTIONS)
 for t in m['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  for j,v in enumerate(t['value'][i]):out[j]+=v/len(m['trees'])
 return out

@contextlib.contextmanager
def exact_storage(c):
 old=rt.native.run
 def run(*args,**kw):
  # Both timed controls use this same exact allocation implementation.
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-storage/kira')
  os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  return old(*args,**kw)
 rt.native.run=run
 try:yield
 finally:rt.native.run=old

def reduce(c,basis,method='learned',reference=None):
 start=time.perf_counter();action='native';decision=None
 if len(c['definition']['propagators'])>31:return dict(success=False,status='unsupported_native_index_count',model_applicable=True)
 if method=='fixed':action=READ(HERE/'trained_model/fixed.json')['action']
 if method=='learned':
  m=READ(HERE/'trained_model/freeze.json');x=features(c);s=predict(m['model'],x);cfg=m['selection'];a=cfg['anchor'];i=min(range(len(ACTIONS)),key=s.__getitem__)
  action=ACTIONS[i if s[i]<s[a]-cfg['margin'] else a]
  decision=dict(action=action,scores=s,seconds=time.perf_counter()-start,model_used=True,family_identifier_used=False)
 with exact_storage(c):r=rt.run(c,basis,'native',reference,first=action,timeout=45)
 r.update(method=method,selection=decision,complete_seconds=time.perf_counter()-start)
 return r

def main():
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args();req=READ(a.input);c=req['case'];method=req['method'];ref=req.get('reference');basis=req.get('basis')
 try:
  if method in ['reference','check']:
   b=inputs.bounds(c,'expanded')
   if method=='check':b[1]+=1
   with exact_storage(c),rt.environment():
    r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=60,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=2 if method=='check' else 1,threads=1)
   if ref:rt.verify(r,ref)
  else:r=reduce(c,basis,method,ref)
 except Exception as e:r=dict(success=False,status='exception',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc()[-1600:])
 r=rt.compact(r);r.update(case=c['id'],method=method,worker=os.uname().nodename)
 raw=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0);assert len(raw)<1024**2
 Path(a.output).write_bytes(raw)
if __name__=='__main__':main()
