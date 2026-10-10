"""Apply the third policy with a prescribed basis; target reference coefficients are optional."""
import argparse,json,pathlib,time
from s04_experiment import setup,workflow
HERE=pathlib.Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--family-file",type=pathlib.Path,required=True);ap.add_argument("--masters-file",type=pathlib.Path,required=True);ap.add_argument("--size",type=int,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);ap.add_argument("--base",choices=["native","seed","row","both"],default="native");ap.add_argument("--force-model",action="store_true");a=ap.parse_args()
 start=time.perf_counter();c=json.loads(a.family_file.read_text());c["split"]="application";basis=json.loads(a.masters_file.read_text());basis=basis.get("masters") if isinstance(basis,dict) else basis
 config=json.loads((HERE/"trained_model/deployment.json").read_text());route=config.get("by_topology",{}).get(c["topology_group"],{"mode":"off","threshold":0})
 mode="learned" if a.force_model else route["mode"];threshold=config["threshold"] if a.force_model else route["threshold"]
 out=a.output.resolve();assert HERE in out.parents and not out.exists();setup()
 preparation=time.perf_counter()-start
 r=workflow(c,a.size,mode,threshold,out,None,base=a.base,basis=basis)
 print(json.dumps(dict(success=r["success"],mode=mode,base=a.base,input_and_routing_seconds=preparation,workflow_seconds=r["complete_seconds"],application_seconds=preparation+r["complete_seconds"],reference_coefficients_used=False)))
if __name__=="__main__":main()
