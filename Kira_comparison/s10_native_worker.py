"""Native Kira seeding from frozen learned seed envelopes, with default fallback."""
import argparse,sys,time,pathlib,subprocess
from s01_common import *
from s02_worker import seed_select,kira_run,supplied
def native_selected(fam,trim,w,plan,selected,margin=1):
 phase_begin=time.perf_counter()
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
 r=max(sum(max(0,v) for v in a) for a in bounds)+margin
 s=max(sum(max(0,-v) for v in a) for a in bounds)+margin
 spec=dict(topologies=["F"],sectors=definition["top_level_sectors"],r=r,s=s)
 reduction=dict(reduce=[spec],select_integrals={"select_mandatory_list":[["targets"]]},
  preferred_masters="masters",run_initiate=True,run_triangular=True,run_back_substitution=True)
 if selected is not None:
  sectors={}
  for a in selected:
   sector=sum(1<<j for j,v in enumerate(a) if v>0)
   if not sector:continue
   r0=sum(max(0,v) for v in a);s0=sum(max(0,-v) for v in a);d0=sum(max(0,v-1) for v in a)
   v=sectors.setdefault(sector,dict(topologies=["F"],sectors=[sector],r=0,s=0,d=0))
   v["r"]=max(v["r"],r0);v["s"]=max(v["s"],s0);v["d"]=max(v["d"],d0)
  if not sectors:raise ValueError("empty_native_seed_envelope")
  reduction["reduce"]=[sectors[k] for k in sorted(sectors)]
 if trim:
  spec["d"]=max(sum(max(0,v-1) for v in a) for a in bounds)+margin
  reduction["truncate_sp"]=[dict(topologies=["F"],l=N-s)]
 (w/"jobs.yaml").write_text(json.dumps({"jobs":[{"reduce_sectors":reduction},{"kira2file":{"target":[["targets"]]}}]}))
 result=kira_run(w,plan)
 paths=list((w/"results/F").glob("kira_targets.kira"))
 if len(paths)!=1:raise ValueError("Missing native export")
 from s17_native_combine import combine
 remaining=plan["timeout_seconds"]-10-(time.perf_counter()-phase_begin)
 if remaining<=0:raise subprocess.TimeoutExpired("native_phase",plan["timeout_seconds"]-10)
 output,combination=combine(fam,paths[0],w/"combine",dict(plan,timeout_seconds=remaining+10),supplied)
 result.update(native_seconds=result["seconds"],combination=combination,
  seconds=result["seconds"]+combination["seconds"],bounds=reduction['reduce'],component_integrals=len(component),
  export_sha256=sha(paths[0]),combination_export_sha256=combination["export_sha256"])

 return output,result

def main():
 import sympy as sp
 ap=argparse.ArgumentParser();ap.add_argument("case",type=int);ap.add_argument("size",type=int);ap.add_argument("policy")
 ap.add_argument("scratch",type=pathlib.Path);ap.add_argument("output",type=pathlib.Path);args=ap.parse_args()
 plan=read(HERE/"native_seed/plan.json");begin=time.perf_counter();fam=load_case(plan["family_cases"][args.case],args.size)
 result=dict(family=fam["id"],loops=fam["meta"]["loops"],domain=fam["domain"],policy=args.policy,
  requested_size=args.size,targets=[t["id"] for t in fam["targets"]],input_load_seconds=time.perf_counter()-begin)
 begin=time.perf_counter();model={};attempts=[];selected=None
 if args.policy=="ml_native_seeds":selected,model=seed_select(fam)
 try:
  rows,a=native_selected(fam,args.policy in ("kira_native_trim","kira_native_tight"),args.scratch/"attempt0",
    dict(plan,timeout_seconds=70) if args.policy in ("ml_native_seeds","kira_native_tight") else plan,selected,
    margin=0 if args.policy=="kira_native_tight" else 1)
  attempts.append(a);complete=all(t["id"] in rows and all(k in fam["masters"] or c==0 for k,c in rows[t["id"]].items()) for t in fam["targets"])
 except (RuntimeError,ValueError,subprocess.TimeoutExpired) as error:
  if args.policy not in ("ml_native_seeds","kira_native_tight"):raise
  logpath=args.scratch/"attempt0/run.log"
  log=logpath.read_text(errors="replace") if logpath.exists() else ""
  counters={k:[int(v) for v in re.findall(pattern,log)] for k,pattern in {
    "generated_equations":r"(\d+) equations:\s*\d+ zero \+",
    "selected_equations":r"Number of selected equations to reduce:\s*(\d+)",
    "forward_insertions":r"redundant:\s*\d+; insertions (\d+)",
    "reduced_equations":r"(\d+) equations were reduced"}.items()}
  attempts.append(dict(seconds=time.perf_counter()-begin-model.get("load_seconds",0),error=str(error),
    counters=counters,bounds="initial native bounds; see archived jobs.yaml"));rows={};complete=False
 if not complete and args.policy in ("ml_native_seeds","kira_native_tight"):
  rows,a=native_selected(fam,False,args.scratch/"attempt1",dict(plan,timeout_seconds=110),None);attempts.append(a)
 result.update(attempts=attempts,model=model,fallback=len(attempts)>1,first_attempt_complete=complete,
   warm_seconds=time.perf_counter()-begin-model.get("load_seconds",0))
 begin=time.perf_counter();checks=exact_check(rows,fam)
 result.update(verification_seconds=time.perf_counter()-begin,checks=checks,success=all(x["status"]=="exact_match" for x in checks))
 result["warm_with_verification_seconds"]=result["warm_seconds"]+result["verification_seconds"]
 result["script_seconds"]=result["input_load_seconds"]+result["warm_seconds"]+model.get("load_seconds",0)+result["verification_seconds"]
 write(args.output,result)
 print(json.dumps(dict(family=fam["id"],policy=args.policy,success=result["success"])),flush=True)
if __name__=="__main__":main()
