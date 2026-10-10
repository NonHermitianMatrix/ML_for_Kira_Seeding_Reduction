"""Compare the eight supported integral orderings on validation cases."""
import json,os,pathlib,subprocess,sys,time
from s03_records import read_record
from s14_runtime_config import configuration
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 config=configuration();manifest=json.loads((HERE/"families.json").read_text())
 cases=[c for c in manifest["cases"] if c["split"]=="validation"]
 out=HERE/"ordering_validation";out.mkdir(exist_ok=True)
 for case_no,case in enumerate(cases):
  size=min(32,len(case["targets"]));name=case["id"]
  ref=ROOT/"Kira_comparison/multiloop_native/references"/f"{name}_n{size}.json.gz"
  if not ref.exists():ref=HERE/"references"/f"{name}_n{size}.json.gz"
  assert read_record(ref)["success"]
  ordering=list(range(1,9));ordering=ordering[case_no%8:]+ordering[:case_no%8]
  for order in ordering:
   path=out/f"{name}_o{order}_r0.json.gz"
   if not path.exists():
    env=dict(os.environ,KIRA_RUNTIME_SCRATCH=config["scratch_location"],KIRA_RUNTIME_BINARY=".tools/kira-integrated-runtime/kira")
    subprocess.run([sys.executable,str(HERE/"s02_run.py"),name,"--size",str(size),"--policy","native","--margin","1","--timeout","150","--reference",str(ref),"--check-masters","--ordering",str(order),"--output",str(path)],env=env,cwd=ROOT,check=True,timeout=210)
   r=read_record(path);assert not r.get("mismatches"),path
   print(json.dumps({k:r.get(k) for k in ["case","integral_ordering","success","status","complete_seconds","metrics","stage_metrics"]}),flush=True)
if __name__=="__main__":main()
