"""Run the frozen early equation policy with exact native fallback."""
import argparse,json,os,pathlib,time
from s04_workflows import HERE,PARENT,ROOT,OLD,EARLY,setup,workflow
from s06_validate import method
def structural_key(c):
 d=c["definition"]
 return dict(loop_momenta=d["loop_momenta"],external_momenta=d["external_momenta"],momenta=[p["momentum"] for p in d["propagators"]],physical_propagators=d["physical_propagators"],top_level_sectors=d["top_level_sectors"])
def previous(c,n):
 old=json.loads((PARENT/"trained_model/deployment_final.json").read_text())
 enabled=c["topology_group"]=="sunrise" and c["targets"][:n]==old["required_targets"]
 return dict(binary=OLD,mode="learned" if enabled else "off",threshold=old["threshold"] if enabled else 0,model="previous" if enabled else None)
def select(c,n,policy):
 if policy=="native":return dict(binary=EARLY)
 if policy=="previous":return previous(c,n)
 config=json.loads((HERE/"trained_model/deployment.json").read_text())
 domain=config["domains"].get(c["topology_group"])
 supported=domain is not None and structural_key(c)==domain["structure"] and c["targets"][:n]==domain["targets"].get(str(n))
 if not supported:return previous(c,n)
 if policy=="control":
  return dict(binary=EARLY,mode="distance",threshold=config["distance_by_topology"][c["topology_group"]])
 route=config["by_topology"][c["topology_group"]]
 if route["label"]=="previous":return previous(c,n)
 args=method(route["label"]);args.pop("label");args["binary"]=EARLY
 if policy=="deployed":
  if route.get("seed"):
   os.environ["KIRA_SEED_THRESHOLD"]=str(route["seed_thresholds"][str(n)])
   args["base"]="combined_closed" if route["row"] else "seed_closed"
  elif route["row"]:args["base"]="learned"
  if route["row"]:args["weights"]=ROOT/route["row_weights"]
 return args
def reduce(c,n,out,reference=None,basis=None,policy="deployed",started=None):
 start=time.perf_counter() if started is None else started
 args=select(c,n,policy)
 return workflow(c,n,label=policy,ref=reference,out=out,basis=basis,started=start,**args)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--family-file",type=pathlib.Path,required=True);ap.add_argument("--masters-file",type=pathlib.Path,required=True)
 ap.add_argument("--size",type=int,required=True);ap.add_argument("--output",type=pathlib.Path,required=True)
 ap.add_argument("--policy",choices=["deployed","native","previous"],default="deployed");a=ap.parse_args()
 setup();start=time.perf_counter()
 c=json.loads(a.family_file.read_text());c["split"]="application";basis=json.loads(a.masters_file.read_text())
 if isinstance(basis,dict):basis=basis["masters"]
 out=a.output.resolve()
 assert HERE in out.parents and not out.exists()
 assert 0<a.size<=len(c["targets"]) and isinstance(basis,list)
 r=reduce(c,a.size,out,basis=basis,policy=a.policy,started=start)
 print(json.dumps({k:r[k] for k in ["case","size","label","mode","model","base","success","complete_seconds","attempt_count","reference_checked"]}))
if __name__=="__main__":main()
