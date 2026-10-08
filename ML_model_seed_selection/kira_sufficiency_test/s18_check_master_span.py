"""Test exact membership in the span of identities and specified masters."""
import gzip,shutil,time
from s03_kira_adapter import *
metas=[m for m in read(MODEL/"split_manifest.json")["families"] if m["split"]=="test"]
entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
dest=HERE/"span_pilot";dest.mkdir(exist_ok=True)
for meta in [metas[0],metas[16],next(m for m in metas if m["family"]=="vacuum_L12_profile015")]:
 family=load_family(meta,entries[meta["family"]]);blocks=selected_blocks(family)
 w=Path(os.environ["KIRA_SCRATCH"])/meta["family"];manifest=export(family,blocks,w)
 manifest["input_sha256"]=sha(w/"system.kira");run=run_kira(w)
 write(dest/(meta["family"]+".run.json"),run);write(dest/(meta["family"]+".manifest.json"),manifest)
 for name in ["run.log","system.kira","results/Tuserweight/kira_targets.kira","results/Tuserweight/masters"]:
  if (w/name).exists():
   with (w/name).open("rb") as inp,gzip.open(str(dest/(meta["family"]+"_"+name.replace("/","_")+".gz")),"wb") as out:shutil.copyfileobj(inp,out)
 if run["status"]=="completed":
  result=parse_output(w/"results/Tuserweight/kira_targets.kira")
  counts={p:collections.Counter() for p in ["predicted","full","background"]};bb={b["id"]:b for b in manifest["blocks"]}
  for key,t in manifest["targets"].items():
   row=result.get(int(key));state="missing" if row is None else "complete" if all(exact_zero(c) for c in row.values()) else "incomplete"
   for policy,tids in bb[t["block"]]["policies"].items():
    if t["target"] in tids:counts[policy][state]+=1
  run["counts"]={p:dict(c) for p,c in counts.items()};write(dest/(meta["family"]+".run.json"),run)
 print(meta["family"],json.dumps(run),flush=True)
 shutil.rmtree(w)
