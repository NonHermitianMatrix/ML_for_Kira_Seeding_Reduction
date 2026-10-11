"""Fresh validation and reserved single-request and stream comparisons."""
import argparse,subprocess,random,statistics
from s00_arithmetic import *
def read_rows(stage):return [json.loads(p.read_text()) for p in (HERE/stage/"results").glob("*.json")]
def median(rows,group,variant,key="complete_seconds"):
 return statistics.median(r[key] for r in rows if r["input"]==group and r["variant"]==variant)
def check_freeze():
 for filename in [HERE/"freeze.json",PRE/"freeze.json",prior.BATCH/"trained_model/freeze.json",prior.BATCH/"trained_model/native_freeze.json"]:
  for n,h in json.loads(filename.read_text())["sha256"].items():assert base.sha(ROOT/n)==h,n
def prepare():
 for stage,lower,upper,count,seed in [("validation",2003,3001,4,193711),("model_test",4001,6007,8,193713)]:
  rng=random.Random(seed)
  for k in range(count):
   cases=[]
   for j,r in enumerate([2,3,4]):
    B=([8,14][k%2] if stage=="validation" else [8,11,14][k%3]);n=([16,48][k//2] if stage=="validation" else [16,48,96][k//3])
    c=base.make_case("validation",12000+3*k+j,r,B,n)
    c.update(id=stage+"_"+str(k)+"_r"+str(r),mass_ratios=rng.sample(range(lower,upper),r))
    cases.append(c)
   base.write(HERE/stage/"inputs"/("group"+str(k)+".json"),dict(requests=cases))
def freeze():
 rows=read_rows("validation");assert len(rows)==48 and all(r["success"] and r["fallbacks"]==0 for r in rows)
 groups=sorted({r["input"] for r in rows});ratios={}
 for v in ["baseline","transforms","taylor","both"]:
  ratios[v]=math.exp(sum(math.log(median(rows,g,v)/median(rows,g,"baseline")) for g in groups)/len(groups))
 best=min(ratios,key=ratios.get);chosen=best if ratios[best]<.98 else "baseline"
 base.write(HERE/"deployment.json",dict(variant=chosen,policy="extreme",validation_ratios=ratios,model_retrained=False,rule="Use the fastest validation arithmetic variant if complete time improves by at least two percent. Preserve the preceding ordering policy."))
 files=[HERE/n for n in ["s00_arithmetic.py","s01_engine.py","s02_application.py","s03_check.py","s04_study.py","deployment.json"]]
 files+=list((HERE/"model_test/inputs").glob("*.json"))
 files += [PRE/"freeze.json",prior.BATCH/"trained_model/freeze.json",prior.BATCH/"trained_model/native_freeze.json"]
 base.write(HERE/"freeze.json",dict(sha256={str(p.relative_to(ROOT)):base.sha(p) for p in files}))
 print("frozen policy",chosen,ratios,flush=True)
def trials(stage):
 if stage=="model_test":check_freeze()
 variants=["baseline","transforms","taylor","both"];repeats=3 if stage=="validation" else 5
 tasks=[(p,v,r) for p in sorted((HERE/stage/"inputs").glob("*.json")) for v in variants for r in range(repeats)]
 random.Random(53911).shuffle(tasks)
 for inp,v,rep in tasks:
  dest=HERE/stage/"results"/(inp.stem+"_"+v+"_"+str(rep)+".json")
  if dest.exists() and "external_seconds" in json.loads(dest.read_text()):continue
  if dest.exists():
   archive=HERE/stage/"interrupted";archive.mkdir(exist_ok=True);dest.rename(archive/dest.name)
  start=time.perf_counter()
  p=subprocess.run([sys.executable,str(HERE/"s02_application.py"),"--input",str(inp),"--output",str(dest),"--variant",v],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
  if p.returncode:raise RuntimeError(p.stdout[-4000:])
  x=json.loads(dest.read_text());x.update(external_seconds=time.perf_counter()-start,input=str(inp.relative_to(HERE)),repetition=rep);base.write(dest,x)
  print(stage,inp.stem,v,round(x["complete_seconds"],6),flush=True)
 base.write(HERE/stage/"complete.json",dict(complete=True,applications=len(tasks)))
def streams():
 check_freeze();selected=json.loads((HERE/"deployment.json").read_text())["variant"]
 groups=sorted((HERE/"model_test/inputs").glob("*.json"))
 orders=[list(range(4)),list(range(4,8)),[0,2,4,6,1,3,5,7]]
 tasks=[(i,mode,rep) for i in range(3) for mode in ["baseline_cold","baseline_stream","optimized_cold","optimized_stream"] for rep in range(3)]
 random.Random(63311).shuffle(tasks)
 for k,mode,rep in tasks:
  dest=HERE/"model_test/streams"/("sequence"+str(k)+"_"+mode+"_"+str(rep)+".json")
  if dest.exists():continue
  variant=selected if mode.startswith("optimized") else "baseline";records=[];commands=[];start=time.perf_counter()
  for index,j in enumerate(orders[k]):
   output=HERE/"model_test/stream_results"/(dest.stem+"_part"+str(index)+".json")
   records.append(str(output.relative_to(HERE)));commands.append(dict(input=str(groups[j]),output=str(output)))
  if mode.endswith("_stream"):
   p=subprocess.run([sys.executable,str(HERE/"s02_application.py"),"--stream","--variant",variant],input="".join(json.dumps(c)+"\n" for c in commands),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300)
   assert p.returncode==0,p.stderr
   answers=[json.loads(s) for s in p.stdout.splitlines()];assert len(answers)==len(commands) and all(x["ok"] for x in answers)
  else:
   for c in commands:
    p=subprocess.run([sys.executable,str(HERE/"s02_application.py"),"--variant",variant,"--input",c["input"],"--output",c["output"]],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    assert p.returncode==0,p.stderr;assert json.loads(p.stdout)["ok"]
  seconds=time.perf_counter()-start
  rows=[json.loads((HERE/n).read_text()) for n in records]
  assert all(r["success"] and r["fallbacks"]==0 for r in rows)
  expected=[json.loads((HERE/"model_test/results"/(groups[j].stem+"_baseline_0.json")).read_text())["coefficients_sha256"] for j in orders[k]]
  assert [r["coefficients_sha256"] for r in rows]==expected
  pids={r["worker_pid"] for r in rows}
  assert len(pids)==(1 if mode.endswith("_stream") else len(rows))
  base.write(dest,dict(success=True,mode=mode,variant=variant,sequence=k,repetition=rep,external_seconds=seconds,complete_seconds=sum(r["complete_seconds"] for r in rows),requests=len(rows),records=records,worker_processes=len(pids),coefficients_match_cold_baseline=True))
  print("stream",mode,k,round(seconds,6),flush=True)
 base.write(HERE/"model_test/streams_complete.json",dict(complete=True,streams=len(tasks),request_applications=192))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["prepare","validation","freeze","test","streams"]);a=ap.parse_args()
 if a.stage=="prepare":prepare()
 elif a.stage=="freeze":freeze()
 elif a.stage=="streams":streams()
 else:trials("model_test" if a.stage=="test" else "validation")
if __name__=="__main__":main()
