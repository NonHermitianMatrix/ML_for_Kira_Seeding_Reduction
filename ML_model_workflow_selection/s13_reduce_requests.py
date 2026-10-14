"""Reduce compatible target requests together and return their separate rows."""
import argparse,copy,json,time
from pathlib import Path
from s05_study import HERE,ROOT,BINARY,sha,workflow,save
from s08_reduce import select

def reduce_requests(requests,basis,use_model=True):
    begin=time.perf_counter()
    assert requests and all(r['targets'] for r in requests)
    definition=requests[0]['definition']
    assert all(r['definition']==definition for r in requests),'Requests must share one exact family definition.'
    indices=len(definition['propagators'])
    unique=list(dict.fromkeys(tuple(t) for r in requests for t in r['targets']))
    assert 1<=len(unique)<=128 and all(len(t)==indices for t in unique)
    joint=copy.deepcopy(requests[0]);joint['targets']=[list(t) for t in unique];joint['size']=len(unique)
    joint.setdefault('group',joint['id']);joint.setdefault('split','application')
    frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
    assert sha(BINARY)==frozen['binary_sha256']
    if use_model or frozen['best_fixed'] in ['seed','equation']:
        for p,digest in frozen['weights'].items():assert sha(ROOT/p)==digest
    if use_model:
        manifest=json.loads((HERE/'cases.json').read_text())
        config,reason=select(joint,frozen,manifest)
    else:config,reason=frozen['best_fixed'],'training_best_fixed'
    decision=time.perf_counter()-begin
    result=workflow(joint,None,config,basis=basis)
    if result['success']:
        coefficients=result['attempts'][-1]['coefficients']
        partition=[{'id':r['id'],'coefficients':{
            ','.join(map(str,t)):coefficients[','.join(map(str,t))] for t in r['targets']}} for r in requests]
    else:partition=[]
    result.update(complete_seconds=time.perf_counter()-begin,decision_seconds=decision,selection_reason=reason,
                  answers_withheld=True,request_count=len(requests),partition_coefficients=partition)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--requests',type=Path,required=True)
    parser.add_argument('--basis',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert args.output.resolve().is_relative_to((HERE/'model_test').resolve())
    result=reduce_requests(json.loads(args.requests.read_text()),json.loads(args.basis.read_text()))
    save(args.output,result)
    print(json.dumps({k:result[k] for k in ['success','configuration','request_count','complete_seconds']}))
    if not result['success']:raise SystemExit(1)

if __name__=='__main__':main()
