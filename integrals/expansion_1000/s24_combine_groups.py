"""Combine completed disjoint groups before independent mathematical validation."""
import json,os
from s01_generate import HERE,write,sha
from pathlib import Path
assert os.environ.get("JOB_ID")
assert json.loads((HERE/"compression_pilot.json").read_text())["status"]=="passed"
compression=[json.loads((HERE/("compression_group_%d.json"%i)).read_text()) for i in (1,2,3)]
assert all(c["status"]=="complete" and c["families"]==4000 for c in compression)
groups=[json.loads((HERE/("group_%d_summary.json"%i)).read_text()) for i in (1,2,3)]
assert all(g["status"]=="complete" and len(g["families"])==4000 for g in groups)
families=sorted([f for g in groups for f in g["families"]],key=lambda f:(f["loops"],f["profile"]))
assert len(families)==len({f["family"] for f in families})==12000
assert {f["loops"] for f in families}==set(range(1,13))
assert sum(f["master_count"] for f in families)==36012
assert sum(f["counts"]["targets"] for f in families)==1536000
write(HERE/"generation_summary.json",dict(status="complete",families=families,master_count=36012,targets=1536000,compression=compression,workers=12,groups=[{k:v for k,v in g.items() if k!="families"} for g in groups],elapsed_seconds=max(g["elapsed_seconds"] for g in groups),combiner_sha256=sha(Path(__file__))))
print("Completed 12000 families",flush=True)
