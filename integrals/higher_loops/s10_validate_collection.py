"""Audit links and source hashes across the complete expanded collection."""
import argparse,collections,gzip,hashlib,itertools,json,os,time
from pathlib import Path
from functools import lru_cache
HERE=Path(__file__).resolve().parent;DATA=HERE.parent;ROOT=DATA.parent
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
@lru_cache(maxsize=None)
def link(value):
 assert not Path(value).is_absolute() and ".." not in Path(value).parts
 assert (DATA/value).is_file()
def rows(p):
 with gzip.open(p,"rt",encoding="utf-8") as f:
  for line in f:yield json.loads(line)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--family",action="append");ap.add_argument("--compare-source");args=ap.parse_args()
 if args.compare_source:raise ValueError("Original migration-source comparisons use the preserved original catalog. This audit verifies its archived evidence and current file hashes.")
 assert os.environ.get("JOB_ID"),"Submit the collection audit through the scheduler."
 catalog=read(DATA/"catalog.json");split=read(ROOT/"ML_model_seed_selection/split_manifest.json")
 metas={m["family"]:m for m in split["families"]};entries={e["family"]:e for e in catalog["families"]}
 assert set(metas)==set(entries) and len(entries)==2100
 check=read(HERE/"validation.json");newproof={m["family"]:m for m in check["families"]}
 assert check["status"]=="passed" and len(newproof)==1100
 selected=sorted(args.family or entries)
 assert set(selected)<=set(entries)
 seen=set();totals=collections.Counter();by_split={s:collections.Counter() for s in ("train","test")};start=time.time()
 for number,fid in enumerate(selected,1):
  e=entries[fid];meta=metas[fid];manifest=read(DATA/e["manifest"])
  for name,info in manifest["files"].items():
   p=DATA/name;assert p.is_file() and p.stat().st_size==info["bytes"] and sha(p)==info["sha256"],name
  definition=read(DATA/e["definition"]);basis=read(DATA/e["master_basis"])
  assert definition["id"]==basis["family"]==fid and len(definition["loop_momenta"])==meta["loops"]
  assert len(basis["masters"])==e["master_count"]
  masterids={tuple(m["indices"]):m["id"] for m in basis["masters"]};assert len(masterids)==len(basis["masters"])
  if fid in newproof:assert basis["status"]=="analytically_verified_restricted_basis"
  else:assert basis["status"]=="validated"
  rel=DATA/e["records"];seeds={tuple(a) for a in read(rel/"candidate_seeds.json")["indices"]}
  identities={r["id"]:r["source"] for r in rows(rel/"identities.jsonl.gz")}
  identity_ids=set(identities)
  count=collections.Counter(masters=len(masterids),source_equations=len(identities),files_checked=len(manifest["files"]))
  targetids=[]
  streams=[rows(DATA/e[k]) for k in ("targets_file","references","traces")]
  for inp,ref,trace in itertools.zip_longest(*streams):
   assert inp is not None and ref is not None and trace is not None
   tid=inp["id"];assert tid==ref["id"]==trace["id"] and tid.startswith(fid+":") and tid not in seen
   seen.add(tid);targetids.append(tid)
   assert inp["family"]==ref["family"]==fid
   assert ref["master_ids"]==[masterids[tuple(t["indices"])] for t in ref["master_coefficients"]]
   wanted={tuple(a) for a in ref["sufficient_seeds"]};assert wanted<=seeds
   used=[];actual=set();ops=collections.Counter()
   for step in trace["steps"]:
    eid=step["pivot_equation"];assert eid in step["allowed_pivot_equations"]
    assert set(step["allowed_pivot_equations"])<=identity_ids
    used.append(eid);source=identities[eid]
    if source["kind"]=="ibp":actual.add(tuple(source["seed"]))
    ops.update(step["operations"])
   assert actual==wanted and list(dict.fromkeys(used))==ref["source_equations"]
   assert dict(ops)==ref["arithmetic_operations"] or all(ops[k]==ref["arithmetic_operations"].get(k,0) for k in ("divisions","multiplications","subtractions"))
   assert trace["total_operations"]==ref["arithmetic_operations"]
   assert len(trace["steps"])==ref["reduction_steps"]
   assert trace["final_master_row"]==ref["samples"][0]["master_coefficients"]
   for key in ("master_basis","family_definition","candidate_seeds","equation_pool","reference_records","elimination_records"):
    link(inp[key])
   count["targets"]+=1;count["elimination_steps"]+=len(trace["steps"])
   count["single_integrals" if inp["kind"]=="single_integral" else "integral_expressions"]+=1
   count["positive_seed_labels"]+=len(wanted);count["candidate_seed_labels"]+=len(seeds)
  assert count["targets"]==e["targets"]==meta["counts"]["targets"]
  assert count["single_integrals"]==e["single_integral"] and count["integral_expressions"]==e["integral_expression"]
  assert count["positive_seed_labels"]==meta["counts"]["positive_seed_labels"]
  assert count["candidate_seed_labels"]==meta["counts"]["candidate_seed_labels"]
  if fid in newproof:assert newproof[fid]["targets"]==count["targets"]
  count["families"]=1;totals.update(count);by_split[meta["split"]].update(count)
  if number%50==0:print("Collection links",number,len(selected),flush=True)
 if args.family:print(json.dumps(dict(status="passed",counts=dict(totals))),flush=True);return
 assert totals["masters"]==catalog["master_records"]==12967
 assert totals["targets"]==catalog["targets"]==381272
 assert totals["single_integrals"]==catalog["single_integrals"]
 ids=read(DATA/"splits.json")
 assert set(ids["train"]).isdisjoint(ids["test"]) and set(ids["train"])|set(ids["test"])==seen and not ids["validation"]
 original=HERE/"original_validation_summary.json"
 if not original.exists():
  old=DATA/"validation_summary.json";assert read(old)["family_count"]==1000
  original.write_bytes(old.read_bytes())
 assert read(original)["status"]=="passed"
 result=dict(status="passed",family_count=2100,layout_totals=dict(totals),split_counts={k:dict(v) for k,v in by_split.items()},
  earlier_mathematical_validation=dict(file=str(original.relative_to(DATA)),sha256=sha(original)),
  higher_loop_mathematical_validation=dict(file="higher_loops/validation.json",sha256=sha(HERE/"validation.json")),
  catalog_sha256=sha(DATA/"catalog.json"),split_sha256=sha(ROOT/"ML_model_seed_selection/split_manifest.json"),elapsed_seconds=time.time()-start,
  statement="Every family manifest and cross-folder target linkage was checked. The original mathematical evidence and the independent higher-loop checks remain separately preserved. Current grouped split assignments supersede historical labels stored inside original records.")
 (DATA/"validation_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
