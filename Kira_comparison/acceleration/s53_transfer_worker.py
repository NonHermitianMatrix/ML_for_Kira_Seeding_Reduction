"""One bounded native trial; labels are read only after reduction."""
import argparse,json,os,pathlib,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import load_case,write,read,exact_check,sha
import s10_native_worker as native
from s02_worker import kira_run as stock_run
_original_load_case = load_case
def load_case(case,size):
 offset=read(HERE/"transfer_plan.json")["target_offset"]
 fam=_original_load_case(case,size+offset);fam["targets"]=fam["targets"][offset:]
 assert len(fam["targets"])==size
 return fam
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("partition");ap.add_argument("case",type=int);ap.add_argument("size",type=int)
 ap.add_argument("policy");ap.add_argument("scratch",type=pathlib.Path);ap.add_argument("output",type=pathlib.Path)
 a=ap.parse_args();plan=read(HERE/"transfer_plan.json");begin=time.perf_counter()
 fam=load_case(plan[a.partition][a.case],a.size)
 record=dict(family=fam["id"],group=fam["meta"]["group"],partition=a.partition,policy=a.policy,
  size=a.size,targets=[t["id"] for t in fam["targets"]],input_load_seconds=time.perf_counter()-begin)
 model={};selected=None
 seed_policy=read(HERE/"frozen_policy.json")["selected_seed_policy"] if a.policy=="combined" else a.policy
 if seed_policy.startswith("ml_"):
  t=time.perf_counter()
  from s01_fast_seed import FastSeed
  predictor=FastSeed();model["load_seconds"]=time.perf_counter()-t
  t=time.perf_counter();shared=predictor.shared(fam["definition"],fam["masters"],fam["seeds"]);selected=set();probabilities=[]
  predicted_targets=fam["targets"]
  if seed_policy.startswith("ml_components"):
   components=sorted({tuple(t["indices"]) for x in fam["targets"] for t in x["terms"]}-set(fam["masters"]))
   predicted_targets=[dict(id="F["+",".join(map(str,c))+"]",terms=[dict(indices=list(c),coefficient="1")]) for c in components]
  for target in predicted_targets:
   values=predictor.predict(target,shared)
   probabilities.append(dict(target=target["id"],probabilities=[float(x) for x in values]))
   selected.update(s for s,p in zip(fam["seeds"],values) if p>=(0.1 if seed_policy=="ml_low" else 0.01 if seed_policy in ("ml_lower","ml_components_lower") else 0.5))
  initial=set(selected)
  if seed_policy in ("ml_halo","ml_components_halo"):
   selected.update(b for b in fam["seeds"] if any(sum(abs(x-y) for x,y in zip(b,c))<=1 for c in initial))
  model["pre_expansion_seeds"]=len(initial)
  model.update(inference_seconds=time.perf_counter()-t,candidates=len(fam["seeds"]),selected=len(selected),
   selected_seeds=[list(x) for x in sorted(selected)],probabilities=probabilities)
 elif a.policy=="pool_filter":selected=set(fam["seeds"])
 if selected is not None:
  (a.scratch/"seeds.txt").write_text("".join("F["+",".join(map(str,s))+"]\n" for s in sorted(selected)))
 def filtered_run(w,p):
  oldrun=subprocess.run
  def run(argv,**kw):
   argv=list(argv);argv[0]=str(ROOT/".tools/kira-acceleration/kira")
   env=dict(kw["env"])
   if a.policy in ("ml_filter","pool_filter","ml_low","ml_lower","ml_halo","ml_components","ml_components_halo","ml_components_lower"):
    env.update(KIRA_ML_SEEDS=str(a.scratch/"seeds.txt"),KIRA_ML_SEED_AUDIT=str(w/"seed_audit.json"))
   kw["env"]=env
   return oldrun(argv,**kw)
  subprocess.run=run
  try:return stock_run(w,p)
  finally:subprocess.run=oldrun
 native.kira_run=filtered_run if a.policy in ("ml_filter","pool_filter","gate_disabled","ml_low","ml_lower","ml_halo","ml_components","ml_components_halo","ml_components_lower") else stock_run
 if a.policy in ("row_fast","row_native","row_source","row_cpp","row_cpp_audit","row_cpp_native","combined"):
  from s01_common import sample_point
  point,prime=sample_point(fam["definition"])
  context=dict(family={k:fam["definition"][k] for k in ("loop_momenta","external_momenta","propagators","invariants","scalarproduct_rules")},
   master_columns=[",".join(map(str,x)) for x in fam["masters"]],point=point,prime=prime)
  write(a.scratch/"context.json",context)
  if (a.policy.startswith("row_cpp") or a.policy=="combined"):
   import math
   from s01_fast_seed import text_features
   fv=list(text_features(json.dumps(context["family"],sort_keys=True,separators=(",",":")),32))
   fv += [math.log1p(len(context["family"][k])) for k in ("loop_momenta","propagators","external_momenta","invariants")]
   lines=[str(prime)+" "+str(len(fam["definition"]["propagators"])),str(len(point))]
   lines += [k+" "+str(v) for k,v in sorted(point.items())]
   lines += [str(len(fam["masters"]))]+[json.dumps(",".join(map(str,x))) for x in fam["masters"]]
   lines += [str(len(fv))]+[format(x,".17g") for x in fv]
   (a.scratch/"cpp_context.txt").write_text("\n".join(lines)+"\n")
  def row_run(w,p):
   oldrun=subprocess.run
   def run(argv,**kw):
    argv=list(argv);argv[0]=str(ROOT/(".tools/kira-cpp-row/kira" if (a.policy.startswith("row_cpp") or a.policy=="combined") else ".tools/kira-live-build/kira"))
    kw["env"]=dict(kw["env"],KIRA_LIVE_POLICY="native" if a.policy in ("row_native","row_cpp_native") else "learned",
     KIRA_ROW_SCOPE="compiled_source" if (a.policy.startswith("row_cpp") or a.policy=="combined") else "source" if a.policy=="row_source" else "full",
     KIRA_CPP_CONTEXT=str(a.scratch/"cpp_context.txt"),KIRA_CPP_TRACE=str(w/"cpp_choices.jsonl"),
     KIRA_LIVE_METRICS=str(w/"forward.jsonl"),KIRA_LIVE_TRACE=str(w/"row_trace.txt"),
     KIRA_LIVE_CONTEXT=str(a.scratch/"context.json"),
     KIRA_LIVE_PYTHON=str(ROOT/".tools/seed-model/venv/bin/python"),KIRA_LIVE_SERVER=str(HERE/"s11_row_server.py"))
    if a.policy=="combined":
     kw["env"].update(KIRA_ML_SEEDS=str(a.scratch/"seeds.txt"),KIRA_ML_SEED_AUDIT=str(w/"seed_audit.json"))
    if a.policy=="row_cpp_audit":kw["env"]["KIRA_CPP_FEATURE_AUDIT"]="1"
    return oldrun(argv,**kw)
   subprocess.run=run
   try:result=stock_run(w,p)
   finally:subprocess.run=oldrun
   result["forward"]=[json.loads(line) for line in (w/"forward.jsonl").read_text().splitlines()]
   return result
  native.kira_run=row_run
 attempts=[];rows={};t=time.perf_counter()
 try:
  rows,result=native.native_selected(fam,a.policy in ("trim","tight","gate_disabled","row_fast","row_native","row_source","row_cpp","row_cpp_audit","row_cpp_native"),a.scratch/"attempt0",
   dict(plan,timeout_seconds=plan["timeout_seconds"]-10),selected,margin=0 if a.policy=="tight" else 1)
  attempts.append(result)
  complete=all(x["id"] in rows and all(k in fam["masters"] or c==0 for k,c in rows[x["id"]].items()) for x in fam["targets"])
 except (ValueError,RuntimeError,subprocess.TimeoutExpired) as e:
  attempts.append(dict(error=str(e),seconds=time.perf_counter()-t));complete=False
 record["first_attempt_complete"]=complete
 record.update(attempts=attempts,model=model,success=False)
 write(a.output,record)
 if not complete and a.policy in ("trim","gate_disabled","row_native","row_cpp_native"):
  raise RuntimeError("Baseline attempt did not complete within its resource limit")
 if not complete:
  native.kira_run=stock_run
  remaining=plan["timeout_seconds"]-15-(time.perf_counter()-begin)
  if remaining<=10:raise RuntimeError("No time left for fallback")
  rows,result=native.native_selected(fam,True,a.scratch/"attempt1",dict(plan,timeout_seconds=remaining),None)
  attempts.append(result)
 record.update(attempts=attempts,model=model,fallback=len(attempts)>1,reduction_seconds=time.perf_counter()-t)
 record["seed_audits"]={p.parent.name:read(p) for p in a.scratch.glob("attempt*/seed_audit.json")}
 t=time.perf_counter();checks=exact_check(rows,fam)
 record.update(verification_seconds=time.perf_counter()-t,checks=checks,success=all(x["status"]=="exact_match" for x in checks))
 record["script_seconds"]=time.perf_counter()-begin
 write(a.output,record)
 print(json.dumps({k:record[k] for k in ["family","policy","fallback","success","script_seconds"]}),flush=True)
if __name__=="__main__":main()
