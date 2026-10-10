"""Profile preparation on one validation case without using the timing as a benchmark."""
import json,os,pathlib,resource,shutil,subprocess,sys
import s02_run as engine
from s03_records import read_record,write_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 case=next(c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["id"]=="validation_01_double_box")
 reference=ROOT/"Kira_comparison/multiloop_native/references/validation_01_double_box_n32.json.gz"
 os.environ["KIRA_RUNTIME_SCRATCH"]="node";os.environ["KIRA_RUNTIME_BINARY"]=".tools/kira-runtime-fast/kira"
 original_popen=subprocess.Popen;original_remove=shutil.rmtree
 for tracing in [False,True]:
  path=HERE/"preparation_profile"/("strace.json.gz" if tracing else "cpu.json.gz")
  if path.exists():continue
  captured={}
  def popen(args,*a,**kw):
   if tracing and str(args[0]).endswith("/kira"):
    args=["/usr/bin/strace","-f","-c","-o",str(pathlib.Path(kw["cwd"])/"syscalls.txt"),*args]
   return original_popen(args,*a,**kw)
  def remove(where,*a,**kw):
   p=pathlib.Path(where)/"syscalls.txt"
   if p.exists():captured["system_calls"]=p.read_text()
   return original_remove(where,*a,**kw)
  subprocess.Popen=popen;shutil.rmtree=remove
  before=resource.getrusage(resource.RUSAGE_CHILDREN)
  try:r=engine.run(case,32,"native",path,timeout=180,margin=1,reference=reference,records=False,archive=False,check_masters=True)
  finally:subprocess.Popen=original_popen;shutil.rmtree=original_remove
  after=resource.getrusage(resource.RUSAGE_CHILDREN)
  r.update(captured);r["profile_only"]=True;r["traced"]=tracing
  r["child_user_cpu_seconds"]=after.ru_utime-before.ru_utime;r["child_system_cpu_seconds"]=after.ru_stime-before.ru_stime
  write_record(path,r)
  print(json.dumps(dict(traced=tracing,success=r["success"],seconds=r["complete_seconds"],user_cpu=r["child_user_cpu_seconds"],system_cpu=r["child_system_cpu_seconds"],syscalls=r.get("system_calls",""))),flush=True)
if __name__=="__main__":main()
