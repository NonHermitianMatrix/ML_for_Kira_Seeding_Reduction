"""Use a compiled lossless reader without changing the first frozen implementation."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
# Keep the preceding modules and saved tree unchanged.
import s00_backend as backend
import s02_engine as engine
from s00_backend import *
spec=importlib.util.spec_from_file_location("_exact_reader",HERE/"build/reader.so")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
python_reader=backend.decode_expanded
def compiled_reader(data,keys):return module.expanded(data,keys)
backend.decode_expanded=compiled_reader
engine.decode_expanded=compiled_reader
def main():
 from s04_check import kernel
 kernel_path=HERE/"development/kernel_check.json";before=kernel_path.read_bytes()
 # Compare readers directly; never overwrite the initial exact-check record.
 rng=random.Random(857713);checks=0
 for k in range(250):
  rows=[{0:old.normalized([rng.randrange(-10**30,10**30) for j in range(rng.randrange(1,15))],rng.randrange(1,10**30))}]
  data=native(common_packet(rows,[1,7,12,32]),{})
  assert compiled_reader(data,[[0]])==python_reader(data,[[0]]);checks+=4
  try:compiled_reader(data[:-1],[[0]])
  except ValueError:pass
  else:raise AssertionError("Truncated output accepted")
 assert before==kernel_path.read_bytes()
 write(HERE/"development/reader_check.json",dict(all_passed=True,loop_checks=checks,truncation_checks=250))
 print("compiled reader checks",checks,flush=True)
if __name__=="__main__":main()
