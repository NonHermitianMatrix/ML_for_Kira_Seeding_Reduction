"""Bounded diagnostic of equivalent target-first quotient ordering."""
import gzip,shutil,collections
from s03_kira_adapter import *
from s08_verify import nonzero_witness,check_span_records
fid="box_profile_0078"
meta=next(m for m in read(MODEL/"split_manifest.json")["families"] if m["family"]==fid)
entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
family=load_family(meta,entries[fid]);blocks=selected_blocks(family)
w=Path(os.environ["KIRA_SCRATCH"])/"target_first";manifest=export(family,blocks,w,quotient=True)
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
manifest["master_unit_rows"]=[permutation[i] for i in manifest["master_unit_rows"]]
manifest["input_sha256"]=sha(w/"system.kira")
run=run_kira(w);dest=HERE/"quotient_ordering_pilot";dest.mkdir(exist_ok=True)
if run["status"]=="completed":
 refs={r["id"]:r for r in rows(DATA/meta["references"])}
 output=parse_output(w/"results/Tuserweight/kira_targets.kira");records=[]
 for weight,t in manifest["targets"].items():
  row=output.get(int(weight))
  if row is None:raise ValueError("Missing quotient output")
  witnesses=[]
  for k,c in row.items():
   witness=nonzero_witness(c,refs[t["target"]]["samples"])
   if witness is not None:witnesses.append(witness)
  records.append(dict(block=t["block"],target=t["target"],status="insufficient" if witnesses else "sufficient"))
 run["sample_checks"]=check_span_records(family,blocks,records,refs)
 counts={k:collections.Counter() for k in ["predicted","full","background"]}
 byblock={b["id"]:b for b in blocks}
 for r in records:
  for policy,ids in byblock[r["block"]]["policies"].items():
   if r["target"] in ids:counts[policy][r["status"]]+=1
 run["counts"]={k:dict(v) for k,v in counts.items()}
 write(dest/"records.json",records)
write(dest/"run.json",run);write(dest/"manifest.json",manifest)
for name in ["run.log","system.kira","results/Tuserweight/kira_targets.kira"]:
 if (w/name).exists():
  with (w/name).open("rb") as inp,gzip.open(str(dest/(name.replace("/","_")+".gz")),"wb") as out:shutil.copyfileobj(inp,out)
print(json.dumps(run),flush=True)
