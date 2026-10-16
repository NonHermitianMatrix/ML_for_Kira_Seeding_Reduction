"""Use the validated portfolio with a target batch and a prescribed master basis."""
import argparse, copy, json, time
from pathlib import Path
import s15_portfolio_study as policy
from s08_reduce import load_json

class Reducer:
    def __init__(self):
        start=time.perf_counter()
        self.frozen=load_json(policy.OUT/'trained_model/freeze.json')
        self.protocol=load_json(policy.OUT/'protocol.json')
        assert policy.study.sha(policy.OUT/'protocol.json')==self.frozen['protocol_sha256']
        assert policy.study.sha(policy.ROOT/'.tools/kira-adaptive/kira')==self.protocol['binary_sha256']
        for name,digest in self.protocol['source_hashes'].items():assert policy.study.sha(policy.HERE/name)==digest
        self.portfolio=policy.runtime.Portfolio()
        self.loading_seconds=time.perf_counter()-start

    def close(self):self.portfolio.close()

    def reduce(self,case,basis):
        start=time.perf_counter();d=case['definition'];n=len(d['propagators'])
        assert 0<n<=31 and isinstance(basis,list)
        assert not d.get('cut_propagators'),'This application does not support cut propagators'
        assert case['size']==len(case['targets']) and case['size']>0
        tops=d['top_level_sectors']
        assert tops and all(isinstance(s,int) and 0<s<2**n for s in tops)
        for row in case['targets']+basis:
            assert len(row)==n and all(type(v) is int for v in row)
            sector=sum(1<<i for i,v in enumerate(row) if v>0)
            assert any((sector&top)==sector for top in tops),'Integral outside the declared sector domain'
        r=policy.reduce(self.portfolio,case,basis,self.frozen)
        r.update(application_seconds=time.perf_counter()-start,model_loading_seconds=self.loading_seconds,
            basis_note='All targets reach the prescribed basis. This check does not establish that this basis is minimal.')
        return r

def self_test():
    case=next(c for c in json.loads((policy.OUT/'protocol.json').read_text())['cases'] if c['id']=='sunrise_p306_dots')
    ref=policy.OUT/'references'/(case['id']+'.json.gz');basis=policy.rt.read(ref)['masters']
    reducer=Reducer()
    try:
        for name,example in [('public',case),('unknown_graph',dict(case,topology_group='unseen'))]:
            result=reducer.reduce(example,basis);policy.rt.verify(case,result,ref)
            assert result['success'] and result['reference_checked'] and not result['reference_coefficients_supplied']
            if name=='unknown_graph':assert result['action']=='native' and result['selection_reason']=='unknown_graph'
            policy.rt.save(policy.OUT/'application_test'/(name+'.json.gz'),result)
        invalid=copy.deepcopy(case);invalid['targets'][0][0]=1.5
        rejected=False
        try:reducer.reduce(invalid,basis)
        except AssertionError:rejected=True
        assert rejected
        cut=copy.deepcopy(case);cut['definition']['cut_propagators']=[1]
        rejected=False
        try:reducer.reduce(cut,basis)
        except AssertionError:rejected=True
        assert rejected
        zero=copy.deepcopy(case)
        zero.update(id='scaleless_empty_target',targets=[[0]*len(case['definition']['propagators'])],size=1)
        result=reducer.reduce(zero,[])
        assert result['success']
        assert set(result['coefficients'])=={','.join('0' for _ in zero['targets'][0])}
        import sympy as sp
        assert all(sp.cancel(sp.sympify(v.replace('^','**'),rational=True))==0
            for row in result['coefficients'].values() for v in row.values())
        result.update(analytic_check='All indices zero: a scaleless integral vanishes in dimensional regularization.',
            analytic_zero_checked=True)
        policy.rt.save(policy.OUT/'application_test/scaleless_empty_basis.json.gz',result)
        policy.study.write(policy.OUT/'application_test/validation.json',dict(complete=True,all_exact=True,
            integer_validation=True,cut_validation=True,unknown_graph_guard=True,scaleless_empty_basis=True,source_sha256=policy.study.sha(__file__)))
    finally:reducer.close()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--self-test',action='store_true')
    for name in ['case','basis','output']:parser.add_argument('--'+name)
    args=parser.parse_args()
    if args.self_test:self_test();return
    if not all([args.case,args.basis,args.output]):parser.error('--case, --basis and --output are required')
    reducer=Reducer()
    try:r=reducer.reduce(json.loads(Path(args.case).read_text()),json.loads(Path(args.basis).read_text()))
    finally:reducer.close()
    policy.rt.save(Path(args.output),r)
    print(json.dumps({k:r[k] for k in ['success','action','fallback_count','application_seconds','model_loading_seconds']}))
    if not r['success']:raise SystemExit(2)

if __name__=='__main__':main()
