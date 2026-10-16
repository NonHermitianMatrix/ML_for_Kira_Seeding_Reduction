"""Check sector-domain initialization and frozen-policy transfer at higher loops."""
import copy,gzip,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import s00_cases as definitions

def read(p):return json.load(gzip.open(p,'rt'))
def save(p,r):
    p.parent.mkdir(exist_ok=True)
    data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
    used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
    assert used+len(data)+4096<16*1024**2
    p.write_bytes(data)
def emit(**r):print(json.dumps(r),flush=True)

def main():
    if not (HERE/'build.json').exists():subprocess.run([sys.executable,str(HERE/'s04_build_sector_test.py')],check=True)
    import s03_ablation as a
    spec=importlib.util.spec_from_file_location('sector_native',HERE/'s05_native_runner.py')
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    binary=ROOT/'.tools/kira-higher-scattering/kira'
    cases=[definitions.family(k,L,h) for h in [223,224] for L in [3,4] for k in ['bubble_box','ladder']]
    methods=['original','sector_native','sector_models','sector_equation','sector_row','separate_requests']
    p=HERE/'sector_protocol.json'
    protocol=dict(cases=cases,methods=methods,repetitions=3,timeout_seconds=120,
                  binary_sha256=a.sha(binary),source_sha256=a.sha(__file__),
                  reference='A larger seed region must reproduce all target coefficients in the same basis.',
                  failure_rule='Keep a failed first trial and omit later repetitions of that failed arm. Do not estimate its speedup.',
                  frozen_models=json.loads((HERE/'ablation_protocol.json').read_text())['frozen_models'])
    if p.exists():assert json.loads(p.read_text())==protocol
    else:p.write_text(json.dumps(protocol,indent=2)+'\n')

    def attempt(c,basis=None,scoped=True,equation=False,row=False,bounds=None,reference=None):
        a.st.previous.study.setup('learned' if equation else 'off',a.st.previous.study.OLD if equation else None,.01)
        os.environ.update(KIRA_RUNTIME_BINARY=str(binary),KIRA_EPHEMERAL_DB='1')
        if scoped:os.environ['KIRA_RESTRICT_SECTOR_INIT']='1'
        else:os.environ.pop('KIRA_RESTRICT_SECTOR_INIT',None)
        return native.run(c,c['size'],'learned' if row else 'native',HERE/'unused',timeout=120,margin=0,
                         weights=ROOT/'ML_model_reduction/cost_training/trained_weights.txt' if row else None,
                         archive=False,records=False,basis=basis,reference=reference,check_masters=basis is not None,
                         scratch_cap=32*1024**2,bounds=bounds,ordering=1)

    # Compare unchanged and restricted initialization before interpreting new graphs.
    for k in a.st.KINDS:
        c=a.st.make_case(k,221,'top','reserved')
        ref=HERE/'references'/(c['id']+'.json.gz');out=HERE/'parity'/(c['id']+'.json.gz')
        if out.exists():assert read(out)['success'];continue
        if not ref.exists() or not read(ref)['success']:continue
        r=attempt(c,read(ref)['masters'],reference=ref)
        if not r['success']:r=attempt(c,read(ref)['masters'],bounds=[v+1 for v in a.st.seed_bounds(c,'native')[1]],reference=ref)
        save(out,a.st.compact(r));emit(stage='sector_parity',case=c['id'],success=r['success'],status=r['status'])
        assert r['success'] and r['reference_checked'],'Sector restriction failed exact parity'

    for ci,c in enumerate(cases):
        n=c['definition']['physical_propagators'];ref=HERE/'higher_references'/(c['id']+'.json.gz')
        # Numeric kinematics are distinct from every development profile.
        if not ref.exists():
            r=attempt(c,bounds=[n+2,1,2]);save(ref,a.st.compact(r))
            emit(stage='higher_reference',case=c['id'],success=r['success'],status=r['status'],seconds=r['complete_seconds'])
        r=read(ref)
        if not r['success']:continue
        if not any(row and row!={t:'1'} for t,row in r.get('coefficients',{}).items()):
            emit(stage='higher_reference_inadequate',case=c['id'],reason='No nonzero nonidentity target reduction')
            continue
        check=HERE/'higher_references'/(c['id']+'_check.json.gz')
        if not check.exists():
            rr=attempt(c,r['masters'],bounds=[n+2,2,2],reference=ref);save(check,a.st.compact(rr))
            emit(stage='higher_reference_check',case=c['id'],success=rr['success'],status=rr['status'],seconds=rr['complete_seconds'])
        if not read(check)['success']:continue
        basis=r['masters'];failed=set()
        for rep in range(3):
            shift=(ci+rep)%len(methods)
            for method in methods[shift:]+methods[:shift]:
                out=HERE/'higher_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if method in failed:continue
                if out.exists():
                    if not read(out)['success']:failed.add(method)
                    continue
                begin=time.perf_counter();choices={};attempts=[]
                if method=='sector_models':
                    choices={key:model.select(f,c) for key,model,f in [('graph',a.gm,a.GF),('seed',a.bm,a.BF),('workers',a.tm,a.TF)]}
                    assert choices['graph'][0]=='native' and choices['seed'][0]==choices['workers'][0]=='previous',choices
                if method=='separate_requests':
                    rows={};success=True
                    for indices in [[0,1],[2]]:
                        cc=copy.deepcopy(c);cc['targets']=[c['targets'][i] for i in indices];cc['size']=len(indices)
                        rr=attempt(cc,basis,bounds=[n+2,1,2],reference=ref);attempts.append(a.st.compact(rr))
                        success=success and rr['success'];rows.update(rr.get('coefficients',{}))
                    result=dict(success=success,coefficients=rows,attempts=attempts,fallback_count=0)
                else:
                    rr=attempt(c,basis,scoped=method!='original',equation=method=='sector_equation',row=method=='sector_row',bounds=[n+2,1,2])
                    attempts.append(a.st.compact(rr))
                    if not rr['success'] and method in ['sector_equation','sector_row']:
                        rr=attempt(c,basis,bounds=[n+2,1,2]);attempts.append(a.st.compact(rr))
                    result=dict(success=rr['success'],coefficients=rr.get('coefficients',{}),attempts=attempts,fallback_count=len(attempts)-1)
                a.bw.verify(c,result,basis,ref)
                result.update(case=c['id'],method=method,repetition=rep,choices=choices,complete_seconds=time.perf_counter()-begin,
                              original_binary_same_code=True,restricted_initialization=method!='original')
                save(out,result);emit(stage='higher_test',case=c['id'],method=method,success=result['success'],seconds=result['complete_seconds'])
                if not result['success']:failed.add(method)
    emit(stage='higher_test_complete')
if __name__=='__main__':main()
