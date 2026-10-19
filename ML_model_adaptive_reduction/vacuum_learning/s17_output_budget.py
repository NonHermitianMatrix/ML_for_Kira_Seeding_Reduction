"""Keep transient request files within their separate output budget."""
from s00_vac_common import *
import fcntl

def output(path,obj):
 p=Path(path).resolve();assert p.parent==(HERE/'requests').resolve(),'Use the bounded requests directory.'
 raw=json.dumps(obj,separators=(',',':')).encode();assert len(raw)<3*1024**2
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<256*1024
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  used=sum(q.stat().st_blocks*512 for q in (HERE/'requests').iterdir() if q.is_file())
  assert used+len(raw)+8192<512*1024,'The runtime file budget is full.'
  q=p.with_suffix(p.suffix+'.tmp');q.write_bytes(raw);q.replace(p)
