"""Counterbalanced exact comparison of disposable database settings."""
import json,os,pathlib,subprocess,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 cases=json.loads((HERE/"families.json").read_text())["cases"]
 name="validation_01_double_box";case=next(c for c in cases if c["id"]==name)
 ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n32.json.gz"
 for rep in range(3):
  for enabled in ([0,1] if rep%2==0 else [1,0]):
   dest=HERE/"database_pilot"/f"{name}_db{enabled}_r{rep}.json.gz"
   if not dest.exists():
    env=dict(os.environ,KIRA_RUNTIME_BINARY=".tools/kira-runtime-db/kira",KIRA_EPHEMERAL_DB=str(enabled),KIRA_RUNTIME_SCRATCH="node")
    subprocess.run([sys.executable,str(HERE/"s02_run.py"),name,"--size","32","--policy","native","--margin","1","--timeout","160","--reference",str(ref),"--check-masters","--no-records","--output",str(dest)],env=env,check=True,timeout=210)
   r=read_record(dest);assert r["success"] and r["reference_checked"],r["status"]
   print(json.dumps(dict(database=enabled,repeat=rep,seconds=r["complete_seconds"],operations=sum(m["operations"] for m in r["metrics"]))),flush=True)
if __name__=="__main__":main()
