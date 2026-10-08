"""Independently check final exports, selected identities, paths and complete trial coverage."""
from s01_common import *
from s08_verify import evaluate
def vector(terms,point,p):
 out={}
 for t in terms:
  a=tuple(t["indices"]);v=(out.get(a,0)+evaluate(t["coefficient"],point,p))%p
  if v:out[a]=v
  else:out.pop(a,None)
 return out
def main():
 frozen=read(HERE/"frozen_inputs.json")
 for name,digest in frozen["sha256"].items():assert sha(ROOT/name)==digest,name
 plan=read(HERE/"plan.json");checked=0;targets_checked=0;failed=[];hashes={};pathsteps=0
 for i,case in enumerate(plan["family_cases"]):
  meta=case["meta"];maximum=min(16,meta["counts"]["targets"]);fam=load_case(case,maximum)
  refs={r["id"]:r for r in old.rows(DATA/meta["references"])}
  ids={e["id"]:e for e in fam["identities"]};inputmap={x["id"]:x for x in fam["targets"]}
  sizes=sorted(set(min(s,meta["counts"]["targets"]) for s in plan["batch_sizes"]))
  policies=plan["policies"]+(plan["native_policies"] if case["domain"]!="vacuum" else [])
  for size in sizes:
   want=[x["id"] for x in fam["targets"][:size]]
   for rep in range(plan["repetitions"]):
    for policy in policies:
     name="%02d_n%02d_r%d_%s.json.gz"%(i,size,rep,policy);pfile=HERE/"results"/name
     with gzip.open(pfile,"rt") as f:r=json.load(f)
     hashes[name]=sha(pfile);checked+=1
     assert (r["case"],r["size"],r["repetition"],r["policy"])==(i,size,rep,policy)
     assert r["cold_seconds"]>0 and r["process_tree_peak_rss_bytes"]>0
     if r["resource_status"]!="completed":
      failed.append(dict(trial=r["trial"],status=r["resource_status"]));continue
     assert r["targets"]==want
     assert r["success"]==all(c["status"]=="exact_match" for c in r["checks"])
     if not r["success"]:failed.append(dict(trial=r["trial"],status="incomplete_or_mismatch"))
     if policy=="ml_seeds":
      positions=set()
      for item in r["model"]["probabilities"]:
       assert item["target"] in want and len(item["probabilities"])==len(fam["seeds"])
       assert all(0<=v<=1 for v in item["probabilities"])
       positions.update(j for j,v in enumerate(item["probabilities"]) if v>=.5)
      selected={fam["seeds"][j] for j in positions}
      assert selected=={tuple(x) for x in r["model"]["selected_seeds"]}
      available=[e for e in fam["identities"] if e["source"]["kind"]!="ibp" or tuple(e["source"]["seed"]) in selected]
      expected=[e["id"] for e in connected(available,fam["targets"][:size],fam["masters"])]
      assert r["attempts"][0]["source_ids"]==expected
      assert len(r["attempts"])==(1 if r["first_attempt_complete"] else 2)
     if policy=="kira_pool" or r["fallback"]:
      expected=[e["id"] for e in connected(fam["identities"],fam["targets"][:size],fam["masters"])]
      assert r["attempts"][-1]["source_ids"]==expected
     for c in r["checks"]:
      if c["status"]!="exact_match":continue
      ref=refs[c["target"]]
      for sample in ref["samples"]:
       point=tuple(sorted(sample["point"].items()));prime=sample["prime"]
       expected={tuple(map(int,k.split(","))):int(v)%prime for k,v in sample["master_coefficients"].items() if int(v)%prime}
       assert vector(c["coefficients"],point,prime)==expected,(r["trial"],c["target"])
       targets_checked+=1
     if policy in ("ml_reduction","local_reduction"):
      assert sum(step["operations"] for row in r["model"]["paths"] for step in row["path"])==r["model"]["coefficient_field_operations"]
      for row in r["model"]["paths"]:
       target=inputmap[row["target"]];ref=refs[row["target"]]
       for sample in ref["samples"]:
        point=tuple(sorted(sample["point"].items()));prime=sample["prime"];v=vector(target["terms"],point,prime)
        for step in row["path"]:
         src=vector(ids[step["equation"]]["terms"],point,prime);pivot=tuple(step["pivot"])
         if not v.get(pivot):continue
         assert src.get(pivot),(r["trial"],"singular independent pivot")
         factor=v[pivot]*pow(src[pivot],-1,prime)%prime
         for a,c in src.items():
          value=(v.get(a,0)-factor*c)%prime
          if value:v[a]=value
          else:v.pop(a,None)
         assert pivot not in v;pathsteps+=1
        if row["status"]=="complete":
         expected={tuple(map(int,k.split(","))):int(c)%prime for k,c in sample["master_coefficients"].items() if int(c)%prime}
         assert v==expected
     # Independently interpret the actual archived Kira export, including native labels.
     attempt=len(r["attempts"])-1
     keys=[k for k in r["evidence"] if k.startswith("attempt%d/"%attempt) and k.endswith("kira_targets.kira") and "/combine/" not in k]
     assert len(keys)==1
     raw=r["evidence"][keys[0]];assert hashlib.sha256(raw.encode()).hexdigest()==r["attempts"][-1]["export_sha256"]
     rows={};block=[]
     def consume(lines):
      entries=[]
      for line in lines:
       pattern=r"F\[([-\d,]+)\]\*\((.*)\)" if policy.startswith("kira_native") else r"(\d+)\*\((.*)\)"
       match=re.fullmatch(pattern,line.strip());assert match
       key=tuple(map(int,match[1].split(","))) if policy.startswith("kira_native") else int(match[1])
       entries.append((key,match[2]))
      assert old.exact_equal(entries[0][1],"-1")
      rows[entries[0][0]]=entries[1:]
     for line in raw.splitlines()+[""]:
      if line.strip():block.append(line)
      elif block:consume(block);block=[]
     for tid in want:
      for sample in refs[tid]["samples"]:
       point=tuple(sorted(sample["point"].items()));prime=sample["prime"];got={}
       if policy.startswith("kira_native"):
        for a,v in vector(inputmap[tid]["terms"],point,prime).items():
         for b,c in rows.get(a,[(a,"1")]):
          got[b]=(got.get(b,0)+v*evaluate(c,point,prime))%prime
       else:
        manifest=r["attempts"][-1]["manifest"]
        weight=next(int(k) for k,v in manifest["targets"].items() if v["target"]==tid)
        for n,c in rows.get(weight,[]):
         a=tuple(manifest["mapping"][str(n)]["indices"]);got[a]=(got.get(a,0)+evaluate(c,point,prime))%prime
       got={a:v for a,v in got.items() if v}
       check=next(c for c in r["checks"] if c["target"]==tid)
       assert got==vector(check["coefficients"],point,prime)
  print(json.dumps(dict(family=fam["id"],trials_checked=checked)),flush=True)
 assert len(list((HERE/"results").glob("*.json.gz")))==checked
 write(HERE/"validation.json",dict(passed=True,trials=checked,independent_master_sample_checks=targets_checked,
  independent_row_steps=pathsteps,incomplete_trials=failed,result_sha256=hashes,frozen_inputs_sha256=sha(HERE/"frozen_inputs.json"),
  checks="complete grid, frozen sources, threshold masks, connected source sets, raw Kira exports, independent modular coefficient and row checks"))
if __name__=="__main__":main()
