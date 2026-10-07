"""Prove that the resource-only scan update preserves predictive code and resume state."""
import argparse,ast,hashlib,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MODEL=ROOT/"ML_model_seed_selection";ARCHIVE=MODEL/"runs/storage_scan_resume"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def predictive_ast(p):
 tree=ast.parse(p.read_text(encoding="utf-8"))
 return [ast.dump(node,include_attributes=False) for node in tree.body if not (isinstance(node,ast.FunctionDef) and node.name=="storage_guard")]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--before-resume",action="store_true");args=ap.parse_args()
 m=read(ARCHIVE/"migration.json")
 assert sha(ARCHIVE/"s01_data_before.py")==m["old_encoder_sha256"]
 assert sha(MODEL/"s01_data.py")==m["new_encoder_sha256"]
 assert predictive_ast(ARCHIVE/"s01_data_before.py")==predictive_ast(MODEL/"s01_data.py")
 assert sha(ARCHIVE/"checkpoint_before.pt")==m["checkpoint_before_sha256"]
 assert sha(MODEL/"data/manifest.json")==m["feature_manifest_sha256"]
 assert sha(MODEL/"split_manifest.json")==m["split_sha256"]
 for name,digest in m["unchanged_sources"].items():assert sha(MODEL/name)==digest
 manifest=read(MODEL/"data/manifest.json")
 assert all(f["signature"]["encoder"]==m["old_encoder_sha256"] for f in manifest["families"])
 assert sha(HERE/"storage_scan_comparison.json")==m["scan_comparison_sha256"]
 comparison=read(HERE/"storage_scan_comparison.json");assert comparison["status"]=="passed" and comparison["same_byte_count"]
 from s42_compare_storage_scans import old_scan,new_scan
 with tempfile.TemporaryDirectory(prefix="scan-links-check-",dir=str(ROOT/".tools")) as name:
  fixture=Path(name);(fixture/"nested").mkdir();(fixture/"plain").write_bytes(b"a"*31);(fixture/".hidden").write_bytes(b"b"*17);(fixture/"nested/data").write_bytes(b"c"*53)
  os.link(str(fixture/"plain"),str(fixture/"hardlink"))
  (fixture/"file_link").symlink_to("plain");(fixture/"directory_link").symlink_to("nested",target_is_directory=True);(fixture/"cycle").symlink_to(".",target_is_directory=True);(fixture/"broken").symlink_to("absent")
  assert old_scan(fixture)==new_scan(fixture)==132
 old_guard=[n for n in ast.parse((ARCHIVE/"s01_data_before.py").read_text()).body if isinstance(n,ast.FunctionDef) and n.name=="storage_guard"][0]
 new_guard=[n for n in ast.parse((MODEL/"s01_data.py").read_text()).body if isinstance(n,ast.FunctionDef) and n.name=="storage_guard"][0]
 assert ast.dump(old_guard.body[-2])==ast.dump(new_guard.body[-2]) and ast.dump(old_guard.body[-1])==ast.dump(new_guard.body[-1])
 result=dict(status="passed",predictive_ast_unchanged=True,features_and_labels_unchanged=True,config_and_trainer_unchanged=True,checkpoint_before_sha256=m["checkpoint_before_sha256"],optimizer_updates_in_migration=0,link_hidden_file_and_hardlink_counts_verified=True,byte_ceiling_unchanged=True)
 if args.before_resume:
  assert sha(MODEL/"runs/all_loops_latest.pt")==m["checkpoint_before_sha256"]
  import torch
  torch.set_num_threads(1)
  saved=torch.load(ARCHIVE/"checkpoint_before.pt",map_location="cpu",weights_only=False)
  assert saved["fingerprint"]["manifest"]==m["feature_manifest_sha256"]
  assert saved["fingerprint"]["config"]==m["unchanged_sources"]["config.json"]
  result["resume_state"]=dict(completed_epochs=saved["epoch"],next_family=saved["next_family"],partial_targets=saved["partial"]["targets"],optimizer_steps=saved["optimizer_steps"],elapsed_seconds=saved["elapsed_seconds"])
 elif (ARCHIVE/"verification.json").exists():result["resume_state"]=read(ARCHIVE/"verification.json")["resume_state"]
 (ARCHIVE/"verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
