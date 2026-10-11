"""Fresh native-inference validation followed by frozen independent confirmation."""
import argparse,subprocess,statistics
from s00_common import *
def records(stage):return [json.loads(p.read_text()) for p in (HERE/stage/"native_results").glob("*.json") if "_part" not in p.name]
def med(rows,backend,group):
 return statistics.median(r["complete_seconds"] for r in rows if r["backend"]==backend and r["input"]==group and r["packed"])
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["prepare","validation","freeze","test"]);a=ap.parse_args()
 policy=json.loads((HERE/"trained_model/deployment.json").read_text());model=policy["model"]
 if a.stage=="prepare":
  known={tuple(sorted(json.loads(p.read_text())["mass_ratios"])) for stage in ["validation","model_test"] for p in (HERE/stage/"inputs").glob("*.json")}
  for stage,s in [("validation","validation"),("test","model_test")]:
   cases=[make_case(stage,1000+k,[2,3,4][k%3],[9,13][(k//3)%2],[32,80][(k//6)%2]) for k in range(12)]
   assert all(tuple(sorted(c["mass_ratios"])) not in known for c in cases)
   for i in range(4):write(HERE/s/"native_inputs"/("group"+str(i)+".json"),dict(requests=cases[3*i:3*i+3]))
  return
 if a.stage=="freeze":
  rows=records("validation");assert len(rows)==36 and all(r["success"] and r["fallbacks"]==0 for r in rows)
  groups=sorted(set(r["input"] for r in rows))
  ratios={b:math.exp(sum(math.log(med(rows,b,g)/med(rows,"control",g)) for g in groups)/len(groups)) for b in ["python","native","control"]}
  best=min(["python","native"],key=lambda b:ratios[b]);chosen=best if ratios[best]<.98 else "control"
  write(HERE/"trained_model/native_deployment.json",dict(backend=chosen,model=model,control=policy["control"],validation_ratios=ratios,rule="Use the fastest validated learned backend if complete time is at least 2 percent lower than the simple control."))
  paths=[HERE/n for n in ["s16_native.py","s17_application.py","s18_native_study.py","trained_model/native_deployment.json"]]+list((HERE/"trained_model").glob("*.so"))+list((HERE/"trained_model").glob("*.c"))+list((HERE/"model_test/native_inputs").glob("*.json"))
  write(HERE/"trained_model/native_freeze.json",dict(sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},base_freeze_sha256=sha(HERE/"trained_model/freeze.json")))
  print(json.dumps(ratios),flush=True);return
 stage="validation" if a.stage=="validation" else "model_test"
 if a.stage=="test":
  freeze=json.loads((HERE/"trained_model/native_freeze.json").read_text())
  assert freeze["base_freeze_sha256"]==sha(HERE/"trained_model/freeze.json")
  for n,h in freeze["sha256"].items():assert sha(ROOT/n)==h
  for n,h in json.loads((HERE/"trained_model/freeze.json").read_text())["sha256"].items():assert sha(ROOT/n)==h
 tasks=[(p,b,rep) for p in (HERE/stage/"native_inputs").glob("*.json") for b in (["python","native","control"] if stage=="validation" else ["python","native","control","previous"]) for rep in range(3 if stage=="validation" else 5)]
 random.Random(79261).shuffle(tasks)
 for inp,backend,rep in tasks:
  dest=HERE/stage/"native_results"/(inp.stem+"_"+backend+"_"+str(rep)+".json")
  if dest.exists():continue
  begin=time.perf_counter();p=subprocess.run([sys.executable,str(HERE/"s17_application.py"),"--input",str(inp),"--output",str(dest),"--backend",backend,"--model",model],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
  if p.returncode:raise RuntimeError(p.stdout[-5000:])
  x=json.loads(dest.read_text());x.update(external_seconds=time.perf_counter()-begin,input=str(inp.relative_to(HERE)));write(dest,x);print(p.stdout.strip(),flush=True)
 write(HERE/stage/"native_complete.json",dict(complete=True,workflows=len(tasks)))
if __name__=="__main__":main()
