"""Run one original-Kira or frozen final-method request."""
from pathlib import Path
import argparse,gzip,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument("method");p.add_argument("input");p.add_argument("output");a=p.parse_args()
c=json.loads(Path(a.input).read_text())
if a.method=="default":
 import s00_original_runner as n
 r=n.run(c,c["size"],"stock",HERE/"unused",timeout=600,margin=1,archive=False,records=False,compact=False,scratch_cap=8*1024**2,basis=c["comparison_masters"])
 r.pop("log",None)
 r=dict(success=r.get("success",False),blocks=[dict(case=c,indices=list(range(len(c["definition"]["propagators"]))),result=r)])
else:
 sys.path.insert(0,str(ROOT/"ML_model_adaptive_reduction/triangle_reduction"))
 from s32_deploy import run
 r=run(c,"integrated")
raw=json.dumps(r,separators=(",",":")).encode()
assert len(raw)<2*1024**2
Path(a.output).write_bytes(gzip.compress(raw,mtime=0))
