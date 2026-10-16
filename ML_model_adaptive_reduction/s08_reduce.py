"""Apply the frozen cost policy to a target batch and a prescribed master basis."""
import argparse,json,time
from functools import lru_cache
from pathlib import Path
import s05_study as study
import s12_graph_policy as graph_policy
rt=study.rt
def signature(c):
    d=c['definition']
    return (tuple(d['loop_momenta']),tuple(d['external_momenta']),
        tuple((p['momentum'],str(p['mass_squared'])=='0') for p in d['propagators']),
        tuple(d['top_level_sectors']),len(d['invariants']))
@lru_cache(maxsize=2)
def training_domain(case_sha):
    cs=[c for c in json.loads((rt.HERE/'cases.json').read_text())['cases'] if c['split']=='training']
    x=[study.features(c) for c in cs]
    return set(signature(c) for c in cs),list(zip(map(min,zip(*x)),map(max,zip(*x))))
@lru_cache(maxsize=4)
def _load_json(path,device,inode,size,modified):
    return json.loads(Path(path).read_text())
def load_json(path):
    p=Path(path);s=p.stat()
    return _load_json(str(p),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
def reduce(case,basis,frozen=None):
    start=time.perf_counter()
    f=frozen or load_json(rt.HERE/'trained_model/freeze.json')
    assert graph_policy.file_digest(rt.ROOT/'.tools/kira-adaptive/kira')==f['binary_sha256']
    assert graph_policy.file_digest(rt.HERE/'s02_runtime.py')==f['runtime_sha256']
    assert graph_policy.file_digest(rt.HERE/'s05_study.py')==f['study_sha256']
    assert graph_policy.file_digest(rt.HERE/'cases.json')==f['cases_sha256']
    d=case['definition'];n=len(d['propagators']);tops=d['top_level_sectors']
    assert 0<n<=31 and case['size']==len(case['targets']) and isinstance(basis,list)
    for a in case['targets']+basis:
        assert len(a)==n and all(isinstance(v,int) for v in a)
        sector=sum(1<<i for i,v in enumerate(a) if v>0)
        assert any((sector&top)==sector for top in tops),'Targets and masters must lie within the declared sector domain'
    shapes,ranges=training_domain(f['cases_sha256']);x=study.features(case)
    supported=case['topology_group'] in study.KINDS+['bubble_box3','bubble_box4'] and signature(case) in shapes and all(lo-1e-12<=v<=hi+1e-12 for v,(lo,hi) in zip(x,ranges))
    guard=load_json(graph_policy.PATH) if graph_policy.PATH.exists() else None
    action=(graph_policy.select(f,guard,case) if guard else study.select(f,case)) if supported else 'native'
    selected=time.perf_counter();r=rt.workflow(case,basis,action)
    r.update(choice_seconds=selected-start,application_seconds=time.perf_counter()-start,
             policy_supported=supported,answers_supplied=False,
             graph_guard_used=guard is not None,
             learned_choice_used=supported and (guard is None or guard['graphs'].get(case['topology_group'],{}).get('enabled',False)),
             basis_note='Success means all target integrals reach the supplied basis. Minimality of that supplied basis is not inferred.')
    return r
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();case=json.loads(Path(a.case).read_text());basis=json.loads(Path(a.basis).read_text())
    r=reduce(case,basis);rt.save(Path(a.output),r)
    print(json.dumps({k:r[k] for k in ['success','action','fallback_count','choice_seconds','application_seconds']}),flush=True)
    if not r['success']:raise SystemExit(2)
if __name__=='__main__':main()
