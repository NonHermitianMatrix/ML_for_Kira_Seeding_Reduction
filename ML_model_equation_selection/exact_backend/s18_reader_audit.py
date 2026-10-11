"""Independently audit reserved coefficients, binary readers and fixed policies."""
from s16_reader_study import *
def audit():
 check_freeze()
 cold=list((HERE/"reader_final_test/results").glob("*.json"));stream=list((HERE/"reader_final_test/stream_results").glob("*.json"))
 expected=read(HERE/"reader_final_test/complete.json")["applications"];assert len(cold)==expected and len(stream)==144
 unique={};payloads={};policies={}
 inputs={sha(p):p for p in (HERE/"reader_final_test/inputs").glob("*.json")}
 for p in cold+stream:
  r=read(p);assert r["success"] and r["fallbacks"]==0,p
  identity=(r["coefficient_format"],r["coefficients_sha256"])
  if identity not in payloads:
   coeff=load_coeff(r);payloads[identity]=hashlib.sha256(json.dumps(coeff,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  h=payloads[identity];inp=inputs[r["request_sha256"]]
  if inp in unique:assert unique[inp][0]==h,p
  else:unique[inp]=(h,r)
  if "canonical_coefficients_sha256" in r:assert r["canonical_coefficients_sha256"]==h
  if r.get("mode")=="learned":policies[r["route"]]=policies.get(r["route"],0)+1
  eh=r["evidence_sha256"];raw=gzip.decompress((HERE/"objects"/(eh+".json.gz")).read_bytes());assert hashlib.sha256(raw).hexdigest()==eh
 positions=0;symbolic_checks=0
 for inp,(h,r) in unique.items():
  requests=read(inp)["requests"];coeff=load_coeff(r)
  for c in requests:
   rows=base.decode(coeff["symbolic_coefficients"][c["id"]])
   for b,row in zip(c["targets"],rows):
    assert row=={j:p for j,p in base.symbolic_oracle(c["mass_ratios"],b).items() if p};symbolic_checks+=len(row)
   for L in c["loops"]:
    rows=base.decode(coeff["coefficients"][c["id"]][str(L)])
    assert len(rows)==len(c["targets"])
    for b,row in zip(c["targets"],rows):
     assert row=={j:p for j,p in base.old.oracle(L,c["mass_ratios"],b).items() if p};positions+=len(row)
 assert len(unique)==12
 assert read(HERE/"reader_final_test/integration/summary.json")["all_passed"]
 assert read(HERE/"development/kernel_check.json")["all_passed"]
 guard()
 write(HERE/"reader_final_test/audit.json",dict(all_exact=True,applications=len(cold)+len(stream),cold_applications=len(cold),stream_applications=len(stream),distinct_input_batches=12,symbolic_coefficient_positions=symbolic_checks,expanded_coefficient_positions=positions,all_output_formats_identical=True,independent_old_oracle_passed=True,integration_passed=True,learned_routes=policies))
 print("audit passed",len(cold)+len(stream),positions,flush=True)


def integration():
 folder=HERE/"reader_final_test/integration";folder.mkdir(exist_ok=True,parents=True)
 c=base.make_case("test",41501,3,7,8);c.update(id="same_identifier",mass_ratios=[90001,90007,90101],loops=[1,12,16,24,32])
 changed=dict(c,mass_ratios=[91001,91007,91103],loops=[2,5,13]);invalid=dict(c,mass_ratios=[90001,90001,90101])
 commands=[]
 for i,cc in enumerate([c,changed,invalid,c]):
  inp=folder/("input"+str(i)+".json");write(inp,dict(requests=[cc]));commands.append(dict(input=str(inp),output=str(folder/("output"+str(i)+".json"))))
 args=[sys.executable,str(HERE/"s15_application.py"),"--stream","--mode","learned"]
 p=subprocess.run(args,input="".join(json.dumps(x)+"\n" for x in commands),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
 assert p.returncode==0,p.stderr;answers=[json.loads(x) for x in p.stdout.splitlines()];assert [x["ok"] for x in answers]==[True,True,False,True]
 records=[read(folder/("output"+str(i)+".json")) for i in [0,1,3]];assert len({r["worker_pid"] for r in records})==1
 assert records[0]["coefficients_sha256"]==records[2]["coefficients_sha256"]!=records[1]["coefficients_sha256"]
 checked=0
 for i,cc in [(0,c),(1,changed),(3,c)]:
  r=read(folder/("output"+str(i)+".json"));coeff=load_coeff(r)
  for L in cc["loops"]:
   for b,row in zip(cc["targets"],base.decode(coeff["coefficients"][cc["id"]][str(L)])):
    assert row=={j:p for j,p in base.old.oracle(L,cc["mass_ratios"],b).items() if p};checked+=len(row)
 result=apply([c],"learned",{},inject_failure=True);assert result["success"] and result["fallbacks"]==1 and result["kira_invoked"];save(folder/"forced_fallback.json",result)
 r=read(folder/"output0.json");raw=gzip.decompress((HERE/"objects"/(r["coefficients_sha256"]+".bin.gz")).read_bytes())
 try:decode_binary(raw[:-1])
 except (AssertionError,ValueError):pass
 else:raise AssertionError("Truncated coefficient payload accepted")
 limited=dict(commands[0],output=str(folder/"limited.json"))
 p=subprocess.run(args+["--max-requests","1"],input=json.dumps(limited)+"\n"+json.dumps(limited)+"\n",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
 assert p.returncode!=0 and len(p.stdout.splitlines())==1
 write(folder/"summary.json",dict(all_passed=True,changed_physical_inputs_isolated=True,invalid_request_rejected=True,worker_reused=True,model_route_checked=True,request_cap_checked=True,forced_kira_fallback_checked=True,truncated_output_rejected=True,expanded_coefficient_checks=checked))
 print("integration checks",checked,flush=True)

def reader_comparison():
 import s14_reader
 records=[]
 for inp in sorted((HERE/"reader_final_test/inputs").glob("*.json")):
  record=read(HERE/"reader_final_test/results"/(inp.stem+"_native_binary_0.json"))
  raw=gzip.decompress((HERE/"objects"/(record["coefficients_sha256"]+".bin.gz")).read_bytes())
  tasks=[(name,k) for name in ["python","compiled"] for k in range(5)];random.Random(715019+int(inp.stem[5:])).shuffle(tasks)
  reference=None
  try:
   for name,k in tasks:
    s14_reader.backend.decode_expanded=s14_reader.python_reader if name=="python" else s14_reader.compiled_reader
    start=time.perf_counter();value=decode_binary(raw);elapsed=time.perf_counter()-start
    h=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if reference is None:reference=h
    assert reference==h
    records.append(dict(input=inp.name,reader=name,repetition=k,seconds=elapsed,canonical_sha256=h))
  finally:s14_reader.backend.decode_expanded=s14_reader.compiled_reader
 ratios=[]
 for inp in sorted({x["input"] for x in records}):
  med={name:statistics.median(x["seconds"] for x in records if x["input"]==inp and x["reader"]==name) for name in ["python","compiled"]}
  ratios.append(med["compiled"]/med["python"])
 write(HERE/"reader_final_test/reader_comparison.json",dict(all_exact=True,measurements=records,ratio=math.exp(sum(map(math.log,ratios))/len(ratios)),metric="In-memory decoding of identical complete binary payloads",batches=12))
 print("reader comparison passed",len(records),flush=True)

if __name__=="__main__":
 integration()
 audit()
 reader_comparison()
