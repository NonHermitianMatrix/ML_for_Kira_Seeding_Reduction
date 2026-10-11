"""Check exact arithmetic, binary round trips, worker isolation and Kira fallback."""
import argparse,subprocess
from s02_engine import *
def kernel():
 rng=random.Random(742933);state={};checks=0
 for k in range(350):
  a=[rng.randrange(-10**25,10**25) for _ in range(rng.randrange(1,15))];d=rng.randrange(1,10**25)
  a,d=old.normalized(a,d);rows=[{0:(a,d)}];loops=rng.sample([1,2,3,7,12,16,32,101],4)
  inp=common_packet(rows,loops);actual=decode_expanded(native(inp,state),[[0]])
  want=python_expand(rows,loops,state);assert actual==want
  for L in loops:
   expected=base.old.poly_substitute(tuple(F(x,d) for x in a),L)
   assert base.decode(actual[str(L)])[0][0]==base.canonical(expected);checks+=1
 for R in [2,3,4]:
  for B in [2,7,14]:
   c=base.make_case("validation",31200+R*B,R,B,24);c["mass_ratios"]=[70001+7*j*j+j for j in range(R)]
   for policy in POLICIES:
    rows=recurrence(c,dependencies(c,policy));checker=TaylorInteger(c["mass_ratios"],c["targets"])
    for b,row in zip(c["targets"],rows):
     assert row==checker.coefficient(b)
     assert {j:tuple(F(x,d) for x in a) for j,(a,d) in row.items()}=={j:p for j,p in base.symbolic_oracle(c["mass_ratios"],b).items() if p}
     checks+=len(row)
   reference=old_apply([c],"both","extreme",OldState())
   for mode in ["integer","native_json","native_binary"]:
    r=apply([c],mode,{})
    assert not r["fallbacks"]
    coeff=decode_binary(r["_binary"]) if "_binary" in r else r
    for key in ["symbolic_coefficients","coefficients"]:assert coeff[key]==reference[key]
    checks+=1
 bad=common_packet([{0:((1,2),3)}],[1])[:-1]
 try:native(bad,state)
 except AssertionError:pass
 else:raise AssertionError("Malformed input accepted")
 write(HERE/"development/kernel_check.json",dict(all_passed=True,exact_checks=checks,malformed_native_input_rejected=True))
 print("exact kernel checks",checks,flush=True)
def integration():
 folder=HERE/"model_test/integration";folder.mkdir(exist_ok=True,parents=True)
 c=base.make_case("test",41501,3,7,8);c.update(id="same_identifier",mass_ratios=[90001,90007,90101],loops=[1,12,16,24,32])
 changed=dict(c,mass_ratios=[91001,91007,91103],loops=[2,5,13]);invalid=dict(c,mass_ratios=[90001,90001,90101])
 commands=[]
 for i,cc in enumerate([c,changed,invalid,c]):
  inp=folder/("input"+str(i)+".json");write(inp,dict(requests=[cc]));commands.append(dict(input=str(inp),output=str(folder/("output"+str(i)+".json"))))
 args=[sys.executable,str(HERE/"s03_application.py"),"--stream","--mode","learned"]
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
 except AssertionError:pass
 else:raise AssertionError("Truncated coefficient payload accepted")
 limited=dict(commands[0],output=str(folder/"limited.json"))
 p=subprocess.run(args+["--max-requests","1"],input=json.dumps(limited)+"\n"+json.dumps(limited)+"\n",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
 assert p.returncode!=0 and len(p.stdout.splitlines())==1
 write(folder/"summary.json",dict(all_passed=True,changed_physical_inputs_isolated=True,invalid_request_rejected=True,worker_reused=True,model_route_checked=True,request_cap_checked=True,forced_kira_fallback_checked=True,truncated_output_rejected=True,expanded_coefficient_checks=checked))
 print("integration checks",checked,flush=True)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["kernel","integration"]);a=ap.parse_args();globals()[a.stage]()
