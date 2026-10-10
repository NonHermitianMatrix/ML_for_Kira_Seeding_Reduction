"""Choose temporary-storage placement from the separate exact native pilot."""
import hashlib,json,math,pathlib,statistics
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
def configuration():
 ratios=[];hashes={}
 for margin in [0,1]:
  times={}
  for location in ["project","node"]:
   times[location]=[]
   for repeat in range(2):
    p=HERE/"scratch_pilot"/f"m{margin}_{location}_r{repeat}.json.gz"
    r=read_record(p);assert r["success"] and not r.get("mismatches")
    hashes[str(p.relative_to(HERE))]=hashlib.sha256(p.read_bytes()).hexdigest()
    times[location].append(r["complete_seconds"])
  ratios.append(statistics.median(times["node"])/statistics.median(times["project"]))
 ratio=math.exp(sum(map(math.log,ratios))/len(ratios))
 record=dict(scratch_location="node" if ratio<1 else "project",node_to_project_ratio=ratio,pilot_sha256=hashes,scope="native validation scratch placement; no learned-policy claim")
 p=HERE/"runtime_config.json"
 if p.exists():assert json.loads(p.read_text())==record
 else:p.write_text(json.dumps(record,indent=2)+"\n")
 return record
if __name__=="__main__":print(json.dumps(configuration()))
