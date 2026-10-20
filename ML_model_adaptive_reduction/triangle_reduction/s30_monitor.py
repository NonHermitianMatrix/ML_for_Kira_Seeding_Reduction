"""Count active scratch files while tolerating concurrent file removal."""
from s00_triangle_common import *
from contextlib import contextmanager

class Scanner:
 def __init__(self):self.calls=0;self.vanished=0;self.peak=0;self.seconds=0.
 def __call__(self,path):
  start=time.perf_counter();self.calls+=1;size=0;stack=[os.fspath(path)]
  while stack:
   current=stack.pop()
   try:
    with os.scandir(current) as entries:
     for e in entries:
      try:
       if e.is_dir(follow_symlinks=False):stack.append(e.path)
       elif e.is_file():size+=e.stat().st_blocks*512
      except FileNotFoundError:self.vanished+=1
   except FileNotFoundError:self.vanished+=1
  self.peak=max(self.peak,size);self.seconds+=time.perf_counter()-start;return size
 def record(self):return dict(calls=self.calls,vanished_entries=self.vanished,peak_bytes=self.peak,seconds=self.seconds)

@contextmanager
def monitor(c):
 scanner=Scanner()
 if c.get('topology_group') not in ['double_box','nonplanar_box','sunrise','vacuum3']:
  yield scanner;return
 namespace=helper().rt.native.run.__globals__;old=namespace['disk'];namespace['disk']=scanner
 try:yield scanner
 finally:namespace['disk']=old
