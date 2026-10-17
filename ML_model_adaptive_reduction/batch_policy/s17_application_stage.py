"""Run the fixed application subset while independent reserved tests finish."""
import subprocess,sys
from s00_runtime import HERE,ROOT,FILTER,rt,inputs

def main():
    assert sum((HERE/f'test_worker_{i}.json').exists() for i in range(4))>=1
    p=rt.read(HERE/'model_test/protocol.json')
    assert inputs.sha(HERE/'trained_model/freeze.json')==p['freeze_sha256']
    f=rt.read(HERE/'trained_model/freeze.json')
    for n,h in f['sources'].items():assert inputs.sha(HERE/n)==h,n
    assert inputs.sha(rt.BINARY)==f['native_sha256']
    assert inputs.sha(HERE/'fixed_inputs.json')==f['filter_source_sha256']
    assert inputs.sha(FILTER/'trained_model/freeze.json')==rt.read(HERE/'fixed_inputs.json')['source_freeze_sha256']
    for g in ['double_box','ladder3','nonplanar_box','massless4']:
        cases=[c for c in p['cases'] if c['topology_group']==g and '_h721_' in c['id'] and c['shape']=='all']
        for c in cases:assert (HERE/'references'/(c['id']+'.json.gz')).exists(),c['id']
    for script,args in [(HERE/'s16_deployment.py',['--prepare']),
                        (HERE/'s08_application.py',[]),
                        (ROOT/'ML_model_adaptive_reduction/massless_banana/s05_route_test.py',[])]:
        subprocess.run([sys.executable,str(script)]+args,check=True)
    inputs.write(HERE/'application_stage.json',dict(complete=True,
        scope='The predeclared application subset uses completed exact references and frozen decisions. No reserved timing outcomes enter its selection.',
        concurrent_native_workers_at_most=4))
    print('APPLICATION_STAGE_COMPLETE',flush=True)

if __name__=='__main__':main()
