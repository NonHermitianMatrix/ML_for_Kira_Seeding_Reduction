"""A single entry point for bounded, exact target-dependent Kira reductions."""
import gzip,json,os,time
from pathlib import Path
import s01_native_runner as native
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
ACTIONS=['native','tight','dots','rank','order5','equation','expanded']
def read(p):
    with gzip.open(p,'rt') as f:return json.load(f)
def save(p,r):
    p.parent.mkdir(parents=True,exist_ok=True)
    data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
    assert len(data)<16*1024**2
    used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
    assert used+len(data)<64*1024**2
    temporary=p.with_suffix('.writing');temporary.write_bytes(data);temporary.replace(p)
def compact(r):
    return {k:v for k,v in r.items() if k not in ['log','input','raw_export','choices','predictions','equation_records'] } | {'log_tail':r.get('log','')[-3500:]}
def bounds(c,action):
    ts=c['targets'];b=[max(sum(max(0,a) for a in t) for t in ts),max(sum(max(0,-a) for a in t) for t in ts),max(sum(max(0,a-1) for a in t) for t in ts)]
    delta={'native':(0,0,0),'tight':(-1,-1,-1),'dots':(-1,0,-1),'rank':(0,-1,0),'order5':(0,0,0),'equation':(0,0,0),'expanded':(1,1,1)}[action]
    return [max(0,x+y) for x,y in zip(b,delta)]
def attempt(c,basis=None,action='native',reference=None,indexed=True,custom=None,timeout=180):
    os.environ.update(KIRA_RUNTIME_SCRATCH='node',KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-adaptive/kira'),
        KIRA_EPHEMERAL_DB='1',KIRA_RESTRICT_SECTOR_INIT='1',KIRA_PROJECT_ZERO_CRITERION='1',KIRA_EQ_MODE='off',KIRA_EQ_COLLECT='0',
        KIRA_PARALLEL_EVAL='1',KIRA_FAST_EVAL='1',KIRA_SPARSE_FEATURES='1',KIRA_ROW_PAIR_FASTPATH='1')
    if action=='equation':
        folder=ROOT/'ML_model_equation_selection/scattering_training'
        weight=folder/'trained_model'/(c['topology_group']+'.txt')
        threshold=.01
        if weight.exists():threshold=json.loads((folder/'freeze.json').read_text())['policies'][c['topology_group']+'_equation']['threshold']
        else:weight=ROOT/'ML_model_equation_selection/early_generation/trained_model/early_d12/weights.txt'
        os.environ.update(KIRA_EQ_MODE='learned',KIRA_EQ_WEIGHTS=str(weight),KIRA_EQ_THRESHOLD=str(threshold))
    if indexed:os.environ['KIRA_INDEX_SECTOR_FILES']='1'
    else:os.environ.pop('KIRA_INDEX_SECTOR_FILES',None)
    return native.run(c,c['size'],'native',HERE/'unused',timeout=timeout,margin=0,reference=reference,
        archive=False,records=False,basis=basis,check_masters=basis is not None or reference is not None,
        scratch_cap=32*1024**2,bounds=custom or bounds(c,action),ordering=5 if action=='order5' else 1)
def verify(c,r,ref):
    import sympy as sp
    begin=time.perf_counter();want=read(ref)['coefficients'];got=r.get('coefficients',{})
    mismatches=[];checks=0
    if set(got)!=set(want):mismatches.append('target set')
    for t,row in got.items():
        for m in set(row)|set(want.get(t,{})):
            a,b=row.get(m,'0'),want.get(t,{}).get(m,'0');checks+=1
            if a!=b and sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))!=0:mismatches.append([t,m])
    r.update(reference_checked=not mismatches,mismatches=mismatches,coefficient_checks=checks,
             verification_seconds=time.perf_counter()-begin)
    r['success']=r['success'] and not mismatches
def workflow(c,basis,action,ref=None,indexed=True):
    begin=time.perf_counter();attempts=[]
    plan=list(dict.fromkeys([action,'native','expanded']))
    for a in plan:
        rr=attempt(c,basis,a,indexed=indexed);attempts.append(compact(rr))
        if rr['success']:break
    result=dict(case=c['id'],action=action,success=rr['success'],coefficients=rr.get('coefficients',{}),
                attempts=attempts,fallback_count=len(attempts)-1)
    if ref:verify(c,result,ref)
    result['complete_seconds']=time.perf_counter()-begin
    return result
