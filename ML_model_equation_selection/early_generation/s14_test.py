"""Evaluate the frozen policy on previously reserved physical profiles."""
import argparse,json,time
import sympy as sp
from s04_workflows import HERE,ROOT,setup,reference,read,sha,guard
from s12_reduce import reduce
def check():
 f=json.loads((HERE/"trained_model/freeze.json").read_text())
 for n,d in f["sha256"].items():assert sha(ROOT/n)==d,n
 return f
def exact(r,ref,seen):
 assert r["success"] and r["complete_seconds"]>=sum(a["complete_seconds"] for a in r["attempts"])
 a=r["attempts"][-1];assert a["basis_admitted"] and a["complete"] and not a.get("unresolved_integrals")
 want=read(ref)["coefficients"];got=a["coefficients"];assert got.keys()==want.keys()
 pairs=0
 for target,row in got.items():
  for master in row.keys()|want[target].keys():
   key=(row.get(master,"0"),want[target].get(master,"0"));pairs+=1
   if key in seen:continue
   assert sp.cancel(sp.sympify(key[0].replace("^","**"),rational=True)-sp.sympify(key[1].replace("^","**"),rational=True))==0
   seen.add(key)
 return pairs
def main():
 frozen=check();setup();manifest=json.loads((HERE/"families_test.json").read_text());case_map={c["id"]:c for c in manifest["cases"]}
 for i,b in enumerate(manifest["batches"]):
  c=case_map[b["case"]];n=b["size"];ref=reference(c,n);methods=manifest["methods"]
  for rep in range(manifest["repetitions"]):
   ordered=methods[rep%len(methods):]+methods[:rep%len(methods)]
   if (i+rep)%2:ordered=list(reversed(ordered))
   for method in ordered:
    out=HERE/"model_test"/f'{c["id"]}_n{n}_{method}_r{rep}.json.gz'
    if out.exists():continue
    r=reduce(c,n,out,reference=ref,policy=method)
    assert r["reference_checked"]
    print(json.dumps(dict(case=c["id"],size=n,rep=rep,method=method,seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
 for c in manifest["cases"]:
  n=21 if c["topology_group"]=="sunrise" else 128;ref=reference(c,n);out=HERE/"model_test/application"/f'{c["id"]}.json.gz'
  if not out.exists():
   r=reduce(c,n,out,basis=read(ref)["masters"]);assert r["success"] and not r["reference_checked"]
 seen=set();pairs=0;count=0;attempts=0;failed=0;rss=0;scratch=0
 for directory in [HERE/"model_test",HERE/"model_test/application"]:
  for p in sorted(directory.glob("*.json.gz")):
   r=read(p);c=case_map[r["case"]];ref=reference(c,r["size"]);pairs+=exact(r,ref,seen);count+=1
   assert r["reference_checked"]==(directory.name!="application")
   attempts+=len(r["attempts"]);failed+=sum(not a["success"] for a in r["attempts"])
   rss=max([rss]+[a.get("peak_rss_bytes",0) for a in r["attempts"]]);scratch=max([scratch]+[a.get("peak_scratch_bytes",0) for a in r["attempts"]])
 assert count==frozen["workflows"]+frozen["applications"];check();guard()
 audit=dict(all_passed=True,main_workflows=frozen["workflows"],basis_only_applications=frozen["applications"],workflows=count,attempts=attempts,failed_attempts=failed,coefficient_pairs=pairs,distinct_coefficient_pairs=len(seen),peak_process_tree_rss_bytes=rss,peak_scratch_bytes=scratch,frozen_sources_unchanged=True)
 (HERE/"model_test/verification.json").write_text(json.dumps(audit,indent=2)+"\n");print(json.dumps(audit),flush=True)
if __name__=="__main__":main()
