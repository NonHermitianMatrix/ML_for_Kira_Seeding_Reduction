"""Run one bounded complete Kira reduction, retaining compact exact evidence."""
import argparse,gzip,hashlib,json,os,pathlib,re,resource,shutil,signal,subprocess,tempfile,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];MODEL=ROOT/"ML_model_reduction/cost_training"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
from s04_records import write_record as packed, read_record as read
def label(a):return "F["+",".join(map(str,a))+"]"
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2400*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def disk(path):
 size=0
 for p in path.rglob("*"):
  try:
   if p.is_file():size+=p.stat().st_blocks*512
  except FileNotFoundError:pass
 return size
def process_rss(pid):
 todo=[pid];seen=set();rss=0
 while todo:
  current=todo.pop()
  if current in seen:continue
  seen.add(current);base=pathlib.Path("/proc")/str(current)
  try:
   for line in (base/"status").read_text().splitlines():
    if line.startswith("VmRSS:"):rss+=1024*int(line.split()[1])
   for thread in (base/"task").iterdir():
    try:todo.extend(map(int,(thread/"children").read_text().split()))
    except (OSError,ValueError):pass
  except (OSError,ValueError):pass
 return rss
def parse_export(text):
 rows={};block=[]
 def consume(lines):
  pairs=[]
  for line in lines:
   m=re.fullmatch(r"F\[([^]]+)\]\*\((.*)\)",line.strip())
   if not m:raise ValueError("Unsupported native export line: "+line[:120])
   a=tuple(map(int,m[1].split(",")));pairs.append((a,m[2]))
  if pairs[0][1]!="-1":raise ValueError("Unexpected leading export coefficient")
  rows[",".join(map(str,pairs[0][0]))]=dict(((",".join(map(str,a))),c) for a,c in pairs[1:])
 for line in text.splitlines()+[""]:
  if line.strip():block.append(line)
  elif block:consume(block);block=[]
 return rows
def run(case,size,policy,output,timeout=300,margin=1,reference=None,weights=None,records=True,archive=True,check_masters=False,force=None,scratch_cap=None):
 assert case["split"]!="reserved" or (HERE/"freeze.json").exists(),"Reserved calculations require frozen policies"
 begin=time.perf_counter();p=None;definition=case["definition"];target=case["targets"][:size]
 assert len(target)==size,(case["id"],size,len(target))
 plan=json.loads((HERE/"resource_plan.json").read_text());cap=scratch_cap or plan["scratch_per_trial_bytes"]
 assert cap<=plan.get("reference_scratch_bytes",cap)
 scratch=pathlib.Path(tempfile.mkdtemp(prefix=f"run_{os.getpid()}_",dir=ROOT/".tools/kira-cost-training"))
 result=dict(case=case["id"],group=case["group"],topology=case["topology_group"],split=case["split"],
  loops=len(definition["loop_momenta"]),size=size,policy=policy,targets=target,margin=margin,
  success=False,complete=False,status="running",reference=str(reference) if reference else None)
 try:
  (scratch/"config").mkdir();n=len(definition["propagators"]);t=definition["physical_propagators"]
  config={"integralfamilies":[dict(name="F",loop_momenta=definition["loop_momenta"],top_level_sectors=definition["top_level_sectors"],
   propagators=[[p["momentum"],p["mass_squared"]] for p in definition["propagators"]])]}
  ext=definition["external_momenta"]
  kin=dict(incoming_momenta=ext+["qaux"] if ext else [],outgoing_momenta=[],
   momentum_conservation=["qaux","-"+"-".join(ext)] if ext else [],kinematic_invariants=[],scalarproduct_rules=definition["scalarproduct_rules"])
  (scratch/"config/integralfamilies.yaml").write_text(json.dumps(config))
  (scratch/"config/kinematics.yaml").write_text(json.dumps(dict(kinematics=kin)))
  (scratch/"targets").write_text("".join(label(a)+"\n" for a in target))
  r=max(sum(max(0,v) for v in a) for a in target)+margin
  s=max(sum(max(0,-v) for v in a) for a in target)+margin
  dots=max(sum(max(0,v-1) for v in a) for a in target)+margin
  spec=dict(topologies=["F"],sectors=definition["top_level_sectors"],r=r,s=s,d=dots)
  reduction=dict(reduce=[spec],select_integrals={"select_mandatory_list":[["targets"]]},
   run_initiate=True,run_triangular=True,run_back_substitution=True)
  if reference:
   ref=read(reference);basis=ref["masters"]
   (scratch/"masters").write_text("".join(label(a)+"\n" for a in basis));reduction["preferred_masters"]="masters"
  if check_masters or policy in ("seed","combined","seed_closed","combined_closed","closure","seed_closed_low","combined_closed_low"):
   if not reference:raise ValueError("Master admission needs a prescribed basis")
   reduction["check_masters"]=True
  if policy in ("seed","combined","seed_closed","combined_closed","closure","seed_closed_low","combined_closed_low"):
   from s07_seed import choose
   selected,predictions,timing=choose(definition,basis,target,spec,closure="closed" in policy or policy=="closure",use_model=policy!="closure",threshold=.001 if policy.endswith("_low") else .01)
   result["predictions"]=predictions;result["model"]=timing
   (scratch/"seeds.txt").write_text("".join(label(a)+"\n" for a in selected))
  jobs={"jobs":[{"reduce_sectors":reduction},{"kira2file":{"target":[["targets"]]}}]}
  (scratch/"jobs.yaml").write_text(json.dumps(jobs))
  binary=ROOT/(".tools/kira-fast-expression/kira" if policy=="stock" else ".tools/kira-cost-tree/kira")
  env=dict(os.environ,FERMATPATH=str(ROOT/".tools/Ferl7/fer64"),KIRA_COST_MODE="learned" if policy in ("combined","combined_closed","combined_closed_low") else policy if policy in ("collect","learned","forced") else "native",
   KIRA_COST_METRICS=str(scratch/"metrics.jsonl"),KIRA_COST_TRAIN_GROUPS="100")
  if records and policy in ("collect","learned","combined","combined_closed","combined_closed_low","forced"):env["KIRA_COST_RECORDS"]=str(scratch/"choices.jsonl")
  if force:
   env["KIRA_COST_FORCE_GROUP"]=str(force[0]);env["KIRA_COST_FORCE_SOURCE"]=str(force[1])
  if weights:env["KIRA_COST_WEIGHTS"]=str(weights)
  if policy in ("seed","combined","seed_closed","combined_closed","closure","seed_closed_low","combined_closed_low"):
   env["KIRA_ML_SEEDS"]=str(scratch/"seeds.txt");env["KIRA_ML_SEED_AUDIT"]=str(scratch/"seed_audit.json")
  result["limits"]=dict(complete_timeout_seconds=timeout,scratch_bytes=cap,tree_rss_bytes=2100*1024**2,address_bytes=2400*1024**2,file_bytes=64*1024**2)
  result["preparation_seconds"]=time.perf_counter()-begin
  start=time.perf_counter();reason=None;peak=0;peakdisk=0
  with (scratch/"run.log").open("w") as f:
   p=subprocess.Popen([str(binary),"--parallel=1","jobs.yaml"],cwd=scratch,env=env,stdout=f,stderr=subprocess.STDOUT,preexec_fn=limits,start_new_session=True)
   tick=0
   while p.poll() is None:
    elapsed=time.perf_counter()-start;peak=max(peak,process_rss(p.pid))
    if tick%4==0:peakdisk=max(peakdisk,disk(scratch))
    if elapsed>max(1,timeout-(start-begin)-10):reason="time_limit"
    elif peak>2100*1024**2:reason="memory_limit"
    elif peakdisk>cap:reason="scratch_limit"
    if reason:
     os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=2)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
     break
    time.sleep(.1);tick+=1
  result.update(kira_seconds=time.perf_counter()-start,returncode=p.returncode,peak_rss_bytes=peak,peak_scratch_bytes=peakdisk)
  log=(scratch/"run.log").read_text(errors="replace")
  result["log"]=log
  result["master_admission_rejected"]="check_masters: found additional master integrals" in log
  if (scratch/"seed_audit.json").exists():result["seed_audit"]=json.loads((scratch/"seed_audit.json").read_text())
  result["counters"]={k:[int(x) for x in re.findall(pattern,log)] for k,pattern in {
   "generated_equations":r"(\d+) equations:\s*\d+ zero \+",
   "selected_equations":r"Number of selected equations to reduce:\s*(\d+)",
   "forward_insertions":r"redundant:\s*\d+; insertions (\d+)"}.items()}
  result["metrics"]=[json.loads(x) for x in (scratch/"metrics.jsonl").read_text().splitlines()] if (scratch/"metrics.jsonl").exists() else []
  if (scratch/"choices.jsonl").exists():
   text=(scratch/"choices.jsonl").read_text();result["choice_sha256"]=hashlib.sha256(text.encode()).hexdigest()
   result["choices"]=[json.loads(x) for x in text.splitlines()]
  result["input"]=dict(config=config,kinematics=kin,jobs=jobs)
  paths=list((scratch/"results/F").glob("kira_targets.kira"))
  if p.returncode==0 and len(paths)==1:
   raw=paths[0].read_text();result["raw_export"]=raw;result["export_sha256"]=sha(paths[0])
   rows=parse_export(raw)
   # Kira omits identity reductions for explicitly declared master targets.
   # Restore only identities confirmed by its native export log.
   declared=re.findall(r"This requested integral is a master integral: F\[([^]]+)\]",log)
   for key in declared:
    if key not in rows:rows[key]={key:"1"}
   result["identity_master_targets"]=declared
   result["coefficients"]=rows
   result["masters"]=[list(map(int,k.split(","))) for k in sorted({k for row in rows.values() for k in row})]
   expected={",".join(map(str,a)) for a in target}
   result["complete"]=set(rows)==expected
   if reference and result["complete"]:
    def equal(left,right):
     if left==right:return True
     import sympy as sp
     return sp.cancel(sp.sympify(left.replace("^","**"),rational=True)-sp.sympify(right.replace("^","**"),rational=True))==0
    failures=[]
    for a,row in rows.items():
     want=ref["coefficients"].get(a)
     if want is None:failures.append(a);continue
     for m in set(row)|set(want):
      if not equal(row.get(m,"0"),want.get(m,"0")):failures.append(a);break
    result["mismatches"]=failures
    result["success"]=not failures
   else:result["success"]=result["complete"]
   result["status"]="completed" if result["success"] else "reference_mismatch" if reference else "missing_targets"
  else:result["status"]=reason or "kira_error"
 except Exception as e:result["status"]="exception";result["error"]=repr(e)
 finally:
  if p is not None and p.poll() is None:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   p.wait()
  result["complete_seconds"]=time.perf_counter()-begin
  result["reference_checked"]=bool(reference and result["success"])
  try:
   if archive:packed(output,result)
  finally:shutil.rmtree(scratch)
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("case");ap.add_argument("--size",type=int,default=8)
 ap.add_argument("--policy",default="stock");ap.add_argument("--timeout",type=int,default=300);ap.add_argument("--margin",type=int,default=1)
 ap.add_argument("--output",type=pathlib.Path,required=True);ap.add_argument("--reference",type=pathlib.Path);ap.add_argument("--weights",type=pathlib.Path)
 a=ap.parse_args();cases=json.loads((HERE/"families.json").read_text())["cases"];case=next(c for c in cases if c["id"]==a.case)
 assert case["split"]!="reserved" or (HERE/"freeze.json").exists(),"Reserved calculations require frozen policies"
 r=run(case,a.size,a.policy,a.output,a.timeout,a.margin,a.reference,a.weights)
 print(json.dumps({k:r[k] for k in ["case","size","policy","status","success","complete_seconds"]}),flush=True)
if __name__=="__main__":main()
