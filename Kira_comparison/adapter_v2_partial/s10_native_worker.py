"""Native Kira seeding from frozen learned seed envelopes, with default fallback."""
import argparse,sys,time,pathlib,subprocess
from s01_common import *
from s02_worker import seed_select,kira_run
def native_selected(fam,trim,w,plan,selected):
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
  spec["d"]=max(sum(max(0,v-1) for v in a) for a in bounds)+1
  reduction["truncate_sp"]=[dict(topologies=["F"],l=N-s)]
 (w/"jobs.yaml").write_text(json.dumps({"jobs":[{"reduce_sectors":reduction},{"kira2file":{"target":[["targets"]]}}]}))
 result=kira_run(w,plan)
 paths=list((w/"results/F").glob("kira_targets.kira"))
 if len(paths)!=1:raise ValueError("Missing native export")
 import sympy as sp
 solved={};block=[]
 def consume(lines):
  entries=[]
  for line in lines:
   m=re.fullmatch(r"F\[([-\d,]+)\]\*\((.*)\)",line.strip())
   if not m:raise ValueError("Native output syntax: "+line[:200])
   entries.append((tuple(map(int,m[1].split(","))),sp.sympify(m[2].replace("^","**"),rational=True)))
  a,c=entries[0];assert c==-1
  out={}
  for b,v in entries[1:]:out[b]=out.get(b,0)+v
  solved[a]=out
 for line in paths[0].read_text().splitlines()+[""]:
  if line.strip():block.append(line)
  elif block:consume(block);block=[]
 output={}
 for target in fam["targets"]:
  out={}
  for a,c in rational_rows(target["terms"]).items():
   rhs=solved.get(a,{a:sp.S.One})
   for b,v in rhs.items():out[b]=out.get(b,0)+c*v
  output[target["id"]]={b:sp.cancel(v) for b,v in out.items() if v!=0}
 result.update(bounds=reduction['reduce'],component_integrals=len(component),export_sha256=sha(paths[0]))
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
  rows,a=native_selected(fam,args.policy=="kira_native_trim",args.scratch/"attempt0",
    dict(plan,timeout_seconds=70) if selected is not None else plan,selected)
  attempts.append(a);complete=all(t["id"] in rows and all(k in fam["masters"] or c==0 for k,c in rows[t["id"]].items()) for t in fam["targets"])
 except (RuntimeError,ValueError,subprocess.TimeoutExpired) as error:
  if args.policy!="ml_native_seeds":raise
  attempts.append(dict(seconds=time.perf_counter()-begin-model.get("load_seconds",0),error=str(error),
    counters={},bounds="learned envelope; see archived jobs.yaml"));rows={};complete=False
 if not complete and args.policy=="ml_native_seeds":
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
