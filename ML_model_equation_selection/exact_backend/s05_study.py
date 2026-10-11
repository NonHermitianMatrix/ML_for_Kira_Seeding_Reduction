"""Collect complete runtime labels, validate policies, then freeze independent tests."""
import argparse,subprocess,tempfile,shutil,itertools
from s02_engine import *
def prepare():
 for stage,count,seed,lo in [("training",96,712791,100003),("validation",12,712793,300007),("model_test",12,712799,700001)]:
  rng=random.Random(seed)
  for k in range(count):
   cases=[]
   for j,R in enumerate([2,3,4]):
    B=[4,8,11,14][k%4];n=[8,32,96][(k//4)%3]
    c=base.make_case("training",52000+{"training":0,"validation":1000,"model_test":2000}[stage]+3*k+j,R,B,n)
    # Disjoint ranges and varied spacing change rational coefficient sizes.
    offset=lo+1000*k+31*j
    pattern=k%3
    if pattern==0:rho=[offset+v for v in rng.sample(range(1,23),R)]
    elif pattern==1:rho=[offset+v for v in rng.sample(range(1,501),R)]
    else:rho=[(offset+v)*(10**j) for j,v in enumerate(rng.sample(range(1,29),R))]
    c.update(id=stage+"_"+str(k)+"_r"+str(R),mass_ratios=rho,loops=list(range(1,13)))
    cases.append(c)
   write(HERE/stage/"inputs"/("group"+str(k).zfill(3)+".json"),dict(requests=cases))
 write(HERE/"protocol.json",dict(training_batches=96,validation_batches=12,test_batches=12,policies=POLICIES,model="multi-output depth-four regression tree for log complete warm-worker runtime",training_repetitions=3,validation_repetitions=3,test_repetitions=5,validation_rule="Select fastest complete-time variant only if at least two percent faster than baseline; preserve simple policy unless learned route beats the best fixed policy by two percent. Freeze before reserved test.",family="coupled_vacuum_unit_massless",loops=list(range(1,13)),max_total_massive_power=14))
def labels():
 root=Path(os.environ["TMPDIR"])/("kira-exact-labels-"+str(os.getpid()));root.mkdir();rows=[];state={}
 try:
  for inp in sorted((HERE/"training/inputs").glob("*.json")):
   dest=HERE/"training/results"/(inp.stem+".json")
   if dest.exists():continue
   tasks=[(p,k) for p in POLICIES for k in range(3)];random.Random(81193+int(inp.stem[5:])).shuffle(tasks);rec=[];coefficient_hash=None
   for policy,k in tasks:
    t=time.perf_counter();requests=read(inp)["requests"];r=apply(requests,"native_binary",state,forced_policy=policy);assert r["success"] and r["fallbacks"]==0
    saved=save(root/"result.json",r,root/"objects");elapsed=time.perf_counter()-t
    if coefficient_hash is None:coefficient_hash=saved["coefficients_sha256"]
    assert coefficient_hash==saved["coefficients_sha256"]
    rec.append(dict(policy=policy,repetition=k,total_seconds=elapsed,calculation_seconds=r["complete_seconds"],saving_seconds=saved["saving_seconds"],equations=r["equations"],coefficient_hash=coefficient_hash))
   write(dest,dict(input=str(inp.relative_to(HERE)),input_sha256=sha(inp),measurements=rec,all_exact=True))
   shutil.rmtree(root/"objects");print("labels",inp.stem,flush=True);guard()
 finally:shutil.rmtree(root)
def train():
 from sklearn.tree import DecisionTreeRegressor
 import numpy as np
 xs=[];ys=[];records=sorted((HERE/"training/results").glob("*.json"));assert len(records)==96
 for p in records:
  r=read(p);xs.append(features(read(HERE/r["input"])["requests"]));ys.append([math.log(statistics.median(x["total_seconds"] for x in r["measurements"] if x["policy"]==policy)) for policy in POLICIES])
 model=DecisionTreeRegressor(max_depth=4,min_samples_leaf=6,random_state=731119);model.fit(np.array(xs,dtype=np.float64),np.array(ys));t=model.tree_
 nodes=[[int(t.feature[i]),float(t.threshold[i]),int(t.children_left[i]),int(t.children_right[i]),[float(x) for x in t.value[i,:,0]]] for i in range(t.node_count)]
 write(HERE/"trained_model/cost_tree.json",dict(policies=POLICIES,nodes=nodes,feature_count=len(xs[0]),target="log seconds including exact arithmetic, checks and output writing in a warm worker",training_batches=96))
 checks=0
 for x,expected in zip(xs,model.predict(np.array(xs))):
  i=0
  while nodes[i][0]>=0:
   f,threshold,l,r,_=nodes[i];i=l if x[f]<=threshold else r
  assert all(a==b for a,b in zip(nodes[i][4],expected));checks+=len(expected)
 write(HERE/"training/model_check.json",dict(all_passed=True,score_checks=checks,node_count=t.node_count,training_batches=96,training_measurements=1440))
 print("trained",t.node_count,"nodes",flush=True)
def arms(stage):
 out=[(m,None) for m in MODES]
 if stage=="validation":out += [("native_binary",p) for p in POLICIES if p!="extreme"]
 else:
  p=read(HERE/"deployment.json")["best_fixed_policy"]
  if p!="extreme":out.append(("native_binary",p))
 return out
def key(mode,policy):return mode if not policy else mode+"_"+policy
def trials(stage):
 if stage=="model_test":check_freeze()
 repeats=3 if stage=="validation" else 5
 tasks=[(p,m,policy,k) for p in sorted((HERE/stage/"inputs").glob("*.json")) for m,policy in arms(stage) for k in range(repeats)]
 random.Random(815711 if stage=="validation" else 815719).shuffle(tasks)
 for inp,mode,policy,k in tasks:
  dest=HERE/stage/"results"/(inp.stem+"_"+key(mode,policy)+"_"+str(k)+".json")
  if dest.exists() and "external_seconds" in read(dest):continue
  command=[sys.executable,str(HERE/"s03_application.py"),"--input",str(inp),"--output",str(dest),"--mode",mode]
  if policy:command+=["--policy",policy]
  t=time.perf_counter();p=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180);elapsed=time.perf_counter()-t
  assert p.returncode==0,(command,p.stderr[-3000:]);r=read(dest);assert r["success"] and r["fallbacks"]==0
  # Include decoding so compact output cannot hide work needed by consumers.
  t=time.perf_counter();coeff=load_coeff(r);readtime=time.perf_counter()-t
  canonical=hashlib.sha256(json.dumps(coeff,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  r.update(input=str(inp.relative_to(HERE)),arm=key(mode,policy),repetition=k,external_seconds=elapsed,read_seconds=readtime,roundtrip_seconds=elapsed+readtime,canonical_coefficients_sha256=canonical)
  write(dest,r);print(stage,inp.stem,r["arm"],round(elapsed,5),flush=True)
 write(HERE/stage/"complete.json",dict(complete=True,applications=len(tasks)))
def ratios(rows,metric):
 groups=sorted({r["input"] for r in rows});aa=sorted({r["arm"] for r in rows});out={}
 for arm in aa:
  values=[]
  for g in groups:
   x=statistics.median(r[metric] for r in rows if r["input"]==g and r["arm"]==arm)
   b=statistics.median(r[metric] for r in rows if r["input"]==g and r["arm"]=="baseline");values.append(x/b)
  out[arm]=math.exp(sum(map(math.log,values))/len(values))
 return out
def freeze():
 rows=[read(p) for p in (HERE/"validation/results").glob("*.json")];assert len(rows)==324
 rr=ratios(rows,"roundtrip_seconds")
 fixed=["native_binary"]+["native_binary_"+p for p in POLICIES if p!="extreme"];best_fixed=min(fixed,key=rr.get);p="extreme" if best_fixed=="native_binary" else best_fixed[len("native_binary_"):]
 best_simple=min((arm for arm in rr if arm!="learned"),key=rr.get)
 selected="learned" if rr["learned"]<.98*rr[best_simple] else best_simple
 if selected.startswith("native_binary_"):mode="native_binary";policy=selected[len("native_binary_"):]
 else:mode=selected;policy=None
 value=rr[selected]
 if value>=.98:mode="baseline";policy=None
 write(HERE/"deployment.json",dict(mode=mode,policy=policy,best_fixed_policy=p,validation_ratios=rr,selection_metric="complete process time plus output decoding",learned_beats_best_fixed_by_two_percent=rr["learned"]<.98*rr[best_fixed]))
 files=[HERE/n for n in ["s00_backend.py","s01_transform.cpp","s02_engine.py","s03_application.py","s04_check.py","s05_study.py","build/transform.so","build/build.json","trained_model/cost_tree.json","deployment.json","protocol.json","training/model_check.json"]]
 for stage in ["training","validation"]:
  files+=list((HERE/stage/"inputs").glob("*.json"))+list((HERE/stage/"results").glob("*.json"))
 files+=list((HERE/"model_test/inputs").glob("*.json"))+[POLY/"freeze.json"]
 write(HERE/"freeze.json",dict(sha256={str(f.relative_to(ROOT)):sha(f) for f in files}))
 print("frozen",mode,policy,rr,flush=True)
def check_freeze():
 for file in [HERE/"freeze.json",POLY/"freeze.json",old.PRE/"freeze.json",prior.BATCH/"trained_model/freeze.json",prior.BATCH/"trained_model/native_freeze.json"]:
  for n,h in read(file)["sha256"].items():assert sha(ROOT/n)==h,n
def streams():
 check_freeze();files=sorted((HERE/"model_test/inputs").glob("*.json"));dep=read(HERE/"deployment.json")
 configs=[("baseline","baseline",None),("native","native_binary",None),("learned","learned",None),("deployed",dep["mode"],dep["policy"])]
 # Three disjoint four-batch streams.
 tasks=[(i,label,m,p,k) for i in range(3) for label,m,p in configs for k in range(3)];random.Random(552931).shuffle(tasks)
 for seq,label,mode,policy,k in tasks:
  dest=HERE/"model_test/streams"/("seq"+str(seq)+"_"+label+"_"+str(k)+".json")
  if dest.exists():continue
  commands=[]
  for j,inp in enumerate(files[seq*4:seq*4+4]):
   out=HERE/"model_test/stream_results"/(dest.stem+"_part"+str(j)+".json");commands.append(dict(input=str(inp),output=str(out)))
  command=[sys.executable,str(HERE/"s03_application.py"),"--stream","--mode",mode]
  if policy:command+=["--policy",policy]
  t=time.perf_counter();p=subprocess.run(command,input="".join(json.dumps(x)+"\n" for x in commands),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300);elapsed=time.perf_counter()-t
  assert p.returncode==0,p.stderr[-3000:];responses=[json.loads(x) for x in p.stdout.splitlines()];assert len(responses)==4 and all(x["ok"] and x["fallbacks"]==0 for x in responses)
  rr=[read(x["output"]) for x in commands];assert len({r["worker_pid"] for r in rr})==1
  t=time.perf_counter();decoded=[load_coeff(r) for r in rr];readtime=time.perf_counter()-t
  write(dest,dict(success=True,sequence=seq,arm=label,mode=mode,policy=policy,repetition=k,external_seconds=elapsed,read_seconds=readtime,roundtrip_seconds=elapsed+readtime,records=[str(Path(x["output"]).relative_to(HERE)) for x in commands],canonical_coefficients_sha256=[hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest() for x in decoded]))
  print("stream",seq,label,round(elapsed,4),flush=True)
 write(HERE/"model_test/streams_complete.json",dict(complete=True,stream_runs=36,applications=144))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["prepare","labels","train","validation","freeze","test","streams"]);a=ap.parse_args()
 if a.stage=="validation":trials("validation")
 elif a.stage=="test":trials("model_test")
 else:globals()[a.stage]()
if __name__=="__main__":main()
