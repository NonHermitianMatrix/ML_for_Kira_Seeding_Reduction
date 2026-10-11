"""Sequential paired fresh-case evaluation, with all calculation costs counted."""
import argparse,subprocess,statistics
from s00_common import *
def trial(c,mode,model,out):
 start=time.perf_counter()
 p=subprocess.run([sys.executable,str(HERE/"s02_reduce.py"),"--input",str(c),"--output",str(out),"--mode",mode,"--model",model],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
 if p.returncode:
  write(out.with_suffix(".failure.json"),dict(returncode=p.returncode,log=p.stdout));raise RuntimeError(p.stdout[-4000:])
 result=json.loads(out.read_text());result["external_seconds"]=time.perf_counter()-start;write(out,result)
 print(p.stdout.strip(),flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["pilot","validation","test"]);a=ap.parse_args()
 if a.stage=="pilot":
  subprocess.run([sys.executable,str(HERE/"s01_train.py")],check=True)
  cases=sorted((HERE/"validation/inputs").glob("*r4_b12.json"))[:1]
  methods=[("previous","forest16.json"),("extreme","forest16.json"),("model","forest16.json"),("exhaustive","forest16.json")];repeats=1;stage=HERE/"validation/pilot"
 elif a.stage=="validation":
  cases=sorted((HERE/"validation/inputs").glob("*.json"))
  methods=[(m,"forest16.json") for m in ["previous","extreme","old_model","first","sum_ascending","sum_descending","exhaustive"]]+[("model",n) for n in ["forest4.json","forest16.json"]]
  repeats=3;stage=HERE/"validation/results"
 else:
  freeze=json.loads((HERE/"trained_model/freeze.json").read_text())
  for n,h in freeze["sha256"].items():assert sha(ROOT/n)==h,n
  policy=json.loads((HERE/"trained_model/deployment.json").read_text())
  cases=sorted((HERE/"model_test/inputs").glob("*.json"))
  methods=[("previous","forest16.json"),("extreme","forest16.json"),("old_model","forest16.json"),("model",policy["model"]),(policy["control"],"forest16.json"),("exhaustive","forest16.json")]
  methods=list(dict.fromkeys(methods));repeats=5;stage=HERE/"model_test/results"
 tasks=[(c,m,r) for c in cases for m in methods for r in range(repeats)]
 random.Random(61017).shuffle(tasks)
 for c,(mode,model),r in tasks:
  dest=stage/(c.stem+"_"+mode+"_"+model.replace(".json","")+"_"+str(r)+".json")
  if not dest.exists():trial(c,mode,model,dest)
 write(stage.parent/(a.stage+"_complete.json"),dict(complete=True,workflows=len(tasks)))
if __name__=="__main__":main()
