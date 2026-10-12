"""Audit symbolic exports and test a larger seed region and fresh specializations."""
import copy,gzip,json,pathlib,re,sys
from functools import lru_cache
import sympy as sp
from s02_study import HERE,ROOT,load,save,attempt,setup
from s00_native_run import run,parse_export
@lru_cache(maxsize=32768)
def expr(s):return sp.sympify(s.replace("^","**"),rational=True)
@lru_cache(maxsize=32768)
def equal(a,b):return sp.cancel(expr(a)-expr(b))==0
def main():
 cases=json.loads((HERE/"cases.json").read_text())["cases"];checks=0;unique=set();summaries=[];symbols={}
 for c in cases:
  refpath=HERE/"references"/(c["id"]+".json.gz");ref=load(refpath);assert ref["success"],c["id"]
  observed=set()
  for row in ref["coefficients"].values():
   for x in row.values():observed.update(map(str,expr(x).free_symbols))
  symbols[c["id"]]=sorted(observed)
  for p in sorted((HERE/"model_test").glob(c["id"]+"_*.json.gz")):
   r=load(p);assert r["success"],p
   final=r["attempts"][-1];assert final["reference_checked"]
   raw=parse_export(final["raw_export"])
   for a in final["identity_master_targets"]:raw.setdefault(a,{a:"1"})
   assert raw==final["coefficients"]
   assert set(raw)==set(ref["coefficients"])
   for a,row in raw.items():
    for m in row.keys()|ref["coefficients"][a].keys():
     x,y=row.get(m,"0"),ref["coefficients"][a].get(m,"0")
     assert equal(x,y),(p,a,m);checks+=1;unique.add((c["id"],a,m,x,y))
  # Increased native seed bounds test the reference within its preferred basis.
  out=HERE/"model_test"/("audit_enlarged_"+c["id"]+".json.gz")
  if out.exists():larger=load(out)
  else:larger=attempt(c,ref=refpath,margin=2);save(out,larger)
  summaries.append(dict(case=c["id"],enlarged_seed_success=larger["success"],status=larger["status"],seconds=larger["complete_seconds"]))
  print(json.dumps(summaries[-1]),flush=True)
  if c["definition"]["invariants"]:
   numeric=copy.deepcopy(c);numeric["id"]="specialization_"+c["id"];numeric["split"]="audit"
   vals=[-163,-167,-173,-179,-181];subs={sp.Symbol(n):v for (n,_),v in zip(c["definition"]["invariants"],vals)}
   nd=numeric["definition"];nd["invariants"]=[]
   nd["scalarproduct_rules"]=[[a,str(expr(b).subs(subs))] for a,b in nd["scalarproduct_rules"]]
   nd["parameters"]=dict(symbolic=False,values={str(k):v for k,v in subs.items()})
   out=HERE/"model_test"/("audit_"+numeric["id"]+".json.gz")
   if out.exists():nr=load(out)
   else:
    setup("off");nr=run(numeric,numeric["size"],"native",out,timeout=150,margin=1,records=False,archive=False,
     check_masters=True,basis=ref["masters"],scratch_cap=32*1024**2);save(out,nr)
   assert nr["success"],(numeric["id"],nr["status"])
   assert set(nr["coefficients"])==set(ref["coefficients"])
   nchecked=0
   for a,row in ref["coefficients"].items():
    for m in row.keys()|nr["coefficients"][a].keys():
     diff=expr(row.get(m,"0")).subs(subs)-expr(nr["coefficients"][a].get(m,"0"))
     assert sp.cancel(diff)==0,(c["id"],a,m);nchecked+=1
   summaries[-1]["specialization"]=dict(values={str(k):v for k,v in subs.items()},coefficient_pairs=nchecked,success=True)
 # Compare certified physical systems with independently generated native IBP reductions.
 from s04_optimal_paths import systems
 certificate_native=[]
 for sysdef in systems():
  bubble=sysdef["name"]=="massless_bubble"
  definition=dict(name="F",kind=sysdef["name"],loop_momenta=["k1"],external_momenta=["p"] if bubble else [],
   physical_propagators=2 if bubble else 1,propagators=[dict(momentum="k1",mass_squared="0"),dict(momentum="k1-p",mass_squared="0")] if bubble else [dict(momentum="k1",mass_squared="m2")],
   invariants=[["s",2]] if bubble else [["m2",2]],scalarproduct_rules=[[["p","p"],"s"]] if bubble else [],
   top_level_sectors=[3 if bubble else 1],parameters=dict(symbolic=True))
  c=dict(id="certificate_"+sysdef["name"],group=sysdef["name"],topology_group=sysdef["name"],split="audit",definition=definition,
   size=3,targets=[[2,1],[1,2],[2,2]] if bubble else [[2],[3],[4]])
  out=HERE/"optimal_paths"/("native_"+sysdef["name"]+".json.gz")
  if out.exists():nr=load(out)
  else:
   setup("off");nr=run(c,3,"native",out,timeout=150,margin=1,records=False,archive=False,
    check_masters=True,basis=[[1,1]] if bubble else [[1]],scratch_cap=32*1024**2);save(out,nr)
  assert nr["success"],(c["id"],nr["status"])
  master="1,1" if bubble else "1"
  for target,want in zip(c["targets"],sysdef["expected"]):
   actual=nr["coefficients"][",".join(map(str,target))]
   assert set(actual)=={master} and sp.cancel(expr(actual[master])-want)==0
  certificate_native.append(dict(system=sysdef["name"],native_master_coefficients_verified=3))
 count=len([p for p in (HERE/"model_test").glob("*.json.gz") if not p.name.startswith("audit_")])
 assert count==70,count
 result=dict(success=True,certificate_native_checks=certificate_native,comparison_workflows=count,exact_coefficient_pairs=checks,unique_coefficient_pairs=len(unique),
  observed_symbols=symbols,expanded_seed_checks=summaries,all_expanded_seed_checks_pass=all(x["enlarged_seed_success"] for x in summaries))
 (HERE/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k not in ["observed_symbols","expanded_seed_checks"]}),flush=True)
if __name__=="__main__":main()
