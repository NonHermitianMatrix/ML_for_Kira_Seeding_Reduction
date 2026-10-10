"""Complete native workflows with bounded fallback and exact reference checks."""
import hashlib,json,pathlib,time
from s02_run import run
from s04_records import write_record,read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def execute(case,size,policy,output,reference,timeout=360,weights=None,trace=False,start=None):
 begin=time.perf_counter() if start is None else start;deadline=begin+timeout;attempts=[];good=[];bad=[];fatal=False
 targets=case["targets"][:size];assert len(targets)==size
 split=policy.startswith("split_");width=32 if split else size
 chunks=[targets[i:i+width] for i in range(0,size,width)]
 model_policy={"stock":"stock","native":"native","tight":"native","row":"learned","row_full":"learned","seed":"seed","combined":"combined",
  "split_native":"native","split_combined":"combined","seed_safe":"seed_closed","combined_safe":"combined_closed",
  "split_seed_safe":"seed_closed","split_combined_safe":"combined_closed","closure_safe":"closure","split_closure_safe":"closure","seed_full_safe":"seed_closed","seed_full_low_safe":"seed_closed_low","closure_full_safe":"closure","combined_full_safe":"combined_closed","combined_full_low_safe":"combined_closed_low"}[policy]
 full=policy in ("stock","native","row_full");safe=policy.endswith("_safe")
 for index,chunk in enumerate(chunks):
  part=dict(case,targets=chunk);remaining=deadline-time.perf_counter()
  if remaining<=15:bad.extend(chunk);continue
  allocation=remaining/(len(chunks)-index)
  phases=[(model_policy,1 if full or "_full_" in policy else 0)]
  if not full:
   if safe and "_full_" not in policy:phases.append(("native",0))
   phases.append(("native",1))
  complete=False
  for attempt,(method,margin) in enumerate(phases):
   remaining=deadline-time.perf_counter();allocation=remaining/(len(chunks)-index)
   if allocation<=15:break
   allowance=allocation if attempt==len(phases)-1 else min(120,max(15,.4*allocation))
   r=run(part,len(chunk),method,None,timeout=allowance,margin=margin,reference=reference,
     weights=weights,records=trace,archive=False,check_masters=True)
   r["chunk"]=index;r["attempt"]=attempt;attempts.append(r)
   if r["success"]:good.extend(chunk);complete=True;break
   if r.get("mismatches"):fatal=True;break
  if not complete:bad.extend(chunk)
 elapsed=time.perf_counter()-begin
 record=dict(case=case["id"],group=case["group"],topology=case["topology_group"],split=case["split"],
  loops=len(case["definition"]["loop_momenta"]),size=size,policy=policy,success=len(good)==size and not fatal,
  completed_targets=len(good),incomplete_targets=len(bad),complete_seconds=elapsed,timeout_seconds=timeout,
  fallback_attempts=sum(r["attempt"]>0 for r in attempts),attempts=[],trace=trace,
  reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
  row_weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest() if weights else None)
 output=pathlib.Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 for i,r in enumerate(attempts):
  p=output.parent/"attempts"/(output.name.removesuffix(".json.gz")+f"_a{i}.json.gz")
  write_record(p,r);record["attempts"].append(str(p.relative_to(HERE)))
 write_record(output,record)
 return record
