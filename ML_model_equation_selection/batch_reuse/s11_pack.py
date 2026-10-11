"""Reduce several independent mass profiles in one exact Kira system."""
import argparse,gzip,os,tempfile,shutil
from s00_common import *
from s08_reader import parse as coefficient_reader
import importlib.util
spec=importlib.util.spec_from_file_location("batch_driver",HERE/"s02_reduce.py")
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
def packed(requests,mode,model_name):
 start=time.perf_counter()
 assert os.environ.get("JOB_ID"),"Use a bounded scheduler job"
 assert 1<=len(requests)<=8 and len(set(c["id"] for c in requests))==len(requests)
 assert sum(len(c["targets"]) for c in requests)<=512
 for c in requests:validate(c)
 t=time.perf_counter();model=load_model(model_name) if mode=="model" and any(len(c["mass_ratios"])>2 for c in requests) else None
 model_load=time.perf_counter()-t;t=time.perf_counter();all_rows=[];choice=[]
 for c in requests:
  target=list(map(tuple,c["targets"]))
  if mode in ["extreme","old_model"]:
   nodes=json.loads((OLD/"trained_model/depth4.json").read_text())["nodes"] if mode=="old_model" else None
   rows,_=old.closure(target,"learned" if mode=="old_model" else mode,nodes);p=None;scores=[]
  else:
   p,scores=select(target,mode,model);rows=dependency(target,p)
  all_rows.append(rows);choice.append(dict(case=c["id"],permutation=p,predicted_log_costs=scores,equations=len(rows),weighted_cost=cost(rows)))
 assert sum(map(len,all_rows))<=12000,"Packed equation cap"
 select_seconds=time.perf_counter()-t
 w=Path(tempfile.mkdtemp(prefix="packed_kira_",dir=os.environ.get("TMPDIR",str(ROOT/".tools/kira-batch-reuse"))))
 try:
  master_columns=[];all_equations=[];targets=[]
  for k,(c,rows) in enumerate(zip(requests,all_rows)):
   r=len(c["mass_ratios"])
   master_columns.extend((k,tuple(int(i==j) for i in range(r))) for j in range(r))
   all_equations.extend({(k,b):v for b,v in old.equation(a,p,c["mass_ratios"]).items()} for a,p in rows.items())
   targets.extend((k,tuple(b)) for b in c["targets"])
  columns=set(targets)|{b for eq in all_equations for b in eq}
  ordered=master_columns+sorted(columns-set(master_columns),key=lambda kb:(sum(kb[1]),kb))
  mapping={a:i for i,a in enumerate(ordered)}
  offsets=[];m=0
  for c in requests:offsets.append(m);m+=len(c["mass_ratios"])
  with (w/"system.kira").open("w") as f:
   for eq in all_equations:
    for b,v in eq.items():f.write(str(mapping[b])+"*("+v+")\n")
    f.write("\n")
   for i,b in enumerate(targets):f.write(str(len(ordered)+i)+"*(1)\n"+str(mapping[b])+"*(-1)\n\n")
  (w/"targets").write_text("".join(str(len(ordered)+i)+"\n" for i in range(len(targets))))
  (w/"masters").write_text("".join(str(j)+"\n" for j in range(m)))
  (w/"jobs.yaml").write_text(driver.previous.JOBS)
  prepared=time.perf_counter()-start;source_sha=sha(w/"system.kira")
  algebra=driver.previous.run_kira(w);raw=(w/"results/Tuserweight/kira_targets.kira").read_text();t=time.perf_counter()
  parsed=driver.previous.parse(raw);symbolic={c["id"]:[] for c in requests}
  for i,(k,b) in enumerate(targets):
   row=parsed[len(ordered)+i];lo=offsets[k];hi=lo+len(requests[k]["mass_ratios"])
   assert all(lo<=j<hi for j in row),"Unresolved or cross-family coefficient"
   symbolic[requests[k]["id"]].append({j-lo:coefficient_reader(v,"z") for j,v in row.items()})
  parse_seconds=time.perf_counter()-t;t=time.perf_counter();checks=0;positions=0
  for c in requests:
   for b,row in zip(c["targets"],symbolic[c["id"]]):
    want=symbolic_oracle(c["mass_ratios"],b)
    assert all(canonical(row.get(j,()))==canonical(want.get(j,())) for j in set(row)|set(want))
    checks+=len(want);positions+=len(want)*len(c["loops"])
  verify=time.perf_counter()-t;t=time.perf_counter()
  coefficients={c["id"]:{str(L):encode([{j:substitute(p,L) for j,p in row.items()} for row in symbolic[c["id"]]]) for L in c["loops"]} for c in requests}
  return dict(case="pack_"+"_".join(c["id"] for c in requests),mode=mode,packed=True,success=True,fallbacks=0,complete_seconds=time.perf_counter()-start,model=model_name if mode=="model" else None,model_load_seconds=model_load,selection_seconds=select_seconds,preparation_seconds=prepared,parse_seconds=parse_seconds,verification_seconds=verify,substitution_seconds=time.perf_counter()-t,algebra=algebra,equations=sum(map(len,all_rows)),weighted_cost=sum(cost(x) for x in all_rows),source_sha256=source_sha,choices=choice,symbolic_coefficient_checks=checks,loop_coefficient_positions=positions,raw_export=raw,source_choices=[[c["id"],[[b,p] for b,p in rows.items()]] for c,rows in zip(requests,all_rows)],symbolic_coefficients={k:encode(v) for k,v in symbolic.items()},coefficients=coefficients,binary_sha256=sha(driver.previous.BINARY))
 finally:shutil.rmtree(w)
def apply(requests,mode,model):
 begin=time.perf_counter()
 try:return packed(requests,mode,model)
 except (AssertionError,RuntimeError,KeyError,ValueError) as exc:
  # A valid supported batch can retry each family independently.
  assert 1<=len(requests)<=8 and sum(len(c["targets"]) for c in requests)<=512
  for c in requests:validate(c)
  results=[driver.apply(c,mode,model) for c in requests]
  return dict(success=True,mode=mode,packed=True,fallbacks=1+sum(x["fallbacks"] for x in results),failure=str(exc),complete_seconds=time.perf_counter()-begin,individual_results=results)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--mode",default="deployed");ap.add_argument("--model",default="forest16.json");ap.add_argument("--separate",action="store_true");a=ap.parse_args()
 begin=time.perf_counter();requests=json.loads(a.input.read_text())["requests"]
 assert ROOT in a.output.resolve().parents
 if a.mode=="deployed":
  p=json.loads((HERE/"trained_model/deployment.json").read_text());a.mode=p["packed_mode"];a.model=p["model"]
 if a.separate:
  results=[driver.apply(c,a.mode,a.model) for c in requests]
  result=dict(success=all(x["success"] for x in results),mode=a.mode,packed=False,fallbacks=sum(x["fallbacks"] for x in results),equations=sum(x["equations"] for x in results),algebra=dict(seconds=sum(x["algebra"]["seconds"] for x in results),peak_tree_rss_bytes=max(x["algebra"]["peak_tree_rss_bytes"] for x in results),peak_scratch_bytes=max(x["algebra"]["peak_scratch_bytes"] for x in results)))
  # Save the exact individual evidence separately; serialization is outside calculation timing.
  result["complete_seconds"]=time.perf_counter()-begin
  result["individual_records"]=[]
  for i,x in enumerate(results):
   dest=a.output.with_name(a.output.stem+"_part"+str(i)+".json");driver.save(dest,x);result["individual_records"].append(str(dest.relative_to(HERE)))
  write(a.output,result)
 else:
  result=apply(requests,a.mode,a.model);result["complete_seconds"]=time.perf_counter()-begin;driver.save(a.output,result)
 print(json.dumps({k:result[k] for k in ["success","mode","packed","complete_seconds","fallbacks"]}),flush=True)
if __name__=="__main__":main()
