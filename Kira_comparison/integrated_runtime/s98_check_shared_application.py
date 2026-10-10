"""Check real basis-only reductions against reference answers after execution."""
import hashlib,json,os,pathlib,subprocess,sys,time
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 from s93_freeze_shared import verify
 verify()
 manifest=json.loads((HERE/"reserved_families.json").read_text());cases={c["id"]:c for c in manifest["cases"]}
 specs=[("runtime_reserved_00_sunrise",21,["native","row","auto","both"]),("runtime_reserved_02_double_box",32,["native","seed","auto","both"])]
 outdir=HERE/"fast_evaluation/shared_application_checks";outdir.mkdir(exist_ok=True)
 results=[]
 for name,size,policies in specs:
  case=cases[name];refpath=HERE/"reserved_references"/f"{name}_n{size}.json.gz";reference=read_record(refpath)
  casefile=outdir/(name+"_input.json");masterfile=outdir/(name+"_masters.json")
  casefile.write_text(json.dumps(case,sort_keys=True)+"\n");masterfile.write_text(json.dumps(reference["masters"])+"\n")
  for policy in policies:
   path=outdir/f"{name}_{policy}.json.gz"
   if not path.exists():
    subprocess.run([sys.executable,str(HERE/"s88_reduce.py"),"--family-file",str(casefile),"--masters-file",str(masterfile),"--size",str(size),"--policy",policy,"--output",str(path)],check=True,timeout=540)
   r=read_record(path);assert r["success"] and r["basis_admitted"] and not r["reference_checked"]
   trials=[read_record(ROOT/n) for n in r["attempts"]]
   assert all(t["reference"] is None for t in trials)
   final=trials[-1];assert final["verification_mode"]=="native_exact_basis"
   # The caller performs this independent oracle comparison only after reduction.
   from s30_verify import check
   rows=check.parse(final);wanted=check.parse(reference);comparisons=0
   for a,row in rows.items():
    for m in set(row)|set(wanted[a]):
     ln,ld=check.rational(row.get(m,"0"));rn,rd=check.rational(wanted[a].get(m,"0"))
     assert (ln*rd-rn*ld).is_zero,(name,policy,a,m);comparisons+=1
   route=read_record(path.with_name(path.name.removesuffix(".json.gz")+"_routing.json.gz"))
   assert route["application_seconds"]>=r["complete_seconds"]
   result=dict(case=name,size=size,requested_policy=policy,applied_policy=route["applied_policy"],basis_only=True,reference_supplied_to_reducer=False,
    native_exact_reduction_completed=True,independent_postrun_coefficient_check=True,coefficient_comparisons=comparisons,application_seconds=route["application_seconds"],result=str(path.relative_to(ROOT)))
   results.append(result);print(json.dumps(result),flush=True)
 result=dict(all_passed=True,checks=len(results),mode="Known master indices supplied without target reference coefficients; independent postrun oracle comparisons.",results=results,
  sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/"s86_run_shared.py",HERE/"s87_workflow_shared.py",HERE/"s88_reduce.py",HERE/"s98_check_shared_application.py"]})
 (HERE/"fast_evaluation/application_verification.json").write_text(json.dumps(result,indent=2)+"\n")
if __name__=="__main__":main()
