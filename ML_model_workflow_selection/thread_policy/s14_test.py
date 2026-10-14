"""Run the frozen comparison with bounded record writing outside measured time."""
import gzip,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
import s05_fit as model
w=model.w

def load(name,filename):
 spec=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

class RecordWriter:
 """Account for each saved record and rescan storage every 32 writes."""
 def __init__(self):self.used=None;self.count=0
 def __call__(self,p,r):
  p=Path(p);assert p.resolve().is_relative_to(HERE.resolve())
  p.parent.mkdir(parents=True,exist_ok=True)
  data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0);assert len(data)<1024**2
  if self.used is None or self.count%32==0:self.used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())
  # Reserve space for growing text logs and other small metadata between scans.
  reserve=1024**2;allocation=((len(data)+4095)//4096)*4096
  assert self.used+2*allocation+reserve<w.CAP
  before=p.stat().st_blocks*512 if p.exists() else 0
  tmp=p.with_suffix('.tmp');assert not tmp.exists();tmp.write_bytes(data);tmp.replace(p)
  self.used+=p.stat().st_blocks*512-before;self.count+=1

def main():
 frozen=json.loads((HERE/'trained_model/freeze.json').read_text());model.check_freeze(frozen)
 manifest=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),freeze_sha256=model.sha(HERE/'trained_model/freeze.json'),timing='Only record persistence changes. Complete reduction timing ends before records are written. Every exact check and full native attempt stays active.')
 path=HERE/'test_writer.json'
 if path.exists():assert json.loads(path.read_text())==manifest
 else:w.write(path,manifest)
 w.save=RecordWriter()
 load('worker_reserved_tests','s06_test.py').main()
 load('worker_reserved_analysis','s08_analyze.py').main()
 load('worker_public_checks','s10_public_checks.py').main()
 w.emit(stage='pipeline_complete')
if __name__=='__main__':main()
