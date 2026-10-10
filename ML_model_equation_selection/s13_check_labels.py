"""Repeat a native collection to check labels and features before fitting."""
import hashlib,json,os
from s04_experiment import HERE,setup,cases,reference,run,read,packed
def main():
 setup();c,n=cases("training")[0];p=HERE/"training"/f'{c["id"]}_n{n}.json.gz';first=read(p)
 os.environ.update(KIRA_EQ_MODE="collect",KIRA_EQ_COLLECT="1")
 out=HERE/"integration/label_repeat.json.gz"
 second=run(c,n,"native",out,timeout=180,margin=first["margin"],reference=reference(c,n),records=False,check_masters=True,archive=False)
 def rows(r):return {x.split("\t")[0]:x.split("\t")[1:26] for x in r["equation_records"].splitlines()}
 a,b=rows(first),rows(second);assert first["success"] and second["success"] and a==b,"Unstable equation labels or features"
 packed(out,second)
 result=dict(all_passed=True,candidates=len(a),positives=sum(int(v[0]) for v in a.values()),features_and_labels_identical=True,header_sha256=hashlib.sha256((HERE/"integration/s00_equation_policy.h").read_bytes()).hexdigest())
 assert result["positives"]>0
 (HERE/"integration/label_verification.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
