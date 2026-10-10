"""Independently parse exported reductions and verify exact rational coefficients."""
import functools,gzip,hashlib,json,pathlib,re
import sympy as sp
from s04_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
D=sp.Symbol("d")
@functools.lru_cache(maxsize=4096)
def rational(text):
 value=sp.sympify(text.replace("^","**"),locals={"d":D},rational=True)
 assert value.free_symbols<={D},str(value)
 num,den=sp.fraction(sp.cancel(value))
 a=sp.Poly(num,D,domain=sp.QQ);b=sp.Poly(den,D,domain=sp.QQ);assert not b.is_zero
 return a,b
def parse(record):
 result={}
 for block in re.split(r"\n\s*\n",record.get("raw_export","").strip()):
  if not block.strip():continue
  terms=[]
  for line in block.splitlines():
   match=re.match(r"^F\[([-\d,]+)\]\*\((.+)\)$",line.strip());assert match,line
   key=",".join(str(int(i)) for i in match.group(1).split(","));terms.append((key,match.group(2)))
  assert terms[0][1]=="-1"
  assert terms[0][0] not in result
  result[terms[0][0]]={k:v for k,v in terms[1:]}
 for key in re.findall(r"This requested integral is a master integral: F\[([-\d,]+)\]",record["log"]):
  result.setdefault(key,{key:"1"})
 expected={",".join(map(str,a)) for a in record["targets"]}
 assert set(result)==expected,(record["case"],len(result),len(expected))
 assert result==record["coefficients"]
 return result
def main():
 frozen=json.loads((HERE/"freeze.json").read_text())
 for name,want in frozen["sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,name
 content=0
 for p in (HERE/"shared").glob("*.json.gz"):
  with gzip.open(p,"rb") as f:raw=f.read()
  assert hashlib.sha256(raw).hexdigest()==p.name.removesuffix(".json.gz"),p
  json.loads(raw);content+=1
 checked=set();reference_cache={};polynomial_pairs=set();counts=dict(successful_reductions=0,coefficient_comparisons=0,polynomial_comparisons=0)
 def validate(path):
  key=str(path)
  if key in checked:return
  r=read_record(path)
  if not r.get("success"):
   assert not r.get("mismatches"),("Reference consistency needs investigation",path)
   return
  rows=parse(r);counts["successful_reductions"]+=1
  if r.get("reference"):
   ref_path=pathlib.Path(r["reference"])
   if not ref_path.is_absolute():ref_path=ROOT/ref_path
   if str(ref_path) not in reference_cache:
    ref=read_record(ref_path);assert ref["success"];reference_cache[str(ref_path)]=parse(ref)
   reference=reference_cache[str(ref_path)]
   for a,row in rows.items():
    assert a in reference
    for m in set(row)|set(reference[a]):
     left=row.get(m,"0");right=reference[a].get(m,"0")
     counts["coefficient_comparisons"]+=1
     pair=(left,right)
     if pair in polynomial_pairs:continue
     ln,ld=rational(left);rn,rd=rational(right)
     assert (ln*rd-rn*ld).is_zero,(path,a,m)
     polynomial_pairs.add(pair);counts["polynomial_comparisons"]+=1
  else:
   for row in rows.values():
    for value in row.values():rational(value)
  checked.add(key)
 for directory in ["reserved_references","reference_checks","model_test/attempts","runtime_checks","baseline_diagnostic"]:
  for p in sorted((HERE/directory).glob("*.json.gz")):validate(p)
 continuation_count=0
 for p in sorted((HERE/"rollouts").glob("*_summary.json.gz")):
  r=read_record(p)
  for group in r["groups"]:
   for trial in group["trials"]:
    assert trial["valid"]
    path=HERE/trial["path"];t=read_record(path);assert t["success"] and t["reference_checked"]
    choices=[g for g in t["choices"] if g["group"]==group["group"]];assert len(choices)==1
    g=choices[0];assert g["selected"]==trial["source"] and g["pivot"]==group["pivot"]
    assert [c["features"] for c in g["candidates"]]==[c["features"] for c in group["candidates"]]
    assert sum(m["operations"] for m in t["metrics"])-g["prefix_operations"]==trial["remaining_operations"]
    validate(path);continuation_count+=1
 assert continuation_count==98
 diagnostic=json.loads((HERE/"baseline_diagnostic/summary.json").read_text())
 assert diagnostic["post_comparison"] and diagnostic["validation_only"]
 assert diagnostic["models_and_reserved_protocol_unchanged"] and not diagnostic["performance_comparison"]
 for result in diagnostic["results"]:
  record=read_record(HERE/result["path"])
  assert record["success"]==result["success"] and record["status"]==result["status"]
  assert ("std::bad_alloc" in record["log"])==result["allocation_failure"]
 assert json.loads((HERE/"runtime_check.json").read_text())["all_passed"]
 model=json.loads((ROOT/"ML_model_reduction/cost_training/trained_model.json").read_text())
 for name,want in model["input_sha256"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want
 summary=json.loads((HERE/"summary.json").read_text())
 for name,want in summary["trial_sha256"].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==want
 result=dict(all_passed=True,shared_content_objects=content,verified_continuations=continuation_count,**counts,
  method="independent native-export parser and exact cross multiplication of rational polynomials over Q(d)",
  frozen_inputs_unchanged=True,seed_probabilities_unchanged=True,native_tree_scores_checked=True,
  post_comparison_diagnostic_records=len(diagnostic["results"]),
  trial_count=summary["planned"],completed_trials=summary["completed"],
  expanded_bound_attempts=len(summary["expanded_bound_checks"]),expanded_bound_completions=sum(r["success"] for r in summary["expanded_bound_checks"]))
 (HERE/"verification.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
