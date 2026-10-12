"""Reduce symbolic scattering targets using a supplied basis, without target answers."""
import argparse,json,pathlib,time
from s02_study import HERE,ROOT,setup,save
from s00_native_run import run
def reduce(case,masters,experimental_filter=False):
 started=time.perf_counter();attempts=[]
 size=len(case["targets"])
 assert 0<size<=128
 assert isinstance(masters,list) and all(isinstance(a,list) for a in masters)
 sequence=[("off",0),("off",1)]
 if experimental_filter:sequence.insert(0,("learned",0))
 for mode,margin in sequence:
  setup(mode)
  r=run(case,size,"native",HERE/"unused",timeout=150,margin=margin,basis=masters,
   records=False,archive=False,check_masters=True,scratch_cap=32*1024**2)
  attempts.append(r)
  assert not r["reference_checked"] and r["reference"] is None
  if r["success"]:break
 return dict(case=case["id"],success=attempts[-1]["success"],
  route="experimental_filter" if experimental_filter else "native_guard",
  complete_seconds=time.perf_counter()-started,attempts=attempts,fallback_count=len(attempts)-1,
  input_contains_reference_coefficients=False)
def main():
 ap=argparse.ArgumentParser()
 group=ap.add_mutually_exclusive_group(required=True)
 group.add_argument("--case");group.add_argument("--family-file",type=pathlib.Path)
 ap.add_argument("--masters-file",type=pathlib.Path,required=True)
 ap.add_argument("--output",type=pathlib.Path,required=True)
 ap.add_argument("--experimental-filter",action="store_true")
 a=ap.parse_args()
 if a.case:
  cases=json.loads((HERE/"cases.json").read_text())["cases"]
  case=next(c for c in cases if c["id"]==a.case)
 else:case=json.loads(a.family_file.read_text())
 masters=json.loads(a.masters_file.read_text());masters=masters.get("masters") if isinstance(masters,dict) else masters
 dest=a.output.resolve();assert HERE in dest.parents and not dest.exists()
 result=reduce(case,masters,a.experimental_filter);save(dest,result)
 print(json.dumps({k:v for k,v in result.items() if k!="attempts"}),flush=True)
 if not result["success"]:raise SystemExit(1)
if __name__=="__main__":main()
