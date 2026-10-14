"""Apply the best fixed training strategy to compatible requests; keep ML optional."""
import argparse,json
from pathlib import Path
from s05_study import HERE,save
from s13_reduce_requests import reduce_requests

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--requests',type=Path,required=True)
    parser.add_argument('--basis',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--learned',action='store_true',help='Use the frozen learned choice instead of the best fixed training strategy.')
    args=parser.parse_args()
    assert args.output.resolve().is_relative_to((HERE/'model_test').resolve())
    result=reduce_requests(json.loads(args.requests.read_text()),json.loads(args.basis.read_text()),use_model=args.learned)
    result['application_policy']='learned' if args.learned else 'best_fixed_training'
    save(args.output,result)
    print(json.dumps({k:result[k] for k in ['success','configuration','application_policy','request_count','complete_seconds']}))
    if not result['success']:raise SystemExit(1)

if __name__=='__main__':main()
