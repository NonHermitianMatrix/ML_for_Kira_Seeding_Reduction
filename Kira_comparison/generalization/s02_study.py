"""Frozen transfer tests with symbolic coefficients and exact native fallback."""
import argparse,gzip,hashlib,json,os,pathlib,statistics,sys,time
from s00_native_run import run
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WEIGHTS=ROOT/"ML_model_equation_selection/early_generation/trained_model/early_d12/weights.txt"
BINARY=ROOT/".tools/kira-early-generation/kira"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 with gzip.open(p,"rt") as f:return json.load(f)
def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(p,"wt",compresslevel=9) as f:json.dump(r,f,separators=(",",":"))
 used=sum(x.stat().st_blocks*512 for x in HERE.rglob("*") if x.is_file())
 assert used<8*1024**2,("retained limit",used)
def setup(mode="off"):
 os.environ.update(KIRA_RUNTIME_SCRATCH="node",KIRA_RUNTIME_BINARY=str(BINARY),
  KIRA_EQ_MODE=mode,KIRA_EQ_THRESHOLD="0.01",KIRA_EQ_WEIGHTS=str(WEIGHTS),KIRA_EQ_COLLECT="0",
  KIRA_PARALLEL_EVAL="1",KIRA_FAST_EVAL="1",KIRA_SPARSE_FEATURES="1",KIRA_ROW_PAIR_FASTPATH="1")
def attempt(c,mode="off",ref=None,margin=0):
 setup(mode)
 return run(c,c["size"],"native",HERE/"unused",timeout=150,margin=margin,reference=ref,
  records=False,archive=False,check_masters=bool(ref),scratch_cap=32*1024**2)
def reference(c):
 out=HERE/"references"/(c["id"]+".json.gz")
 if out.exists():return out
 r=attempt(c,margin=1);save(out,r)
 print(json.dumps(dict(stage="reference",case=c["id"],success=r["success"],status=r["status"],seconds=r["complete_seconds"])),flush=True)
 return out
def workflow(c,method,ref):
 begin=time.perf_counter();attempts=[]
 for mode,margin in ([("learned",0),("off",0),("off",1)] if method=="learned" else [("off",0),("off",1)]):
  r=attempt(c,mode,ref,margin);attempts.append(r)
  if r["success"] or r.get("mismatches"):break
 return dict(case=c["id"],method=method,success=attempts[-1]["success"],attempts=attempts,
  complete_seconds=time.perf_counter()-begin,fallback_count=len(attempts)-1)
def freeze():
 record=dict(parent_commit="4fe02746cd5e56281559807ff245e65638f33c1a",
  weights_sha256=sha(WEIGHTS),binary_sha256=sha(BINARY),
  sources={p.name:sha(p) for p in [HERE/n for n in ["s00_native_run.py","s01_cases.py","s02_study.py"]]},
  cases_sha256=sha(HERE/"cases.json"),methods=["native","learned"],threshold=.01,repetitions=5,
  primary_time="Driver-running complete time, including preparation, inference, native IBP generation, exact symbolic comparison, cleanup and all fallback. Reference discovery and independent audits excluded.",
  independence="New graph families and symbolic kinematics were absent from model training. No fitting or policy selection uses these results.",
  optimum_scope="Separate finite certificates specify allowed pivots and coefficient-operation counts; unrestricted optimality is not claimed.")
 p=HERE/"freeze.json"
 if p.exists():assert json.loads(p.read_text())==record
 else:p.write_text(json.dumps(record,indent=2)+"\n")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("action",choices=["prepare","pilot","freeze","test"]);a=ap.parse_args()
 if a.action=="prepare":
  import s01_cases;s01_cases.main();freeze()
  a.action="pilot"
 manifest=json.loads((HERE/"cases.json").read_text())
 if a.action=="freeze":freeze();return
 if a.action=="pilot":
  for c in manifest["pilots"]:
   ref=reference(c)
   if not load(ref)["success"]:continue
   for method in ["native","learned"]:
    out=HERE/"development"/f'{c["id"]}_{method}.json.gz'
    if out.exists():continue
    r=workflow(c,method,ref);save(out,r)
    print(json.dumps({k:r[k] for k in ["case","method","success","complete_seconds","fallback_count"]}),flush=True)
 elif a.action=="test":
  freeze()
  for c in manifest["cases"]:
   ref=reference(c)
   if not load(ref)["success"]:continue
   for rep in range(5):
    for method in (["native","learned"] if rep%2==0 else ["learned","native"]):
     out=HERE/"model_test"/f'{c["id"]}_{method}_{rep}.json.gz'
     if out.exists():continue
     r=workflow(c,method,ref);r["repetition"]=rep;save(out,r)
     print(json.dumps({k:r[k] for k in ["case","method","success","complete_seconds","fallback_count"]}),flush=True)
if __name__=="__main__":main()
