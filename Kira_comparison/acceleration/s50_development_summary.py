"""Summarize every early-admission development trial without claiming a timing test."""
import json,pathlib
from s39_records import read_record
HERE=pathlib.Path(__file__).resolve().parent
expected={"preflight_pilot":6,"adaptive_pilot":8,"adaptive_validation":8,"residual_pilot":4}
out={}
for stage,count in expected.items():
 paths=sorted((HERE/stage).glob("*.json.gz"))
 assert len(paths)==count,(stage,len(paths),count)
 audit=json.loads((HERE/(stage+"_validation.json")).read_text())
 assert audit["passed"] and audit["trials"]==count
 rows=[]
 for p in paths:
  r=read_record(p)
  assert not any(x.get("status")=="mismatch" for x in r.get("checks",[]))
  rows.append(dict(trial=r["trial"],family=r.get("family"),partition=r["partition"],case=r["case"],size=r["size"],
   policy=r["policy"],seconds=r["cold_seconds"],success=r["success"],status=r["status"],fallback=r.get("fallback"),
   selected=r.get("model",{}).get("selected"),rounds=[dict(budget=x["budget"],rejected=x["rejected_master_basis"],seconds=x["seconds"]) for x in r.get("preflight",[])]))
 out[stage]=dict(planned=count,exact_successes=sum(r["success"] for r in rows),rows=rows,
  independent_master_sample_checks=audit["independent_master_sample_checks"])
result=dict(scope="Single development trials on existing training/adapter-validation families; no independent speedup inference.",
 stages=out,all_stages_complete=True)
(HERE/"development_summary.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({s:{k:v for k,v in x.items() if k!="rows"} for s,x in out.items()}))
