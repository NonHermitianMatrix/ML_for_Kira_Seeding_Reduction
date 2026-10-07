"""Generate disjoint loop groups in three bounded scheduler array tasks."""
import concurrent.futures,json,os,socket,time
from s01_generate import HERE,ROOT,write,sha
from s15_generate_parallel import loop_group,guard
from pathlib import Path
def main():
 assert os.environ.get("JOB_ID") and int(os.environ.get("NSLOTS","1"))>=4
 task=int(os.environ["SGE_TASK_ID"]);assert task in (1,2,3)
 loops=list(range(4*task-3,4*task+1));started=time.time();initial=guard();result=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
  remaining={pool.submit(loop_group,L):L for L in loops};last=time.time()
  while remaining:
   done,_=concurrent.futures.wait(remaining,timeout=30,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:
    L=remaining.pop(future);result.extend(future.result());print("Completed loop",L,flush=True)
   counts={}
   for L in loops:
    p=HERE/("loop_%02d_progress.json"%L)
    if p.exists():counts[str(L)]=json.loads(p.read_text())["completed"]
   write(HERE/("group_%d_progress.json"%task),dict(group=task,loops=loops,completed=sum(counts.values()),per_loop=counts,total=4000,elapsed_seconds=time.time()-started))
   if time.time()-last>300+task*30:guard();last=time.time()
 assert len(result)==4000
 write(HERE/("group_%d_summary.json"%task),dict(status="complete",group=task,loops=loops,families=result,workers=4,host=socket.gethostname(),job_id=os.environ["JOB_ID"],elapsed_seconds=time.time()-started,initial_project_bytes=initial,final_project_bytes=guard(),runner_sha256=sha(Path(__file__))))
if __name__=="__main__":main()
