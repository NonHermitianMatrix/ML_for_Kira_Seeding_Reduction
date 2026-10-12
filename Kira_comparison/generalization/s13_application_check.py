"""Check the answer-free native application and its explicit experimental fallback."""
import hashlib,json,pathlib
from s02_study import HERE,ROOT,load,save
from s12_reduce import reduce
from s07_audit import equal
def main():
 cases=json.loads((HERE/"cases.json").read_text())["cases"]
 frozen=dict(application_sha256=hashlib.sha256((HERE/"s12_reduce.py").read_bytes()).hexdigest(),
  policy="Native by default; unchanged experimental filter only when explicitly requested.",
  test_cases=[dict(case=c["id"],experimental=e) for c in cases for e in ([False,True] if c["definition"]["invariants"] else [False])])
 directory=HERE/"application";directory.mkdir(exist_ok=True)
 p=directory/"freeze.json"
 if p.exists():assert json.loads(p.read_text())==frozen
 else:p.write_text(json.dumps(frozen,indent=2)+"\n")
 records=[]
 for c in cases:
  ref=load(HERE/"references"/(c["id"]+".json.gz"))
  location=HERE/("symbolic_kinematics" if c["definition"]["invariants"] else "scattering_families")/"bases"
  location.mkdir(exist_ok=True);(location/(c["id"]+".json")).write_text(json.dumps({"masters":ref["masters"]},indent=2)+"\n")
  for experimental in ([False,True] if c["definition"]["invariants"] else [False]):
   p=directory/(c["id"]+("_experimental" if experimental else "_native")+".json.gz")
   if p.exists():r=load(p)
   else:r=reduce(c,ref["masters"],experimental);save(p,r)
   assert r["success"] and not r["input_contains_reference_coefficients"]
   final=r["attempts"][-1];assert not final["reference_checked"]
   assert set(final["coefficients"])==set(ref["coefficients"])
   count=0
   for target,row in ref["coefficients"].items():
    actual=final["coefficients"][target]
    for master in row.keys()|actual.keys():
     assert equal(row.get(master,"0"),actual.get(master,"0"))
     count+=1
   records.append(dict(case=c["id"],experimental=experimental,success=True,coefficient_pairs=count,
    fallback_count=r["fallback_count"],seconds=r["complete_seconds"]))
   print(json.dumps(records[-1]),flush=True)
 result=dict(success=True,applications=len(records),coefficient_pairs=sum(x["coefficient_pairs"] for x in records),
  reference_answers_withheld_from_application=True,records=records)
 (directory/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
if __name__=="__main__":main()
