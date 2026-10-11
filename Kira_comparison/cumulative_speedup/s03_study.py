"""Execute paired frozen comparisons with resource monitoring."""
from s00_cumulative import *
import argparse,tempfile,shutil
def trial(inp,arm,rep,folder):
 dest=folder/(inp.stem+"_"+arm+"_"+str(rep)+".json")
 assert not dest.exists(),"Never overwrite an executed trial"
 command=[sys.executable,str(HERE/"s02_worker.py"),"--input",str(inp),"--output",str(dest),"--arm",arm]
 if rep==0:command.append("--archive-logs")
 scratch=tempfile.mkdtemp(prefix="kira_cumulative_",dir=os.environ.get("TMPDIR","/tmp"))
 env=dict(os.environ,TMPDIR=scratch)
 t=time.perf_counter();peak=0;disk=0;reason=None
 p=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True,preexec_fn=limits)
 tick=0
 try:
  while p.poll() is None:
   peak=max(peak,legacy.rss(p.pid))
   if tick%5==0:disk=max(disk,allocated(env["TMPDIR"]))
   if time.perf_counter()-t>1200:reason="wall_limit"
   if peak>2200*1024**2:reason="rss_limit"
   if disk>64*1024**2:reason="scratch_limit"
   if reason:stop_tree(p.pid);break
   time.sleep(.01);tick+=1
 except BaseException:
  stop_tree(p.pid);p.communicate(timeout=5);shutil.rmtree(scratch,ignore_errors=True);raise
 output=p.communicate(timeout=5)[0];elapsed=time.perf_counter()-t
 shutil.rmtree(scratch,ignore_errors=True)
 if p.returncode or reason:
  write(dest.with_suffix(".failure.json"),dict(arm=arm,input=inp.name,repetition=rep,reason=reason,returncode=p.returncode,seconds=elapsed,output=output[-12000:]))
  raise RuntimeError("Trial failed: "+str(dest))
 record=read(dest);start=time.perf_counter();values=backend.load_coeff(record,OBJECTS)["coefficients"];reading=time.perf_counter()-start
 record.update(input=inp.name,repetition=rep,external_seconds=elapsed,read_seconds=reading,roundtrip_seconds=elapsed+reading,canonical_coefficients_sha256=digest(values),peak_tree_rss_bytes=peak,peak_scratch_bytes=disk)
 write(dest,record);guard()
 print(json.dumps(dict(arm=arm,case=inp.stem,rep=rep,seconds=record["roundtrip_seconds"],success=record["success"])),flush=True)
 return record
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["pilot","freeze","test","shard"]);ap.add_argument("--shard",type=int);a=ap.parse_args()
 assert os.environ.get("JOB_ID");guard()
 if a.stage=="freeze":
  assert read(HERE/"pilot/complete.json")["all_exact"]
  assert not (HERE/"freeze.json").exists()
  files=frozen_files();write(HERE/"freeze.json",dict(sha256={str(p.relative_to(ROOT)):sha(p) for p in files},source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())))
  print("frozen",len(files),flush=True);return
 if a.stage=="pilot":inputs=[HERE/"pilot/input.json"];repeats=1;folder=HERE/"pilot/results"
 else:check_freeze();inputs=sorted((HERE/"test/inputs").glob("*.json"));repeats=5;folder=HERE/"test/results"
 if a.stage=="shard":
  assert a.shard in range(4)
  inputs=[inp for i,inp in enumerate(inputs) if i%4==a.shard]
 folder.mkdir(parents=True,exist_ok=True);results=[]
 stage_root=folder.parent if a.stage!="shard" else HERE/"test/shards"/("part%d"%a.shard)
 environment=dict(scratch_parent=os.environ.get("TMPDIR","/tmp"),scratch_filesystem=subprocess.check_output(["df","-PT",os.environ.get("TMPDIR","/tmp")]).decode(),host=socket.gethostname(),python=sys.version,job_id=os.environ.get("JOB_ID"),queue=os.environ.get("QUEUE"),slots=os.environ.get("NSLOTS","1"),cpu_model=next((x.split(":",1)[1].strip() for x in Path("/proc/cpuinfo").read_text().splitlines() if x.startswith("model name")),"unknown"),versions={})
 for name,binary in BINARIES.items():
  v=subprocess.run([str(binary),"--version"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=10)
  environment["versions"][name]=dict(returncode=v.returncode,text=v.stdout[:2000],sha256=sha(binary))
 write(stage_root/"environment.json",environment)
 blocks=[(inp,rep) for inp in inputs for rep in range(repeats)];rng=random.Random(911032);rng.shuffle(blocks)
 for inp,rep in blocks:
  arms=ARMS[:];rng.shuffle(arms);group=[]
  for arm in arms:
   dest=folder/(inp.stem+"_"+arm+"_"+str(rep)+".json")
   if dest.exists():
    r=read(dest);assert r["success"] and r["request_sha256"]==sha(inp) and r["repetition"]==rep
   else:r=trial(inp,arm,rep,folder)
   group.append(r);results.append(r)
  assert len({r["canonical_coefficients_sha256"] for r in group})==1,"Paired output mismatch"
 if a.stage in ("test","shard"):check_freeze()
 write(stage_root/"complete.json",dict(all_exact=True,applications=len(results),input_batches=len(inputs),repetitions=repeats,arms=ARMS,worker_host=socket.gethostname()))
 print("completed",a.stage,len(results),flush=True)
if __name__=="__main__":main()
