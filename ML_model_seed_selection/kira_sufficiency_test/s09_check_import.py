"""Check supported symbolic-system import modes on the small legacy-family pilot."""
import gzip,shutil,time
from s03_kira_adapter import *
metas={m["family"]:m for m in read(MODEL/"split_manifest.json")["families"] if m["split"]=="test"}
pred={x["family"]:x for x in read(MODEL/"model_test/prediction_manifest.json")["families"]}
fid="box_massless_one_offshell";family=load_family(metas[fid],pred[fid],limit=6)
blocks=selected_blocks(family);refs={x["id"]:x for x in rows(DATA/metas[fid]["references"])}
dest=HERE/"import_checks";dest.mkdir(exist_ok=True)
for name in ["compact_attempt0","compact_attempt1","compact_attempt2"]:
 w=Path(os.environ["KIRA_SCRATCH"])/name;manifest=export(family,blocks,w,quotient=False)
 if "compact" in name:
  content=(w/"system.kira").read_text()
  content="\n".join("".join(line.split()) for line in content.split("\n"))
  if "sort_" in name:
   groups=content.strip().split("\n\n")
   content="\n\n".join("\n".join(sorted(g.splitlines(),key=lambda s:int(s.split("*")[0]),reverse=True)) for g in groups)+"\n\n"
  (w/"system.kira").write_text(content)
 if "otf" in name:(w/"jobs.yaml").write_text(JOBS.replace("otf: false","otf: true"))
 run=run_kira(w)
 records=assess(family,manifest,parse_output(w/"results/Tuserweight/kira_targets.kira"),refs) if run["status"]=="completed" else []
 states=collections.Counter(r["status"] for r in records)
 write(dest/(name+".json"),dict(run=run,states=dict(states),records=records))
 for f in ["system.kira","run.log","jobs.yaml"]:
  with (w/f).open("rb") as a,gzip.open(str(dest/(name+"_"+f+".gz")),"wb") as b:shutil.copyfileobj(a,b)
 print(name,dict(states),flush=True)
