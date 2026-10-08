"""Small exact Kira fixtures before testing predicted seed sets."""
import hashlib,json,os,resource,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
WORK=ROOT/".tools/kira-seed-sufficiency"
def main():
 assert os.environ.get("JOB_ID"),"Use a bounded compute allocation"
 WORK.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,FERMATPATH=str(ROOT/".tools/Ferl7/fer64"),OMP_NUM_THREADS="1")
 examples={
  "sufficient":"0*(d-3)\n1*(2*m2)\n\n2*(1)\n1*(-1)\n",
  "insufficient":"2*(1)\n1*(-1)\n",
  "disjoint":"0*(d-3)\n2*(2*m2)\n\n4*(1)\n2*(-1)\n\n5*(1)\n3*(-1)\n"
 }
 results=[]
 for name,system in examples.items():
  w=WORK/("fixture_"+name);w.mkdir(exist_ok=True)
  (w/"system.kira").write_text(system+"\n")
  selected=["4","5"] if name=="disjoint" else ["2"]
  masters=["0","1"] if name=="disjoint" else ["0"]
  (w/"targets").write_text("\n".join(selected)+"\n")
  (w/"masters").write_text("\n".join(masters)+"\n")
  (w/"jobs.yaml").write_text("""jobs:
  - reduce_user_defined_system:
      input_system: {files: ["system.kira"], config: false, otf: false}
      select_integrals:
        select_mandatory_list:
          - [targets]
      preferred_masters: masters
      run_initiate: true
      run_triangular: true
      run_back_substitution: true
  - kira2file:
      target:
        - [targets]
""")
  start=time.monotonic()
  with (w/"run.log").open("wb") as log:
   proc=subprocess.run([str(ROOT/".tools/kira/bin/kira"),"--parallel=1","jobs.yaml"],cwd=str(w),env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
  outputs={str(p.relative_to(w)):p.read_text(errors="replace")[:20000] for p in w.rglob("*") if p.is_file() and (p.suffix in (".kira",".m") or p.name in ("masters","masters.final"))}
  record=dict(name=name,returncode=proc.returncode,seconds=time.monotonic()-start,files=[str(p.relative_to(w)) for p in w.rglob("*") if p.is_file()],outputs=outputs,log=(w/"run.log").read_text(errors="replace")[-10000:])
  results.append(record)
  print(json.dumps(record),flush=True)
 (HERE/"fixture_runs.json").write_text(json.dumps(results,indent=2)+"\n")
if __name__=="__main__":main()
