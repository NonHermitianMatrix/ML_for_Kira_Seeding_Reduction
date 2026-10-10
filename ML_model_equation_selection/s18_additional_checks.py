"""Check composition with existing models, basis-only use, and held-out labels."""
import json,os,pathlib,time
from s04_experiment import HERE,ROOT,setup,cases,reference,workflow,run,read,packed
from s09_predict import predict
def main():
 setup();os.environ["KIRA_RUNTIME_BINARY"]=".tools/kira-equation-selection/kira-lazy"
 model=json.loads((HERE/"trained_model/model.json").read_text());config=json.loads((HERE/"trained_model/deployment.json").read_text())
 chosen=[(c,n) for c,n in cases("testing") if n==21 or n==128]
 # These labels are collected only after model/threshold freeze; they never update weights.
 stats=dict(rows=0,positives=0,tp=0,fp=0,fn=0,tn=0,squared_error=0.0)
 hist=[[0,0] for _ in range(20)];profiles=[]
 for c,n in chosen:
  ref=reference(c,n);out=HERE/"model_test/labels"/f'{c["id"]}_n{n}.json.gz'
  os.environ.update(KIRA_EQ_MODE="collect",KIRA_EQ_COLLECT="1")
  r=run(c,n,"native",out,timeout=180,margin=0,reference=ref,records=False,check_masters=True,archive=False)
  if not r["success"]:r=run(c,n,"native",out,timeout=180,margin=1,reference=ref,records=False,check_masters=True,archive=False)
  packed(out,r);assert r["success"]
  local=dict(rows=0,positives=0,tp=0,fp=0,fn=0,tn=0,squared_error=0.0)
  for line in r["equation_records"].splitlines():
   v=line.split("\t");y=int(v[1]);p=predict(list(map(float,v[2:26])),model);label=p>=config["threshold"]
   local["rows"]+=1;local["positives"]+=y;local["squared_error"]+=(p-y)**2
   local["tp" if label and y else "fp" if label else "fn" if y else "tn"]+=1
   hist[min(19,int(p*20))][y]+=1
  for k,v in local.items():stats[k]+=v
  profiles.append(dict(case=c["id"],size=n,**local))
  print(json.dumps(dict(phase="held_out_labels",case=c["id"],rows=local["rows"])),flush=True)
 label_report=dict(totals=stats,profiles=profiles,histogram=hist,threshold=config["threshold"],label_definition=model["label"],no_test_fitting=True)
 (HERE/"model_test/label_metrics.json").write_text(json.dumps(label_report,indent=2)+"\n")
 # Compare using the row policy alone and both existing policies on four profiles.
 composition=[]
 for c,n in chosen[::2]:
  ref=reference(c,n)
  for base in ["row","both"]:
   for rep in range(3):
    for mode in (["off","auto"] if rep%2==0 else ["auto","off"]):
     out=HERE/"model_test/composition"/f'{c["id"]}_{base}_{mode}_r{rep}.json.gz'
     r=workflow(c,n,mode,0,out,ref,base=base);assert r["success"] and r["reference_checked"];composition.append({k:r[k] for k in ["case","group","topology","size","mode","base","complete_seconds","attempt_count"]})
 # Run actual third-policy applications without target reference coefficients.
 applications=[]
 for c,n in chosen:
  ref=reference(c,n);basis=read(ref)["masters"];out=HERE/"model_test/application"/f'{c["id"]}_n{n}.json.gz'
  r=workflow(c,n,"auto",0,out,None,basis=basis)
  assert r["success"] and not r["reference_checked"]
  # Cross-check after the production reducer returns.
  got=r["attempts"][-1]["coefficients"];want=read(ref)["coefficients"]
  import sympy as sp
  for target,row in got.items():
   for m in row.keys()|want[target].keys():
    assert sp.cancel(sp.sympify(row.get(m,"0").replace("^","**"),rational=True)-sp.sympify(want[target].get(m,"0").replace("^","**"),rational=True))==0
  applications.append(dict(case=c["id"],size=n,success=True,reference_supplied_to_reducer=False,independent_check_passed=True))
 (HERE/"model_test/composition.json").write_text(json.dumps(dict(all_passed=True,workflows=len(composition),results=composition),indent=2)+"\n")
 (HERE/"model_test/application_verification.json").write_text(json.dumps(dict(all_passed=True,checks=len(applications),results=applications),indent=2)+"\n")
 print(json.dumps(dict(composition_workflows=len(composition),basis_only_applications=len(applications),all_passed=True)),flush=True)
if __name__=="__main__":main()
