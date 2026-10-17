"""Load only the parts of the frozen policy that deployment uses."""
import argparse,json,time
from s00_runtime import HERE,rt,inputs,choose,run,validate,equivalent_partitions,save

def normalize(c):
    if all(k in c for k in ['group','split','topology_group']):return c
    c=dict(c);c.setdefault('group','application');c.setdefault('split','application')
    if 'topology_group' not in c:
        cfg=rt.read(HERE/'fixed_inputs.json');sig=inputs.signature(c)
        matches=[g for g,signatures in cfg['signatures'].items() if sig in signatures]
        c['topology_group']=matches[0] if len(matches)==1 else 'unknown'
    return c

def prepare():
    f=rt.read(HERE/'trained_model/freeze.json')
    fields=['enabled','gate','fixed_by_graph','domain']
    if f['enabled']:fields.append('model')
    policy={k:f[k] for k in fields}
    policy['source_freeze_sha256']=inputs.sha(HERE/'trained_model/freeze.json')
    p=HERE/'trained_model/deployment.json'
    if p.exists():assert rt.read(p)==policy
    else:inputs.write(p,policy)
    count=0;metadata_checks=0
    for stage in ['training','validation','model_test']:
        for c in rt.read(HERE/stage/'protocol.json')['cases']:
            assert choose(c,policy)==choose(c,f),c['id']
            minimal={k:c[k] for k in ['id','size','targets','definition']}
            normalized=normalize(minimal)
            assert normalized['topology_group']==c['topology_group'],c['id']
            assert choose(normalized,policy)==choose(c,f),c['id']
            assert set(minimal)=={'id','size','targets','definition'}
            metadata_checks+=1
            count+=1
    audit=dict(passed=True,choice_parity_checks=count,model_enabled=f['enabled'],
        minimal_input_checks=metadata_checks,
        full_policy_bytes=(HERE/'trained_model/freeze.json').stat().st_size,
        deployment_bytes=p.stat().st_size,source_freeze_sha256=policy['source_freeze_sha256'],
        deployment_sha256=inputs.sha(p),
        scope='Use only physical inputs and frozen choices. No reserved timings or coefficients enter preparation.')
    inputs.write(HERE/'deployment_checks.json',audit)
    print('DEPLOYMENT_CHECKS',json.dumps(audit),flush=True)

def reduce(c,basis,method='learned',reference=None):
    start=time.perf_counter();c=normalize(c)
    if method!='learned':
        from s00_runtime import reduce as original
        r=original(c,basis,method,reference);r['complete_seconds']=time.perf_counter()-start
        return r
    validate(c,basis);scores=None
    equivalent=equivalent_partitions(c)
    if equivalent:action='whole_off';ml=False
    else:
        policy=rt.read(HERE/'trained_model/deployment.json')
        action,scores=choose(c,policy);ml=True
    selection=time.perf_counter()-start
    r=run(c,basis,action,ml,reference)
    r.update(method=method,decision_seconds=selection,scores=scores,
        prediction_skipped_equivalent_partitions=equivalent,
        compact_deployment=True,complete_seconds=time.perf_counter()-start)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true')
    p.add_argument('--case');p.add_argument('--basis');p.add_argument('--output')
    p.add_argument('--method',default='learned',choices=['learned','fixed','fixed_off','previous','off'])
    a=p.parse_args()
    if a.prepare:prepare()
    else:
        if not all([a.case,a.basis,a.output]):p.error('Supply --case, --basis, and --output.')
        r=reduce(rt.read(a.case),rt.read(a.basis),a.method);save(a.output,r)
        print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],partition=r['action'])))
