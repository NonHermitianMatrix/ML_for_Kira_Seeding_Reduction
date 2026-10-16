"""Apply the frozen learned portfolio with exact sector polynomial projection."""
import contextlib, json, os, time
from pathlib import Path
import s17_reduce as previous
import s23_parametric_runner as native
policy=previous.policy; rt=policy.rt; HERE=policy.HERE; ROOT=policy.ROOT
OUT=HERE/'parametric_preparation'

@contextlib.contextmanager
def projected(enabled=True,replay=True):
    original=rt.native.run
    saved=os.environ.get('KIRA_PROJECT_PARAMETRIC')
    saved_replay=os.environ.get('KIRA_REUSE_SELECTED_EQUATIONS')
    def run(*args,**kwargs):
        os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-parametric/kira')
        if enabled:os.environ['KIRA_PROJECT_PARAMETRIC']='1'
        else:os.environ.pop('KIRA_PROJECT_PARAMETRIC',None)
        if replay:os.environ['KIRA_REUSE_SELECTED_EQUATIONS']='1'
        else:os.environ.pop('KIRA_REUSE_SELECTED_EQUATIONS',None)
        return native.run(*args,**kwargs)
    rt.native.run=run
    try:yield
    finally:
        rt.native.run=original
        if saved is None:os.environ.pop('KIRA_PROJECT_PARAMETRIC',None)
        else:os.environ['KIRA_PROJECT_PARAMETRIC']=saved
        if saved_replay is None:os.environ.pop('KIRA_REUSE_SELECTED_EQUATIONS',None)
        else:os.environ['KIRA_REUSE_SELECTED_EQUATIONS']=saved_replay

class Reducer:
    def __init__(self):
        start=time.perf_counter()
        build=json.loads((OUT/'integration/build.json').read_text())
        assert policy.study.sha(ROOT/'.tools/kira-parametric/kira')==build['binary_sha256']
        if (OUT/'protocol.json').exists():
            protocol=json.loads((OUT/'protocol.json').read_text())
            for name,digest in protocol['sources'].items():assert policy.study.sha(HERE/name)==digest
        self.previous=previous.Reducer()
        self.frozen=self.previous.frozen
        self.loading_seconds=time.perf_counter()-start
    def close(self):self.previous.close()
    def reduce(self,case,basis,method='selected'):
        start=time.perf_counter();cpu0=policy.runtime.cpu()
        if method=='previous':return self.previous.reduce(case,basis)
        # Reuse the same validation, without invoking a reduction.
        d=case['definition'];n=len(d['propagators']);tops=d['top_level_sectors']
        assert 0<n<=31 and isinstance(basis,list) and case['size']==len(case['targets'])>0
        assert not d.get('cut_propagators') and not d.get('symbolic_ibp')
        assert tops and all(type(s) is int and 0<s<2**n for s in tops)
        for t in case['targets']+basis:
            assert len(t)==n and all(type(v) is int for v in t)
            sector=sum(1<<i for i,v in enumerate(t) if v>0)
            assert any(sector&top==sector for top in tops)
        selected,reason=policy.select(self.frozen,case)
        if method=='native':selected,reason='native','native_control'
        if method=='fixed':
            graph=self.frozen['graphs'].get(case['topology_group'])
            selected=graph['fixed'] if graph and policy.signature(case) in graph['definitions'] else 'native'
            reason='fixed_control'
        decision=time.perf_counter()-start
        server_cpu=0.
        if selected=='published' and case['topology_group'] in policy.study.KINDS:
            # Preserve this uncommon separate service unchanged. Its costs count.
            before=policy.runtime.cpu()
            r=self.previous.portfolio.run(case,basis,selected)
            server_cpu=max(0.,r.get('cpu_seconds',0.)-(policy.runtime.cpu()-before))
            enabled=False
        else:
            seed='native' if selected in ['native','published'] else 'rank_plus' if selected.startswith('rank') else policy.runtime.graph.select(self.previous.portfolio.frozen,self.previous.portfolio.guard,case)
            with projected():
                r=self.previous.portfolio.direct(case,basis,seed,2 if selected.endswith('2') else 1)
            enabled=True
        r.update(action=selected,selection_reason=reason,decision_seconds=decision,
            complete_seconds=time.perf_counter()-start,cpu_seconds=policy.runtime.cpu()-cpu0+server_cpu,
            early_projection=enabled,reference_coefficients_supplied=False)
        r['model_loading_seconds']=self.loading_seconds
        return r

def pilot():
    cases=json.loads((HERE/'cases.json').read_text())['cases'];p=Reducer()
    try:
        for name in ['bubble_box4_p301','bubble_box3_p301','double_box_p301_mixed','nonplanar_box_symbolic_0']:
            matches=[c for c in cases if c['id']==name]
            if not matches:
                matches=[c for c in cases if c['topology_group']=='nonplanar_box' and c['split']=='training' and c['definition']['invariants']]
            assert len(matches)==1,name
            c=matches[0];ref=HERE/'references'/(c['id']+'.json.gz');basis=rt.read(ref)['masters']
            for method in ['previous','selected']:
                path=OUT/'development'/f'{c["id"]}_{method}.json.gz'
                if path.exists():continue
                r=p.reduce(c,basis,method);rt.verify(c,r,ref);rt.save(path,r)
                print(json.dumps(dict(case=c['id'],method=method,seconds=r['complete_seconds'],success=r['success'],stages=[x for a in r['attempts'] for x in a.get('stage_metrics',[]) if x['stage']=='parametric_construction'])),flush=True)
                assert r['success'] and r['reference_checked']
    finally:p.close()
def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case');parser.add_argument('--basis');parser.add_argument('--output')
    args=parser.parse_args()
    if args.case:
        assert args.basis and args.output
        c=json.loads(Path(args.case).read_text());basis=json.loads(Path(args.basis).read_text())
        client=Reducer()
        try:r=client.reduce(c,basis)
        finally:client.close()
        rt.save(Path(args.output),r)
        print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],action=r['action'])))
    else:pilot()
if __name__=='__main__':main()
