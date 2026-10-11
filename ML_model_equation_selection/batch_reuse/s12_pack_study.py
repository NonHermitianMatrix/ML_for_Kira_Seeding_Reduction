"""Paired packed/separate applications, preserving identical targets and checks."""
import argparse,subprocess
from s00_common import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["validation","test"]);a=ap.parse_args()
 stage=HERE/("validation" if a.stage=="validation" else "model_test")
 cases=sorted((stage/"inputs").glob("*.json"),key=lambda p:int(p.stem.split("_")[1]))
 if a.stage=="validation":
  groups=[cases[i:i+3] for i in range(0,12,3)];repeats=3
  p=json.loads((HERE/"trained_model/deployment.json").read_text());model=p["model"];control=p["control"]
 else:
  freeze=json.loads((HERE/"trained_model/freeze.json").read_text())
  for n,h in freeze["sha256"].items():assert sha(ROOT/n)==h,n
  groups=[cases[i:i+3] for i in range(0,12,3)];repeats=5;p=json.loads((HERE/"trained_model/deployment.json").read_text());model=p["model"];control=p["control"]
 tasks=[]
 for g,group in enumerate(groups):
  inp=stage/"packs"/("group"+str(g)+".json");write(inp,dict(requests=[json.loads(c.read_text()) for c in group]))
  for mode in ["model",control]:
   for packed in [True,False]:
    for rep in range(repeats):tasks.append((inp,mode,packed,rep))
 random.Random(112039).shuffle(tasks)
 for inp,mode,packed,rep in tasks:
  dest=stage/"pack_results"/(inp.stem+"_"+mode+"_"+str(int(packed))+"_"+str(rep)+".json")
  if dest.exists():continue
  command=[sys.executable,str(HERE/"s11_pack.py"),"--input",str(inp),"--output",str(dest),"--mode",mode,"--model",model]
  if not packed:command.append("--separate")
  begin=time.perf_counter();proc=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
  if proc.returncode:raise RuntimeError(proc.stdout[-5000:])
  result=json.loads(dest.read_text());result.update(external_seconds=time.perf_counter()-begin,input=str(inp.relative_to(HERE)));write(dest,result)
  print(proc.stdout.strip(),flush=True)
 write(stage/"pack_complete.json",dict(complete=True,workflows=len(tasks)))
if __name__=="__main__":main()
