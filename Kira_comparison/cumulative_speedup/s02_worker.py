"""Run a complete matched reduction and save lossless exact coefficients."""
from s00_cumulative import *
import argparse
def original(requests,arm,archive_logs=False):
 start=time.perf_counter();legacy.BINARY=BINARIES[arm];coeff={};attempts=[];checks=0;verify=0.;evidence_seconds=0.
 for c in requests:
  legacy.validate(c);expanded={}
  for L in c["loops"]:
   rows,info=legacy.solve(c,"dense",L=L)
   t=time.perf_counter()
   for b,row in zip(c["targets"],rows):
    got={j:legacy.canonical(p) for j,p in row.items() if legacy.canonical(p)}
    want={j:legacy.canonical(p) for j,p in legacy.oracle(L,c["mass_ratios"],tuple(b)).items() if legacy.canonical(p)}
    assert got==want,(c["id"],L,b);checks+=len(want)
   verify+=time.perf_counter()-t
   expanded[str(L)]=packed(rows)
   t=time.perf_counter()
   raw=info.pop("raw_export")
   info["raw_export_sha256"]=backend.object_store(raw.encode(),".txt",OBJECTS)
   source=info.pop("source_choices")
   info["source_choices_sha256"]=digest(source)
   log=info["algebra"].pop("log")
   info["log_sha256"]=hashlib.sha256(log.encode()).hexdigest()
   if archive_logs:info["archived_log_sha256"]=backend.object_store(log.encode(),".txt",OBJECTS)
   info["profile"]=c["id"];attempts.append(info);evidence_seconds+=time.perf_counter()-t
  coeff[c["id"]]=expanded
 return dict(success=True,mode=arm,route="separate_dense",fallbacks=0,kira_invoked=True,attempts=attempts,coefficients=coeff,symbolic_coefficients={},source_choices=[],raw_export="",complete_seconds=time.perf_counter()-start,verification_seconds=verify,evidence_seconds=evidence_seconds,coefficient_checks=checks,solver_calls=len(attempts),kira_seconds=sum(a["algebra"]["seconds"] for a in attempts),preparation_seconds=sum(a["preparation_seconds"] for a in attempts),equations=sum(a["equations"] for a in attempts))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);ap.add_argument("--arm",choices=ARMS,required=True);ap.add_argument("--archive-logs",action="store_true");a=ap.parse_args()
 assert os.environ.get("JOB_ID")
 t=time.perf_counter();requests=read(a.input)["requests"]
 if a.arm=="final":
  dep=read(EXACT/"reader_final_deployment.json")
  result=engine.apply(requests,dep["mode"],{},dep["policy"])
  result["solver_calls"]=int(result["kira_invoked"]);result["evidence_seconds"]=0.
 else:result=original(requests,a.arm,a.archive_logs)
 result.update(complete_seconds=time.perf_counter()-t,request_sha256=sha(a.input),worker_host=socket.gethostname(),worker_pid=os.getpid(),worker_cpu_affinity=sorted(os.sched_getaffinity(0)),arm=a.arm)
 saved=backend.save(a.output,result,OBJECTS)
 print(json.dumps(dict(ok=saved["success"],arm=a.arm,coefficient_sha256=saved["coefficients_sha256"])),flush=True)
if __name__=="__main__":main()
