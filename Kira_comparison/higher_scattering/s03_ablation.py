"""Compare frozen decisions on the same fresh targets, basis and allocation."""
import copy,gzip,hashlib,json,os,resource,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_workflow_selection/thread_policy'))
import s06_test as threads
tm=threads.model;tw=threads.w;runtime=tw.runtime
bm=runtime.previous_model;bw=runtime.prior;gm=bw.old;st=bw.st
native=runtime.native
TF=json.loads((tw.HERE/'trained_model/freeze.json').read_text())
BF=runtime.FROZEN;GF=bw.FROZEN
for model,f in [(tm,TF),(bm,BF),(gm,GF)]:model.check_freeze(f)
METHODS=['native','graph_fixed','graph_model','seed_fixed','seed_model','worker_fixed','worker_model','equation_filter','seed_filter','row_model']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.load(gzip.open(p,'rt'))
def save(p,r):
    p.parent.mkdir(exist_ok=True)
    data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
    used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
    assert used+len(data)+4096<8*1024**2,(used,len(data))
    p.write_bytes(data)

def native_attempt(c,basis=None,margin=0,row=False,ref=None):
    st.previous.study.setup('off')
    os.environ.update(KIRA_RUNTIME_BINARY=str(st.previous.BINARY),KIRA_EPHEMERAL_DB='1')
    return native.run(c,c['size'],'learned' if row else 'native',HERE/'unused',timeout=120,margin=margin,
                      weights=ROOT/'ML_model_reduction/cost_training/trained_weights.txt' if row else None,
                      archive=False,records=False,check_masters=basis is not None,basis=basis,reference=ref,
                      scratch_cap=32*1024**2,ordering=1)

def reference(c):
    path=HERE/'references'/(c['id']+'.json.gz')
    if path.exists():return path if read(path)['success'] else None
    r=native_attempt(c,margin=1)
    save(path,st.compact(r))
    print(json.dumps(dict(stage='reference',case=c['id'],success=r['success'],status=r['status'],seconds=r['complete_seconds'])),flush=True)
    if not r['success']:return None
    # A larger seed region must reproduce the coefficients in the same basis.
    p=HERE/'references'/(c['id']+'_check.json.gz')
    check=native_attempt(c,basis=r['masters'],margin=2,ref=path)
    save(p,st.compact(check))
    print(json.dumps(dict(stage='reference_check',case=c['id'],success=check['success'],status=check['status'],seconds=check['complete_seconds'])),flush=True)
    return path if check['success'] and check['reference_checked'] else None

def run(c,basis,method,ref):
    start=time.perf_counter();cpu0=sum(resource.getrusage(k).ru_utime+resource.getrusage(k).ru_stime for k in [resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN])
    reason='fixed';cfg=method
    if method in ['native','graph_fixed','graph_model','equation_filter','seed_filter']:
        if method=='graph_fixed':cfg=gm.canonical(c,GF['policies'][c['topology_group']]['best_fixed'])
        elif method=='graph_model':cfg,reason=gm.select(GF,c)
        elif method.endswith('_filter'):cfg=method.split('_')[0]
        else:cfg='native'
        r=st.workflow(c,None,cfg,basis);r['coefficients']=r['attempts'][-1].get('coefficients',{})
    elif method in ['seed_fixed','seed_model']:
        if method=='seed_model':cfg,reason=bm.select(BF,c)
        else:cfg=BF['policies'][c['topology_group']]['best_fixed']
        r=bw.workflow(c,basis,cfg)
    elif method in ['worker_fixed','worker_model']:
        if method=='worker_model':cfg,reason=tm.select(TF,c)
        else:cfg=TF['policies'][c['topology_group']]['best_fixed']
        r=runtime.workflow(c,basis,cfg)
    elif method=='row_model':
        a=native_attempt(c,basis,row=True);attempts=[st.compact(a)]
        if not a['success']:
            a=native_attempt(c,basis,margin=1);attempts.append(st.compact(a))
        r=dict(success=a['success'],attempts=attempts,coefficients=a.get('coefficients',{}),fallback_count=len(attempts)-1)
    else:raise ValueError(method)
    bw.verify(c,r,basis,ref)
    cpu1=sum(resource.getrusage(k).ru_utime+resource.getrusage(k).ru_stime for k in [resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN])
    r.update(case=c['id'],topology=c['topology_group'],loops=len(c['definition']['loop_momenta']),method=method,
             choice=cfg,selection_reason=reason,complete_seconds=time.perf_counter()-start,cpu_seconds=cpu1-cpu0)
    return r

def main():
    path=HERE/'ablation_protocol.json'
    cases=[st.make_case(k,h,'top','reserved') for h in [221,222] for k in st.KINDS]
    protocol=dict(cases=cases,methods=METHODS,repetitions=3,models='Frozen published models. No refitting or test-based choice.',
                  frozen_models={str(p.relative_to(ROOT)):sha(p) for p in [tw.HERE/'trained_model/freeze.json',bw.HERE/'trained_model/freeze.json',st.HERE/'trained_model/freeze.json',ROOT/'ML_model_reduction/cost_training/trained_weights.txt']},
                  time_includes='Preparation, decisions, exact algebra, checks, cleanup and fallback. Models loaded before timing.',
                  fixed_controls='Best fixed strategies selected on the earlier training data, not these test cases.',
                  source_sha256=sha(__file__))
    if path.exists():assert json.loads(path.read_text())==protocol
    else:path.write_text(json.dumps(protocol,indent=2)+'\n')
    for ci,c in enumerate(cases):
        ref=reference(c)
        if ref is None:continue
        basis=read(ref)['masters']
        for rep in range(3):
            shift=(ci+rep)%len(METHODS)
            for method in METHODS[shift:]+METHODS[:shift]:
                p=HERE/'ablation_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if p.exists():continue
                r=run(c,basis,method,ref);r['repetition']=rep;save(p,r)
                print(json.dumps(dict(stage='ablation',case=c['id'],method=method,success=r['success'],seconds=r['complete_seconds'],choice=r['choice'],reason=r['selection_reason'])),flush=True)
    print('ABLATION_COMPLETE',flush=True)
if __name__=='__main__':main()
