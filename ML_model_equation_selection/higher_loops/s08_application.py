"""Apply the frozen higher-loop deployment to a new supported family request."""
import argparse,time
from s02_reduce import apply,compact_save
from s00_math import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
 ap.add_argument("--policy",choices=["deployed","learned","dense"],default="deployed");args=ap.parse_args()
 start=time.perf_counter();request=json.loads(args.input.read_text());policy=json.loads((HERE/"trained_model/deployment.json").read_text())
 mode=policy["deployed_mode"] if args.policy=="deployed" else args.policy
 assert ROOT in args.output.resolve().parents
 result=apply(request,mode,policy["model"],shared=True);result["application_policy"]=args.policy
 result["complete_seconds"]=time.perf_counter()-start;compact_save(args.output,result)
 print(json.dumps({k:result[k] for k in ["case","mode","success","loops","complete_seconds","coefficient_checks"]}))
if __name__=="__main__":main()
