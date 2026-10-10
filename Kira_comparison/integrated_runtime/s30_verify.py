"""Independently check all retained exact exports and complete workflow accounting."""
import functools,gzip,hashlib,importlib.util,json,pathlib,sys,array,base64
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
from s03_records import read_record
previous=ROOT/"Kira_comparison/multiloop_native"
sys.path.insert(0,str(previous))
spec=importlib.util.spec_from_file_location("independent_polynomial_check",previous/"s26_verify.py")
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
@functools.lru_cache(maxsize=64)
def seed_candidates(case_id,r,s,d):
 from s07_seed import candidates
 cases=json.loads((HERE/"reserved_families.json").read_text())["cases"]
 case=next(c for c in cases if c["id"]==case_id)
 return candidates(case["definition"],r,s,d)
def check_integration(record,counts):
 if record.get("split")!="reserved":return
 if "seed_audit" in record:
  p=record["predictions"];spec=record["input"]["jobs"]["jobs"][0]["reduce_sectors"]["reduce"][0]
  candidates=seed_candidates(record["case"],spec["r"],spec["s"],spec["d"])
  assert len(candidates)==p["candidate_count"]
  indices=array.array("h",(v for a in candidates for v in a))
  if sys.byteorder!="little":indices.byteswap()
  assert hashlib.sha256(indices.tobytes()).hexdigest()==p["candidate_sha256"]
  bits=base64.b64decode(p["selection_bits_base64"])
  selected={a for i,a in enumerate(candidates) if bits[i//8] & (1<<(i%8))}
  used={tuple(map(int,x.removeprefix("F[").removesuffix("]").split(","))) for x in record["seed_audit"]["used"]}
  assert used<=selected and record["seed_audit"]["allowed"]==len(selected)
  counts["integrated_seed_attempts"]+=1;counts["used_selected_seeds"]+=len(used)
 learned=[m for m in record.get("metrics",[]) if m["mode"]=="learned"]
 if learned:
  config=json.loads((HERE/"deployment.json").read_text())
  model=config["row_by_topology"].get(record["topology"],dict(model=config["unknown_row_model"]))["model"]
  weights=ROOT/"ML_model_reduction/runtime_training/trajectory_candidates"/model/"weights.txt"
  assert record["weights_sha256"]==hashlib.sha256(weights.read_bytes()).hexdigest()
  counts["integrated_learned_attempts"]+=1
  counts["learned_row_groups"]+=sum(m["groups"] for m in learned)
  counts["changed_row_sources"]+=sum(m["changed_sources"] for m in learned)
def main():
 if (HERE/"freeze.json").exists():
  frozen=json.loads((HERE/"freeze.json").read_text())
  for name,want in frozen["sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,name
 if (HERE/"pair_freeze.json").exists():
  frozen=json.loads((HERE/"pair_freeze.json").read_text())
  for name,want in frozen["sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,name
 checked=set();refs={};pairs=set();counts=dict(native_successes=0,coefficient_comparisons=0,polynomial_comparisons=0,failed_attempts=0,rejected_basis_disagreements=0,workflows=0,integrated_seed_attempts=0,used_selected_seeds=0,integrated_learned_attempts=0,learned_row_groups=0,changed_row_sources=0)
 for p in (HERE/"shared").glob("*.gz"):
  with gzip.open(p,"rb") as f:raw=f.read()
  assert hashlib.sha256(raw).hexdigest()==p.name.removesuffix(".json.gz")
 def validate(p):
  if str(p) in checked:return
  r=read_record(p);checked.add(str(p))
  if "attempts" in r:
   trials=[read_record(ROOT/name) for name in r["attempts"]]
   assert len(trials)==r["attempt_count"]
   assert r["success"]==trials[-1]["success"]
   assert r["complete_seconds"]+1e-7>=sum(t["complete_seconds"] for t in trials)
   assert r["operations"]==sum(sum(m.get("operations",0) for m in t.get("metrics",[])) for t in trials)
   assert r["equations"]==sum((t.get("counters",{}).get("generated_equations") or [0])[0] for t in trials)
   for name in r["attempts"]:validate(ROOT/name)
   counts["workflows"]+=1;return
  if "success" not in r or "targets" not in r:return
  check_integration(r,counts)
  if not r["success"]:
   if r.get("mismatches"):
    assert r.get("reference")
    reference=read_record(pathlib.Path(r["reference"]))
    assert set(map(tuple,r["masters"]))-set(map(tuple,reference["masters"])),p
    counts["rejected_basis_disagreements"]+=1
   counts["failed_attempts"]+=1;return
  rows=check.parse(r);counts["native_successes"]+=1
  if r.get("reference"):
   rp=pathlib.Path(r["reference"]);rp=rp if rp.is_absolute() else ROOT/rp
   if str(rp) not in refs:
    rr=read_record(rp);assert rr["success"];refs[str(rp)]=check.parse(rr)
   reference=refs[str(rp)]
   for a,row in rows.items():
    assert a in reference
    for m in set(row)|set(reference[a]):
     left=row.get(m,"0");right=reference[a].get(m,"0");counts["coefficient_comparisons"]+=1
     pair=(left,right)
     if pair not in pairs:
      ln,ld=check.rational(left);rn,rd=check.rational(right)
      assert (ln*rd-rn*ld).is_zero,(p,a,m)
      pairs.add(pair);counts["polynomial_comparisons"]+=1
  else:
   for row in rows.values():
    for value in row.values():check.rational(value)
 for folder in HERE.iterdir():
  if folder.is_dir() and folder.name!="shared":
   for p in sorted(folder.glob("*.json.gz")):validate(p)
 result=dict(all_passed=True,method="Independent native export parsing and exact cross multiplication of rational polynomials over Q(d); workflow count and failed-attempt timing audit.",**counts)
 (HERE/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
