"""Validate exact master-span decisions independently before the full run."""
import gzip,shutil,collections
from s06_evaluate import *
def main():
 metas={m["family"]:m for m in read(MODEL/"split_manifest.json")["families"] if m["split"]=="test"}
 entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
 dest=HERE/"span_pilot";results=[]
 for fid in ["box_massless_one_offshell","box_profile_0078","vacuum_L12_profile015"]:
  family=load_family(metas[fid],entries[fid]);blocks=selected_blocks(family)
  w=Path(os.environ["KIRA_SCRATCH"])/fid;manifest=export(family,blocks,w)
  run=read(dest/(fid+".run.json"));assert sha(w/"system.kira")==run["input_sha256"]
  out=w/"raw.kira"
  with gzip.open(str(dest/(fid+"_results_Tuserweight_kira_targets.kira.gz")),"rb") as a,out.open("wb") as b:shutil.copyfileobj(a,b)
  assert sha(out)==run["output_sha256"]
  refs={r["id"]:r for r in rows(DATA/metas[fid]["references"])}
  records=assess_span(family,manifest,parse_output(out),refs)
  checks=check_span_records(family,blocks,records,refs)
  byblock={b["id"]:b for b in manifest["blocks"]};states={}
  for rec in records:
   for policy,ids in byblock[rec["block"]]["policies"].items():
    if rec["target"] in ids:states[rec["target"],policy]=rec["status"]=="sufficient"
  explicit=0
  if fid=="box_massless_one_offshell":
   old=json.load(gzip.open(str(HERE/"archive_coefficient_reductions/results/worker_00"/(fid+".summary.json.gz")),"rt"))
   for t in old["target_results"]:
    for policy in POLICIES:
     assert states[t["target"],policy]==(t[policy]=="exact_match");explicit+=1
  if fid=="vacuum_L12_profile015":
   old=json.load(gzip.open(str(HERE/"pilot"/(fid+"_000.json.gz")),"rt"));oldblocks={b["id"]:b for b in old["manifest"]["blocks"]}
   for t in old["records"]:
    for policy,ids in oldblocks[t["block"]]["policies"].items():
     if t["target"] in ids:
      assert states[t["target"],policy]==(t["status"]=="exact_match");explicit+=1
  results.append(dict(family=fid,targets=len(family["targets"]),independent_rank_checks=checks,explicit_coefficient_decisions_compared=explicit,input_regenerated=True))
  shutil.rmtree(w);clear_caches()
 write(dest/"validation.json",dict(passed=True,families=results))
 protocol();print(json.dumps(results),flush=True)
if __name__=="__main__":main()
