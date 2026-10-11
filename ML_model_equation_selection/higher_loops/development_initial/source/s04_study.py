"""Run predeclared comparisons in sequential bounded worker processes."""
import argparse,hashlib,random,subprocess,sys,time
from s00_math import *
def trial(c,mode,model,shared,out):
 command=[sys.executable,str(HERE/"s02_reduce.py"),"--input",str(c),"--output",str(out),"--mode",mode]
 if model:command+=["--model",model]
 if not shared:command+=["--separate-loops"]
 start=time.perf_counter();p=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1200)
 text=p.stdout
 if p.returncode:
  write(out.with_suffix(".failure.json"),dict(command=command,returncode=p.returncode,log=text,external_seconds=time.perf_counter()-start))
  raise RuntimeError(text[-5000:])
 result=json.loads(out.read_text());result["external_seconds"]=time.perf_counter()-start;write(out,result)
 print(json.dumps(dict(case=result["case"],mode=mode,model=model,shared=shared,seconds=result["external_seconds"],success=True)),flush=True)
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["pilot","validation","test"]);args=ap.parse_args()
 if args.stage=="pilot":
  subprocess.run([sys.executable,str(HERE/"s01_train.py")],check=True)
  subprocess.run([sys.executable,str(HERE/"s03_cases.py")],check=True)
  cases=[HERE/"validation/inputs/validation_r3_b6.json"]
  methods=[("dense",None,True),("learned","depth8.json",True),("smallest",None,True)]
  repeats=1;out=HERE/"validation/pilot"
 elif args.stage=="validation":
  cases=sorted((HERE/"validation/inputs").glob("*.json"))
  methods=[(m,None,True) for m in ["dense","first","smallest","largest","extreme"]]+[("learned","depth%d.json"%d,True) for d in [4,8,12]]
  repeats=3;out=HERE/"validation/results"
 else:
  freeze=json.loads((HERE/"trained_model/freeze.json").read_text())
  for n,h in freeze["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
  policy=json.loads((HERE/"trained_model/deployment.json").read_text())
  cases=sorted((HERE/"model_test/inputs").glob("*.json"))
  methods=[("dense",None,False),("dense",None,True),(policy["control"],None,True),("learned",policy["model"],True),("learned",policy["model"],False)]
  repeats=3;out=HERE/"model_test/results"
 out.mkdir(parents=True,exist_ok=True)
 tasks=[(c,m,rep) for c in cases for rep in range(repeats) for m in methods]
 random.Random(33071).shuffle(tasks)
 for c,(mode,model,shared),rep in tasks:
  name=c.stem+"_"+mode+"_"+(model or "none").replace(".json","")+"_"+str(int(shared))+"_"+str(rep)+".json"
  dest=out/name
  if dest.exists():continue
  trial(c,mode,model,shared,dest)
 write(out.parent/(args.stage+"_complete.json"),dict(stage=args.stage,workflows=len(tasks),completed=True))
if __name__=="__main__":main()
