"""Fresh validation and reserved tests for the compiled coefficient reader."""
import argparse,subprocess
import s14_reader
from s02_engine import *
from s05_study import ratios,key,check_freeze as first_freeze

def prepare():
 for stage,count,seed,lo in [("reader_final_test",12,1144703,600011)]:
  rng=random.Random(seed)
  for k in range(count):
   cases=[]
   for j,R in enumerate([2,3,4]):
    B=[4,8,11,14][k%4];n=[8,32,96][(k//4)%3]
    c=base.make_case("training",62000+{"training":0,"reader_validation":1000,"reader_final_test":3000}[stage]+3*k+j,R,B,n)
    # Disjoint ranges and varied spacing change rational coefficient sizes.
    offset=lo+1000*k+31*j
    pattern=k%3
    if pattern==0:rho=[offset+v for v in rng.sample(range(1,23),R)]
    elif pattern==1:rho=[offset+v for v in rng.sample(range(1,501),R)]
    else:rho=[(offset+v)*(10**j) for j,v in enumerate(rng.sample(range(1,29),R))]
    c.update(id=stage+"_"+str(k)+"_r"+str(R),mass_ratios=rho,loops=list(range(1,13)))
    cases.append(c)
   write(HERE/stage/"inputs"/("group"+str(k).zfill(3)+".json"),dict(requests=cases))
 write(HERE/"reader_final_protocol.json",dict(training_batches_reused=96,validation_batches=12,test_batches=12,policies=POLICIES,model="multi-output depth-four regression tree for log complete warm-worker runtime",training_repetitions=3,validation_repetitions=3,test_repetitions=5,validation_rule="Select fastest complete-time variant only if at least two percent faster than baseline; preserve simple policy unless learned route beats the best fixed policy by two percent. Freeze before reserved test.",family="coupled_vacuum_unit_massless",loops=list(range(1,13)),max_total_massive_power=14))

def arms(stage):
 out=[(m,None) for m in MODES]
 if stage=="reader_validation":out += [("native_binary",p) for p in POLICIES if p!="extreme"]
 else:
  p=read(HERE/"reader_final_deployment.json")["best_fixed_policy"]
  if p!="extreme":out.append(("native_binary",p))
 return out

def trials(stage):
 if stage=="reader_final_test":check_freeze()
 repeats=3 if stage=="reader_validation" else 5
 tasks=[(p,m,policy,k) for p in sorted((HERE/stage/"inputs").glob("*.json")) for m,policy in arms(stage) for k in range(repeats)]
 random.Random(815711 if stage=="reader_validation" else 815719).shuffle(tasks)
 for inp,mode,policy,k in tasks:
  dest=HERE/stage/"results"/(inp.stem+"_"+key(mode,policy)+"_"+str(k)+".json")
  if dest.exists() and "external_seconds" in read(dest):continue
  command=[sys.executable,str(HERE/"s15_application.py"),"--input",str(inp),"--output",str(dest),"--mode",mode]
  if policy:command+=["--policy",policy]
  t=time.perf_counter();p=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180);elapsed=time.perf_counter()-t
  assert p.returncode==0,(command,p.stderr[-3000:]);r=read(dest);assert r["success"] and r["fallbacks"]==0
  # Include decoding so compact output cannot hide work needed by consumers.
  t=time.perf_counter();coeff=load_coeff(r);readtime=time.perf_counter()-t
  canonical=hashlib.sha256(json.dumps(coeff,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  r.update(input=str(inp.relative_to(HERE)),arm=key(mode,policy),repetition=k,external_seconds=elapsed,read_seconds=readtime,roundtrip_seconds=elapsed+readtime,canonical_coefficients_sha256=canonical)
  write(dest,r);print(stage,inp.stem,r["arm"],round(elapsed,5),flush=True)
 write(HERE/stage/"complete.json",dict(complete=True,applications=len(tasks)))

def freeze():
 rows=[read(p) for p in (HERE/"reader_validation/results").glob("*.json")];assert len(rows)==324;assert all(r["input"].startswith("reader_validation/") for r in rows)
 rr=ratios(rows,"roundtrip_seconds")
 fixed=["native_binary"]+["native_binary_"+p for p in POLICIES if p!="extreme"];best_fixed=min(fixed,key=rr.get);p="extreme" if best_fixed=="native_binary" else best_fixed[len("native_binary_"):]
 best_simple=min((arm for arm in rr if arm!="learned"),key=rr.get)
 selected="learned" if rr["learned"]<.98*rr[best_simple] else best_simple
 if selected.startswith("native_binary_"):mode="native_binary";policy=selected[len("native_binary_"):]
 else:mode=selected;policy=None
 value=rr[selected]
 if value>=.98:mode="baseline";policy=None
 write(HERE/"reader_final_deployment.json",dict(mode=mode,policy=policy,best_fixed_policy=p,validation_ratios=rr,selection_metric="complete process time plus output decoding",learned_beats_best_fixed_by_two_percent=rr["learned"]<.98*rr[best_fixed]))
 files=[HERE/n for n in ["s13_reader.cpp","s14_reader.py","s15_application.py","s16_reader_study.py","build/reader.so","build/reader_build.json","reader_final_deployment.json","reader_final_protocol.json","freeze.json"]]
 files+=list((HERE/"reader_validation/inputs").glob("*.json"))+list((HERE/"reader_validation/results").glob("*.json"))+list((HERE/"reader_final_test/inputs").glob("*.json"))
 write(HERE/"reader_final_freeze.json",dict(sha256={str(f.relative_to(ROOT)):sha(f) for f in files}))
 print("frozen",mode,policy,rr,flush=True)

def streams():
 check_freeze();files=sorted((HERE/"reader_final_test/inputs").glob("*.json"));dep=read(HERE/"reader_final_deployment.json")
 configs=[("baseline","baseline",None),("native","native_binary",None),("learned","learned",None),("deployed",dep["mode"],dep["policy"])]
 # Three disjoint four-batch streams.
 tasks=[(i,label,m,p,k) for i in range(3) for label,m,p in configs for k in range(3)];random.Random(552931).shuffle(tasks)
 for seq,label,mode,policy,k in tasks:
  dest=HERE/"reader_final_test/streams"/("seq"+str(seq)+"_"+label+"_"+str(k)+".json")
  if dest.exists():continue
  commands=[]
  for j,inp in enumerate(files[seq*4:seq*4+4]):
   out=HERE/"reader_final_test/stream_results"/(dest.stem+"_part"+str(j)+".json");commands.append(dict(input=str(inp),output=str(out)))
  command=[sys.executable,str(HERE/"s15_application.py"),"--stream","--mode",mode]
  if policy:command+=["--policy",policy]
  t=time.perf_counter();p=subprocess.run(command,input="".join(json.dumps(x)+"\n" for x in commands),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300);elapsed=time.perf_counter()-t
  assert p.returncode==0,p.stderr[-3000:];responses=[json.loads(x) for x in p.stdout.splitlines()];assert len(responses)==4 and all(x["ok"] and x["fallbacks"]==0 for x in responses)
  rr=[read(x["output"]) for x in commands];assert len({r["worker_pid"] for r in rr})==1
  t=time.perf_counter();decoded=[load_coeff(r) for r in rr];readtime=time.perf_counter()-t
  write(dest,dict(success=True,sequence=seq,arm=label,mode=mode,policy=policy,repetition=k,external_seconds=elapsed,read_seconds=readtime,roundtrip_seconds=elapsed+readtime,records=[str(Path(x["output"]).relative_to(HERE)) for x in commands],canonical_coefficients_sha256=[hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest() for x in decoded]))
  print("stream",seq,label,round(elapsed,4),flush=True)
 write(HERE/"reader_final_test/streams_complete.json",dict(complete=True,stream_runs=36,applications=144))

def check_freeze():
 first_freeze()
 for n,h in read(HERE/"reader_final_freeze.json")["sha256"].items():assert sha(ROOT/n)==h,n
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["prepare","validation","freeze","test","streams"]);a=ap.parse_args()
 if a.stage=="validation":trials("reader_validation")
 elif a.stage=="test":trials("reader_final_test")
 else:globals()[a.stage]()
if __name__=="__main__":main()
