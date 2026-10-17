"""Check the existing higher-loop native and analytic paths through the new API."""
import subprocess
from s00_engine import *

def main():
 protocol=rt.read(OLD/'integration_test/protocol.json');cases=[c for c in protocol['cases'] if c['topology_group']=='massless4' or c['id'].startswith('analytic_')]
 assert len(cases)==2
 for c in cases:
  refp=OLD/'integration_test/analytic_reference.json' if c['id'].startswith('analytic_') else ROOT/'ML_model_adaptive_reduction/batch_policy/references'/(c['id']+'.json.gz')
  ref=rt.read(refp);assert ref['success']
  for rep in range(2):
   for method in ['previous','learned']:
    outpath=HERE/'compatibility_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
    if outpath.exists():continue
    with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'],prefix='joint_compat_') as td:
     cp=Path(td)/'case.json';bp=Path(td)/'basis.json';out=Path(td)/'out.json.gz'
     cp.write_text(json.dumps({k:c[k] for k in ['id','size','definition','targets']}));bp.write_text(json.dumps(ref['masters']))
     tick=time.perf_counter();p=subprocess.run([sys.executable,str(HERE/'s05_application.py'),'--case',str(cp),'--basis',str(bp),'--output',str(out),'--method',method,'--no-reuse'],capture_output=True,text=True,timeout=180)
     assert p.returncode==0,p.stderr[-1800:]
     r=rt.read(out);rt.verify(r,refp);assert r['success'] and r['reference_checked']
     r.update(case=c['id'],method=method,repetition=rep,process_complete_seconds=time.perf_counter()-tick);save(outpath,r)
 save(HERE/'compatibility_test/summary.json',dict(complete=True,all_exact=True,requests=8,cases=[c['id'] for c in cases],scope='Existing four-loop native and eight-loop analytic requests; checks preservation of earlier paths.'))

if __name__=='__main__':main()
