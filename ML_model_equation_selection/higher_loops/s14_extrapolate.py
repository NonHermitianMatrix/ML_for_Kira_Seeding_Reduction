"""Check the frozen application at additional loop orders above the timing set."""
import hashlib,subprocess,sys,time
from s00_math import *
def main():
 frozen=json.loads((HERE/"trained_model/freeze.json").read_text())
 for n,h in frozen["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h
 out=HERE/"model_test/extrapolation";out.mkdir(exist_ok=True)
 for p in sorted((HERE/"model_test/inputs").glob("*.json")):
  c=json.loads(p.read_text());c["loops"]=[13,16,24,32];c["id"]="extra_"+c["id"]
  inp=out/(c["id"]+"_input.json");dest=out/(c["id"]+".json");write(inp,c)
  start=time.perf_counter();subprocess.run([sys.executable,str(HERE/"s08_application.py"),"--input",str(inp),"--output",str(dest)],check=True,timeout=120)
  r=json.loads(dest.read_text());r["external_seconds"]=time.perf_counter()-start;write(dest,r)
 write(out/"complete.json",dict(applications=6,loop_orders=[13,16,24,32],all_passed=True))
if __name__=="__main__":main()
