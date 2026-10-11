"""Run independent paired groups on four explicitly allocated physical cores."""
from s00_cumulative import *
def main():
 assert os.environ.get("JOB_ID") and int(os.environ.get("NSLOTS","0"))==4
 check_freeze();guard()
 allowed=sorted(os.sched_getaffinity(0));cores=[];seen=set()
 for cpu in allowed:
  p=Path("/sys/devices/system/cpu")/("cpu"+str(cpu))/"topology"
  identity=((p/"physical_package_id").read_text().strip(),(p/"core_id").read_text().strip())
  if identity not in seen:cores.append(cpu);seen.add(identity)
 assert 4<=len(cores)<=8,(allowed,cores,"Expected the scheduler's four-core binding")
 cores=cores[:4]
 root=HERE/"test/shards";root.mkdir(parents=True,exist_ok=True)
 write(HERE/"test/environment.json",dict(worker_host=socket.gethostname(),job_id=os.environ["JOB_ID"],slots=4,allowed_cpus=allowed,selected_physical_cpus=cores,maximum_concurrent_workers=4,per_worker_thread_count=1))
 running=[];logs=[]
 try:
  for shard,cpu in enumerate(cores):
   log=(root/("part%d.log"%shard)).open("w");logs.append(log)
   cmd=["taskset","-c",str(cpu),sys.executable,str(HERE/"s03_study.py"),"shard","--shard",str(shard)]
   running.append(subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True))
  while any(p.poll() is None for p in running):
   if any(p.poll() not in (None,0) for p in running):raise RuntimeError("A comparison shard failed; records retained")
   guard();time.sleep(1)
  assert all(p.returncode==0 for p in running)
 finally:
  for p in running:
   if p.poll() is None:stop_tree(p.pid);p.wait(timeout=5)
  for log in logs:log.close()
 totals=[read(root/("part%d"%i)/"complete.json") for i in range(4)]
 assert all(x["all_exact"] and x["applications"]==30 for x in totals)
 check_freeze()
 write(HERE/"test/complete.json",dict(all_exact=True,applications=120,input_batches=8,repetitions=5,arms=ARMS,worker_host=socket.gethostname(),matched_core_binding=True,concurrent_workers=4))
 print("completed all 120 matched workflows",flush=True)
if __name__=="__main__":main()
