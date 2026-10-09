"""Fix new timing cases and resource limits before measuring the new interface."""
import collections,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rank(s):return hashlib.sha256(("fermat-exit-v1:"+s).encode()).hexdigest()
def main():
 split=json.loads((ROOT/"ML_model_seed_selection/split_manifest.json").read_text())
 old=json.loads((HERE.parent/"acceleration/plan.json").read_text())
 prior=json.loads((HERE.parent/"plan.json").read_text())
 excluded={x["meta"]["group"] for x in old["test"]+prior["family_cases"] if x["meta"]["family"].startswith("box")}
 groups=collections.defaultdict(list)
 for row in split["families"]:
  if row["split"]=="test" and row["family"].startswith("box") and row["group"] not in excluded:groups[row["group"]].append(row)
 selected=[row for g in sorted(groups,key=rank)[:6] for row in sorted(groups[g],key=lambda x:rank(x["family"]))[:2]]
 assert len(selected)==12 and len({x["group"] for x in selected})==6
 plan=dict(schema=1,development=old["train"][:3],test=[dict(meta=x,domain="box",partition="test") for x in selected],
  policies=["stock_pool","stock_ml","exit_pool","exit_ml"],target_sizes=[1,16],repetitions=5,
  threshold=0.01,threads=1,concurrency=2,timeout_seconds=180,rss_limit_bytes=1700000000,
  address_space_bytes=1900000000,scratch_limit_bytes=33554432,retained_limit_bytes=12000000,
  base_publication_upper_bytes=9748197386,new_tools_reserve_bytes=16000000,new_report_reserve_bytes=48000000,
  metadata_reserve_bytes=8000000,
  seed_checkpoint_sha256=sha(ROOT/"ML_model_seed_selection/trained_model.pt"),
  row_checkpoint_sha256=sha(ROOT/"ML_model_reduction/trained_model.pt"),
  split_sha256=sha(ROOT/"ML_model_seed_selection/split_manifest.json"),
  selection="Two SHA256-ranked instances in each of six original-test kinematic groups excluded from all prior cost-test box groups.",
  scope="Cold complete supplied-equation reductions. Four-way control isolates responsive Fermat shutdown and the unchanged seed model. Generation of the shared identity pools is outside every measured method.",
  primary="exit_ml versus stock_ml for one target; also compare exit_ml versus exit_pool and stock_pool.",
  secondary="Sixteen-target batches; failures and skipped repetitions retained; no policy tuning on test outcomes.")
 plan["working_publication_upper_bytes"]=plan["base_publication_upper_bytes"]+4*plan["retained_limit_bytes"]+plan["new_tools_reserve_bytes"]+plan["new_report_reserve_bytes"]+plan["metadata_reserve_bytes"]+2*plan["scratch_limit_bytes"]
 assert plan["working_publication_upper_bytes"]<10000000000
 p=HERE/"plan.json"
 if p.exists():assert json.loads(p.read_text())==plan
 else:p.write_text(json.dumps(plan,indent=2)+"\n")
 print(json.dumps({"families":[x["family"] for x in selected],"storage_upper":plan["working_publication_upper_bytes"]}))
if __name__=="__main__":main()
