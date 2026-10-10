"""One fresh measured workflow process; evidence writing follows the stop time."""
import os,time
START=float(os.environ.get("KIRA_WORKFLOW_START",time.perf_counter()))
import argparse,json,pathlib
from s08_workflow import execute
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument("case");p.add_argument("size",type=int);p.add_argument("policy")
 p.add_argument("output",type=pathlib.Path);p.add_argument("reference",type=pathlib.Path)
 p.add_argument("--timeout",type=float,default=360);p.add_argument("--trace",action="store_true");a=p.parse_args()
 case=next(c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["id"]==a.case)
 r=execute(case,a.size,a.policy,a.output,a.reference,timeout=a.timeout,
   weights=ROOT/"ML_model_reduction/cost_training/trained_weights.txt",trace=a.trace,start=START)
 print(json.dumps({k:r[k] for k in ["case","size","policy","success","complete_seconds","fallback_attempts","completed_targets"]}),flush=True)
if __name__=="__main__":main()
