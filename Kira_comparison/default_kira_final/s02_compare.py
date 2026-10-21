"""Compare original Kira with the frozen final method on the 20 native requests."""
from pathlib import Path
import gzip,json,hashlib,os,sys,subprocess,time,socket,signal,shutil,statistics
H=Path(__file__).resolve().parent;R=H.parents[1];T=R/"ML_model_adaptive_reduction/triangle_reduction"
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix==".gz" else p.read_bytes())
def write(p,r):
 raw=gzip.compress(json.dumps(r,separators=(",",":")).encode(),mtime=0)
 assert len(raw)<2*1024**2
 p.write_bytes(raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get("JOB_ID")
protocol=read(H/"protocol.json.gz")
assert all(sha(R/p)==v for p,v in protocol["sources"].items())
sys.path.insert(0,str(T))
from s04_triangle_measure import compare
from s30_monitor import Scanner
scanner=Scanner()
from s00_triangle_common import helper
lim=helper().inputs.module("default_final_limits",helper().BLOCK/"s11_extension_test.py")
os.environ["KIRA_RUNTIME_SCRATCH"]="node"
cases=protocol["cases"];results=H/"results";results.mkdir(exist_ok=True)
for rep in range(3):
 for c in cases[::(-1 if rep%2 else 1)]:
  ref=read(T/"test_references"/(c["id"]+".json.gz"))
  for method in (["default","method"] if rep%2==0 else ["method","default"]):
   dest=results/(c["id"]+"_"+str(rep)+"_"+method+".json.gz")
   if dest.exists():continue
   inp=H/"request.json";out=H/"output.json.gz"
   inp.write_text(json.dumps(c));out.unlink(missing_ok=True)
   start=time.perf_counter()
   process=subprocess.Popen([sys.executable,str(H/"s01_request.py"),method,str(inp),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
   reason=None;err=b"";peak=0
   try:
    while process.poll() is None:
     scratch=[]
     for root in [Path(os.environ["TMPDIR"]),R/".tools/kira-integrated-runtime"]:
      scratch.extend(root.glob("ml_kira_*"))
     used=0
     for q in scratch:used+=scanner(q)
     peak=max(peak,used)
     if time.perf_counter()-start>60:reason="wall_time_limit"
     if used>8*1024**2:reason="scratch_limit"
     if reason:
      pids=list(lim.descendants(process.pid))
      for pid in pids:
       try:os.kill(pid,signal.SIGKILL)
       except ProcessLookupError:pass
      try:os.killpg(process.pid,signal.SIGKILL)
      except ProcessLookupError:pass
      process.wait()
      for q in scratch:
       if any(q.name.startswith("ml_kira_"+str(pid)+"_") for pid in pids+[process.pid]):shutil.rmtree(q,ignore_errors=True)
      break
     time.sleep(.02)
    _,err=process.communicate(timeout=5)
    r=read(out) if out.exists() else dict(success=False,status=reason or "missing_output")
   finally:
    inp.unlink(missing_ok=True);out.unlink(missing_ok=True)
   elapsed=time.perf_counter()-start
   ok,n=compare(c,r,ref)
   record=dict(case=c["id"],group=c["topology_group"],loops=len(c["definition"]["loop_momenta"]),repetition=rep,method=method,seconds=elapsed,verified=ok,checks=n,limit=reason,peak_scratch_bytes=peak,returncode=process.returncode,stderr_tail=err.decode(errors="replace")[-1500:],result=r,host=socket.gethostname())
   write(dest,record)
   print(rep,method,c["id"],round(elapsed,4),ok,reason,flush=True)
rows=[]
for c in cases:
 vals={m:[read(results/(c["id"]+"_"+str(rep)+"_"+m+".json.gz")) for rep in range(3)] for m in ["default","method"]}
 rows.append(dict(case=c["id"],group=c["topology_group"],loops=len(c["definition"]["loop_momenta"]),times={m:[v["seconds"] for v in vv] for m,vv in vals.items()},verified={m:all(v["verified"] for v in vv) for m,vv in vals.items()},statuses={m:[v["limit"] or v["result"].get("status",str(v["verified"])) for v in vv] for m,vv in vals.items()}))
groups={}
for g in sorted({r["group"] for r in rows}):
 rr=[r for r in rows if r["group"]==g];matched=[r for r in rr if all(r["verified"].values())]
 totals={m:sum(statistics.median(r["times"][m]) for r in matched) for m in ["default","method"]}
 groups[g]=dict(requests=len(rr),matched=len(matched),completed={m:sum(r["verified"][m] for r in rr) for m in ["default","method"]},seconds=totals,speedup=totals["default"]/totals["method"] if matched else None)
matched=[r for r in rows if all(r["verified"].values())]
totals={m:sum(statistics.median(r["times"][m]) for r in matched) for m in ["default","method"]}
summary=dict(complete=True,requests=len(cases),repetitions=3,matched=len(matched),rows=rows,groups=groups,seconds=totals,speedup=totals["default"]/totals["method"] if matched else None,checks=sum(read(p)["checks"] for p in results.glob("*.json.gz")),all_outputs_verified=all(all(r["verified"].values()) for r in rows),timer="fresh-request startup, input loading, preparation, inference, algebra, export reading, cleanup; coefficient audit outside",protocol_sha256=sha(H/"protocol.json.gz"))
(H/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({k:v for k,v in summary.items() if k not in ["rows","groups"]}),flush=True)
