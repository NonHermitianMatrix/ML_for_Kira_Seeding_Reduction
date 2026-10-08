"""Export disjoint seed selections and read Kira's exact symbolic reductions."""
import os,resource,shutil,subprocess,time,re
from pathlib import Path
from s02_common import *
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
def allocated(p):
 total=0
 for base,dirs,files in os.walk(str(p)):
  for name in files:
   try:total+=os.stat(os.path.join(base,name)).st_blocks*512
   except FileNotFoundError:pass
 return total
def batches(blocks,limit=50000):
 batch=[];n=0
 for b in blocks:
  size=len(b["equations"])+len(b["targets"])
  if batch and n+size>limit:yield batch;batch=[];n=0
  if size>120000:raise ValueError("Single component equation limit")
  batch.append(b);n+=size
 if batch:yield batch
def export(family,blocks,w,quotient=True):
 w.mkdir(parents=True,exist_ok=False)
 masters=family["masters"];counter=0;maps={};targetmap={};reverse={};basis=[]
 # All protected master copies precede every other integral copy.
 for b in blocks:
  mapping={}
  for a in masters:
   mapping[a]=counter;basis.append(counter);reverse[counter]=(b["id"],a);counter+=1
  maps[b["id"]]=mapping
 for b in blocks:
  mapping=maps[b["id"]]
  columns={tuple(t["indices"]) for e in b["equations"] for t in e["terms"]}
  columns.update(tuple(t["indices"]) for x in b["targets"] for t in x["terms"])
  for a in sorted(columns-set(mapping),key=index_key):
   mapping[a]=counter;reverse[counter]=(b["id"],a);counter+=1
 for b in blocks:
  for target in b["targets"]:
   targetmap[counter]=(b["id"],target["id"]);counter+=1
 lookup={(bid,tid):weight for weight,(bid,tid) in targetmap.items()}
 lines=0
 with (w/"system.kira").open("w") as out:
  for b in blocks:
   mapping=maps[b["id"]]
   for e in b["equations"]:
    for term in e["terms"]:
     out.write("%d*(%s)\n"%(mapping[tuple(term["indices"])],"".join(term["coefficient"].split()).replace("**","^")))
    out.write("\n");lines+=1
   for target in b["targets"]:
    out.write("%d*(1)\n"%lookup[b["id"],target["id"]])
    for term in target["terms"]:
     out.write("%d*(-(%s))\n"%(mapping[tuple(term["indices"])],"".join(term["coefficient"].split()).replace("**","^")))
    out.write("\n");lines+=1
 if quotient:
  with (w/"system.kira").open("a") as out:
   for i in basis:out.write("%d*(1)\n\n"%i);lines+=1
 assert (w/"system.kira").stat().st_size<32000000
 (w/"targets").write_text("".join("%d\n"%i for i in targetmap))
 (w/"masters").write_text("".join("%d\n"%i for i in basis))
 (w/"jobs.yaml").write_text(JOBS)
 manifest=dict(family=family["id"],blocks=[dict(id=b["id"],candidate_positions=b["mask"],policies=b["policies"],
   source_equations=[e["id"] for e in b["equations"]],available_equations=b["available_equations"],
   ibp_equations=b["ibp_equations"],background_equations=b["background_equations"]) for b in blocks],
   mapping={str(i):dict(block=bid,indices=list(a)) for i,(bid,a) in reverse.items()},
   targets={str(i):dict(block=bid,target=tid) for i,(bid,tid) in targetmap.items()},
   input_sha256=sha(w/"system.kira"),equations=lines,columns=counter,
   test_space="quotient by the specified master span" if quotient else "explicit coefficients",master_unit_rows=basis if quotient else [])
 return manifest
def run_once(w,timeout=600,scratch_limit=67108864):
 env=dict(os.environ,FERMATPATH=str(ROOT/".tools/Ferl7/fer64"),OMP_NUM_THREADS="1",
          OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1")
 start=time.monotonic();reason=None;peak=allocated(w)
 with (w/"run.log").open("wb") as log:
  proc=subprocess.Popen([str(ROOT/".tools/kira/bin/kira"),"--parallel=1","jobs.yaml"],cwd=str(w),env=env,
                        stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  while proc.poll() is None:
   if time.monotonic()-start>timeout:reason="timeout"
   size=allocated(w);peak=max(peak,size)
   if size>scratch_limit:reason="scratch_limit"
   if reason:
    import signal
    os.killpg(proc.pid,signal.SIGTERM)
    try:proc.wait(timeout=3)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
    break
   time.sleep(.2)
 result=dict(returncode=proc.returncode,seconds=time.monotonic()-start,status=reason or ("completed" if proc.returncode==0 else "kira_error"),
             peak_scratch_allocated_bytes=peak,log_sha256=sha(w/"run.log"))
 output=w/"results/Tuserweight/kira_targets.kira"
 if output.exists():result.update(output_sha256=sha(output),output_bytes=output.stat().st_size)
 return result
def run_kira(w,timeout=600,scratch_limit=67108864):
 input_hash=sha(w/"system.kira");result=run_once(w,timeout,scratch_limit)
 assert sha(w/"system.kira")==input_hash
 result["input_sha256"]=input_hash
 if result["status"]!="completed":
  result["log_tail"]=(w/"run.log").read_text(errors="replace")[-12000:]
 return result
def parse_output(path):
 result={};block=[]
 def consume(lines):
  parsed=[]
  for line in lines:
   m=re.fullmatch(r"([0-9]+)\*\((.*)\)",line.strip())
   if not m:raise ValueError("Unexpected Kira output: "+line[:200])
   i=int(m.group(1));c=m.group(2).replace("^","**");validate_expression(c);parsed.append((i,c))
  lhs,coefficient=parsed[0]
  assert exact_equal(coefficient,"-1"),("Unexpected target coefficient",lhs,coefficient)
  assert lhs not in result
  values=collections.defaultdict(list)
  for i,c in parsed[1:]:values[i].append(c)
  result[lhs]={i:"+".join("("+v+")" for v in cs) for i,cs in values.items()}
 with Path(path).open() as f:
  for line in f:
   if line.strip():block.append(line)
   elif block:consume(block);block=[]
 if block:consume(block)
 return result
def assess(family,manifest,output,reference_by_id):
 masters=set(family["masters"]);records=[]
 for weight,t in manifest["targets"].items():
  bid=t["block"];tid=t["target"];row=output.get(int(weight));terms=[];residual=[]
  if row is None:
   records.append(dict(block=bid,target=tid,status="missing_export"));continue
  for i,c in row.items():
   if exact_zero(c):continue
   entry=manifest["mapping"].get(str(i))
   assert entry is not None,("Auxiliary variable in result",i)
   assert entry["block"]==bid,("Cross-system variable",bid,entry)
   a=tuple(entry["indices"]);terms.append(dict(indices=list(a),coefficient=c))
   if a not in masters:residual.append(list(a))
  if residual:state="residual_nonmasters"
  else:
   expected=collections.defaultdict(list)
   for term in reference_by_id[tid]["master_coefficients"]:expected[tuple(term["indices"])].append(term["coefficient"])
   predicted={tuple(t["indices"]):t["coefficient"] for t in terms}
   good=all(exact_equal(predicted.get(a,"0"),"+".join("("+v+")" for v in expected.get(a,["0"]))) for a in masters)
   state="exact_match" if good else "coefficient_mismatch"
  records.append(dict(block=bid,target=tid,status=state,terms=terms,residual_indices=residual))
 return records

def assess_span(family,manifest,output,reference_by_id):
 from s08_verify import nonzero_witness
 masters=set(family["masters"]);records=[]
 for weight,t in manifest["targets"].items():
  bid=t["block"];tid=t["target"];row=output.get(int(weight));terms=[];witnesses=[]
  if row is None:raise ValueError("Missing quotient-space export: "+tid)
  points=reference_by_id[tid]["samples"]
  for i,c in row.items():
   entry=manifest["mapping"].get(str(i))
   assert entry is not None and entry["block"]==bid,("Unexpected output variable",i,entry)
   a=tuple(entry["indices"])
   if a in masters:continue
   witness=nonzero_witness(c,points)
   if witness is not None:
    terms.append(dict(indices=list(a),coefficient=c));witnesses.append(witness)
  records.append(dict(block=bid,target=tid,status="insufficient" if terms else "sufficient",
    residual_terms=terms,nonzero_witnesses=witnesses))
 return records
