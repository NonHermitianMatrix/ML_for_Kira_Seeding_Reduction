"""Check that shared features preserve all learned probabilities and equation masks."""
import json,os,pathlib
from s04_experiment import HERE,ROOT,setup,cases,reference,run,packed
from s09_predict import predict
def main():
 setup();model=json.loads((HERE/"trained_model/model.json").read_text());total=0;checks=[]
 for c,n in [(c,n) for c,n in cases("validation") if n==21 or n==128]:
  ref=reference(c,n);pair=[]
  for version in os.environ.get("KIRA_EQ_PARITY_VERSIONS","kira,kira-fast").split(","):
   os.environ.update(KIRA_RUNTIME_BINARY=".tools/kira-equation-selection/"+version,KIRA_EQ_MODE="learned",KIRA_EQ_THRESHOLD=".001",KIRA_EQ_COLLECT="1",KIRA_EQ_WEIGHTS=str(HERE/"trained_model/weights.txt"))
   out=HERE/"integration"/f'parity_{os.environ.get("KIRA_EQ_PARITY_TAG","")}{c["id"]}_n{n}_{version}.json.gz'
   r=run(c,n,"native",out,timeout=180,margin=0,reference=ref,records=False,check_masters=True,archive=False)
   values={}
   for line in r["equation_records"].splitlines():
    v=line.split("\t");x=list(map(float,v[2:26]));p=float(v[26]);keep=int(v[27])
    assert predict(x,model)==p and int(p>=.001)==keep
    values[v[0]]=(x,p,keep)
   pair.append((r,values));packed(out,r)
  assert pair[0][1].keys()==pair[1][1].keys()
  diagnostic_differences=0
  for key in pair[0][1]:
   u,v=pair[0][1][key],pair[1][1][key]
   assert u[1:]==v[1:],(c["id"],key,"probability/mask")
   assert all(x==y for j,(x,y) in enumerate(zip(u[0],v[0])) if j!=16),(c["id"],key,"decision features")
   diagnostic_differences+=u[0][16]!=v[0][16]
  assert pair[0][0]["status"]==pair[1][0]["status"]
  assert pair[0][0].get("raw_export")==pair[1][0].get("raw_export")
  total+=len(pair[0][1]);checks.append(dict(case=c["id"],size=n,candidates=len(pair[0][1]),coefficient_spelling_differences=diagnostic_differences,status=pair[0][0]["status"]))
 result=dict(all_passed=True,candidate_probabilities_and_features=total,checks=checks)
 (HERE/"integration"/os.environ.get("KIRA_EQ_PARITY_REPORT","fast_verification.json")).write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result),flush=True)
if __name__=="__main__":main()
