"""Compile unchanged trained trees and compare all scores exactly."""
import argparse,ctypes,gzip,struct,subprocess
from s00_common import *
def load_native(name):
 library=ctypes.CDLL(str(HERE/"trained_model"/name.replace(".json",".so")))
 f=library.predict;f.argtypes=[ctypes.POINTER(ctypes.c_double),ctypes.c_int,ctypes.POINTER(ctypes.c_double)];f.restype=ctypes.c_int
 return dict(library=library,function=f)
def select_native(targets,mode,model=None):
 if mode!="model":return select(targets,mode,model)
 r=len(targets[0]);choices=options(r)
 if r==2:return choices[0],[]
 base=feature(targets,tuple(range(r)));pairlist=list(itertools.combinations(range(4),2));xs=[]
 for p in choices:
  x=base[:4]
  for j in list(p)+list(range(r,4)):x.extend(base[4+4*j:8+4*j])
  for i,j in pairlist:
   if j>=r:x.extend([0,0]);continue
   k=pairlist.index(tuple(sorted((p[i],p[j]))));x.extend(base[20+2*k:22+2*k])
  xs.extend(x)
 arr=(ctypes.c_double*len(xs))(*xs);out=(ctypes.c_double*len(choices))()
 assert model["function"](arr,len(choices),out)==0
 scores=list(out)
 return choices[min(range(len(scores)),key=lambda i:(scores[i],choices[i]))],scores
def compile_models():
 metadata={}
 for name in ["forest4.json","forest16.json"]:
  model=json.loads((HERE/"trained_model"/name).read_text());flat=[];offsets=[0]
  for tree in model["trees"]:flat+=tree;offsets.append(len(flat))
  source="#include <stddef.h>\ntypedef struct {int f;double t;int l,r;double v;} Node;\n"
  source+="static const Node nodes[]={\n"+",\n".join("{%d,%s,%d,%d,%s}"%(n[0],float(n[1]).hex(),n[2],n[3],float(n[4]).hex()) for n in flat)+"};\n"
  source+="static const int offsets[]={"+",".join(map(str,offsets))+"};\n"
  source+="int predict(const double*x,int n,double*out){if(n<1||n>24)return 1;for(int k=0;k<n;k++){double s=0;for(int t=0;t<"+str(len(model["trees"]))+";t++){int i=0;for(int depth=0;depth<16;depth++){const Node*a=&nodes[offsets[t]+i];if(a->f<0){s+=a->v;break;}i=x[k*32+a->f]<=a->t?a->l:a->r;}}out[k]=s/"+str(len(model["trees"]))+".0;}return 0;}\n"
  src=HERE/"trained_model"/name.replace(".json",".c");lib=src.with_suffix(".so");src.write_text(source)
  command=["gcc","-O2","-std=c99","-shared","-fPIC",str(src),"-o",str(lib)]
  subprocess.run(command,check=True,timeout=60)
  metadata[name]=dict(source_sha256=sha(src),library_sha256=sha(lib),compiler=subprocess.check_output(["gcc","--version"],text=True).splitlines()[0],command=command)
 with gzip.open(HERE/"training/examples.json.gz","rt") as f:records=json.load(f)
 checks=0;timings={}
 for name in ["forest4.json","forest16.json"]:
  native=load_native(name);python_model=load_model(name);ta=tb=0
  for rec in records:
   target=rec["request"]["targets"]
   a=time.perf_counter();p,s=select(target,"model",python_model);ta+=time.perf_counter()-a
   b=time.perf_counter();pn,sn=select_native(target,"model",native);tb+=time.perf_counter()-b
   assert pn==p and sn==s;checks+=len(s)
  timings[name]=dict(python_seconds=ta,native_seconds=tb,ratio=tb/ta)
 write(HERE/"training/native_check.json",dict(all_passed=True,score_checks=checks,timings=timings,build=metadata))
 print(json.dumps(dict(score_checks=checks,timings=timings),indent=2),flush=True)
if __name__=="__main__":compile_models()
