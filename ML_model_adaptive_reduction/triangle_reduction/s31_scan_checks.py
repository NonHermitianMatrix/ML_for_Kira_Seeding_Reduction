"""Reproduce a disappearing-directory race and check the bounded replacement."""
from s00_triangle_common import *
from s30_monitor import Scanner
import pathlib,shutil

def main():
 root=HERE/'scanner_temporary';assert not root.exists();root.mkdir();(root/'keep').write_bytes(b'k'*17);victim=root/'removed'
 native=helper().rt.native.run.__globals__['disk'];original=os.scandir;accessor=pathlib._normal_accessor;old_accessor=accessor.scandir
 def setup():victim.mkdir();(victim/'item').write_bytes(b'v'*17)
 def hook(path):
  if not isinstance(path,int) and Path(path)==victim and victim.exists():
   os.scandir=original;accessor.scandir=old_accessor
   try:shutil.rmtree(victim)
   finally:os.scandir=hook;accessor.scandir=hook
  return original(path)
 try:
  setup();expected=(root/'keep').stat().st_blocks*512+(victim/'item').stat().st_blocks*512;scan=Scanner();assert scan(root)==expected
  os.scandir=hook;accessor.scandir=hook;old_failed=False
  try:native(root)
  except FileNotFoundError:old_failed=True
  finally:os.scandir=original;accessor.scandir=old_accessor
  assert old_failed,'The old scanner must expose the tested race'
  setup();os.scandir=hook;accessor.scandir=hook;safe=Scanner()
  try:result=safe(root)
  finally:os.scandir=original;accessor.scandir=old_accessor
  assert result==(root/'keep').stat().st_blocks*512 and safe.vanished==1
  # A real access failure must still stop the monitor.
  def denied(path):raise PermissionError('controlled access failure')
  os.scandir=denied;propagated=False
  try:Scanner()(root)
  except PermissionError:propagated=True
  finally:os.scandir=original
  assert propagated
  write(HERE/'scanner_checks.json',dict(complete=True,stable_count_correct=True,old_scanner_raised_on_removed_directory=old_failed,new_scanner_completed=True,remaining_file_bytes=result,vanished_entries=safe.vanished,permission_errors_propagate=True,source_sha256=sha(HERE/'s30_monitor.py')))
 finally:os.scandir=original;accessor.scandir=old_accessor;shutil.rmtree(root)
 print('scanner checks passed',flush=True)
if __name__=='__main__':main()
