"""Fresh disjoint validation and reserved comparisons of exact pre-reduction."""
import argparse,subprocess,random,statistics
from s00_contract import *
def records(stage):return [json.loads(p.read_text()) for p in (HERE/stage/"results").glob("*.json")]
def med(rows,method,group,key="complete_seconds"):
 return statistics.median(r[key] for r in rows if r["method"]==method and r["input"]==group)
def check_freeze():
 f=json.loads((HERE/"freeze.json").read_text())
 for n,h in f["sha256"].items():assert base.sha(ROOT/n)==h,n
 for name in ["freeze.json","native_freeze.json"]:
  for n,h in json.loads((BATCH/"trained_model"/name).read_text())["sha256"].items():assert base.sha(ROOT/n)==h,n
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["prepare","pilot","validation","freeze","test"]);a=ap.parse_args()
 if a.stage=="prepare":
  # New mass ranges are disjoint from prior training, validation and tests.
  for stage,lower,upper,seed,count in [("pilot",401,497,230111,2),("validation",503,797,230113,6),("model_test",809,1297,230117,8)]:
   rng=random.Random(seed)
   for k in range(count):
    cases=[]
    for j,r in enumerate([2,3,4]):
     B=[8,11,14][k%3];n=[24,48,96][(k//3)%3] if stage!="pilot" else 24
     c=base.make_case("validation",3000+k*3+j,r,B,n);c.update(id=stage+"_"+str(k)+"_r"+str(r),mass_ratios=rng.sample(range(lower,upper),r))
     cases.append(c)
    base.write(HERE/stage/"inputs"/("group"+str(k)+".json"),dict(requests=cases))
  return
 if a.stage=="freeze":
  rows=records("validation");groups=sorted(set(r["input"] for r in rows))
  assert len(rows)==6*4*3 and all(r["success"] and r["fallbacks"]==0 for r in rows)
  ratios={m:math.exp(sum(math.log(med(rows,m,g)/med(rows,"baseline",g)) for g in groups)/len(groups)) for m in ["baseline","model","extreme","analytic"]}
  best=min(ratios,key=ratios.get)
  chosen=best if ratios[best]<.98 else "baseline"
  base.write(HERE/"deployment.json",dict(mode=chosen,validation_ratios=ratios,rule="Select the lowest validation complete time if at least two percent below baseline.",model_retrained=False))
  paths=[HERE/n for n in ["s00_contract.py","s01_application.py","s02_study.py","deployment.json"]]+list((HERE/"model_test/inputs").glob("*.json"))
  paths += [BATCH/"trained_model/freeze.json",BATCH/"trained_model/native_freeze.json"]
  base.write(HERE/"freeze.json",dict(sha256={str(p.relative_to(ROOT)):base.sha(p) for p in paths}))
  print(json.dumps(ratios),flush=True);return
 stage="model_test" if a.stage=="test" else a.stage
 if a.stage=="test":check_freeze()
 methods=["baseline","model","extreme","analytic"]
 repeats=1 if stage=="pilot" else 3 if stage=="validation" else 5
 tasks=[(p,m,r) for p in sorted((HERE/stage/"inputs").glob("*.json")) for m in methods for r in range(repeats)]
 random.Random(721241).shuffle(tasks)
 for inp,m,rep in tasks:
  out=HERE/stage/"results"/(inp.stem+"_"+m+"_"+str(rep)+".json")
  if out.exists():continue
  start=time.perf_counter()
  p=subprocess.run([sys.executable,str(HERE/"s01_application.py"),"--input",str(inp),"--output",str(out),"--mode",m],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
  if p.returncode:raise RuntimeError(p.stdout[-5000:])
  result=json.loads(out.read_text());result.update(external_seconds=time.perf_counter()-start,input=str(inp.relative_to(HERE)))
  base.write(out,result);guard();print(p.stdout.strip(),flush=True)
 base.write(HERE/stage/"complete.json",dict(complete=True,applications=len(tasks)))
if __name__=="__main__":main()
