"""Run bounded native probes of connected higher-loop scattering families."""
import gzip,hashlib,importlib.util,json,os,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('scattering_native',ROOT/'ML_model_workflow_selection/thread_policy/s02_native_runner.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
os.environ.update(KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-workflow/kira'),KIRA_RUNTIME_SCRATCH='node',KIRA_EPHEMERAL_DB='1',KIRA_EQ_MODE='off')

def save(path,r):
    data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
    used=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
    assert used+len(data)+4096<16*1024**2,(used,len(data))
    path.parent.mkdir(exist_ok=True);path.write_bytes(data)

def main():
    protocol=json.loads((HERE/'protocol.json').read_text())
    for c in protocol['cases']:
        p=HERE/'development'/(c['id']+'.json.gz')
        if p.exists():continue
        n=c['definition']['physical_propagators']
        # At this stage the output is a probe, not a verified master reduction.
        r=native.run(c,c['size'],'native',HERE/'unused',timeout=120,margin=0,archive=False,records=False,
                     scratch_cap=16*1024**2,bounds=[n+1,1,1],ordering=1)
        r['verified_reduction']=False
        r['nonidentity_targets']=sum(row!={t:'1'} for t,row in r.get('coefficients',{}).items())
        save(p,r)
        print(json.dumps({k:r.get(k) for k in ['case','status','success','complete_seconds','peak_rss_bytes','peak_scratch_bytes','nonidentity_targets','error']}),flush=True)
    print('PILOT_COMPLETE',flush=True)
if __name__=='__main__':main()
