"""Shared paths, frozen provenance, bounded resources and coefficient output."""
import os,sys,json,time,math,hashlib,gzip,random,statistics,subprocess,signal,socket,resource,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
EXACT=ROOT/"ML_model_equation_selection/exact_backend"
HIGH=ROOT/"ML_model_equation_selection/higher_loops"
sys.path.insert(0,str(EXACT))
import s14_reader as upgraded
import s00_backend as backend
import s02_engine as engine
sys.path.insert(0,str(HIGH))
spec=importlib.util.spec_from_file_location("cumulative_legacy",HIGH/"s02_reduce.py")
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
OBJECTS=HERE/"objects"
ARMS=["original_kira","chain_baseline","final"]
BINARIES={"original_kira":ROOT/".tools/kira/bin/kira","chain_baseline":ROOT/".tools/kira-early-generation/kira"}
def read(p):return json.loads(Path(p).read_text())
def write(p,x):backend.write(Path(p),x)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def allocated(p):return sum(f.stat().st_blocks*512 for f in Path(p).rglob("*") if f.is_file())
def guard():
 plan=read(HERE/"resource_plan.json")
 assert plan["combined_upper_bytes"]<10000000000
 assert allocated(HERE)<plan["new_retained_cap_bytes"]
def check_freeze():
 for n,h in read(HERE/"freeze.json")["sha256"].items():assert sha(ROOT/n)==h,n
def frozen_files():
 files=set(p for p in HERE.glob("s0[0-4]*") if p.is_file())
 files.update((HERE/"test/inputs").glob("*.json"))
 files.update([HERE/"protocol.json",HERE/"resource_plan.json",EXACT/"reader_final_deployment.json",EXACT/"trained_model/cost_tree.json",EXACT/"build/reader.so",EXACT/"build/transform.so",*BINARIES.values(),legacy.FERMAT])
 for mod in list(sys.modules.values()):
  name=getattr(mod,"__file__",None)
  if name:
   p=Path(name).resolve()
   if ROOT in p.parents and p.suffix in [".py",".so"]:files.add(p)
 return sorted(files)
def packed(rows):
 return [{str(j):[[x.numerator,x.denominator] for x in legacy.canonical(p)] for j,p in row.items() if legacy.canonical(p)} for row in rows]
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2400*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
def process_ids(pid):
 todo=[pid];seen=set()
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p)
  try:
   for t in (Path("/proc")/str(p)/"task").iterdir():
    try:todo.extend(map(int,(t/"children").read_text().split()))
    except OSError:pass
  except OSError:pass
 return seen
def stop_tree(pid):
 ids=process_ids(pid)
 for p in sorted(ids,reverse=True):
  try:os.kill(p,signal.SIGTERM)
  except ProcessLookupError:pass
 time.sleep(.3)
 for p in sorted(ids,reverse=True):
  try:os.kill(p,signal.SIGKILL)
  except ProcessLookupError:pass
