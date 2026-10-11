"""Store exactly the same trained trees in a bounded compact representation."""
import gzip,struct
from s00_common import *
def main():
 checks=0
 for name in ["forest4.json","forest16.json"]:
  model=json.loads((HERE/"trained_model"/name).read_text());data=struct.pack("<I",len(model["trees"]))
  for nodes in model["trees"]:
   data+=struct.pack("<I",len(nodes))+b"".join(struct.pack("<hdiid",*n) for n in nodes)
  (HERE/"trained_model"/name.replace(".json",".bin.gz")).write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
  compact=load_model(name);assert compact["trees"]==model["trees"]
  for c in (HERE/"validation/inputs").glob("*.json"):
   req=json.loads(c.read_text())
   for p in options(len(req["mass_ratios"])):
    x=feature(req["targets"],p);assert predict(compact,x)==predict(model,x);checks+=1
 write(HERE/"training/compact_check.json",dict(all_passed=True,identical_score_checks=checks,format="little-endian feature/threshold/children/value with lossless gzip"))
 print("compact identical scores",checks,flush=True)
if __name__=="__main__":main()
