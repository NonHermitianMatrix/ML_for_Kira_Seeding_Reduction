"""Bound compressed writes to a documented 80 MiB worker allowance."""
import contextlib,gzip,io,os
import s06_evaluate as evaluation
BUDGET=83886080
@contextlib.contextmanager
def bounded_gzip(path,binary=False):
 tmp=path.with_name(path.name+".part")
 remaining=BUDGET-evaluation.output_allocated(path.parent)-8192
 old=path.stat().st_blocks*512 if path.exists() else 0
 assert remaining>0,"Worker output allowance reached"
 class Sink:
  def __init__(self,f):self.f=f;self.left=remaining
  def write(self,b):
   if len(b)>self.left:raise RuntimeError("Worker compressed-output allowance reached")
   n=self.f.write(b);self.left-=n;return n
  def flush(self):self.f.flush()
 try:
  with tmp.open("wb") as raw:
   with gzip.GzipFile(fileobj=Sink(raw),mode="wb",compresslevel=6,mtime=0) as compressed:
    if binary:yield compressed
    else:
     with io.TextIOWrapper(compressed,encoding="utf-8") as text:yield text
  os.replace(str(tmp),str(path))
  evaluation._allocated_cache[str(path.parent.resolve())]+=path.stat().st_blocks*512-old
 except BaseException:
  if tmp.exists():tmp.unlink()
  raise
