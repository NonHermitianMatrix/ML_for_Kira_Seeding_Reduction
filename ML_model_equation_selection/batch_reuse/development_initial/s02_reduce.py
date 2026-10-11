"""Kira integration with learned batch choices and shared exact checks."""
import argparse,gzip,os,shutil,tempfile
from s00_common import *
# The filename is also used by the previous release: load it with a unique name.
import importlib.util
spec=importlib.util.spec_from_file_location("previous_reduce",OLD/"s02_reduce.py")
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
def solve(request,mode,model_name):
 assert os.environ.get("JOB_ID"),"Use a bounded scheduler job"
 start=time.perf_counter();validate(request);target=list(map(tuple,request["targets"]))
 t=time.perf_counter();model=json.loads((HERE/"trained_model"/model_name).read_text()) if mode=="model" else None
 load_seconds=time.perf_counter()-t;t=time.perf_counter()
 if mode in ["extreme","old_model"]:
  nodes=json.loads((OLD/"trained_model/depth4.json").read_text())["nodes"] if mode=="old_model" else None
  rows,_=old.closure(target,"learned" if mode=="old_model" else mode,nodes);permutation=None;scores=[]
 else:
  permutation,scores=select(target,mode,model);rows=dependency(target,permutation)
 select_seconds=time.perf_counter()-t
 w=Path(tempfile.mkdtemp(prefix="batch_reuse_",dir=os.environ.get("TMPDIR",str(ROOT/".tools/kira-batch-reuse"))))
 try:
  equations=[old.equation(b,p,request["mass_ratios"]) for b,p in rows.items()]
  r=len(request["mass_ratios"]);masters=[tuple(int(i==j) for i in range(r)) for j in range(r)]
  columns=set(target)|{b for eq in equations for b in eq};ordered=masters+sorted(columns-set(masters),key=lambda b:(sum(b),b));index={b:i for i,b in enumerate(ordered)}
  with (w/"system.kira").open("w") as f:
   for eq in equations:
    for b,c in eq.items():f.write(str(index[b])+"*("+c+")\n")
    f.write("\n")
   for i,b in enumerate(target):f.write(str(len(ordered)+i)+"*(1)\n"+str(index[b])+"*(-1)\n\n")
  (w/"targets").write_text("".join(str(len(ordered)+i)+"\n" for i in range(len(target))))
  (w/"masters").write_text("".join(str(i)+"\n" for i in range(r)))
  (w/"jobs.yaml").write_text(previous.JOBS)
  prepared=time.perf_counter()-start;source_sha=sha(w/"system.kira")
  algebra=previous.run_kira(w);text=(w/"results/Tuserweight/kira_targets.kira").read_text();t=time.perf_counter()
  parsed=previous.parse(text);raw=[]
  for i in range(len(target)):
   row=parsed[len(ordered)+i];assert all(0<=j<r for j in row),"Unresolved integrals"
   raw.append({j:previous.coefficient_reader(c,"z") for j,c in row.items()})
  parse_seconds=time.perf_counter()-t
  t=time.perf_counter();checks=0
  for b,row in zip(target,raw):
   want=symbolic_oracle(request["mass_ratios"],b)
   assert all(canonical(row.get(j,()))==canonical(want.get(j,())) for j in set(row)|set(want)),(b,row,want)
   checks+=len(set(row)|set(want))
  verify=time.perf_counter()-t;t=time.perf_counter()
  coefficients={L:[{j:substitute(p,L) for j,p in row.items()} for row in raw] for L in request["loops"]}
  substitution_seconds=time.perf_counter()-t
  return dict(case=request["id"],mode=mode,success=True,complete_seconds=time.perf_counter()-start,model_load_seconds=load_seconds,selection_seconds=select_seconds,preparation_seconds=prepared,parse_seconds=parse_seconds,verification_seconds=verify,substitution_seconds=substitution_seconds,algebra=algebra,equations=len(rows),weighted_cost=cost(rows),selected_permutation=permutation,predicted_log_costs=scores,symbolic_coefficient_checks=checks,loop_coefficient_positions=checks*len(request["loops"]),fallbacks=0,model=model_name if mode=="model" else None,source_sha256=source_sha,binary_sha256=sha(previous.BINARY),raw_export=text,source_choices=[[b,p] for b,p in rows.items()],symbolic_coefficients=encode(raw),coefficients={str(L):encode(v) for L,v in coefficients.items()})
 finally:shutil.rmtree(w)
def apply(request,mode,model_name):
 begin=time.perf_counter()
 try:return solve(request,mode,model_name)
 except (AssertionError,RuntimeError,KeyError,ValueError) as exc:
  validate(request)
  result=previous.apply(request,"dense",shared=True)
  result.update(mode=mode,fallbacks=result["fallbacks"]+1,failed_learned_attempt=str(exc),complete_seconds=time.perf_counter()-begin,success=True)
  return result
def save(path,result):
 result=dict(result)
 if "algebra" in result:
  result["algebra"]=dict(result["algebra"]);payload={k:result.pop(k) for k in ["raw_export","source_choices","symbolic_coefficients","coefficients"]}
  payload["log"]=result["algebra"].pop("log")
  data=json.dumps(payload,sort_keys=True,separators=(",",":")).encode();digest=hashlib.sha256(data).hexdigest()
  dest=HERE/"objects"/(digest+".json.gz")
  if not dest.exists():
   with gzip.open(dest,"wb",compresslevel=9) as f:f.write(data)
  result["payload_sha256"]=digest
 write(path,result)
 size=sum(p.stat().st_blocks*512 for p in HERE.rglob("*") if p.is_file())
 assert size<json.loads((HERE/"resource_plan.json").read_text())["new_retained_cap_bytes"]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--mode",default="deployed");ap.add_argument("--model",default="forest16.json");a=ap.parse_args()
 begin=time.perf_counter();request=json.loads(a.input.read_text())
 if a.mode=="deployed":
  policy=json.loads((HERE/"trained_model/deployment.json").read_text());a.mode=policy["mode"];a.model=policy["model"]
 if a.mode=="previous":
  result=previous.apply(request,"extreme",shared=True)
  # Preserve prior evidence without writing into the old frozen study.
  for attempt in result["attempts"]:
   attempt.pop("source_choices",None)
   if "algebra" in attempt:attempt["algebra"].pop("log",None)
 else:result=apply(request,a.mode,a.model)
 result["complete_seconds"]=time.perf_counter()-begin
 result["request_sha256"]=sha(a.input);result["driver_sha256"]=sha(Path(__file__))
 save(a.output,result)
 print(json.dumps(dict(case=request["id"],mode=a.mode,seconds=result["complete_seconds"],success=result["success"])),flush=True)
if __name__=="__main__":main()
