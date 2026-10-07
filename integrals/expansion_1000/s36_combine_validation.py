"""Combine disjoint, independently checked family groups without repeating calculations."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
 groups=[read(HERE/("validation_group_%d.json"%g)) for g in (1,2,3)]
 source=hashlib.sha256((HERE/"s03_validate.py").read_bytes()).hexdigest()
 families=[]
 flags=("three_sample_reverse_and_forward_replay","direct_rational_integrand_identity_checks","source_formulas_verified_exactly")
 for group in groups:
  assert group["status"]=="passed" and len(group["families"])==4000
  assert group["validator_sha256"]==source and all(group[k] for k in flags)
  families.extend(group["families"])
 generated=read(HERE/"generation_summary.json")["families"]
 assert len(families)==len({f["family"] for f in families})==12000
 assert {f["family"] for f in families}=={f["family"] for f in generated}
 assert sum(f["targets"] for f in families)==1536000
 assert sum(f["identities"] for f in families)==sum(f["source_equations"] for f in generated)
 pilot=read(HERE/"pilot_validation.json")
 assert pilot["status"]=="passed" and len(pilot["families"])==6 and pilot["validator_sha256"]==source
 result=dict(status="passed",families=sorted(families,key=lambda f:f["family"]),
  targets=1536000,source_identities=sum(f["identities"] for f in families),
  workers=12,group_count=3,summed_group_seconds=sum(g["elapsed_seconds"] for g in groups),
  validator_sha256=source,combiner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  group_validation_sha256={"validation_group_%d.json"%g:hashlib.sha256((HERE/("validation_group_%d.json"%g)).read_bytes()).hexdigest() for g in (1,2,3)})
 result.update({key:True for key in flags})
 (HERE/"validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Independent validation passed",len(families),result["targets"],flush=True)
if __name__=="__main__":main()
