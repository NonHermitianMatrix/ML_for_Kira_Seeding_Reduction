"""Audit the new measurements, fixed models and report aggregates."""
import gzip,hashlib,json,math,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.load(gzip.open(p,'rt'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    d=json.loads((HERE/'summary.json').read_text())
    assert d==json.loads((ROOT/'report/higher_scattering_data.json').read_text())
    assert d['complete'] and d['ablation']['successful']==d['ablation']['trials']==420
    assert d['choice_controls']['trials']==96 and d['choice_controls']['all_exact']
    assert d['parity_trials']==7 and d['parity_all_exact']
    assert len(d['pilot'])==6 and len(d['higher_cases'])==8 and len(d['extended_cases'])==3 and len(d['memory_cases'])==3
    assert d['paused_study'] and (HERE/'pause.json').exists()
    for p,h in d['source_files'].items():assert sha(ROOT/p)==h,p
    protocol=json.loads((HERE/'ablation_protocol.json').read_text())
    for p,h in protocol['frozen_models'].items():assert sha(ROOT/p)==h,p
    build=json.loads((HERE/'build.json').read_text())
    assert sha(ROOT/'.tools/kira-workflow/kira')==build['parent_binary_sha256']
    assert sha(ROOT/'.tools/kira-source/src/kira/trivial_sym.cpp')==build['source_sha256']
    assert sha(ROOT/'.tools/kira-higher-scattering/kira')==build['binary_sha256']
    finished=failed=checks=0
    for folder in ['ablation_test','choice_control_test','higher_test','extended_test','memory_test']:
        for p in (HERE/folder).glob('*.json.gz'):
            r=read(p)
            if r['success']:
                assert r['reference_checked'],p
                assert not r.get('mismatches'),p
                finished+=1;checks+=r.get('coefficient_checks',0)
            else:failed+=1
    for protocol_name,folder in [('sector_protocol.json','higher_references'),('extended_protocol.json','extended_references'),('memory_protocol.json','memory_references')]:
        p=json.loads((HERE/protocol_name).read_text())
        for c in p['cases']:
            L=len(c['definition']['loop_momenta']);N=len(c['definition']['propagators']);n=c['definition']['physical_propagators']
            assert N==L*(L+7)//2 and c['definition']['rank']==N
            path=HERE/folder/(c['id']+'.json.gz')
            if not path.exists():
                assert folder=='memory_references' and d['paused_study']
                continue
            ref=read(path)
            if ref['success']:
                assert any(row and row!={t:'1'} for t,row in ref['coefficients'].items())
                assert all(all(v<=0 for v in master[n:]) for master in ref['masters'])
    for c in d['ablation']['cases']:
        assert all(v['successful']==v['trials']==3 for v in c['methods'].values())
    used=int(subprocess.check_output(['du','-s','--block-size=1',str(HERE)]).split()[0])
    assert used<16*1024**2
    audit=dict(complete=True,finished_test_reductions=finished,unsuccessful_test_reductions=failed,
         all_finished_outputs_exact=True,coefficient_checks=checks,unchanged_models=True,
         original_executable_preserved=True,sector_parity_checks=7,independent_family_rank_checks=True,
         scientific_data_local=False,retained_bytes=used,combined_upper_bytes=9850000000,
         summary_sha256=sha(HERE/'summary.json'))
    (HERE/'validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    (ROOT/'report/higher_scattering_validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit),flush=True)
if __name__=='__main__':main()
