"""Check concurrent output accounting without generating scientific data."""
import ast
import multiprocessing
import tempfile
from pathlib import Path

def main():
 source=Path(__file__).with_name('s00_cost_common.py').read_text()
 node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='allocation_change')
 code=compile(ast.Module(body=[node],type_ignores=[]),'allocation_fixture','exec')
 with tempfile.TemporaryDirectory(prefix='kira-storage-check-') as name:
  root=Path(name).resolve();namespace=dict(Path=Path,HERE=root,CAP=16*1024**2)
  exec(code,namespace);change=namespace['allocation_change']
  def worker(i):
   for j in range(20):
    p=root/str(i)/str(j);change(p,b'x'*6000);change(p,b'x'*900)
    if j%2:change(p)
  context=multiprocessing.get_context('fork')
  processes=[context.Process(target=worker,args=(i,)) for i in range(4)]
  for p in processes:p.start()
  for p in processes:p.join(timeout=30);assert p.exitcode==0
  def check():
   actual=sum(p.stat().st_blocks*512 for p in root.rglob('*') if p.is_file() and p.name not in ['.storage_bytes','.storage_lock'] and p.parent!=root/'requests')
   assert actual==int((root/'.storage_bytes').read_text())
  check()
  transient=root/'requests'/'sample.pending.gz'
  change(transient,b'current output');check();change(transient);check()
  transient.write_bytes(b'output from the previous application');change(transient);check()
  (root/'.storage_bytes').write_text('dirty\n');(root/'recovered.writing').write_bytes(b'old')
  change(root/'recovered',b'new');check();change(root/'recovered');check()
  try:change(root.parent/'outside-budget',b'bad')
  except ValueError:pass
  else:raise AssertionError('Output outside the study was accepted')
 print('Storage accounting checks passed: concurrency, replacement, deletion, recovery, and path boundary.')

if __name__=='__main__':main()
