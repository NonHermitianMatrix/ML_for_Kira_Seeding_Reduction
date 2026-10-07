"""Generate disjoint loop-order groups on twelve allocated CPU slots."""
import concurrent.futures,json,os,resource,socket,subprocess,time
from pathlib import Path
from s01_generate import HERE,ROOT,generate,profiles,write,sha
def loop_group(L):
 start=time.time();results=[]
 for n,(p,rho) in enumerate(profiles(),1):
  result=generate(L,p,rho);results.append(result)
  if n%10==0 or n==1000:
   write(HERE/("loop_%02d_progress.json"%L),dict(loops=L,completed=n,total=1000,latest_family=result["family"],elapsed_seconds=time.time()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
 write(HERE/("loop_%02d_summary.json"%L),dict(loops=L,status="complete",families=results,elapsed_seconds=time.time()-start))
 return results
def guard():
 used=int(subprocess.check_output(["du","-s","-B1",str(ROOT)]).split()[0])
 assert used+200000000<8000000000,used
 return used
def main():
 assert os.environ.get("JOB_ID"),"Use a compute allocation"
 workers=12;assert int(os.environ.get("NSLOTS","1"))>=workers
 started=time.time();initial=guard();result=[];last_check=time.time()
 with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
  remaining={pool.submit(loop_group,L):L for L in range(1,13)}
  while remaining:
   done,_=concurrent.futures.wait(remaining,timeout=30,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:
    L=remaining.pop(future);result.extend(future.result());print("Completed loop order",L,flush=True)
   counts={}
   for L in range(1,13):
    p=HERE/("loop_%02d_progress.json"%L)
    if p.exists():counts[str(L)]=json.loads(p.read_text())["completed"]
   write(HERE/"parallel_progress.json",dict(status="generating",families_completed=sum(counts.values()),per_loop=counts,total=12000,elapsed_seconds=time.time()-started))
   if time.time()-last_check>300:guard();last_check=time.time()
 result.sort(key=lambda x:(x["loops"],x["profile"]))
 assert len(result)==12000 and len({x["family"] for x in result})==12000
 write(HERE/"generation_summary.json",dict(status="complete",families=result,elapsed_seconds=time.time()-started,
  master_count=sum(x["master_count"] for x in result),targets=sum(x["counts"]["targets"] for x in result),
  workers=workers,host=socket.gethostname(),job_id=os.environ["JOB_ID"],initial_project_bytes=initial,final_project_bytes=guard(),
  parallel_source_sha256=sha(Path(__file__))))
 print("Completed",len(result),"families",flush=True)
if __name__=="__main__":main()
