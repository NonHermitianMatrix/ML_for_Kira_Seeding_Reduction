"""Keep new cases, exact references and bounded records in this study."""
import gzip,hashlib,json,time
from pathlib import Path
import s00_runtime as runtime
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
st=runtime.prior.st
old=runtime.prior.old
CAP=16*1024**2
workflow=runtime.workflow
verify=runtime.prior.verify
read=st.read
emit=st.emit
write=st.write
cases=runtime.prior.cases
def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
 assert len(data)<1024**2
 used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())
 assert used+len(data)+4096<CAP
 tmp=p.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(p)
def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if not p.exists():
  r=st.attempt(c,None,'expanded');save(p,st.compact(r))
  emit(stage='reference',case=c['id'],success=r['success'],seconds=r['complete_seconds'])
 assert read(p)['success'],c['id']
 return p
