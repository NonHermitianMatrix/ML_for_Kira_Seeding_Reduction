"""Check direct target ordering without changing seeds or source identities."""
import gzip,shutil
from s03_kira_adapter import *
meta=[m for m in read(MODEL/"split_manifest.json")["families"] if m["split"]=="test"][16]
entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
family=load_family(meta,entries[meta["family"]]);blocks=selected_blocks(family)
w=Path(os.environ["KIRA_SCRATCH"])/"target_first";manifest=export(family,blocks,w)
masters=set(family["masters"])
oldmasters=sorted(int(k) for k,v in manifest["mapping"].items() if tuple(v["indices"]) in masters)
oldtargets=sorted(map(int,manifest["targets"]))
oldothers=sorted(set(map(int,manifest["mapping"]))-set(oldmasters))
permutation={old:new for new,old in enumerate(oldmasters+oldtargets+oldothers)}
lines=[]
for line in (w/"system.kira").read_text().splitlines():
 if line.strip():
  weight,rest=line.split("*",1);line=str(permutation[int(weight)])+"*"+rest
 lines.append(line)
(w/"system.kira").write_text("\n".join(lines)+"\n")
(w/"masters").write_text("".join(str(permutation[i])+"\n" for i in oldmasters))
(w/"targets").write_text("".join(str(permutation[i])+"\n" for i in oldtargets))
manifest["mapping"]={str(permutation[int(k)]):v for k,v in manifest["mapping"].items()}
manifest["targets"]={str(permutation[int(k)]):v for k,v in manifest["targets"].items()}
manifest["input_sha256"]=sha(w/"system.kira")
run=run_kira(w);dest=HERE/"ordering_pilot";dest.mkdir(exist_ok=True)
write(dest/"run.json",run);write(dest/"manifest.json",manifest)
for name in ["run.log","system.kira","results/Tuserweight/kira_targets.kira","results/Tuserweight/masters"]:
 if (w/name).exists():
  with (w/name).open("rb") as inp,gzip.open(str(dest/(name.replace("/","_")+".gz")),"wb") as out:shutil.copyfileobj(inp,out)
print(json.dumps(run),flush=True)
