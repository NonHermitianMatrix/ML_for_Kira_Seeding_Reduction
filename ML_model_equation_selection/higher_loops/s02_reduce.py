"""Generate a sufficient equation system, run bounded Kira and check exact coefficients."""
import argparse,gzip,hashlib,json,os,re,resource,shutil,signal,socket,subprocess,tempfile,threading,time
from s00_math import *
from s10_polynomial import parse as coefficient_reader
BINARY=ROOT/".tools/kira-early-generation/kira"
FERMAT=ROOT/".tools/Ferl7/fer64"
JOBS="""jobs:
  - reduce_user_defined_system:
      input_system: {files: ["system.kira"], config: false, otf: false}
      select_integrals:
        select_mandatory_list:
          - [targets]
      preferred_masters: masters
      run_initiate: true
      run_triangular: true
      run_back_substitution: true
  - kira2file:
      target:
        - [targets]
"""
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allocated(path):
 return sum(p.stat().st_blocks*512 for p in path.rglob("*") if p.is_file())
def rss(pid):
 todo=[pid];seen=set();total=0
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p);base=Path("/proc")/str(p)
  try:
   for line in (base/"status").read_text().splitlines():
    if line.startswith("VmRSS:"):total+=int(line.split()[1])*1024
   for t in (base/"task").iterdir():
    try:todo.extend(map(int,(t/"children").read_text().split()))
    except OSError:pass
  except OSError:pass
 return total
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(1800*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def run_kira(w):
 env=dict(os.environ,FERMATPATH=str(FERMAT),KIRA_COST_MODE="native",KIRA_EQ_MODE="off",KIRA_BOUNDED_BACKSUB="1")
 for key in list(env):
  if key.startswith("KIRA_ML_") or key in ("KIRA_EQ_WEIGHTS","KIRA_EQ_CONTEXT"):env.pop(key,None)
 start=time.perf_counter();peak=0;disk=0;reason=None
 with (w/"run.log").open("w") as log:
  p=subprocess.Popen([str(BINARY),"--parallel=1","jobs.yaml"],cwd=w,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits)
  done=threading.Event()
  def wait():p.wait();done.set()
  threading.Thread(target=wait,daemon=True).start()
  ticks=0
  while not done.is_set():
   peak=max(peak,rss(p.pid))
   if ticks%5==0:disk=max(disk,allocated(w))
   if time.perf_counter()-start>90:reason="timeout"
   if peak>1500*1024**2:reason="rss_limit"
   if disk>64*1024**2:reason="scratch_limit"
   if reason:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=2)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    break
   done.wait(.05);ticks+=1
 result=dict(seconds=time.perf_counter()-start,returncode=p.returncode,peak_tree_rss_bytes=peak,peak_scratch_bytes=max(disk,allocated(w)),reason=reason)
 text=(w/"run.log").read_text(errors="replace")
 result["log"]=text
 if p.returncode or reason:raise RuntimeError(json.dumps(result))
 return result
def parse(text):
 rows={};block=[]
 def consume(lines):
  pairs=[]
  for line in lines:
   m=re.fullmatch(r"(\d+)\*\((.*)\)",line.strip());assert m,line
   pairs.append((int(m[1]),m[2]))
  assert pairs[0][1]=="-1",pairs[0]
  assert pairs[0][0] not in rows
  rows[pairs[0][0]]={i:c for i,c in pairs[1:]}
 for line in text.splitlines()+[""]:
  if line.strip():block.append(line)
  elif block:consume(block);block=[]
 return rows
def export(request,mode,nodes,w,L=None):
 begin=time.perf_counter();r=len(request["mass_ratios"]);targets=list(map(tuple,request["targets"]));rho=request["mass_ratios"]
 if mode=="dense":descriptors=dense(r,max(map(sum,targets)));decision_count=0
 else:
  picked,decision_count=closure(targets,mode,nodes);descriptors=list(picked.items())
 selection_seconds=time.perf_counter()-begin
 equations=[equation(b,p,rho,L) for b,p in descriptors]
 masters=[tuple(int(i==j) for i in range(r)) for j in range(r)]
 columns=set(targets)|{a for row in equations for a in row}
 ordered=masters+sorted(columns-set(masters),key=lambda b:(sum(b),b))
 mapping={a:i for i,a in enumerate(ordered)}
 with (w/"system.kira").open("w") as f:
  for row in equations:
   for b,c in row.items():f.write(str(mapping[b])+"*("+c+")\n")
   f.write("\n")
  for n,b in enumerate(targets):f.write(str(len(ordered)+n)+"*(1)\n"+str(mapping[b])+"*(-1)\n\n")
 (w/"targets").write_text("".join(str(len(ordered)+n)+"\n" for n in range(len(targets))))
 (w/"masters").write_text("".join(str(i)+"\n" for i in range(r)))
 (w/"jobs.yaml").write_text(JOBS)
 return dict(selection_seconds=selection_seconds,equations=len(equations),source_terms=sum(map(len,equations)),columns=len(ordered),target_start=len(ordered),decisions=decision_count,ibp_equations=sum(p is None or len(p)==1 for _,p in descriptors),partial_fraction_equations=sum(p is not None and len(p)==2 for _,p in descriptors),input_sha256=sha(w/"system.kira"),source_choices=[[list(b),list(p) if p is not None else None] for b,p in descriptors])
def solve(request,mode,model=None,L=None):
 root=Path(os.environ.get("TMPDIR",str(ROOT/".tools/kira-higher-loops")))
 assert os.environ.get("JOB_ID"),"Use a scheduled cluster job"
 w=Path(tempfile.mkdtemp(prefix="kira_high_",dir=root));start=time.perf_counter()
 try:
  nodes=None
  if mode=="learned":nodes=json.loads((HERE/"trained_model"/model).read_text())["nodes"]
  model_load_seconds=time.perf_counter()-start
  info=export(request,mode,nodes,w,L);info["model_load_seconds"]=model_load_seconds;prep=time.perf_counter()-start
  result=run_kira(w)
  raw=(w/"results/Tuserweight/kira_targets.kira").read_text();t=time.perf_counter();out=parse(raw);coefficients=[]
  r=len(request["mass_ratios"])
  for i,b in enumerate(request["targets"]):
   row=out[info["target_start"]+i]
   assert all(0<=j<r for j in row),"Unresolved integral"
   coefficients.append({j:coefficient_reader(c,"z" if L is None else "d") for j,c in row.items()})
  return coefficients,dict(info,loop=L,preparation_seconds=prep,algebra=result,parse_seconds=time.perf_counter()-t,raw_export=raw,solver_complete_seconds=time.perf_counter()-start)
 finally:shutil.rmtree(w)
def apply(request,mode="learned",model="depth8.json",shared=True):
 start=time.perf_counter();validate(request);attempts=[];coefficients={};fallbacks=0
 if shared:
  try:raw,info=solve(request,mode,model);attempts.append(info)
  except (AssertionError,RuntimeError,KeyError) as e:
   if mode=="dense":raise
   attempts.append(dict(failure=str(e),seconds=time.perf_counter()-start));fallbacks+=1
   raw,info=solve(request,"dense");attempts.append(info)
  t=time.perf_counter()
  for L in request["loops"]:
   coefficients[L]=[{j:canonical(poly_substitute(p,L)) for j,p in row.items()} for row in raw]
  substitution_seconds=time.perf_counter()-t
 else:
  substitution_seconds=0
  for L in request["loops"]:
   raw,info=solve(request,mode,model,L);attempts.append(info)
   coefficients[L]=[{j:canonical(p) for j,p in row.items()} for row in raw]
 t=time.perf_counter();checks=0
 for L,rows in coefficients.items():
  for b,row in zip(request["targets"],rows):
   want=oracle(L,request["mass_ratios"],tuple(b))
   assert all(canonical(row.get(j,()))==canonical(want.get(j,())) for j in set(row)|set(want)),(L,b,row,want)
   checks+=len(set(row)|set(want))
 verification=time.perf_counter()-t
 return dict(case=request["id"],mode=mode,model=model if mode=="learned" else None,shared=shared,loops=request["loops"],targets=len(request["targets"]),success=True,coefficient_checks=checks,complete_seconds=time.perf_counter()-start,substitution_seconds=substitution_seconds,verification_seconds=verification,fallbacks=fallbacks,attempts=attempts,worker_host=socket.gethostname(),binary_sha256=sha(BINARY),driver_sha256=sha(Path(__file__)),math_sha256=sha(HERE/"s00_math.py"),reader_sha256=sha(HERE/"s10_polynomial.py"))
def compact_save(path,result):
 result=dict(result);result["attempts"]=[dict(a) for a in result["attempts"]]
 for a in result["attempts"]:
  payload={k:a.pop(k) for k in ["raw_export","source_choices"] if k in a}
  if "algebra" in a:
   a["algebra"]=dict(a["algebra"]);payload["log"]=a["algebra"].pop("log")
  data=json.dumps(payload,sort_keys=True,separators=(",",":")).encode();digest=hashlib.sha256(data).hexdigest()
  obj=HERE/"objects"/(digest+".json.gz");obj.parent.mkdir(exist_ok=True)
  if not obj.exists():
   with gzip.open(obj,"wb",compresslevel=9) as f:f.write(data)
  a["payload_sha256"]=digest
 write(path,result)
 assert allocated(HERE)<json.loads((HERE/"resource_plan.json").read_text())["new_retained_cap_bytes"]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--mode",choices=["dense","first","smallest","largest","extreme","learned"],default="learned")
 ap.add_argument("--model",default="depth8.json");ap.add_argument("--separate-loops",action="store_true");a=ap.parse_args()
 start=time.perf_counter();request=json.loads(a.input.read_text())
 result=apply(request,a.mode,a.model,not a.separate_loops);result["complete_seconds"]=time.perf_counter()-start
 compact_save(a.output,result)
 print(json.dumps({k:result[k] for k in ["case","success","complete_seconds","coefficient_checks"]}),flush=True)
if __name__=="__main__":main()
