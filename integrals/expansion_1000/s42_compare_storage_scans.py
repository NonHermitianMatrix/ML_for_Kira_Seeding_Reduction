"""Compare equivalent storage scans on immutable training features."""
import json,os,time,resource
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def old_scan(root):
 total=0
 for p in root.rglob("*"):
  try:
   if p.is_file() and not p.is_symlink():total+=p.stat().st_size
  except FileNotFoundError:pass
 return total
def new_scan(root):
 total=0;pending=[str(root)]
 while pending:
  with os.scandir(pending.pop()) as entries:
   for entry in entries:
    try:
     if entry.is_symlink():continue
     if entry.is_dir(follow_symlinks=False):pending.append(entry.path)
     elif entry.is_file(follow_symlinks=False):total+=entry.stat(follow_symlinks=False).st_size
    except FileNotFoundError:pass
 return total
def main():
 root=ROOT/"ML_model_seed_selection/data/training";checks=[]
 for label,fn in [("old",old_scan),("new",new_scan),("new",new_scan),("old",old_scan)]:
  start=time.monotonic();size=fn(root)
  checks.append(dict(method=label,bytes=size,seconds=time.monotonic()-start));print(checks[-1],flush=True)
 assert len({r["bytes"] for r in checks})==1
 result=dict(status="passed",checks=checks,same_byte_count=True,training_features_only=True,model_updates=0,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 (HERE/"storage_scan_comparison.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
