"""Measure project and node scratch with exact, matched native reductions."""
import json,os,pathlib,socket,subprocess,sys
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 assert os.environ.get("TMPDIR") and os.environ.get("JOB_ID")
 out=HERE/"scratch_pilot";out.mkdir(exist_ok=True)
 info=dict(host=socket.gethostname(),tmpdir=os.environ["TMPDIR"],filesystem=subprocess.check_output(["df","-T",os.environ["TMPDIR"]],text=True))
 (out/"environment.json").write_text(json.dumps(info,indent=2)+"\n")
 case="validation_01_double_box"
 for repeat in range(2):
  for margin in [0,1]:
   order=["project","node"] if (repeat+margin)%2==0 else ["node","project"]
   for location in order:
    path=out/f"m{margin}_{location}_r{repeat}.json.gz"
    if not path.exists():
     env=dict(os.environ,KIRA_RUNTIME_SCRATCH=location,KIRA_RUNTIME_BINARY=".tools/kira-integrated-runtime/kira")
     subprocess.run([sys.executable,str(HERE/"s02_run.py"),case,"--size","128","--policy","native","--margin",str(margin),"--timeout","120","--reference",str(ROOT/"Kira_comparison/multiloop_native/references/validation_01_double_box_n128.json.gz"),"--check-masters","--output",str(path)],env=env,cwd=ROOT,check=True,timeout=170)
    r=read_record(path);assert r["success"] and not r.get("mismatches"),path
    print(json.dumps({k:r.get(k) for k in ["margin","scratch_location","complete_seconds","stage_metrics","metrics"]}),flush=True)
if __name__=="__main__":main()
