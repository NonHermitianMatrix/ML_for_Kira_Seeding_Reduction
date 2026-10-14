"""Check completed experiment records and frozen settings without new reductions."""
import collections,json
from pathlib import Path
from s05_study import HERE,ROOT,BINARY,read,sha,write

def main():
    freeze=HERE/'trained_model/freeze.json';f=json.loads(freeze.read_text())
    for p,key in [(HERE/'cases.json','cases_sha256'),(HERE/'s05_study.py','source_sha256'),
                  (HERE/'s02_run.py','driver_sha256'),(BINARY,'binary_sha256')]:
        assert sha(p)==f[key],p
    for name,digest in f['weights'].items():assert sha(ROOT/name)==digest,name
    candidates=json.loads((HERE/'trained_model/candidates.json').read_text())
    assert len(candidates['models'])==12
    totals={};failures=collections.Counter();first_success=collections.Counter()
    for split,expected in [('training',651),('validation',357)]:
        files=list((HERE/split).glob('*.json.gz'));assert len(files)==expected
        for p in files:
            r=read(p);assert r['success'] and r['attempts'][-1]['reference_checked'],p
            assert all(not a.get('mismatches') for a in r['attempts']),p
            failures[split]+=r['fallback_count'];first_success[split]+=r['fallback_count']==0
        totals[split]=len(files)
    summary=json.loads((HERE/'model_test/summary.json').read_text())
    assert summary['complete'] and summary['all_exact'] and summary['workflows']==620 and summary['applications']==31
    assert summary['freeze_sha256']==sha(freeze)
    batch=json.loads((HERE/'request_batching/summary.json').read_text())
    assert batch['complete'] and batch['all_exact'] and batch['workflows']==200
    assert batch['freeze_sha256']==sha(freeze)
    public={}
    names=['public_application_checks.json','public_joint_checks.json']
    if (HERE/'model_test/public_best_checks.json').exists():names.append('public_best_checks.json')
    for filename in names:
        checks=json.loads((HERE/'model_test'/filename).read_text())
        assert checks['complete'] and checks['all_exact'] and len(checks['cases'])==10
        assert all(c['passed'] for c in checks['cases'])
        public[filename]=dict(applications=len(checks['cases']),coefficient_checks=sum(c['coefficient_checks'] for c in checks['cases']))
    testfiles=list((HERE/'model_test').glob('*.json.gz'));assert len(testfiles)==651+10*len(names),len(testfiles)
    for p in testfiles:
        r=read(p);assert r['success'] and not any(a.get('mismatches') for a in r['attempts']),p
    requestfiles=list((HERE/'request_batching').glob('*.json.gz'));assert len(requestfiles)==210
    for p in requestfiles:
        r=read(p);assert r['success'],p
        for calculation in r.get('workflows',[]):
            assert calculation['success'] and calculation['attempts'][-1]['reference_checked'],p
    size=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
    assert size<40*1024**2,size
    result=dict(complete=True,all_exact=True,training_records=totals['training'],validation_records=totals['validation'],
        reserved_workflows=620,joint_workflows=200,basis_only_applications=31,public_checks=public,
        development_fallback_attempts=dict(failures),development_first_successes=dict(first_success),
        frozen_model=f['model']['name'],freeze_sha256=sha(freeze),retained_allocated_bytes=size)
    write(HERE/'evidence_validation.json',result)
    write(ROOT/'report/workflow_validation.json',result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
