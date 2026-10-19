"""Validate frozen comparisons, documentation, and bounded study output."""
from s00_loop_common import *
import subprocess

def main():
 spec=importlib.util.spec_from_file_location('loop_structure_validation',HERE/'s13_structure_checks.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);structural=module.main()
 p=read(HERE/'protocol.json.gz');s=read(HERE/'summary.json');assert s['complete']
 assert s['protocol_sha256']==sha(HERE/'protocol.json.gz')
 assert (ROOT/'report/loop_coverage13_appendix.tex').read_bytes()==(HERE/'loop_coverage13_appendix.tex').read_bytes()
 assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 for key,path in [('prior_model_sha256',PRIOR/'trained_model/policy.json'),('prior_basis_sha256',PRIOR/'basis_registry.json'),('prior_runtime_sha256',PRIOR/'s02_batch_runtime.py')]:assert sha(path)==p[key]
 assert s['coverage']['trees']['methods']['integrated']['completed']==39
 assert sum(r['checks'].get('checks',0) for r in s['rows'])==819
 assert len(s['rows'])==165
 assert not list((HERE/'requests').glob('*.json')) and not list(HERE.rglob('*.pending.gz'))
 for q in HERE.glob('s*.py'):compile(q.read_text(),str(q),'exec')
 q=ROOT/'report/s01_check_paper.py';z=q.read_text();marker='    result=dict(general_model_test_complete=True'
 extra='''    loop=json.loads((HERE/'loop_coverage13_data.json').read_text())
    assert loop['complete'] and len(loop['rows'])==165
    assert loop['coverage']['trees']['methods']['integrated']['completed']==39
    assert loop['gamma_sample_checks']==819
    assert 'app:loop-tree' in labels and 'sec:loop-tree-results' in labels
    for value in loop['comparisons'].values():
        if value['pairs']:assert abs(value['ratio']-value['new_seconds']/value['control_seconds'])<1e-12
    q=HERE.parent/'ML_model_adaptive_reduction/loop_coverage13/summary.json'
    if q.exists():assert json.loads(q.read_text())==loop
'''
 if "loop=json.loads((HERE/'loop_coverage13_data.json')" not in z:
  assert marker in z;q.write_text(z.replace(marker,extra+marker))
 subprocess.run(['make','-C',str(ROOT/'report'),'all'],check=True)
 subprocess.run([sys.executable,str(q)],check=True)
 size=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file());assert size<CAP
 result=dict(complete=True,structure_checks=structural,appendix_sha256=sha(HERE/'loop_coverage13_appendix.tex'),report_source_sha256={str(q.relative_to(ROOT/'report')):sha(q) for q in (ROOT/'report').glob('*') if q.suffix in ['.tex','.bib']},summary_sha256=sha(HERE/'summary.json'),protocol_sha256=sha(HERE/'protocol.json.gz'),source_sha256={q.name:sha(q) for q in HERE.glob('s*.py')},pdf_sha256={n:sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']},prior_models_unchanged=True,prior_basis_unchanged=True,final_entry_point='s02_runtime.py',study_allocated_bytes=size,native_verified_development_requests=s['development']['native_passes'],reserved_tree_gamma_checks=819,scope='Proof for the declared connected massless bubble-tree family; finite tests through thirteen loops; broader failed cases retained.')
 write(HERE/'validation.json',result);(ROOT/'report/loop_coverage13_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
