"""Independent arithmetic and persistent-interface checks."""
import argparse,random,subprocess
from s01_engine import *
def kernel():
 rng=random.Random(413117);checks=0;cache=Transforms(8)
 for trial in range(1000):
  p=base.canonical([F(rng.randint(-1000,1000),rng.randint(1,100)) for _ in range(rng.randint(0,14))])
  L=rng.choice([1,2,3,7,12,16,32,101])
  out=base.decode(expand([{0:p}],[L],cache)[str(L)])[0][0]
  assert out==base.canonical(base.old.poly_substitute(p,L));checks+=1
 for L in range(1,41):
  actual=base.decode(expand([{0:(F(2,7),F(-3,11),F(4,13))}],[L],cache)[str(L)])[0][0]
  assert actual==base.canonical(base.old.poly_substitute((F(2,7),F(-3,11),F(4,13)),L));checks+=1
 assert len(cache.cache)==8
 hits=0
 for r in [2,3,4]:
  for B in [2,7,14]:
   for k in range(3):
    c=base.make_case("validation",9001+31*k,r,B,24)
    c["targets"]+= [tuple(int(i==j) for i in range(r)) for j in range(r)]
    checker=TaylorCheck(c["mass_ratios"],c["targets"])
    for b in c["targets"]:
     actual=checker.coefficient(b);want=base.symbolic_oracle(c["mass_ratios"],b)
     assert all(base.canonical(actual.get(j,()))==base.canonical(want.get(j,())) for j in set(actual)|set(want))
     checks+=len(want)
    hits+=checker.hits
 assert hits>0
 base.write(HERE/"validation/kernel_check.json",dict(all_passed=True,exact_checks=checks,taylor_factor_hits=hits,transform_capacity_checked=True))
 print("kernel checks",checks,flush=True)
def integration():
 folder=HERE/"model_test/integration";folder.mkdir(parents=True,exist_ok=True)
 c=base.make_case("test",9701,3,7,8);c.update(id="reused_id",mass_ratios=[6011,6043,6073],loops=[1,12,16,24,32])
 cases=[dict(requests=[c])]
 changed=dict(c,mass_ratios=[6101,6113,6151],loops=[2,5,13]);cases.append(dict(requests=[changed]))
 invalid=dict(c,mass_ratios=[6011,6011,6073]);cases.append(dict(requests=[invalid]))
 cases.append(dict(requests=[c]))
 commands=[]
 for k,case in enumerate(cases):
  inp=folder/("input"+str(k)+".json");base.write(inp,case)
  commands.append(dict(input=str(inp),output=str(folder/("output"+str(k)+".json"))))
 args=[sys.executable,str(HERE/"s02_application.py"),"--stream","--policy","model"]
 p=subprocess.run(args,input="".join(json.dumps(c)+"\n" for c in commands),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
 assert p.returncode==0,p.stderr
 answers=[json.loads(line) for line in p.stdout.splitlines()]
 assert [x["ok"] for x in answers]==[True,True,False,True],answers
 checks=0;records=[]
 for i in [0,1,3]:
  x=json.loads((folder/("output"+str(i)+".json")).read_text());records.append(x)
  data=json.loads(gzip.decompress((HERE/"objects"/(x["coefficients_sha256"]+".json.gz")).read_bytes()))
  cc=cases[i]["requests"][0]
  for L in cc["loops"]:
   for b,row in zip(cc["targets"],base.decode(data["coefficients"][cc["id"]][str(L)])):
    want=base.old.oracle(L,cc["mass_ratios"],b)
    assert all(base.canonical(row.get(j,()))==base.canonical(want.get(j,())) for j in set(row)|set(want));checks+=len(want)
 assert len({x["worker_pid"] for x in records})==1
 assert records[0]["coefficients_sha256"]==records[2]["coefficients_sha256"]
 assert records[0]["coefficients_sha256"]!=records[1]["coefficients_sha256"]
 # Corrupt-result injection must recover through the unchanged Kira path.
 result=apply([c],"both","model",State(),inject_failure=True)
 assert result["success"] and result["fallbacks"]==1 and result["kira_invoked"]
 save(folder/"forced_fallback.json",result)
 # Check the public command-count cap with a separate output, without overwriting the earlier records.
 limited=dict(commands[0],output=str(folder/"limited.json"))
 p=subprocess.run(args+["--max-requests","1"],input=json.dumps(limited)+"\n"+json.dumps(limited)+"\n",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
 assert p.returncode!=0 and len(p.stdout.splitlines())==1 and "request limit" in p.stderr
 base.write(folder/"summary.json",dict(all_passed=True,successful_stream_requests=3,invalid_request_rejected=True,continued_after_invalid_request=True,changed_mass_and_loop_data_isolated=True,model_worker_process_reused=True,forced_kira_fallback_passed=True,command_limit_passed=True,expanded_coefficient_checks=checks))
 print("worker integration checks passed",checks,flush=True)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["kernel","integration"]);a=ap.parse_args()
 {"kernel":kernel,"integration":integration}[a.stage]()
