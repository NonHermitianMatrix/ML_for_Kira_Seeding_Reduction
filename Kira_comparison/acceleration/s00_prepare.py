"""Freeze development and evaluation families before new timing outcomes."""
import collections,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rank(x):return hashlib.sha256(("native-acceleration-v1:"+x).encode()).hexdigest()
def main():
 m=json.loads((ROOT/"ML_model_seed_selection/split_manifest.json").read_text())
 old=json.loads((HERE.parent/"plan.json").read_text())
 excluded={x["meta"]["family"] for x in old["family_cases"]}
 excluded_groups={x["meta"]["group"] for x in old["family_cases"] if x["meta"]["family"].startswith("box")}
 train=sorted([x for x in m["families"] if x["split"]=="train" and x["family"].startswith("box")],key=lambda x:rank(x["group"]))
 test=sorted([x for x in m["families"] if x["split"]=="test" and x["family"].startswith("box") and x["family"] not in excluded and x["group"] not in excluded_groups],key=lambda x:rank(x["group"]))
 def cases(rows,split):
  return [dict(meta=x,domain="box",partition=split) for x in rows]
 # Select disjoint kinematic groups before any native timing.
 def grouped(rows):
  groups=collections.defaultdict(list)
  for x in rows:groups[x["group"]].append(x)
  keys=sorted(groups,key=rank)
  return [sorted(groups[k],key=lambda x:rank(x["family"]))[:2] for k in keys]
 tg=grouped(train);eg=grouped(test)
 flatten=lambda groups:[x for g in groups for x in g]
 plan=dict(schema=3,train=cases(flatten(tg[:6]),"train"),validation=cases(flatten(tg[6:9]),"validation"),test=cases(flatten(eg[:6]),"test"),
  target_sizes=[16,64],selection="Two families per SHA256-ranked kinematic group; disjoint development and validation groups; exclude all previous cost-comparison box groups",
  seed_checkpoint_sha256=sha(ROOT/"ML_model_seed_selection/trained_model.pt"),
  row_checkpoint_sha256=sha(ROOT/"ML_model_reduction/trained_model.pt"),
  split_sha256=sha(ROOT/"ML_model_seed_selection/split_manifest.json"),
  repetitions=5,development_repetitions=1,threads=1,concurrency=2,timeout_seconds=180,
  virtual_memory_bytes=1900000000,rss_limit_bytes=1700000000,scratch_limit_bytes=67108864,
  retained_bytes_limit=125000000,previous_project_upper_bytes=8710940188,
  resource_reserve_bytes=800000000,scope="Native symbolic IBP reduction with individual seed filtering and lower-cost learned choices. Development outcomes cannot select test cases.")
 assert plan["previous_project_upper_bytes"]+plan["resource_reserve_bytes"]<10000000000
 out=HERE/"plan.json"
 if out.exists():assert json.loads(out.read_text())==plan
 else:out.write_text(json.dumps(plan,indent=2)+"\n")
 print(json.dumps({k:[x["meta"]["family"] for x in plan[k]] for k in ["train","validation","test"]},indent=2))
if __name__=="__main__":main()
