"""Check publication storage bounds against actual allocated fixture sizes."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 spec=importlib.util.spec_from_file_location("publisher",HERE/"s20_publish_release.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 checks=[]
 with tempfile.TemporaryDirectory(prefix="publication-storage-check-",dir=str(ROOT/".tools")) as folder:
  base=Path(folder);(base/".git").mkdir();(base/"phase").mkdir()
  (base/"immutable.bin").write_bytes(b"x"*32768)
  mod.ROOT=base;mod.HERE=base/"phase";mod._storage_snapshot=None
  def check(label):
   bound=mod.guard();actual=mod.allocated([base])
   assert bound>=actual,(label,bound,actual)
   checks.append(dict(case=label,allocated_bytes=actual,guard_bound=bound))
  check("initial full measurement")
  (base/".git"/"new_blob").write_bytes(bytes(range(256))*4096)
  check("new Git object")
  (base/"phase"/"new_record").write_bytes(b"record\n"*10000)
  check("publication records grow")
  (base/".git"/"new_blob").unlink()
  check("removal never lowers the initial bound")
  initial_mutable=mod.allocated([base/".git",base/"phase"])
  mod._storage_snapshot=(9495000000,initial_mutable)
  try:mod.guard()
  except AssertionError:checks.append(dict(case="9.7 GB stop bound including local and metadata reserves",stopped=True))
  else:raise AssertionError("Storage stop bound was not enforced")
 result=dict(status="passed",checks=checks,temporary_files_removed=True,
  scope="The publisher alone runs after dependent writers complete; its mutable paths are .git and the publication folder.",
  publication_source_sha256=hashlib.sha256((HERE/"s20_publish_release.py").read_bytes()).hexdigest())
 (HERE/"publication_storage_guard_validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
