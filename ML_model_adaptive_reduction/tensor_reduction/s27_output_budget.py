"""Write bounded request output while allowing concurrent transient cleanup."""
from s00_tensor_common import *
def output(path,obj):
 import fcntl
 p=Path(path).resolve();assert p.parent==HERE/'requests';p.parent.mkdir(exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode();assert len(raw)<4*1024**2
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);used=0
  for q in p.parent.iterdir():
   try:used+=q.stat().st_blocks*512 if q.is_file() else 0
   except FileNotFoundError:pass
  assert used+len(raw)+8192<2*1024**2
  q=p.with_suffix(p.suffix+'.tmp');q.write_bytes(raw);q.replace(p)
