"""Bounded native comparisons for decisions made before equation construction."""
import argparse,gzip,hashlib,json,os,pathlib,sys,time
HERE=pathlib.Path(__file__).resolve().parent;PARENT=HERE.parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(PARENT))
from s03_early_run import run
from functools import lru_cache
from s02_records import read as legacy_read
HEAVY_FIELDS=("coefficients","raw_export","targets","input","prescribed_basis","masters","identity_master_targets","predictions","seed_audit")
def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":")).encode()
@lru_cache(maxsize=16)
def payload(name):
 p=(HERE/name).resolve()
 assert HERE in p.parents and p.parent==HERE/"objects"
 with gzip.open(p,"rt") as f:r=json.load(f)
 assert hashlib.sha256(canonical(r)).hexdigest()==p.name.removesuffix(".json.gz")
 return r
def read(p):
 r=legacy_read(p)
 if not isinstance(r,dict) or "attempts" not in r:return r
 for a in r["attempts"]:
  name=a.pop("_shared_payload",None)
  if name:
   extra=payload(name);assert not (a.keys()&extra.keys());a.update(extra)
 r.pop("_storage_format",None)
 return r
OLD=".tools/kira-equation-selection/kira-lazy"
EARLY=".tools/kira-early-generation/kira"
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def setup():
 os.environ.update(KIRA_RUNTIME_SCRATCH="node",KIRA_PARALLEL_EVAL="1",KIRA_FAST_EVAL="1",KIRA_CPP_SEED="1",KIRA_SPARSE_FEATURES="1",KIRA_ROW_PAIR_FASTPATH="1",KIRA_EQ_COLLECT="0")
def guard():
 plan=json.loads((HERE/"resource_plan.json").read_text())
 used=sum(p.stat().st_blocks*512 for p in HERE.rglob("*") if p.is_file())
 assert used<plan["new_retained_cap_bytes"],("retained storage cap",used)
 tools=ROOT/".tools/kira-early-generation"
 used=sum(p.stat().st_blocks*512 for p in tools.rglob("*") if p.is_file())
 assert used<plan["new_tools_cap_bytes"],("tool storage cap",used)
def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 stored=r
 if "attempts" in r:
  stored=dict(r);stored["attempts"]=[]
  for original in r["attempts"]:
   a=dict(original);heavy={k:a.pop(k) for k in HEAVY_FIELDS if k in a}
   digest=hashlib.sha256(canonical(heavy)).hexdigest()
   obj=HERE/"objects"/(digest+".json.gz");obj.parent.mkdir(exist_ok=True)
   if not obj.exists():
    with gzip.open(obj,"wt",compresslevel=9) as f:json.dump(heavy,f,separators=(",",":"))
   a["_shared_payload"]=str(obj.relative_to(HERE));stored["attempts"].append(a)
  stored["_storage_format"]="early-shared-v1"
 temp=p.with_name(p.name+".tmp")
 with gzip.open(temp,"wt",compresslevel=9) as f:json.dump(stored,f,separators=(",",":"))
 temp.replace(p)
 assert read(p)==r,("storage round trip",p)
 guard()
def cases(split,additional_only=False):
 manifests=[json.loads((HERE/"additional_families.json").read_text())]
 if not additional_only:manifests.insert(0,json.loads((PARENT/"families.json").read_text()))
 return [(c,b["size"]) for m in manifests for b in m["batches"] for c in m["cases"] if c["id"]==b["case"] and c["split"]==split]
def set_policy(binary,mode,threshold=0,model=None):
 os.environ.update(KIRA_RUNTIME_BINARY=binary,KIRA_EQ_MODE=mode,KIRA_EQ_THRESHOLD=str(threshold),KIRA_EQ_COLLECT="1" if mode=="collect" else "0")
 if model:os.environ["KIRA_EQ_WEIGHTS"]=str(PARENT/"trained_model/weights.txt" if model=="previous" else HERE/"trained_model"/model/"weights.txt")
def reference(c,n):
 name=f'{c["id"]}_n{n}.json.gz'
 for d in [HERE/"references",PARENT/"references",ROOT/"Kira_comparison/integrated_runtime/references",ROOT/"Kira_comparison/multiloop_native/references",ROOT/"Kira_comparison/integrated_runtime/reserved_references"]:
  p=d/name
  if p.exists():
   r=read(p);assert r["group"]==c["group"] and r["size"]==n,(p,c["id"])
   return p
 p=HERE/"references"/name;set_policy(OLD,"off")
 r=run(c,n,"native",p,timeout=90,margin=1,records=False,archive=False,scratch_cap=16*1024**2)
 save(p,r);assert r["success"],(c["id"],r["status"])
 return p
def workflow(c,n,label,ref,out,binary=EARLY,mode="off",threshold=0,model=None,basis=None,base="native",weights=None,started=None):
 start=time.perf_counter() if started is None else started;attempts=[]
 steps=[(mode,base,0)]
 if mode!="off":steps.append(("off",base,0))
 fallback="learned" if base=="combined_closed" else "native" if base=="seed_closed" else base
 if base in ("seed_closed","combined_closed"):steps.append(("off",fallback,0))
 steps.append(("off",fallback,1))
 for current,policy,margin in steps:
  set_policy(binary,current,threshold,model)
  r=run(c,n,policy,out,timeout=70,margin=margin,reference=ref,records=False,archive=False,check_masters=True,scratch_cap=16*1024**2,basis=basis,weights=weights)
  attempts.append(r)
  if r["success"] or r.get("mismatches"):break
 stages={}
 for a in attempts:
  for m in a.get("stage_metrics",[]):stages[m["stage"]]=stages.get(m["stage"],0)+m["seconds"]
 result=dict(case=c["id"],group=c["group"],topology=c["topology_group"],split=c["split"],size=n,label=label,mode=mode,threshold=threshold,model=model,base=base,success=attempts[-1]["success"],reference_checked=attempts[-1]["reference_checked"],complete_seconds=time.perf_counter()-start,attempt_count=len(attempts),attempts=attempts,stage_seconds=stages,forward_seconds=sum(m.get("forward_seconds",0) for a in attempts for m in a.get("metrics",[])),equation_preparation_seconds=sum(stages.get(k,0) for k in ["generation_modular","equation_regeneration","equation_selection","equation_selection_coeff","modular_solve"]),constructed_calls=sum(a.get("equation_metrics",{}).get("retained_calls",0) for a in attempts),skipped_construction_calls=sum(a.get("equation_metrics",{}).get("construction_skipped_calls",0) for a in attempts))
 save(out,result)
 assert result["success"],(c["id"],label,attempts[-1]["status"])
 return result
def collect():
 for c,n in cases("training",True):
  out=HERE/"training"/f'{c["id"]}_n{n}.json.gz'
  if out.exists():continue
  ref=reference(c,n);set_policy(OLD,"collect")
  r=run(c,n,"native",out,timeout=90,margin=0,reference=ref,records=False,archive=False,check_masters=True,scratch_cap=16*1024**2)
  if not r["success"]:
   save(out.with_name(out.name.replace(".json.gz","_failed.json.gz")),r)
   r=run(c,n,"native",out,timeout=90,margin=1,reference=ref,records=False,archive=False,check_masters=True,scratch_cap=16*1024**2)
  save(out,r);assert r["success"] and r["reference_checked"]
  print(json.dumps(dict(action="collect",case=c["id"],size=n,rows=len(r.get("equation_records","").splitlines()))),flush=True)
def pilot():
 methods=[dict(label="baseline",binary=OLD),dict(label="early_off")]
 for model in ["early_d8","early_d12"]:
  for t in [.001,.003,.01]:methods.append(dict(label=model+"_t"+str(t),mode="learned",threshold=t,model=model))
 for i,(c,n) in enumerate(cases("validation")):
  ref=reference(c,n)
  order=methods[i%len(methods):]+methods[:i%len(methods)]
  for method in order:
   out=HERE/"validation/pilot"/f'{c["id"]}_n{n}_{method["label"]}.json.gz'
   if out.exists():continue
   r=workflow(c,n,ref=ref,out=out,**method)
   print(json.dumps(dict(action="pilot",case=c["id"],size=n,label=r["label"],seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("action",choices=["collect","pilot"]);a=ap.parse_args();setup();guard()
 collect() if a.action=="collect" else pilot()
