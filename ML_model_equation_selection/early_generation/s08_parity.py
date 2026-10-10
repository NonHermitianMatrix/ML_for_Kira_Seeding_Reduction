"""Check the compiled early gate against saved Python probabilities on training candidates."""
import hashlib,json,os,pathlib,subprocess,tempfile,time,shutil
import numpy as np
from s04_workflows import HERE,ROOT,read,guard
def main():
 start=time.perf_counter();tool=ROOT/".tools/kira-early-generation";src=tool/"parity.cpp";exe=tool/"parity"
 src.write_text('#include <cstdint>\n#include <iostream>\n#include <string>\n#include <utility>\n#include <vector>\nnamespace pyred {using pow_type=int; using eqdata=std::vector<std::pair<int,std::string>>;}\n#include "'+str(HERE/"integration/s00_early_policy.h")+'"\nint main(){auto &s=kira_eq::state();size_t op;while(std::cin>>op){std::vector<int>a(s.targets.front().size());for(auto &v:a)std::cin>>v;std::cout<<kira_eq::precheck(a,op)<<"\\n";}}\n')
 subprocess.run(["g++","-O3","-std=c++17",str(src),"-o",str(exe)],check=True)
 known={}
 for f in [HERE.parent/"families.json",HERE/"additional_families.json"]:
  for c in json.loads(f.read_text())["cases"]:known[c["id"]]=c
 records=[];total=0
 scratch=pathlib.Path(tempfile.mkdtemp(prefix="early_parity_",dir=os.environ["TMPDIR"]))
 try:
  for f in sorted(list((HERE.parent/"training").glob("*.json.gz"))+list((HERE/"training").glob("*.json.gz"))):
   if "_failed" in f.name:continue
   r=read(f);c=known[r["case"]];lines=[l.split("\t") for l in r["equation_records"].splitlines()]
   a=np.array([[float(v) for v in l[2:26]] for l in lines])
   seeds=[]
   for l in lines:
    seed,op=l[0].split(":");seeds.append(op+" "+" ".join(v for v in seed.split(",") if v))
   payload="\n".join(seeds)+"\n"
   context=scratch/"context.txt"
   context.write_text(f'{len(c["definition"]["loop_momenta"])} {len(c["definition"]["external_momenta"])} {r["size"]} {len(r["targets"][0])}\n'+"\n".join(" ".join(map(str,t)) for t in r["targets"])+"\n")
   for name in ["early_d8","early_d12"]:
    model=json.loads((HERE/"trained_model"/name/"model.json").read_text());nodes=model["nodes"];ps=[]
    for row in a:
     i=0
     while nodes[i]["feature"]>=0:
      z=nodes[i];i=z["left"] if row[z["feature"]]<=z["threshold"] else z["right"]
     ps.append(nodes[i]["probability"])
    ps=np.array(ps)
    for threshold in [.001,.003,.01]:
     env=dict(os.environ,KIRA_EQ_MODE="learned",KIRA_EQ_CONTEXT=str(context),KIRA_EQ_WEIGHTS=str(HERE/"trained_model"/name/"weights.txt"),KIRA_EQ_THRESHOLD=str(threshold))
     env.pop("KIRA_EQ_METRICS",None)
     raw=subprocess.check_output([str(exe)],input=payload,text=True,env=env)
     got=np.fromstring(raw,sep=" ",dtype=int);want=(ps>=threshold).astype(int)
     assert got.shape==want.shape,(f,name,got.shape,want.shape)
     assert np.array_equal(got,want),(f,name,threshold,int((got!=want).sum()))
     total+=len(got);records.append(dict(file=str(f.relative_to(ROOT)),model=name,threshold=threshold,candidates=len(got),kept=int(got.sum())))
 finally:shutil.rmtree(scratch)
 result=dict(all_passed=True,decisions_checked=total,checks=len(records),seconds=time.perf_counter()-start,scope="The shared C++ gate computes features from original seed/operator indices and target context. Python uses the saved training feature rows. This independently checks feature construction and threshold decisions.",records=records)
 (HERE/"validation/prediction_parity.json").write_text(json.dumps(result,indent=2)+"\n");guard();print(json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":main()
