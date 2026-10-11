"""Audit every saved coefficient, paired input system and frozen dependency."""
from s00_cumulative import *
import tempfile,shutil
def main():
 check_freeze();guard()
 complete=read(HERE/"test/complete.json");assert complete["all_exact"] and complete["applications"]==120
 paths=sorted((HERE/"test/results").glob("*.json"));assert len(paths)==120
 assert not list((HERE/"test/results").glob("*.failure.json"))
 records=[read(p) for p in paths];positions=0;raw_checks=0;source_checks=0;unique={}
 import sympy as sp
 d=sp.Symbol("d")
 for inp in sorted((HERE/"test/inputs").glob("*.json")):
  req=read(inp)["requests"];cohort=[r for r in records if r["input"]==inp.name]
  assert len(cohort)==15 and len({r["canonical_coefficients_sha256"] for r in cohort})==1
  assert len({tuple(r["worker_cpu_affinity"]) for r in cohort})==1
  assert len(cohort[0]["worker_cpu_affinity"])==1
  decoded=None
  for r in cohort:
   assert r["success"] and r["request_sha256"]==sha(inp) and r["fallbacks"]==0
   assert r["arm"] in ARMS and 0<=r["repetition"]<5
   key=(r["coefficient_format"],r["coefficients_sha256"])
   if key not in unique:
    values=backend.load_coeff(r,OBJECTS)["coefficients"]
    assert digest(values)==r["canonical_coefficients_sha256"]
    unique[key]=digest(values)
   assert unique[key]==r["canonical_coefficients_sha256"]
   if r["arm"]=="final":
    assert not r["kira_invoked"] and r["route"]=="extreme"
    if decoded is None:decoded=backend.load_coeff(r,OBJECTS)["coefficients"]
   else:
    assert r["solver_calls"]==36 and len(r["attempts"])==36
    for a in r["attempts"]:
     assert a["algebra"]["returncode"]==0 and not a["algebra"]["reason"]
  for c in req:
   for L in c["loops"]:
    rows=backend.base.decode(decoded[c["id"]][str(L)])
    for b,row in zip(c["targets"],rows):
     expected={j:p for j,p in legacy.oracle(L,c["mass_ratios"],tuple(b)).items() if p}
     assert row==expected;positions+=len(expected)
    attempts=[a for r in cohort if r["arm"]!="final" for a in r["attempts"] if a["profile"]==c["id"] and a["loop"]==L]
    assert len(attempts)==10
    assert len({a["input_sha256"] for a in attempts})==1
    assert len({a["source_choices_sha256"] for a in attempts})==1
    w=Path(tempfile.mkdtemp(prefix="audit_",dir=ROOT/".tools/kira-cumulative/tmp"))
    try:
     regenerated=legacy.export(c,"dense",None,w,L)
     assert regenerated["input_sha256"]==attempts[0]["input_sha256"]
     assert digest(regenerated["source_choices"])==attempts[0]["source_choices_sha256"]
     source_checks+=1
    finally:shutil.rmtree(w)
    for arm in ["original_kira","chain_baseline"]:
     a=next(a for r in cohort if r["arm"]==arm and r["repetition"]==0 for a in r["attempts"] if a["profile"]==c["id"] and a["loop"]==L)
     data=gzip.decompress((OBJECTS/(a["raw_export_sha256"]+".txt.gz")).read_bytes())
     assert hashlib.sha256(data).hexdigest()==a["raw_export_sha256"]
     exported=legacy.parse(data.decode());target=len(c["targets"])-1
     row=exported[a["target_start"]+target]
     expected=rows[target]
     independent={}
     for j,s in row.items():
      poly=sp.Poly(sp.cancel(sp.sympify(s.replace("^","**"),locals={"d":d},rational=True)),d,domain=sp.QQ)
      p=tuple(legacy.F(str(poly.nth(k))) for k in range(poly.degree()+1)) if not poly.is_zero else ()
      if p:independent[j]=p
     assert independent==expected;raw_checks+=len(independent)
 assert len({(r["input"],r["arm"],r["repetition"]) for r in records})==120
 archive=HERE/"development/binding_request"
 for n,h in read(archive/"freeze.json")["sha256"].items():
  path=archive/Path(n).name if n in ["Kira_comparison/cumulative_speedup/s10_parallel.py","Kira_comparison/cumulative_speedup/protocol.json"] else ROOT/n
  assert sha(path)==h,n
 original=read(ROOT/"Kira_comparison/frozen_inputs.json")["sha256"]
 assert sha(BINARIES["original_kira"])==original[".tools/kira/bin/kira"]
 assert sha(legacy.FERMAT)==original[".tools/Ferl7/fer64"]
 check_freeze();guard()
 result=dict(all_exact=True,applications=120,original_kira_calls=1440,chain_baseline_kira_calls=1440,final_kira_calls=0,input_batches=8,physical_mass_profiles=24,loop_orders=list(range(1,13)),expanded_coefficient_positions=positions,regenerated_systems=source_checks,sympy_raw_export_positions=raw_checks,baseline_binary_matches_first_frozen_comparison=True,initial_zero_trial_freeze_preserved=True,coefficient_outputs_identical=True,earlier_sources_unchanged=True,failures=0,fallbacks=0,peak_tree_rss_bytes=max(r["peak_tree_rss_bytes"] for r in records),peak_scratch_bytes=max(r["peak_scratch_bytes"] for r in records))
 write(HERE/"test/audit.json",result);print(json.dumps(result),flush=True)
if __name__=="__main__":main()
