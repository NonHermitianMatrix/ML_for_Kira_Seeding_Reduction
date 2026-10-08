"""One isolated symbolic reduction, with live inference and exact fallback."""
import argparse,os,pathlib,subprocess,time,re,sys
from s01_common import *
def kira_run(w,plan):
 env=dict(os.environ,FERMATPATH=str(ROOT/".tools/Ferl7/fer64"))
 begin=time.perf_counter()
 with (w/"run.log").open("w") as log:
  p=subprocess.run([str(ROOT/".tools/kira/bin/kira"),"--parallel=1","jobs.yaml"],cwd=w,env=env,
                   stdout=log,stderr=subprocess.STDOUT,timeout=plan["timeout_seconds"]-10)
 elapsed=time.perf_counter()-begin
 log=(w/"run.log").read_text(errors="replace")
 counts={k:[int(v) for v in re.findall(pat,log)] for k,pat in {
   "selected_equations":r"Number of selected equations to reduce:\s*(\d+)",
   "selected_terms":r"Number of terms:\s*(\d+)",
   "reduced_equations":r"(\d+) equations were reduced",
   "forward_insertions":r"redundant:\s*\d+; insertions (\d+)",
   "generated_equations":r"(\d+) equations:\s*\d+ zero \+",
   "independent_equations":r"equations:\s*\d+ zero \+\s*(\d+) independent"}.items()}
 result=dict(seconds=elapsed,returncode=p.returncode,counters=counts,log_sha256=sha(w/"run.log"))
 if p.returncode:raise RuntimeError("Kira exit "+str(p.returncode)+": "+log[-1500:])
 return result
def supplied(family,targets,selected,w,plan):
 eqs=[e for e in family["identities"] if selected is None or e["source"]["kind"]!="ibp" or tuple(e["source"]["seed"]) in selected]
 eqs=connected(eqs,targets,family["masters"])
 b=dict(id=0,mask=[],policies={},targets=targets,equations=eqs,available_equations=len(eqs),
        ibp_equations=sum(e["source"]["kind"]=="ibp" for e in eqs),
        background_equations=sum(e["source"]["kind"]!="ibp" for e in eqs))
 manifest=adapter.export(family,[b],w,quotient=False)
 result=kira_run(w,plan);parsed=adapter.parse_output(w/"results/Tuserweight/kira_targets.kira")
 import sympy as sp
 output={}
 for weight,t in manifest["targets"].items():
  if int(weight) not in parsed:continue
  out={}
  for i,c in parsed[int(weight)].items():
   entry=manifest["mapping"].get(str(i))
   if entry is None:raise ValueError("Unexpected auxiliary output")
   out[tuple(entry["indices"])]=sp.sympify(c,rational=True)
  output[t["target"]]=out
 result.update(input_equations=len(eqs)+len(targets),source_equations=len(eqs),source_terms=sum(len(e["terms"]) for e in eqs),
  ibp_equations=b["ibp_equations"],background_equations=b["background_equations"],
  source_ids=[e["id"] for e in eqs],input_sha256=manifest["input_sha256"],
  export_sha256=sha(w/"results/Tuserweight/kira_targets.kira"),manifest=manifest)
 return output,result
def seed_select(fam):
 begin=time.perf_counter()
 import torch
 d=load_module("bench_seed_data",ROOT/"ML_model_seed_selection/s01_data.py")
 m=load_module("bench_seed_model",ROOT/"ML_model_seed_selection/s02_model.py")
 saved=torch.load(ROOT/"ML_model_seed_selection/trained_model.pt",map_location="cpu",weights_only=False)
 cfg=saved["config"];torch.set_num_threads(1);model=m.SeedSelector(cfg);model.load_state_dict(saved["model"]);model.eval()
 load=time.perf_counter()-begin
 begin=time.perf_counter()
 public=d.public_family(fam["definition"],fam["basis"]);shared=d.encode_shared(public,fam["seeds"],cfg)
 probs=[];selected=set()
 with torch.inference_mode():
  for target in fam["targets"]:
   p=model.probabilities(d.encode(target,public,fam["seeds"],cfg,shared)).tolist()
   probs.append(dict(target=target["id"],probabilities=p))
   selected.update(s for s,v in zip(fam["seeds"],p) if v>=0.5)
 return selected,dict(load_seconds=load,inference_seconds=time.perf_counter()-begin,
  candidates=len(fam["seeds"]),selected=len(selected),probabilities=probs,selected_seeds=[list(x) for x in sorted(selected)])
def reduce_targets(fam,learned=True):
 begin=time.perf_counter()
 import sympy as sp
 model_dir=ROOT/"ML_model_reduction";sys.path.insert(0,str(model_dir))
 from s01_state import column,indices,order_key,eliminate,state_from_step
 from s08_verify import evaluate
 predictor=None
 if learned:
  from s05_predict import Predictor
  import torch
  predictor=Predictor();torch.set_num_threads(1)
 load=time.perf_counter()-begin
 begin=time.perf_counter();point,prime=sample_point(fam["definition"]);masters={column(a) for a in fam["masters"]}
 profile=tuple(sorted(point.items()));symbolic={};byid={e["id"]:e for e in fam["identities"]}
 def sampled_terms(terms):
  out={}
  for t in terms:
   k=column(t["indices"]);v=(out.get(k,0)+evaluate(t["coefficient"],profile,prime))%prime
   if v:out[k]=v
   else:out.pop(k,None)
  return out
 identities={};pool=collections.defaultdict(list)
 for e in fam["identities"]:
  mod=sampled_terms(e["terms"])
  nonmaster=[tuple(t["indices"]) for t in e["terms"] if tuple(t["indices"]) not in fam["masters"]]
  lead=max(nonmaster,key=old.index_key,default=None)
  if lead is None or not mod.get(column(lead)):continue
  identities[e["id"]]={"modular_terms":mod};pool[column(lead)].append(e["id"])
 target_out=[];paths=[];allops=0;alltrials=0
 for target in fam["targets"]:
  row=rational_rows(target["terms"]);path=[];status="step_limit"
  for step in range(128):
   remain=[a for a in row if column(a) not in masters and row[a]!=0]
   if not remain:status="complete";break
   pivot=max(remain,key=old.index_key);key=column(pivot);mod=sampled_terms(expression_terms(row));allowed=sorted(pool.get(key,[]))
   if not allowed or not mod.get(key):status="kira_fallback";break
   if learned:
    state=state_from_step(dict(before=mod,pivot_indices=list(pivot),allowed_pivot_equations=allowed),
                          identities,fam["definition"],masters,prime)
    prediction=predictor.predict(state);eid=prediction["selected_step"]["id"];confidence=prediction["confidence"]
   else:
    choices=[]
    for candidate in allowed:
     after,_=eliminate(mod,identities[candidate]["modular_terms"],key,prime)
     choices.append((len(set(after)-masters),len(after),1+2*len(identities[candidate]["modular_terms"]),candidate))
    eid=min(choices)[-1];confidence=None
   if eid not in symbolic:symbolic[eid]=rational_rows(byid[eid]["terms"])
   src=symbolic[eid];factor=sp.cancel(row[pivot]/src[pivot]);before=len(row);new={}
   for a in set(row)|set(src):
    c=sp.cancel(row.get(a,0)-factor*src.get(a,0))
    if c!=0:new[a]=c
   assert pivot not in new
   ops=1+2*len(src);trials=sum(1+2*len(identities[e]["modular_terms"]) for e in allowed)
   allops+=ops;alltrials+=trials
   path.append(dict(equation=eid,pivot=list(pivot),confidence=confidence,operations=ops,
     feature_trial_operations=trials,before_nonzeros=before,after_nonzeros=len(new)))
   row=new
  target_out.append(dict(target,terms=expression_terms(row)))
  paths.append(dict(target=target["id"],status=status,path=path))
 return target_out,dict(load_seconds=load,preprocess_seconds=time.perf_counter()-begin,paths=paths,
  coefficient_field_operations=allops,feature_trial_field_operations=alltrials,point=point,prime=prime,
  used_learned_scores=learned)
def native(fam,trim,w,plan):
 w.mkdir();(w/"config").mkdir()
 # JSON is valid YAML; preserve exact public masses and scalar products.
 definition=fam["definition"];N=len(definition["propagators"]);external=definition["external_momenta"]
 config={"integralfamilies":[dict(name="F",loop_momenta=definition["loop_momenta"],
    top_level_sectors=definition["top_level_sectors"],
    propagators=[[p["momentum"],p["mass_squared"]] for p in definition["propagators"]])]}
 kin={"kinematics":dict(incoming_momenta=external+["qaux"],outgoing_momenta=[],
   momentum_conservation=["qaux","-"+"-".join(external) if external else "0"],
   kinematic_invariants=[[v,2] for v in definition["invariants"]],scalarproduct_rules=definition["scalarproduct_rules"])}
 if not external:
  kin["kinematics"]["incoming_momenta"]=[]
  kin["kinematics"]["momentum_conservation"]=[]
 (w/"config/integralfamilies.yaml").write_text(json.dumps(config))
 (w/"config/kinematics.yaml").write_text(json.dumps(kin))
 component=sorted({tuple(t["indices"]) for x in fam["targets"] for t in x["terms"]})
 def label(a):return "F["+",".join(map(str,a))+"]"
 (w/"targets").write_text("".join(label(a)+"\n" for a in component))
 (w/"masters").write_text("".join(label(a)+"\n" for a in fam["masters"]))
 bounds=component+fam["masters"]
 r=max(sum(max(0,v) for v in a) for a in bounds)+1
 s=max(sum(max(0,-v) for v in a) for a in bounds)+1
 spec=dict(topologies=["F"],sectors=definition["top_level_sectors"],r=r,s=s)
 reduction=dict(reduce=[spec],select_integrals={"select_mandatory_list":[["targets"]]},
  preferred_masters="masters",run_initiate=True,run_triangular=True,run_back_substitution=True)
 if trim:
  spec["d"]=max(sum(max(0,v-1) for v in a) for a in bounds)+1
  reduction["truncate_sp"]=[dict(topologies=["F"],l=N-s)]
 (w/"jobs.yaml").write_text(json.dumps({"jobs":[{"reduce_sectors":reduction},{"kira2file":{"target":[["targets"]]}}]}))
 result=kira_run(w,plan)
 paths=list((w/"results/F").glob("kira_targets.kira"))
 if len(paths)!=1:raise ValueError("Missing native export")
 from s17_native_combine import combine
 output,combination=combine(fam,paths[0],w/"combine",plan,supplied)
 result.update(native_seconds=result["seconds"],combination=combination,
  seconds=result["seconds"]+combination["seconds"],bounds=spec,component_integrals=len(component),
  export_sha256=sha(paths[0]),combination_export_sha256=combination["export_sha256"])

 return output,result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("case",type=int);ap.add_argument("size",type=int);ap.add_argument("policy")
 ap.add_argument("scratch",type=pathlib.Path);ap.add_argument("output",type=pathlib.Path);args=ap.parse_args()
 import sympy as sp
 plan=read(HERE/"plan.json");begin=time.perf_counter();family=load_case(plan["family_cases"][args.case],args.size)
 result=dict(family=family["id"],loops=family["meta"]["loops"],domain=family["domain"],policy=args.policy,
  requested_size=args.size,targets=[x["id"] for x in family["targets"]],input_load_seconds=time.perf_counter()-begin)
 begin=time.perf_counter();attempts=[];details={};selected=None;targets=family["targets"]
 if args.policy=="ml_seeds":selected,details=seed_select(family)
 elif args.policy in ("ml_reduction","local_reduction"):targets,details=reduce_targets(family,args.policy=="ml_reduction")
 if args.policy.startswith("kira_native"):
  rows,attempt=native(family,args.policy.endswith("_trim"),args.scratch/"attempt0",plan)
 else:rows,attempt=supplied(family,targets,selected,args.scratch/"attempt0",plan)
 attempts.append(attempt)
 # Structural completeness uses only the prescribed public basis.
 complete=all(t["id"] in rows and all(a in family["masters"] or c==0 for a,c in rows[t["id"]].items()) for t in family["targets"])
 if not complete and args.policy=="ml_seeds":
  rows,attempt=supplied(family,family["targets"],None,args.scratch/"attempt1",plan);attempts.append(attempt)
 result.update(attempts=attempts,model=details,fallback=len(attempts)>1,first_attempt_complete=complete,
  warm_seconds=time.perf_counter()-begin-details.get("load_seconds",0))
 begin=time.perf_counter();checks=exact_check(rows,family)
 result.update(verification_seconds=time.perf_counter()-begin,checks=checks,success=all(x["status"]=="exact_match" for x in checks))
 result["warm_with_verification_seconds"]=result["warm_seconds"]+result["verification_seconds"]
 result["script_seconds"]=result["input_load_seconds"]+result["warm_seconds"]+details.get("load_seconds",0)+result["verification_seconds"]
 write(args.output,result)
 print(json.dumps(dict(family=result["family"],policy=args.policy,size=args.size,success=result["success"],seconds=result["script_seconds"])),flush=True)
if __name__=="__main__":main()
