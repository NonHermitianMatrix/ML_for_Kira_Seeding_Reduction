"""Repeat independent checks with a larger, scheduler-reserved memory budget."""
import importlib.util,json,os,time
from pathlib import Path
import s00_cases as definitions
import s03_ablation as a
from s06_sector_test import read,save,emit
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def main():
    # Keep the earlier driver and failed attempts intact. Only limits change.
    source=(HERE/'s05_native_runner.py').read_text()
    assert source.count('2400*1024**2')==2 and source.count('2100*1024**2')==2
    source=source.replace('2400*1024**2','6144*1024**2').replace('2100*1024**2','5200*1024**2')
    driver=HERE/'s15_memory_runner.py'
    if driver.exists():assert driver.read_text()==source
    else:driver.write_text(source)
    spec=importlib.util.spec_from_file_location('memory_native',driver)
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    cases=[definitions.family(k,L,225) for L,k in [(4,'bubble_box'),(3,'ladder'),(4,'ladder')]]
    protocol=dict(cases=cases,methods=['native','equation'],repetitions=3,timeout_seconds=600,
        address_mib=6144,tree_rss_mib=5200,scheduler_slots=2,scheduler_h_data_per_slot='4G',
        source_sha256=a.sha(__file__),driver_sha256=a.sha(driver),
        frozen_models=json.loads((HERE/'ablation_protocol.json').read_text())['frozen_models'],
        purpose='Verification after memory-limited enlarged checks. No model refit or test-based strategy selection.',
        reference_rule='Reuse the previously completed native reference; repeat failed reference at larger memory if necessary.',
        timing_rule='Both timed methods use identical enlarged memory limits; three repetitions only after enlarged check passes.')
    p=HERE/'memory_protocol.json'
    if p.exists():assert json.loads(p.read_text())==protocol
    else:p.write_text(json.dumps(protocol,indent=2)+'\n')
    def attempt(c,basis=None,eq=False,bounds=None,ref=None):
        a.st.previous.study.setup('learned' if eq else 'off',a.st.previous.study.OLD if eq else None,.01)
        os.environ.update(KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-higher-scattering/kira'),KIRA_EPHEMERAL_DB='1',KIRA_RESTRICT_SECTOR_INIT='1')
        return native.run(c,c['size'],'native',HERE/'unused',timeout=600,margin=0,archive=False,records=False,
            basis=basis,reference=ref,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=bounds,ordering=1)
    for ci,c in enumerate(cases):
        n=c['definition']['physical_propagators'];bounds=[n+2,1,2]
        ref=HERE/'memory_references'/(c['id']+'.json.gz')
        if not ref.exists():
            old=HERE/'extended_references'/(c['id']+'.json.gz');r=read(old)
            if r['success']:r['reused_reference']=str(old.relative_to(ROOT))
            else:r=attempt(c,bounds=bounds)
            save(ref,a.st.compact(r));emit(stage='memory_reference',case=c['id'],status=r['status'],success=r['success'],seconds=r['complete_seconds'])
        r=read(ref)
        if not r['success']:continue
        assert any(row and row!={t:'1'} for t,row in r['coefficients'].items())
        basis=r['masters'];check=HERE/'memory_references'/(c['id']+'_check.json.gz')
        if not check.exists():
            rr=attempt(c,basis,bounds=[n+2,2,2],ref=ref)
            save(check,a.st.compact(rr));emit(stage='memory_check',case=c['id'],status=rr['status'],success=rr['success'],seconds=rr['complete_seconds'])
        if not read(check)['success']:continue
        failed=set()
        for rep in range(3):
            methods=['native','equation'] if (ci+rep)%2==0 else ['equation','native']
            for method in methods:
                if method in failed:continue
                out=HERE/'memory_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if out.exists():
                    if not read(out)['success']:failed.add(method)
                    continue
                begin=time.perf_counter();attempts=[]
                rr=attempt(c,basis,eq=method=='equation',bounds=bounds);attempts.append(a.st.compact(rr))
                if not rr['success'] and method=='equation':
                    rr=attempt(c,basis,bounds=bounds);attempts.append(a.st.compact(rr))
                result=dict(success=rr['success'],coefficients=rr.get('coefficients',{}),attempts=attempts,fallback_count=len(attempts)-1)
                a.bw.verify(c,result,basis,ref)
                result.update(case=c['id'],method=method,repetition=rep,complete_seconds=time.perf_counter()-begin)
                save(out,result);emit(stage='memory_test',case=c['id'],method=method,success=result['success'],seconds=result['complete_seconds'])
                if not result['success']:failed.add(method)
    emit(stage='memory_complete')
if __name__=='__main__':main()
