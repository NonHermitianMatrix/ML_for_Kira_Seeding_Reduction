"""Apply the confirmed equation policy within its measured target domain."""
import argparse,json,pathlib,time
from s04_experiment import HERE,setup,workflow
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--family-file",type=pathlib.Path,required=True);ap.add_argument("--masters-file",type=pathlib.Path,required=True);ap.add_argument("--size",type=int,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);ap.add_argument("--base",choices=["native","seed","row","both"],default="native");a=ap.parse_args()
 start=time.perf_counter();c=json.loads(a.family_file.read_text());c["split"]="application";basis=json.loads(a.masters_file.read_text());basis=basis.get("masters") if isinstance(basis,dict) else basis
 config=json.loads((HERE/"trained_model/deployment_confirmed.json").read_text())
 enabled=c["topology_group"]=="sunrise" and c["definition"]["kind"]=="sunrise" and len(c["definition"]["loop_momenta"])==2 and c["targets"][:a.size]==config["required_targets"]
 mode="learned" if enabled else "off";threshold=config["threshold"] if enabled else 0
 out=a.output.resolve();assert HERE in out.parents and not out.exists();setup();preparation=time.perf_counter()-start
 r=workflow(c,a.size,mode,threshold,out,None,base=a.base,basis=basis)
 print(json.dumps(dict(success=r["success"],mode=mode,base=a.base,input_and_routing_seconds=preparation,workflow_seconds=r["complete_seconds"],application_seconds=preparation+r["complete_seconds"],reference_coefficients_used=False,supported_equation_domain=enabled)))
if __name__=="__main__":main()
