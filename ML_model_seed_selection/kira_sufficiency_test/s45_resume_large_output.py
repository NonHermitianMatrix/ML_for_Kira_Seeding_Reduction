"""Resume completed or stopped shards within the revised storage reserve."""
import argparse,gzip,shutil,traceback
import s06_evaluate as evaluation
from s06_evaluate import *
from s29_resume_small_batches import process
from s44_output_budget_80 import bounded_gzip,BUDGET
def main(index):
 assert index==10,"This reserve extension is assigned only to worker 10"
 limits=read(HERE/"resource_limits_v3.json")
 assert limits["worker_output_bytes"]==BUDGET
 for donor in limits["completed_donor_workers"]:
  donor_state=read(HERE/("worker_%02d.json"%donor))
  assert donor_state.get("finished") and not donor_state["errors"] and donor_state["completed"]==donor_state["assigned"]
  assert evaluation.output_allocated(HERE/"results"/("worker_%02d"%donor))<=limits["per_worker_output_reserves"][str(donor)]
 assert limits["combined_reserved_bytes"]<10000000000
 for name,digest in limits["scripts"].items():assert sha(HERE/name)==digest
 config=read(HERE/"protocol.json")
 for name,digest in config["scripts"].items():assert sha(HERE/name)==digest
 assert sha(MODEL/"trained_model.pt")==config["model_sha256"]
 assert sha(MODEL/"split_manifest.json")==config["split_sha256"]
 for key,path in [("kira_sha256",".tools/kira/bin/kira"),("fermat_sha256",".tools/Ferl7/fer64")]:
  assert sha(ROOT/path)==config[key]
 execution=read(HERE/"execution_overrides.json")
 assert execution["script_sha256"]==sha(HERE/"s29_resume_small_batches.py")
 assert execution["packing_sha256"]==sha(HERE/"s31_pack_small_batches.py")
 state_path=HERE/("worker_%02d.json"%index)
 previous=read(state_path)
 assert previous.get("finished"),"Do not overlap writers for one shard"
 if not previous["errors"] and previous["completed"]==previous["assigned"]:
  print("Worker already complete.",flush=True);return
 archive=HERE/"archive_output_allowance_v3";archive.mkdir(exist_ok=True)
 shutil.copyfile(str(state_path),str(archive/state_path.name))
 evaluation.bounded_gzip=bounded_gzip
 metas={m["family"]:m for m in read(MODEL/"split_manifest.json")["families"]}
 entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
 selected=config["family_ids"][index::config["workers"]]
 dest=HERE/"results"/("worker_%02d"%index)
 scratch=Path(os.environ["KIRA_SCRATCH"])/("worker_%02d"%index);scratch.mkdir(parents=True,exist_ok=True)
 assert shutil.disk_usage(str(scratch)).free>2*config["scratch_per_worker_bytes"]
 memory={line.split(":")[0]:int(line.split()[1]) for line in Path("/proc/meminfo").read_text().splitlines()}
 assert memory["MemAvailable"]>3*1024*1024
 status=dict(worker=index,assigned=len(selected),completed=0,errors=[],families=[],output_allowance_bytes=BUDGET)
 for fid in selected:
  try:
   clear_caches()
   if evaluation.output_allocated(dest)>BUDGET:raise RuntimeError("Worker output allowance reached")
   output=dest/(fid+".summary.json.gz")
   if output.exists():
    result=json.loads(gzip.open(str(output),"rt").read())
    assert result["prediction_sha256"]==entries[fid]["sha256"]
    assert all(sha(dest/b["detail"])==b["detail_sha256"] and sha(dest/b["output"])==b["output_sha256"] for b in result["batches"])
   else:result=process(metas[fid],entries[fid],dest,scratch)
   status["completed"]+=1;status["families"].append(fid);status["last_family"]=fid
   status["allocated_bytes"]=evaluation.output_allocated(dest);write(state_path,status)
   print(json.dumps(dict(worker=index,family=fid,counts=result["counts"])),flush=True)
  except Exception:
   status["errors"].append(dict(family=fid,traceback=traceback.format_exc()))
   write(state_path,status);print(json.dumps(status["errors"][-1]),flush=True)
   if scratch.exists():shutil.rmtree(scratch)
   scratch.mkdir(parents=True,exist_ok=True)
   if evaluation.output_allocated(dest)>BUDGET-1048576:break
 status["finished"]=True;write(state_path,status)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--worker",type=int,required=True);main(p.parse_args().worker)
