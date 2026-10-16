"""Resolve a known structural definition before applying the frozen portfolio."""
import argparse,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction'))
import s24_parametric_runtime as app
class Reducer(app.Reducer):
    def __init__(self):
        super().__init__();start=time.perf_counter();self.registry={}
        for name,record in self.frozen['graphs'].items():
            for definition in record['definitions']:self.registry.setdefault(definition,[]).append(name)
        self.loading_seconds+=time.perf_counter()-start
    def resolve(self,case):
        matches=self.registry.get(app.policy.signature(case),[])
        if len(matches)==1:return dict(case,topology_group=matches[0]),matches[0]
        return case,None
    def reduce(self,case,basis,method='selected'):
        start=time.perf_counter();resolved,name=self.resolve(case)
        resolution=time.perf_counter()-start
        result=super().reduce(resolved,basis,method)
        result.update(supplied_family_name=case['topology_group'],resolved_family_name=name,family_resolution_seconds=resolution,complete_seconds=time.perf_counter()-start)
        return result
def main():
    import s01_study as study
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['case','basis','output']:parser.add_argument('--'+name)
    args=parser.parse_args()
    if args.case:
        assert args.basis and args.output and ROOT in Path(args.output).resolve().parents
        client=Reducer()
        try:r=client.reduce(json.loads(Path(args.case).read_text()),json.loads(Path(args.basis).read_text()))
        finally:client.close()
        app.rt.save(Path(args.output),r)
        print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],family=r['resolved_family_name'])),flush=True)
        return
    out=HERE/'family_names';out.mkdir(exist_ok=True)
    audit=json.loads((HERE/'family_name_audit.json').read_text())
    names=[r['case'] for r in audit if len(r['matching'])==1 and r['supplied']!=r['matching'][0]]
    cases=[c for c in json.loads((HERE/'protocol.json').read_text())['cases'] if c['id'] in names]
    protocol=dict(cases=cases,methods=['previous','selected','native'],repetitions=3,
        source_sha256=study.sha(Path(__file__)),model_sha256=study.sha(app.policy.OUT/'trained_model/freeze.json'),
        selection='Exact equality with one unique saved structural definition: ordered momentum forms, loop and external names, physical count, sectors, and zero/nonzero mass pattern. Numerical mass and kinematic values are not part of this existing model signature. No timing or coefficient information enters name resolution.',
        references='Reuse only the offline checked references from the initial grid. Every timed request starts a fresh Kira reduction; no answer reuse.',
        report='Use these paired application measurements for the two corrected family names. Preserve and identify the original unknown-name controls.')
    p=out/'protocol.json'
    if p.exists():assert json.loads(p.read_text())==protocol
    else:study.write(p,protocol)
    study.HERE=out
    client=Reducer()
    try:
        with study.bounded():
            for c in cases:
                ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
                assert app.rt.read(ref)['success'] and app.rt.read(check)['success']
                basis=app.rt.read(ref)['masters']
                for rep in range(3):
                    methods=protocol['methods'];shift=(sum(c['id'].encode())+rep)%3
                    for method in methods[shift:]+methods[:shift]:
                        p=out/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                        if p.exists():continue
                        start=time.perf_counter();r=client.reduce(c,basis,method);app.rt.verify(c,r,ref)
                        r.update(case=c['id'],method=method,repetition=rep,complete_seconds=time.perf_counter()-start)
                        study.save(p,app.rt.compact(r));study.emit(stage='family_name',case=c['id'],method=method,success=r['success'],seconds=r['complete_seconds'],resolved=r['resolved_family_name'])
                        assert r['success'] and r['reference_checked']
    finally:client.close()
    study.write(out/'completion.json',dict(complete=True,cases=len(cases),timings=len(cases)*9))
if __name__=='__main__':main()
