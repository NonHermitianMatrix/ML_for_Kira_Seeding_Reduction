"""Check the default joint application without supplying target coefficients."""
import copy,json,os,subprocess,sys,tempfile,time
from pathlib import Path
from s05_study import HERE,read,save,write

def main():
    import sympy as sp
    plan=json.loads((HERE/'request_batching/cases.json').read_text());checks=[]
    frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
    for group in plan['groups']:
        c=group['case'];ref=read(HERE/'request_batching'/(c['id']+'_reference.json.gz'));parts=[]
        for j,ts in enumerate([c['targets'][:group['cut']],c['targets'][group['cut']:]]):
            r=copy.deepcopy(c);r.update(id=c['id']+f'_part{j}',targets=ts,size=len(ts));parts.append(r)
        dest=HERE/'model_test'/('best_'+c['id']+'.json.gz')
        if not dest.exists():
            with tempfile.TemporaryDirectory(prefix='kira_best_',dir=os.environ['TMPDIR']) as td:
                td=Path(td);(td/'requests.json').write_text(json.dumps(parts));(td/'basis.json').write_text(json.dumps(ref['masters']))
                begin=time.perf_counter()
                subprocess.run([sys.executable,str(HERE/'s16_reduce_best.py'),'--requests',str(td/'requests.json'),
                    '--basis',str(td/'basis.json'),'--output',str(dest)],check=True,timeout=400)
                r=read(dest);r['cold_process_seconds']=time.perf_counter()-begin;save(dest,r)
        r=read(dest);assert r['success'] and r['answers_withheld'] and len(r['partition_coefficients'])==2
        assert r['configuration']==frozen['best_fixed'] and r['application_policy']=='best_fixed_training'
        count=0
        for source,result in zip(parts,r['partition_coefficients']):
            assert source['id']==result['id']
            assert set(result['coefficients'])=={','.join(map(str,t)) for t in source['targets']}
            for t,row in result['coefficients'].items():
                want=ref['coefficients'][t]
                for m in set(row)|set(want):
                    a,b=row.get(m,'0'),want.get(m,'0')
                    assert a==b or sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))==0
                    count+=1
        checks.append(dict(case=c['id'],passed=True,coefficient_checks=count,configuration=r['configuration'],cold_process_seconds=r['cold_process_seconds']))
    write(HERE/'model_test/public_best_checks.json',dict(complete=True,all_exact=True,cases=checks))
    import s15_validate_evidence
    s15_validate_evidence.main()

if __name__=='__main__':main()
