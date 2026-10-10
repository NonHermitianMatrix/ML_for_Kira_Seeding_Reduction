"""Confirm a restricted deployment on six fresh physical sunrise profiles."""
import argparse,copy,hashlib,json,math,os,pathlib,statistics
import numpy as np
import sympy as sp
from s04_experiment import HERE,ROOT,setup,reference,workflow
from s02_records import read
from s10_summarize import aggregate,ratio
OUT=HERE/"model_test/confirmation"
def check_freeze():
 f=json.loads((HERE/"trained_model/confirmation_freeze.json").read_text())
 for n,d in f["sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==d,n
 return f
def prepare():
 assert not (HERE/"trained_model/confirmation_freeze.json").exists()
 original=json.loads((HERE/"families.json").read_text())["cases"]
 source=next(c for c in original if c["topology_group"]=="sunrise")
 cases=[]
 for i,(m,p2) in enumerate([([1,2,7],-17),([1,4,7],-19),([2,5,7],-23),([3,5,7],-29),([1,1,4],-31),([1,4,4],-37)]):
  c=copy.deepcopy(source);c.update(id=f"equation_confirmation_{i:02d}_sunrise",split="confirmation")
  pars=dict(masses=m,p2=p2);c["group"]="sunrise:"+json.dumps(pars,sort_keys=True)
  assert all(c["group"]!=z["group"] for z in original)
  for j,v in enumerate(m):c["definition"]["propagators"][j]["mass_squared"]=str(v)
  c["definition"]["parameters"]=pars;c["definition"]["scalarproduct_rules"]=[[["p","p"],str(p2)]]
  cases.append(c)
 manifest=dict(cases=cases,scope="Fresh six-profile confirmation after broad-test vacuum failures; symbolic d and rational kinematics.",repetitions=9,methods=[["off",0],["learned",.001],["distance",4]],workflows=162,composition_workflows=36,applications=6)
 (HERE/"families_confirmation.json").write_text(json.dumps(manifest,indent=2)+"\n")
 config=dict(runtime_binary=".tools/kira-equation-selection/kira-lazy",threshold=.001,by_topology={"sunrise":{"mode":"learned","threshold":.001}},unknown_mode="off",required_targets=source["targets"],scope="Recorded 21-target two-loop sunrise domain. Other topologies and target sets use native equation choices.",reason="The broad frozen test exposed incomplete filters and added fallback cost in new vacuum profiles. The restricted route is fixed before fresh confirmation; model weights stay unchanged.")
 (HERE/"trained_model/deployment_confirmed.json").write_text(json.dumps(config,indent=2)+"\n")
 paths=[HERE/"families_confirmation.json",HERE/"trained_model/deployment_confirmed.json",HERE/"trained_model/model.json",HERE/"trained_model/weights.txt",HERE/"s30_confirmation.py",HERE/"s31_reduce.py",HERE/"s03_run.py",HERE/"s04_experiment.py",HERE/"s02_records.py",ROOT/config["runtime_binary"]]
 frozen=dict(sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},**{k:manifest[k] for k in ["repetitions","methods","workflows","composition_workflows","applications"]})
 (HERE/"trained_model/confirmation_freeze.json").write_text(json.dumps(frozen,indent=2)+"\n")
 print(json.dumps(dict(frozen=True,profiles=6,workflows=162)),flush=True)
def exact_record(r,ref,cache):
 assert r["success"];assert r["complete_seconds"]>=sum(z["complete_seconds"] for z in r["attempts"])
 a=r["attempts"][-1];assert a["basis_admitted"] and a["complete"] and not a.get("unresolved_integrals")
 want=read(ref)["coefficients"];got=a["coefficients"];assert set(got)==set(want)
 pairs=0
 for target,row in got.items():
  for master in row.keys()|want[target].keys():
   key=(row.get(master,"0"),want[target].get(master,"0"));pairs+=1
   if key in cache:continue
   assert sp.cancel(sp.sympify(key[0].replace("^","**"),rational=True)-sp.sympify(key[1].replace("^","**"),rational=True))==0
   cache.add(key)
 return pairs
def confirm():
 frozen=check_freeze();setup();os.environ["KIRA_RUNTIME_BINARY"]=".tools/kira-equation-selection/kira-lazy"
 manifest=json.loads((HERE/"families_confirmation.json").read_text())
 for i,c in enumerate(manifest["cases"]):
  ref=reference(c,21);methods=manifest["methods"]
  for rep in range(9):
   ordered=methods[rep%3:]+methods[:rep%3]
   if (i+rep)%2:ordered=list(reversed(ordered))
   for mode,threshold in ordered:
    out=OUT/f'{c["id"]}_{mode}_r{rep}.json.gz'
    if out.exists():continue
    r=workflow(c,21,mode,threshold,out,ref)
    assert r["success"] and r["reference_checked"]
    print(json.dumps(dict(case=c["id"],rep=rep,mode=mode,seconds=r["complete_seconds"],attempts=r["attempt_count"])),flush=True)
 batches,rows=aggregate(OUT);assert len(rows)==162 and len(batches)==6 and all(m["repeats"]==9 for b in batches for m in b["methods"].values())
 keys=["learned:0.001","distance:4"]
 summary=dict(workflows=162,all_exact=True,failed_attempts=sum(not a["success"] for r in rows for a in r["attempts"]),batches=batches,comparisons={k:{field:ratio(batches,k,field) for field in ["complete_seconds","equation_preparation_seconds","generated_equations","selected_equations"]} for k in keys})
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 for c in manifest["cases"]:
  ref=reference(c,21)
  for rep in range(3):
   for mode in (["off","learned"] if rep%2==0 else ["learned","off"]):
    out=OUT/"composition"/f'{c["id"]}_{mode}_r{rep}.json.gz'
    if out.exists():continue
    r=workflow(c,21,mode,.001 if mode=="learned" else 0,out,ref,base="both");assert r["success"] and r["reference_checked"]
  out=OUT/"application"/f'{c["id"]}.json.gz'
  if not out.exists():
   r=workflow(c,21,"learned",.001,out,None,basis=read(ref)["masters"]);assert r["success"] and not r["reference_checked"]
 bs,cr=aggregate(OUT/"composition");assert len(cr)==36
 composition=dict(workflows=36,all_exact=all(r["success"] and r["reference_checked"] for r in cr),batches=bs,comparisons={f:ratio(bs,"learned:0.001",f) for f in ["complete_seconds","equation_preparation_seconds","generated_equations"]})
 (OUT/"composition_summary.json").write_text(json.dumps(composition,indent=2)+"\n")
 checked=set();pairs=0;count=0;attempts=0;failed=0
 for directory in [OUT,OUT/"composition",OUT/"application"]:
  for p in sorted(directory.glob("*.json.gz")):
   r=read(p);c=next(c for c in manifest["cases"] if c["id"]==r["case"]);ref=reference(c,21)
   pairs+=exact_record(r,ref,checked);count+=1;attempts+=len(r["attempts"]);failed+=sum(not a["success"] for a in r["attempts"])
   assert r["reference_checked"]==(directory.name!="application")
 check_freeze();assert count==204
 audit=dict(all_passed=True,workflows=count,main_workflows=162,composition_workflows=36,basis_only_applications=6,attempts=attempts,failed_attempts=failed,coefficient_pairs=pairs,distinct_coefficient_pairs=len(checked),frozen_files_unchanged=True)
 (OUT/"verification.json").write_text(json.dumps(audit,indent=2)+"\n")
 print(json.dumps(dict(audit=audit,comparisons=summary["comparisons"],composition=composition["comparisons"]),indent=2),flush=True)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("action",choices=["prepare","confirm"]);a=ap.parse_args();prepare() if a.action=="prepare" else confirm()
