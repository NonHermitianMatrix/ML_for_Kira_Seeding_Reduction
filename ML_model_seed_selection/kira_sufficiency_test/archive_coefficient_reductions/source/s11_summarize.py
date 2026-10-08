"""Validate saved solver records, then summarize exact target completion."""
import csv,gzip,collections
from s06_evaluate import *
def main():
 config=read(HERE/"protocol.json")
 assert sha(MODEL/"trained_model.pt")==config["model_sha256"]==EXPECTED_MODEL
 assert sha(MODEL/"split_manifest.json")==config["split_sha256"]==EXPECTED_SPLIT
 for name,digest in config["scripts"].items():assert sha(HERE/name)==digest,(name,"script changed after freezing")
 entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
 meta={m["family"]:m for m in read(MODEL/"split_manifest.json")["families"]}
 for i in range(config["workers"]):
  state=read(HERE/("worker_%02d.json"%i));assert state.get("finished") and not state["errors"],state
 totals={p:collections.Counter() for p in POLICIES};loops={};kinds={};domains={}
 agreement=collections.Counter();allfamilies=[];runs=0;samplechecks=0;kiraseconds=0.;peak=0;selected=0;candidates=0
 for index,fid in enumerate(config["family_ids"]):
  dest=HERE/"results"/("worker_%02d"%(index%config["workers"]))
  record=json.loads(gzip.open(str(dest/(fid+".summary.json.gz")),"rt").read())
  assert record["family"]==fid and record["targets"]==meta[fid]["counts"]["targets"]
  assert record["prediction_sha256"]==entries[fid]["sha256"]
  for name,digest in record["source_sha256"].items():assert sha(DATA/meta[fid][name])==digest
  assert sha(family_file(fid,"identities.jsonl.gz"))==record["identities_sha256"]
  archive=MODEL/"model_test"/entries[fid]["path"];assert sha(archive)==entries[fid]["sha256"]
  with np.load(str(archive),allow_pickle=False) as z:
   ids=[str(x) for x in z["target_ids"]];probabilities=z["probabilities"];labels=z["labels"]
   predicted=probabilities>=config["threshold"];same=(predicted==labels.astype(bool)).all(axis=1)
  pos={tid:i for i,tid in enumerate(ids)};actualcounts={p:collections.Counter() for p in POLICIES};states={}
  seedcount=predicted.shape[1]
  for b in record["batches"]:
   assert sha(dest/b["detail"])==b["detail_sha256"] and sha(dest/b["output"])==b["output_sha256"]
   detail=json.loads(gzip.open(str(dest/b["detail"]),"rt").read());manifest=detail["manifest"]
   assert detail["run"]==b["run"] and b["run"]["status"]=="completed"
   assert b["run"]["input_sha256"]==manifest["input_sha256"]
   raw=gzip.open(str(dest/b["output"]),"rb").read()
   assert hashlib.sha256(raw).hexdigest()==b["run"]["output_sha256"]
   assert len(raw)==b["run"]["output_bytes"]
   blocks={v["id"]:v for v in manifest["blocks"]}
   for block in blocks.values():
    mask=block["candidate_positions"]
    if block["policies"]["full"]:assert mask==list(range(seedcount))
    if block["policies"]["background"]:assert mask==[]
    for tid in block["policies"]["predicted"]:
     assert mask==np.flatnonzero(predicted[pos[tid]]).tolist()
   for r in detail["records"]:
    assert r["status"] in ("exact_match","residual_nonmasters"),r
    if r["status"]=="exact_match":assert not r["residual_indices"]
    else:assert r["residual_indices"]
    for policy,tids in blocks[r["block"]]["policies"].items():
     if r["target"] in tids:
      assert (r["target"],policy) not in states
      states[r["target"],policy]=r["status"];actualcounts[policy][r["status"]]+=1
   runs+=1;samplechecks+=b["run"]["independent_sample_checks"];kiraseconds+=b["run"]["seconds"]
   peak=max(peak,b["run"]["peak_scratch_allocated_bytes"])
  assert record["counts"]=={p:dict(c) for p,c in actualcounts.items()}
  loop=str(record["loops"]);domain="coupled_vacuum" if fid.startswith("vacuum_") else fid.split("_")[0]
  for t in record["target_results"]:
   tid=t["target"];i=pos[tid]
   assert t["selected_seeds"]==int(predicted[i].sum()) and t["candidate_seeds"]==seedcount
   selected+=t["selected_seeds"];candidates+=seedcount
   ok=t["predicted"]=="exact_match";agreement[("same" if same[i] else "different")+("_complete" if ok else "_incomplete")]+=1
   for container,key in [(loops,loop),(kinds,t["kind"]),(domains,domain)]:
    group=container.setdefault(key,dict(targets=0,selected_seeds=0,candidate_seeds=0,**{p:{} for p in POLICIES}))
    group["targets"]+=1;group["selected_seeds"]+=t["selected_seeds"];group["candidate_seeds"]+=seedcount
    for policy in POLICIES:
     assert t[policy]==states[tid,policy]
     group[policy][t[policy]]=group[policy].get(t[policy],0)+1
   for policy in POLICIES:totals[policy][t[policy]]+=1
  allfamilies.append(dict(family=fid,loops=record["loops"],targets=record["targets"],
      predicted_complete=actualcounts["predicted"]["exact_match"],full_complete=actualcounts["full"]["exact_match"],
      background_complete=actualcounts["background"]["exact_match"],seconds=record["seconds"]))
 total=sum(totals["predicted"].values());assert total==config["targets"]
 assert sum(f["targets"] for f in allfamilies)==total and len(allfamilies)==config["families"]
 result=dict(targets=total,families=len(allfamilies),policies={p:dict(c) for p,c in totals.items()},
  by_loop=loops,by_kind=kinds,by_domain=domains,reference_set_agreement=dict(agreement),
  selected_seeds=selected,candidate_seeds=candidates,mean_selected_seeds=selected/total,
  selected_candidate_fraction=selected/candidates,kira_runs=runs,kira_process_seconds=kiraseconds,
  independent_sample_checks=samplechecks,peak_case_scratch_bytes=peak,
  full_candidate_fallback_complete=totals["full"]["exact_match"],model_sha256=EXPECTED_MODEL,split_sha256=EXPECTED_SPLIT,
  protocol_sha256=sha(HERE/"protocol.json"),scope="Symbolic Kira reduction of stored seed-filtered identities, with fixed background relations.")
 write(HERE/"results.json",result)
 with (HERE/"family_results.csv").open("w") as f:
  writer=csv.DictWriter(f,fieldnames=list(allfamilies[0]));writer.writeheader();writer.writerows(allfamilies)
 write(HERE/"validation.json",dict(passed=True,model_frozen=True,split_frozen=True,prediction_hashes_checked=len(allfamilies),
  coefficient_method="Exact integer-polynomial cross multiplication plus three independent finite-field samples",
  complete_kira_runs=runs,independent_sample_checks=samplechecks,unexpected_statuses=0,
  source_hashes_verified=True,threshold_recomputed=True,all_held_out_targets_accounted_for=True,
  result_sha256=sha(HERE/"results.json")))
 print(json.dumps(result,indent=2),flush=True)
if __name__=="__main__":main()
