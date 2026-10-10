"""Independently check new exact coefficients, timing accounting and native model use."""
import collections,hashlib,json,pathlib
from s105_parallel_records import read_record
from s30_verify import check,check_integration
from s113_freeze_parallel import verify
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/parallel_inference"
def main():
 verify();counts=collections.Counter();references={};pairs=set()
 for phase in ["validation","confirmation"]:
  for p in sorted((EXP/phase).glob("*.json.gz")):
   r=read_record(p);assert r["success"] and r["reference_checked"]
   attempts=[read_record(ROOT/n) for n in r["attempts"]]
   assert len(attempts)==r["attempt_count"]
   assert r["complete_seconds"]+1e-7>=sum(a["complete_seconds"] for a in attempts)
   assert r["operations"]==sum(sum(m.get("operations",0) for m in a.get("metrics",[])) for a in attempts)
   for a in attempts:
    check_integration(a,counts)
    if not a["success"]:
     assert not a.get("mismatches");counts["failed_attempts"]+=1;continue
    rows=check.parse(a);ref=pathlib.Path(a["reference"])
    if not ref.is_absolute():ref=ROOT/ref
    if str(ref) not in references:references[str(ref)]=check.parse(read_record(ref))
    target=references[str(ref)]
    for indices,row in rows.items():
     assert indices in target
     for master in set(row)|set(target[indices]):
      left=row.get(master,"0");right=target[indices].get(master,"0");counts["coefficient_comparisons"]+=1
      if (left,right) not in pairs:
       ln,ld=check.rational(left);rn,rd=check.rational(right)
       assert (ln*rd-rn*ld).is_zero,(p,indices,master)
       pairs.add((left,right))
    counts["successful_native_reductions"]+=1
   counts["workflows"]+=1
 assert counts["workflows"]==784
 result=dict(all_passed=True,polynomial_comparisons=len(pairs),method="Independent native export parser and exact polynomial cross multiplication over Q(d); native seed membership and row-policy hash audit; all fallback time retained.",**counts)
 (EXP/"verification.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
