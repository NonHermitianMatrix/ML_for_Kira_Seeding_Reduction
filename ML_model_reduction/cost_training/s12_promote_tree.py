"""Preserve the linear continuation model and install the validated tree candidate."""
import hashlib,json,pathlib,shutil
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 results=json.loads((HERE/"tree_candidate_results.json").read_text())
 assert results["validation"]["geometric_ratio"]<1
 assert (ROOT/".tools/kira-cost-tree/kira").exists()
 old=HERE/"linear_continuation_v2";assert not old.exists();old.mkdir()
 for name in ["trained_model.json","trained_weights.txt","training_results.json","build.json","reduction_cost.patch"]:
  shutil.copy2(HERE/name,old/name)
 for src,dst in [("tree_candidate_model.json","trained_model.json"),("tree_candidate_weights.txt","trained_weights.txt"),("tree_candidate_results.json","training_results.json")]:
  shutil.copy2(HERE/src,HERE/dst)
 model=json.loads((HERE/"trained_model.json").read_text());model["minimum_group_size"]=3;model["maximum_group_size"]=32
 (HERE/"trained_model.json").write_text(json.dumps(model,indent=2)+"\n")
 record=dict(previous_weights_sha256=hashlib.sha256((old/"trained_weights.txt").read_bytes()).hexdigest(),
  weights_sha256=hashlib.sha256((HERE/"trained_weights.txt").read_bytes()).hexdigest(),
  binary_sha256=hashlib.sha256((ROOT/".tools/kira-cost-tree/kira").read_bytes()).hexdigest(),
  reason="lower measured continuation operation count on the untouched development validation states",
  final_reserved_results_used=False)
 (HERE/"tree_promotion.json").write_text(json.dumps(record,indent=2)+"\n")
 print("Installed continuation tree; previous models preserved",flush=True)
if __name__=="__main__":main()
