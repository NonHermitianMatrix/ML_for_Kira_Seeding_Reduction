"""Prepare common native master bases sequentially under the reference budget."""
import hashlib,json,os,pathlib
from s02_run import run
from s03_records import read_record
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def verify():
 frozen=json.loads((HERE/"freeze.json").read_text())
 for n,h in frozen["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 return frozen
def main():
 verify();os.environ.update(KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=".tools/kira-runtime-final/kira",KIRA_SPARSE_FEATURES="1")
 manifest=json.loads((HERE/"reserved_families.json").read_text());cases={c["id"]:c for c in manifest["cases"]}
 for b in manifest["batches"]:
  c=cases[b["case"]];size=b["size"];p=HERE/"reserved_references"/f'{c["id"]}_n{size}.json.gz'
  if p.exists():r=read_record(p)
  else:r=run(c,size,"native",p,timeout=360,margin=1,records=False,scratch_cap=256*1024**2)
  print(json.dumps(dict(case=c["id"],size=size,status=r["status"],seconds=r["complete_seconds"],masters=len(r.get("masters",[])))),flush=True)
  assert r["success"] and r["complete"],(c["id"],size,r["status"])
if __name__=="__main__":main()
