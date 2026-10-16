"""Extend the wall-time allowance while preserving the earlier failed probes."""
import copy,importlib.util,json,os,time
from pathlib import Path
import s00_cases as definitions
import s03_ablation as a
from s06_sector_test import save,read,emit
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('extended_native',HERE/'s05_native_runner.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
METHODS=['native','equation','separate_requests']

def main():
    cases=[definitions.family(k,L,225) for L,k in [(4,'bubble_box'),(3,'ladder'),(4,'ladder')]]
    p=HERE/'extended_protocol.json'
    protocol=dict(cases=cases,methods=METHODS,repetitions=3,timeout_seconds=600,
        source_sha256=a.sha(__file__),binary_sha256=a.sha(ROOT/'.tools/kira-higher-scattering/kira'),
        frozen_models=json.loads((HERE/'ablation_protocol.json').read_text())['frozen_models'],
        purpose='Fresh profiles with a longer limit after bounded feasibility tests. Fixed models and sector-restricted initialization.',
        row_probe='One extra diagnostic trial; not a repeated timing estimate.')
    if p.exists():assert json.loads(p.read_text())==protocol
    else:p.write_text(json.dumps(protocol,indent=2)+'\n')
    def attempt(c,basis=None,equation=False,row=False,bounds=None,ref=None):
        a.st.previous.study.setup('learned' if equation else 'off',a.st.previous.study.OLD if equation else None,.01)
        os.environ.update(KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-higher-scattering/kira'),KIRA_EPHEMERAL_DB='1',KIRA_RESTRICT_SECTOR_INIT='1')
        return native.run(c,c['size'],'learned' if row else 'native',HERE/'unused',timeout=600,margin=0,
              weights=ROOT/'ML_model_reduction/cost_training/trained_weights.txt' if row else None,
              archive=False,records=False,basis=basis,reference=ref,check_masters=basis is not None,
              scratch_cap=32*1024**2,bounds=bounds,ordering=1)
    for ci,c in enumerate(cases):
        n=c['definition']['physical_propagators'];bounds=[n+2,1,2]
        ref=HERE/'extended_references'/(c['id']+'.json.gz')
        if not ref.exists():
            r=attempt(c,bounds=bounds);save(ref,a.st.compact(r));emit(stage='extended_reference',case=c['id'],success=r['success'],status=r['status'],seconds=r['complete_seconds'])
        r=read(ref)
        if not r['success'] or not any(row and row!={t:'1'} for t,row in r.get('coefficients',{}).items()):continue
        basis=r['masters'];check=HERE/'extended_references'/(c['id']+'_check.json.gz')
        if not check.exists():
            rr=attempt(c,basis,bounds=[n+2,2,2],ref=ref);save(check,a.st.compact(rr));emit(stage='extended_check',case=c['id'],success=rr['success'],status=rr['status'],seconds=rr['complete_seconds'])
        if not read(check)['success']:continue
        for rep in range(3):
            shift=(ci+rep)%len(METHODS)
            for method in METHODS[shift:]+METHODS[:shift]:
                out=HERE/'extended_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if out.exists():continue
                begin=time.perf_counter();attempts=[];rows={};success=True
                inputs=[c]
                if method=='separate_requests':
                    inputs=[]
                    for indices in [[0,1],[2]]:
                        cc=copy.deepcopy(c);cc['targets']=[c['targets'][i] for i in indices];cc['size']=len(indices);inputs.append(cc)
                for cc in inputs:
                    rr=attempt(cc,basis,equation=method=='equation',bounds=bounds)
                    attempts.append(a.st.compact(rr))
                    if not rr['success'] and method=='equation':
                        rr=attempt(cc,basis,bounds=bounds);attempts.append(a.st.compact(rr))
                    success=success and rr['success'];rows.update(rr.get('coefficients',{}))
                result=dict(success=success,coefficients=rows,attempts=attempts,fallback_count=len(attempts)-len(inputs))
                a.bw.verify(c,result,basis,ref)
                result.update(case=c['id'],method=method,repetition=rep,complete_seconds=time.perf_counter()-begin)
                save(out,result);emit(stage='extended_test',case=c['id'],method=method,success=result['success'],seconds=result['complete_seconds'])
        out=HERE/'extended_test'/f'{c["id"]}_row_probe.json.gz'
        if not out.exists():
            rr=attempt(c,basis,row=True,bounds=bounds,ref=ref);save(out,a.st.compact(rr));emit(stage='row_probe',case=c['id'],success=rr['success'],status=rr['status'],seconds=rr['complete_seconds'])
    emit(stage='extended_complete')
if __name__=='__main__':main()
