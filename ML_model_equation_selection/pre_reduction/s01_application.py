"""Pre-reduce selected exact identities, then finish and check with Kira."""
import argparse,os,tempfile,shutil
from s00_contract import *
from s08_reader import parse as reader
from s16_native import load_native
def validate_group(requests):
 assert 1<=len(requests)<=8 and len({c["id"] for c in requests})==len(requests)
 assert sum(len(c["targets"]) for c in requests)<=512
 for c in requests:base.validate(c)
def calculate(requests,mode,inject_failure=False):
 start=time.perf_counter();assert os.environ.get("JOB_ID"),"Use a bounded cluster job"
 validate_group(requests)
 direct=mode.startswith("direct_");learned=mode in ["model","direct_model"]
 t=time.perf_counter();model=(load_native("forest4.json") if direct else base.load_model("forest4.json")) if learned and any(len(c["mass_ratios"])>2 for c in requests) else None
 load=time.perf_counter()-t;t=time.perf_counter();choices=[];systems=[]
 for c in requests:
  rows,choice=selected(c,"model" if learned else "extreme",model)
  systems.append(rows);choices.append(dict(case=c["id"],**choice))
 assert sum(map(len,systems))<=12000
 selection=time.perf_counter()-t;t=time.perf_counter()
 exact={c["id"]:recurrence(c,rows) for c,rows in zip(requests,systems)}
 contraction=time.perf_counter()-t
 # Independent Taylor expansion remains separate from the selected recurrence.
 t=time.perf_counter()
 oracle={c["id"]:[base.symbolic_oracle(c["mass_ratios"],b) for b in c["targets"]] for c in requests}
 oracle_seconds=time.perf_counter()-t
 inputs=oracle if mode in ["analytic","direct_analytic"] else exact
 if direct:
  t=time.perf_counter();checks=0
  for c in requests:
   for left,right in zip(exact[c["id"]],oracle[c["id"]]):
    keys=set(left)|set(right)
    assert all(base.canonical(left.get(j,()))==base.canonical(right.get(j,())) for j in keys),"Exact coefficient mismatch"
    checks+=len(keys)
  if inject_failure:raise AssertionError("Injected exact-check failure")
  verify=time.perf_counter()-t;t=time.perf_counter()
  coefficients={c["id"]:{str(L):base.encode([{j:base.substitute(p,L) for j,p in row.items()} for row in inputs[c["id"]]]) for L in c["loops"]} for c in requests}
  return dict(success=True,mode=mode,kira_invoked=False,fallbacks=0,complete_seconds=time.perf_counter()-start,model_load_seconds=load,selection_seconds=selection,contraction_seconds=contraction,oracle_seconds=oracle_seconds,verification_seconds=verify,substitution_seconds=time.perf_counter()-t,choices=choices,equations_before=sum(map(len,systems)),equations_sent=0,weighted_cost=sum(base.cost(s) for s in systems),symbolic_coefficient_checks=checks,loop_coefficient_positions=sum(len(row)*len(c["loops"]) for c in requests for row in inputs[c["id"]]),source_choices=[[c["id"],[[list(b),list(p)] for b,p in rows.items()]] for c,rows in zip(requests,systems)],raw_export="",symbolic_coefficients={k:base.encode(v) for k,v in inputs.items()},coefficients=coefficients)
 w=Path(tempfile.mkdtemp(prefix="kira_contract_",dir=os.environ.get("TMPDIR",str(ROOT/".tools/kira-pre-reduction"))))
 try:
  offsets=[];m=0
  for c in requests:offsets.append(m);m+=len(c["mass_ratios"])
  targets=[];equations=[]
  for k,c in enumerate(requests):
   for row in inputs[c["id"]]:
    n=m+len(targets);targets.append(n)
    equations.append(str(n)+"*(1)\n"+"".join(str(offsets[k]+j)+"*(-("+expression(p)+"))\n" for j,p in sorted(row.items()))+"\n")
  (w/"system.kira").write_text("".join(equations));(w/"targets").write_text("".join(str(n)+"\n" for n in targets))
  (w/"masters").write_text("".join(str(n)+"\n" for n in range(m)));(w/"jobs.yaml").write_text(pack.driver.previous.JOBS)
  source_hash=base.sha(w/"system.kira")
  prepared=time.perf_counter()-start
  algebra=pack.driver.previous.run_kira(w);raw=(w/"results/Tuserweight/kira_targets.kira").read_text()
  t=time.perf_counter();parsed=pack.driver.previous.parse(raw);symbolic={};n=0;checks=0
  for k,c in enumerate(requests):
   out=[]
   for b in c["targets"]:
    row=parsed[m+n];n+=1
    assert all(offsets[k]<=j<offsets[k]+len(c["mass_ratios"]) for j in row),"Unresolved or cross-family integral"
    out.append({j-offsets[k]:reader(p,"z") for j,p in row.items()})
   symbolic[c["id"]]=out
  parse_seconds=time.perf_counter()-t;t=time.perf_counter()
  for c in requests:
   for row,left,right in zip(symbolic[c["id"]],exact[c["id"]],oracle[c["id"]]):
    keys=set(row)|set(left)|set(right)
    assert all(base.canonical(row.get(j,()))==base.canonical(left.get(j,()))==base.canonical(right.get(j,())) for j in keys),"Exact coefficient mismatch"
    checks+=len(keys)
  if inject_failure:raise AssertionError("Injected exact-check failure")
  verify=time.perf_counter()-t;t=time.perf_counter()
  coefficients={c["id"]:{str(L):base.encode([{j:base.substitute(p,L) for j,p in row.items()} for row in symbolic[c["id"]]]) for L in c["loops"]} for c in requests}
  return dict(success=True,mode=mode,kira_invoked=True,fallbacks=0,complete_seconds=time.perf_counter()-start,model_load_seconds=load,selection_seconds=selection,contraction_seconds=contraction,oracle_seconds=oracle_seconds,preparation_seconds=prepared,parse_seconds=parse_seconds,verification_seconds=verify,substitution_seconds=time.perf_counter()-t,algebra=algebra,choices=choices,equations_before=sum(map(len,systems)),equations_sent=len(targets),weighted_cost=sum(base.cost(s) for s in systems),symbolic_coefficient_checks=checks,loop_coefficient_positions=sum(len(row)*len(c["loops"]) for c in requests for row in symbolic[c["id"]]),source_sha256=source_hash,binary_sha256=base.sha(pack.driver.previous.BINARY),source_choices=[[c["id"],[[list(b),list(p)] for b,p in rows.items()]] for c,rows in zip(requests,systems)],raw_export=raw,symbolic_coefficients={k:base.encode(v) for k,v in symbolic.items()},coefficients=coefficients)
 finally:shutil.rmtree(w)
def apply(requests,mode,inject_failure=False):
 start=time.perf_counter();validate_group(requests)
 if mode=="baseline":return pack.apply(requests,"model","forest4.json")
 try:return calculate(requests,mode,inject_failure)
 except (AssertionError,ValueError,KeyError,RuntimeError) as exc:
  # The previous supplied-system route keeps its own exact checks and full fallback.
  result=pack.apply(requests,"model","forest4.json")
  result.update(fallbacks=result["fallbacks"]+1,failed_contraction=str(exc),complete_seconds=time.perf_counter()-start,mode=mode)
  return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--mode",choices=["deployed","baseline","model","extreme","analytic","direct_model","direct_extreme","direct_analytic"],default="deployed");a=ap.parse_args()
 start=time.perf_counter()
 mode=json.loads((HERE/"deployment.json").read_text())["mode"] if a.mode=="deployed" else a.mode
 assert ROOT in a.output.resolve().parents
 requests=json.loads(a.input.read_text())["requests"]
 result=apply(requests,mode);result.update(method=mode,complete_seconds=time.perf_counter()-start,request_sha256=base.sha(a.input))
 save(a.output,result)
 print(json.dumps({k:result[k] for k in ["success","method","complete_seconds","fallbacks"]}),flush=True)
if __name__=="__main__":main()
