"""Verify deployment routing and preserve the preceding frozen releases."""
import hashlib,json,sys
from s04_workflows import HERE,PARENT,ROOT,read,guard
from s12_reduce import select
from s14_test import check
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 frozen=check();summary=json.loads((HERE/"model_test/summary.json").read_text());assert summary["all_exact"]
 manifest=json.loads((HERE/"families_test.json").read_text());cases={c["id"]:c for c in manifest["cases"]}
 config=json.loads((HERE/"trained_model/deployment.json").read_text())
 matched=0
 for b in manifest["batches"]:
  c=cases[b["case"]];n=b["size"];args=select(c,n,"deployed")
  for rep in range(manifest["repetitions"]):
   r=read(HERE/"model_test"/f'{c["id"]}_n{n}_deployed_r{rep}.json.gz')
   assert r["success"] and r["reference_checked"]
   assert r["mode"]==args.get("mode","off") and r["model"]==args.get("model")
   assert r["threshold"]==args.get("threshold",0) and r["base"]==args.get("base","native")
   assert r["attempts"][0]["binary_sha256"]==sha(ROOT/args["binary"])
   matched+=1
  altered=dict(c,targets=list(reversed(c["targets"])))
  assert select(altered,n,"deployed")==select(altered,n,"previous")
  assert select(c,1,"deployed")==select(c,1,"previous")
 old_checks=0
 for p in [PARENT/"trained_model/freeze.json",PARENT/"trained_model/confirmation_freeze.json",PARENT/"trained_model/deployment_verification.json"]:
  d=json.loads(p.read_text())
  for name,value in d["sha256"].items():assert sha(ROOT/name)==value,name;old_checks+=1
 audit=dict(all_passed=True,measured_deployment_workflows=matched,unsupported_target_lists_use_previous_guard=True,previous_release_hashes_checked=old_checks,all_final_frozen_hashes_match=True)
 (HERE/"trained_model/deployment_verification.json").write_text(json.dumps(audit,indent=2)+"\n")
 guard();print(json.dumps(audit))
if __name__=="__main__":main()
