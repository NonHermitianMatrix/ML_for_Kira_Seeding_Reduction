"""Evaluate disjoint held-out families on four allocated CPU slots, then aggregate."""
import hashlib,json,os,socket,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,obj):
 tmp=p.with_name(p.name+".part");tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(tmp,p)
def main():
 cfg=read(HERE/"test_config.json");workers=cfg.get("parallel_workers",1)
 assert os.environ.get("JOB_ID"),"Use a compute allocation"
 assert 1<=workers<=4 and int(os.environ.get("NSLOTS","1"))>=workers
 metas=[f for f in read(ROOT/"ML_model_seed_selection/split_manifest.json")["families"] if f["split"]=="test"]
 metas.sort(key=lambda f:(-f["loops"],f["family"]))
 groups=[[f["family"] for f in metas[i::workers]] for i in range(workers)]
 assert len(set().union(*(set(g) for g in groups)))==sum(map(len,groups))==len(metas)
 processes=[];handles=[];started=time.perf_counter()
 try:
  for i in range(workers):
   handle=(HERE/("worker_%02d.log"%i)).open("w",encoding="utf-8");handles.append(handle)
   proc=subprocess.Popen([sys.executable,str(HERE/"s02_evaluate.py"),"--worker",str(i),"--workers",str(workers)],
                         cwd=str(ROOT),stdout=handle,stderr=subprocess.STDOUT)
   processes.append(proc)
  while any(p.poll() is None for p in processes):
   if any(p.poll() not in (None,0) for p in processes):
    raise RuntimeError("A family-test worker failed; inspect worker logs")
   time.sleep(1)
  assert all(p.returncode==0 for p in processes)
 except BaseException:
  for p in processes:
   if p.poll() is None:p.terminate()
  for p in processes:
   try:p.wait(timeout=15)
   except subprocess.TimeoutExpired:p.kill();p.wait()
  raise
 finally:
  for handle in handles:handle.close()
 summaries=[read(HERE/("worker_%02d_status.json"%i)) for i in range(workers)]
 sig=summaries[0]["signature"]
 for i,s in enumerate(summaries):
  assert s["stage"]=="complete" and s["families"]==groups[i] and s["signature"]==sig
 record=dict(status="workers_complete",workers=workers,host=socket.gethostname(),
  job_id=os.environ["JOB_ID"],allocated_slots=int(os.environ["NSLOTS"]),
  thread_limit_per_worker=1,families_per_worker=list(map(len,groups)),families=len(metas),
  worker_max_rss_kib=[s["max_rss_kib"] for s in summaries],
  signature=sig,elapsed_seconds=time.perf_counter()-started,
  statement="Disjoint families share one compute node; both policies retain paired timing and fixed weights within every family.")
 write(HERE/"parallel_execution.json",record)
 subprocess.run([sys.executable,str(HERE/"s02_evaluate.py"),"--aggregate-only"],cwd=str(ROOT),check=True)
 record["status"]="complete";record["elapsed_seconds"]=time.perf_counter()-started
 write(HERE/"parallel_execution.json",record)
 print("Parallel frozen-family test complete",flush=True)
if __name__=="__main__":main()
