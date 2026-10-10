"""Independently compare all completed test coefficients over Q(d)."""
import collections,hashlib,json,pathlib
import sympy as sp
from s02_records import read
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def main():
 summary=json.loads((HERE/"model_test/summary.json").read_text())
 assert summary["workflows"]==280 and summary["all_exact"]
 freeze=json.loads((HERE/"trained_model/freeze.json").read_text())
 for name,digest in freeze["sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 checked=set();refs={};pairs=0;attempts=0;failed=0;count=0
 for p in sorted((HERE/"model_test").glob("*.json.gz")):
  r=read(p)
  if "mode" not in r:continue
  count+=1;assert r["success"] and r["reference_checked"]
  attempts+=len(r["attempts"]);failed+=sum(not a["success"] for a in r["attempts"])
  a=r["attempts"][-1];assert a["basis_admitted"] and a["complete"] and not a.get("unresolved_integrals")
  assert r["complete_seconds"]>=sum(z["complete_seconds"] for z in r["attempts"])
  refpath=a["reference"]
  if refpath not in refs:refs[refpath]=read(pathlib.Path(refpath))
  want=refs[refpath]["coefficients"];got=a["coefficients"]
  assert set(got)=={",".join(map(str,t)) for t in a["targets"]}
  for target,row in got.items():
   assert target in want
   for master in row.keys()|want[target].keys():
    left=row.get(master,"0");right=want[target].get(master,"0");pairs+=1
    key=(left,right)
    if key in checked:continue
    l=sp.sympify(left.replace("^","**"),rational=True);rr=sp.sympify(right.replace("^","**"),rational=True)
    assert sp.cancel(l-rr)==0,(p,target,master)
    checked.add(key)
 result=dict(all_passed=True,workflows=count,attempts=attempts,failed_attempts=failed,coefficient_pairs=pairs,distinct_coefficient_pairs=len(checked),all_frozen_files_unchanged=True)
 (HERE/"model_test/verification.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
