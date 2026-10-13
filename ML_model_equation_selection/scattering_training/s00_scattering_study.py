"""Train native seed and equation trees on three previously unsupported families."""
import argparse, copy, gzip, hashlib, importlib.util, json, math, os
from pathlib import Path
import statistics, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GENERAL = ROOT / 'Kira_comparison/generalization'
SEED = ROOT / 'ML_model_seed_selection/scattering_training'
sys.path.insert(0, str(GENERAL))
from s00_native_run import run
from s01_cases import build, targets, audit
OLD = ROOT / 'ML_model_equation_selection/early_generation/trained_model/early_d12/weights.txt'
BINARY = ROOT / '.tools/kira-early-generation/kira'
COLLECT = ROOT / '.tools/kira-equation-selection/kira-lazy'
KINDS = ['nonplanar_box', 'pentagon', 'one_mass_box']
FEATURES = list(range(15)) + [22, 23]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    with gzip.open(p, 'rt') as f: return json.load(f)
def guard():
    used = sum(p.stat().st_blocks * 512 for base in [HERE, SEED]
               for p in base.rglob('*') if p.is_file())
    assert used < 32 * 1024**2, ('retained storage limit', used)
def save(p, r):
    p.parent.mkdir(parents=True, exist_ok=True)
    data = gzip.compress(json.dumps(r, separators=(',', ':')).encode(), mtime=0)
    assert len(data) < 8 * 1024**2
    tmp = p.with_suffix('.tmp'); tmp.write_bytes(data); tmp.replace(p); guard()
def write(p, r):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(r, indent=2) + '\n'); guard()
def emit(**r): print(json.dumps(r), flush=True)

def prepare():
    cases = []
    for kind in KINDS:
        for split, profiles in [('training', [10, 11]), ('validation', [12]), ('reserved', [13, 14])]:
            for profile in profiles:
                d = build(kind, False, profile)
                ts = targets(d)[:16]
                cid = f'{kind}_point{profile}'
                cases.append(dict(id=cid, group=cid, split=split, topology_group=kind,
                                  definition=d, targets=ts, size=len(ts), audit=audit(d)))
        for split, start in [('training', 0), ('validation', 4), ('reserved', 8)]:
            d = build(kind, True)
            ts = targets(d)[start:start+4]
            cid = f'{kind}_symbolic_{split}'
            cases.append(dict(id=cid, group=cid, split=split, topology_group=kind,
                              definition=d, targets=ts, size=len(ts), audit=audit(d)))
    # The symbolic index lists are disjoint; rational profiles use new kinematics.
    for kind in KINDS:
        symbolic = [c for c in cases if c['topology_group']==kind and c['definition']['invariants']]
        sets = [set(map(tuple,c['targets'])) for c in symbolic]
        assert not any(sets[i] & sets[j] for i in range(3) for j in range(i))
    record = dict(cases=cases, design='New rational profiles and disjoint symbolic target lists within each known graph. This is adaptation within graph structures, not transfer to unseen topologies.',
                  candidates=[.001, .01, .05], depth=12, minimum_child_rows=8,
                  validation_repetitions=3, test_repetitions=5,
                  test_methods=['native','old_equation','seed','equation'])
    p = HERE/'cases.json'
    if p.exists(): assert json.loads(p.read_text()) == record
    else: write(p,record)
    for base in [HERE, SEED]:
        for folder in (['references','training','validation','trained_model','model_test','logs'] if base==HERE else ['trained_model','model_test']):
            (base/folder).mkdir(parents=True,exist_ok=True)
    emit(stage='prepared', cases=len(cases))

def setup(mode='off', weights=None, threshold=.01, collect=False):
    os.environ.update(KIRA_RUNTIME_SCRATCH='node', KIRA_RUNTIME_BINARY=str(COLLECT if collect else BINARY),
        KIRA_EQ_MODE='collect' if collect else mode, KIRA_EQ_COLLECT='1' if collect else '0',
        KIRA_EQ_THRESHOLD=str(threshold), KIRA_PARALLEL_EVAL='1', KIRA_FAST_EVAL='1',
        KIRA_SPARSE_FEATURES='1', KIRA_ROW_PAIR_FASTPATH='1')
    if weights: os.environ['KIRA_EQ_WEIGHTS']=str(weights)

def attempt(c, ref=None, mode='off', weights=None, threshold=.01, margin=0, collect=False, basis=None):
    setup(mode,weights,threshold,collect)
    return run(c,c['size'],'native',HERE/'unused',timeout=150,margin=margin,
               reference=ref,records=False,archive=False,check_masters=bool(ref or basis),
               scratch_cap=32*1024**2,basis=basis)

def reference(c):
    p=HERE/'references'/(c['id']+'.json.gz')
    if p.exists():
        assert load(p)['success']; return p
    r=attempt(c,margin=1); save(p,r)
    emit(stage='reference',case=c['id'],success=r['success'],seconds=r['complete_seconds'])
    assert r['success'],(c['id'],r['status'])
    return p

def collect(cases):
    for c in cases:
        if c['split']!='training':continue
        p=HERE/'training'/(c['id']+'.json.gz')
        if p.exists(): assert load(p)['success']; continue
        ref=reference(c);r=attempt(c,ref,collect=True)
        if not r['success']:
            save(p.with_name(c['id']+'_failed.json.gz'),r)
            r=attempt(c,ref,collect=True,margin=1)
        assert r['success'] and r['reference_checked'],(c['id'],r['status'])
        assert r.get('equation_records')
        save(p,r);emit(stage='collect',case=c['id'],rows=len(r['equation_records'].splitlines()))

def train(kind, task):
    import numpy as np
    blocks=[];labels=[];files=[]
    for p in sorted((HERE/'training').glob(kind+'*.json.gz')):
        if '_failed' in p.name:continue
        r=load(p);assert r['split']=='training' and r['reference_checked']
        rows=[line.split('\t') for line in r['equation_records'].splitlines()]
        assert all(len(row)==28 for row in rows)
        if task=='seed':
            grouped={}
            for row in rows:
                key=row[0].split(':')[0];x=[float(v) for v in row[2:26]];x[14]=0
                if key in grouped:
                    assert all(grouped[key][0][j]==x[j] for j in FEATURES if j!=14)
                    grouped[key][1]=max(grouped[key][1],int(row[1]))
                else: grouped[key]=[x,int(row[1])]
            x=np.array([v[0] for v in grouped.values()]);y=np.array([v[1] for v in grouped.values()])
        else:
            x=np.array([[float(v) for v in row[2:26]] for row in rows]);y=np.array([int(row[1]) for row in rows])
        blocks.append(x);labels.append(y)
        files.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),rows=len(y),positives=int(y.sum())))
    assert len(files)==3
    weights=np.concatenate([np.full(len(y),1/len(y)) for y in labels]);x=np.vstack(blocks);y=np.concatenate(labels)
    nodes=[];start=time.perf_counter();features=[f for f in FEATURES if task!='seed' or f!=14]
    def impurity(a,b):return a*b/(a+b) if a+b>0 else 0
    def node(ids,depth):
        index=len(nodes);wp=float(weights[ids]@y[ids]);wt=float(weights[ids].sum())
        nodes.append(dict(feature=-1,threshold=0.,left=-1,right=-1,
                          probability=float((y[ids].sum()+.5)/(len(ids)+1)),rows=len(ids),positives=int(y[ids].sum())))
        if depth==12 or len(ids)<16 or wp<1e-12 or wt-wp<1e-12:return index
        best=None;gain=1e-12;parent=impurity(wp,wt-wp)
        for f in features:
            vals=x[ids,f]
            for cut in np.unique(np.quantile(vals,np.linspace(.02,.98,25))):
                mask=vals<=cut;nl=int(mask.sum())
                if min(nl,len(ids)-nl)<8:continue
                left=ids[mask];lp=float(weights[left]@y[left]);lt=float(weights[left].sum())
                g=parent-impurity(lp,lt-lp)-impurity(wp-lp,wt-lt-wp+lp)
                if g>gain:gain=g;best=(f,(float(vals[mask].max())+float(vals[~mask].min()))/2,mask)
        if best:
            f,cut,mask=best;a=node(ids[mask],depth+1);b=node(ids[~mask],depth+1)
            nodes[index].update(feature=f,threshold=cut,left=a,right=b)
        return index
    node(np.arange(len(y)),0)
    base=(SEED if task=='seed' else HERE)/'trained_model'
    model=dict(task=task,topology=kind,nodes=nodes,features=features,depth=12,minimum_child_rows=8,
               rows=len(y),positives=int(y.sum()),training_files=files,training_seconds=time.perf_counter()-start,
               label='At least one native selected-support equation from this seed' if task=='seed' else 'Membership in the native selected integral supports',
               note='Seed trees exclude operator index, so every operator of one seed receives the same score. The early hook skips all equations of a rejected seed. Enumeration still uses Kira.')
    write(base/(kind+'.json'),model)
    (base/(kind+'.txt')).write_text(str(len(nodes))+'\n'+''.join(f'{n["feature"]} {n["threshold"]:.17g} {n["left"]} {n["right"]} {n["probability"]:.17g}\n' for n in nodes))
    emit(stage='trained',kind=kind,task=task,rows=len(y),positives=int(y.sum()),nodes=len(nodes))

def model_path(c,task):return (SEED if task=='seed' else HERE)/'trained_model'/(c['topology_group']+'.txt')
def workflow(c,ref,task,threshold=.01,basis=None):
    begin=time.perf_counter();weights=OLD if task=='old_equation' else model_path(c,task) if task in ['seed','equation'] else None
    steps=([('learned',0)] if weights else [])+[('off',0),('off',1)];attempts=[]
    for mode,margin in steps:
        r=attempt(c,ref,mode,weights,threshold,margin,basis=basis);attempts.append(r)
        if r['success'] or r.get('mismatches'):break
    stages={}
    for r in attempts:
        for s in r.get('stage_metrics',[]):stages[s['stage']]=stages.get(s['stage'],0)+s['seconds']
    result=dict(case=c['id'],task=task,threshold=threshold,success=attempts[-1]['success'],
                fallback_count=len(attempts)-1,attempts=attempts,complete_seconds=time.perf_counter()-begin,
                equation_preparation_seconds=sum(stages.get(k,0) for k in ['generation_modular','equation_regeneration','equation_selection','equation_selection_coeff','modular_solve']))
    return result

def validation(cases):
    for c in cases:
        if c['split']!='validation':continue
        ref=reference(c)
        methods=[('native',.01)]+[(task,t) for task in ['seed','equation'] for t in [.001,.01,.05]]
        for rep in range(3):
            order=methods[rep:]+methods[:rep]
            for task,t in order:
                p=HERE/'validation'/f'{c["id"]}_{task}_{t}_{rep}.json.gz'
                if p.exists():continue
                r=workflow(c,ref,task,t);r['repetition']=rep;save(p,r)
                emit(stage='validation',case=c['id'],task=task,threshold=t,success=r['success'],fallback=r['fallback_count'],seconds=r['complete_seconds'])
    policies={}
    for kind in KINDS:
        vc=[c for c in cases if c['split']=='validation' and c['topology_group']==kind]
        for task in ['seed','equation']:
            options=[]
            for t in [.001,.01,.05]:
                ratios=[];fallback=0;success=True
                for c in vc:
                    native=[load(HERE/'validation'/f'{c["id"]}_native_0.01_{r}.json.gz') for r in range(3)]
                    model=[load(HERE/'validation'/f'{c["id"]}_{task}_{t}_{r}.json.gz') for r in range(3)]
                    fallback+=sum(r['fallback_count'] for r in model)
                    success &= all(r['success'] for r in model+native)
                    ratios.append(statistics.median(r['complete_seconds'] for r in model)/statistics.median(r['complete_seconds'] for r in native))
                options.append(dict(threshold=t,ratio=math.exp(statistics.mean(map(math.log,ratios))),fallback=fallback,success=success))
            # Complete timing determines the best threshold. No test result enters this choice.
            chosen=min(options,key=lambda a:(not a['success'],a['ratio']))
            policies[kind+'_'+task]=dict(chosen,options=options,activate=chosen['success'] and chosen['fallback']==0 and chosen['ratio']<.98)
    freeze=dict(policies=policies,cases_sha256=sha(HERE/'cases.json'),source_sha256=sha(__file__),binary_sha256=sha(BINARY),
                weights={str(p.relative_to(ROOT)):sha(p) for base in [HERE,SEED] for p in (base/'trained_model').glob('*.txt')},
                test_methods=['native','old_equation','seed','equation'],repetitions=5,
                timing='Includes input preparation, inference, native generation, exact comparisons, cleanup, and every fallback. Offline references and training excluded.',
                adaptation='New graph-specific trees; original neural checkpoints and historical tests remain unchanged.')
    p=HERE/'freeze.json'
    if p.exists():assert json.loads(p.read_text())==freeze
    else:write(p,freeze)
    emit(stage='frozen',policies=policies)

def test(cases):
    frozen=json.loads((HERE/'freeze.json').read_text())
    assert sha(HERE/'cases.json')==frozen['cases_sha256'] and sha(BINARY)==frozen['binary_sha256']
    assert sha(__file__)==frozen['source_sha256']
    for p,h in frozen['weights'].items():assert sha(ROOT/p)==h
    for c in cases:
        if c['split']!='reserved':continue
        ref=reference(c)
        for rep in range(5):
            methods=frozen['test_methods'];order=methods[rep%4:]+methods[:rep%4]
            for task in order:
                p=HERE/'model_test'/f'{c["id"]}_{task}_{rep}.json.gz'
                if p.exists():continue
                t=frozen['policies'][c['topology_group']+'_'+task]['threshold'] if task in ['seed','equation'] else .01
                r=workflow(c,ref,task,t);r['repetition']=rep;save(p,r)
                emit(stage='test',case=c['id'],task=task,success=r['success'],fallback=r['fallback_count'],seconds=r['complete_seconds'])
        # Independent enlarged native reference already supplies the basis.
        # Check application without giving target coefficients to the reduction driver.
        for task in ['seed','equation']:
            p=HERE/'model_test'/f'{c["id"]}_{task}_application.json.gz'
            if p.exists():continue
            t=frozen['policies'][c['topology_group']+'_'+task]['threshold']
            reference_data=load(ref);r=workflow(c,None,task,t,basis=reference_data['masters'])
            import sympy as sp
            got=r['attempts'][-1].get('coefficients',{});want=reference_data['coefficients'];checks=0
            assert got.keys()==want.keys()
            for key,row in got.items():
                for m in set(row)|set(want[key]):
                    a=sp.sympify(row.get(m,'0').replace('^','**'),rational=True)
                    b=sp.sympify(want[key].get(m,'0').replace('^','**'),rational=True)
                    assert sp.cancel(a-b)==0;checks+=1
            r['independent_coefficient_checks']=checks;r['answers_withheld']=True;save(p,r)
            emit(stage='application',case=c['id'],task=task,checks=checks,success=r['success'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','collect','train','validate','test','all'])
    a=ap.parse_args().action
    if a in ['prepare','all']:prepare()
    cases=json.loads((HERE/'cases.json').read_text())['cases']
    if a in ['collect','all']:collect(cases)
    if a in ['train','all']:
        for kind in KINDS:
            for task in ['seed','equation']:train(kind,task)
    if a in ['validate','all']:validation(cases)
    if a in ['test','all']:test(cases)
    emit(stage='complete',action=a)
if __name__=='__main__':main()
