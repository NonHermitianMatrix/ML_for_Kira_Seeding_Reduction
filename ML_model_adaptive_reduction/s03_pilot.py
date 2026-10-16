"""Check file-index parity and measure candidate seed regions on development data."""
import json,sys
from pathlib import Path
from s02_runtime import *
sys.path.insert(0,str(ROOT/'Kira_comparison/higher_scattering'))
import s00_cases as cases
def main():
    protocol=json.loads((ROOT/'Kira_comparison/higher_scattering/ablation_protocol.json').read_text())
    for c in protocol['cases'][:7]:
        ref=ROOT/'Kira_comparison/higher_scattering/references'/(c['id']+'.json.gz')
        p=HERE/'development'/(c['id']+'_parity.json.gz')
        if p.exists():continue
        r=workflow(c,read(ref)['masters'],'native',ref);save(p,r)
        print(json.dumps(dict(case=c['id'],action='parity',success=r['success'],seconds=r['complete_seconds'])),flush=True)
        assert r['success'] and r['reference_checked']
    for L,h,folder in [(3,224,'higher_references'),(4,225,'memory_references')]:
        c=cases.family('bubble_box',L,h);ref=ROOT/'Kira_comparison/higher_scattering'/folder/(c['id']+'.json.gz')
        basis=read(ref)['masters'];n=c['definition']['physical_propagators']
        for a,b in [('parity',[n+2,1,2])]:
            p=HERE/'development'/f'{c["id"]}_{a}.json.gz'
            if p.exists():continue
            r=attempt(c,basis,custom=b,reference=ref,timeout=600)
            save(p,compact(r));print(json.dumps(dict(case=c['id'],action=a,success=r['success'],status=r['status'],seconds=r['complete_seconds'],bounds=b)),flush=True)
            if a=='parity':assert r['success'] and r['reference_checked']
if __name__=='__main__':main()
