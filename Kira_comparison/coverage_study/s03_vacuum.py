"""Check all twelve existing loop orders using the restricted exact vacuum identities."""
import gzip,hashlib,json,random,sys,time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_equation_selection/higher_loops'))
import s02_reduce as old
sys.path.insert(0,str(ROOT/'Kira_comparison/cumulative_speedup'))
from s00_cumulative import backend,engine,EXACT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    policy=json.loads((old.HERE/'trained_model/deployment.json').read_text())
    final=json.loads((EXACT/'reader_final_deployment.json').read_text())
    assert policy['deployed_mode']=='extreme'
    cases=[]
    for r in [2,3,4]:
        rng=random.Random(53401+r)
        targets=[list(t) for t in old.compositions(6,r) if sum(v>0 for v in t)>=2]
        rng.shuffle(targets)
        cases.append(dict(id=f'coverage_vacuum_r{r}',family='coupled_vacuum_unit_massless',mass_scale_squared=1,mass_ratios=[823,829,853,857][:r],targets=targets[:6],loops=list(range(1,13))))
    modes=['original','dense','extreme','learned','recurrence']
    protocol=dict(cases=cases,modes=modes,repetitions=3,model=policy['model'],frozen_deployment=policy,
        source_sha256=sha(Path(__file__)),model_sha256=sha(old.HERE/'trained_model'/policy['model']),
        previous_source_sha256=sha(old.HERE/'s02_reduce.py'),
        scope='Unit massless powers and distinct massive denominators with a common total loop momentum. Exact Euler and partial-fraction identities supplied to Kira; not native high-loop IBP generation.',
        time='Complete input checking, model load, equation generation from supplied identities, Kira, export reading, exact substitution and coefficient verification. One loop per request, plus separate shared requests for all twelve orders.',
        exact_deployment=final,exact_model_sha256=sha(EXACT/'trained_model/cost_tree.json'),
        original_binary_sha256=sha(ROOT/'.tools/kira/bin/kira'),unchanged=True)
    path=HERE/'vacuum_protocol.json'
    if path.exists():assert json.loads(path.read_text())==protocol
    else:write(path,protocol)
    for c in cases:
        for loops in [[L] for L in range(1,13)]+[list(range(1,13))]:
            label=str(loops[0]) if len(loops)==1 else 'shared'
            request=dict(c,loops=loops)
            for rep in range(3):
                shift=(len(c['mass_ratios'])+rep)%len(modes)
                for mode in modes[shift:]+modes[:shift]:
                    p=HERE/'vacuum_test'/f'{c["id"]}_{label}_{mode}_{rep}.json.gz'
                    if p.exists():continue
                    start=time.perf_counter()
                    try:
                        if mode=='recurrence':
                            r=engine.apply([request],final['mode'],{},final['policy'])
                            if '_binary' in r:r.update(backend.decode_binary(r.pop('_binary')))
                            checks=0
                            for L,rows in r['coefficients'][c['id']].items():
                                for b,row in zip(request['targets'],rows):
                                    got={int(j):tuple(Fraction(a,b) for a,b in poly) for j,poly in row.items()}
                                    want={j:old.canonical(poly) for j,poly in old.oracle(int(L),c['mass_ratios'],tuple(b)).items()}
                                    assert all(old.canonical(got.get(j,()))==old.canonical(want.get(j,())) for j in set(got)|set(want))
                                    checks+=len(set(got)|set(want))
                            r['coefficient_checks']=checks
                        elif mode=='original':
                            saved=old.BINARY;old.BINARY=ROOT/'.tools/kira/bin/kira'
                            try:r=old.apply(request,'dense',policy['model'],shared=False)
                            finally:old.BINARY=saved
                        else:r=old.apply(request,mode,policy['model'],shared=True)
                    except (RuntimeError,AssertionError,ValueError) as e:
                        r=dict(case=c['id'],success=False,error=str(e),loops=loops)
                    r.update(mode=mode,repetition=rep,request=request,complete_seconds=time.perf_counter()-start)
                    raw=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
                    assert len(raw)<1024**2
                    used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())
                    assert used+len(raw)<16*1024**2
                    p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
                    print(json.dumps(dict(case=c['id'],loops=label,mode=mode,success=r['success'],seconds=r['complete_seconds'])),flush=True)
    write(HERE/'vacuum_completion.json',dict(complete=True,loop_orders=list(range(1,13)),requests=len(cases)*13*3*len(modes)))
if __name__=='__main__':main()
