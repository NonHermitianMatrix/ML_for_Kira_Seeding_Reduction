"""Compare shared-call applications on the same complete collection."""
from s00_triangle_common import *
from s04_triangle_measure import compare
import socket,signal,shutil

def main(w):
 assert os.environ.get('JOB_ID');p=read(HERE/'test_protocol.json.gz');assert all(sha(HERE/n)==s for n,s in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256']
 for rep in range(3):
  if rep%2!=w:continue
  cases=(p['cases']+p['regression'])[::(-1 if rep%2 else 1)]
  for action in ['previous','fixed','integrated'][::(-1 if rep%2 else 1)]:
   dest=HERE/'batch_test'/f'{rep}_{action}.json.gz'
   if dest.exists() and read(dest)['verified']:continue
   if dest.exists():r=read(dest);rows=r["results"];elapsed=r["seconds"]
   else:
    request=HERE/'requests'/f'batch{w}.json';out=HERE/'requests'/f'batch{w}.jsonl';write(request,cases);out.unlink(missing_ok=True)
    command=[sys.executable,str(PRIOR/'s37_batch.py'),'--cases',str(request),'--output',str(out),'--method','integrated'] if action=='previous' else [sys.executable,str(HERE/'s14_triangle_batch.py'),'--cases',str(request),'--output',str(out),'--action',action]
    start=time.perf_counter();process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
    try:_,err=process.communicate(timeout=360)
    except subprocess.TimeoutExpired:
     h=helper();lim=h.inputs.module('triangle_batch_limits',h.BLOCK/'s11_extension_test.py');pids=lim.descendants(process.pid)
     for pid in pids:
      try:os.kill(pid,signal.SIGKILL)
      except ProcessLookupError:pass
     try:os.killpg(process.pid,signal.SIGKILL)
     except ProcessLookupError:pass
     process.communicate()
     for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ.get('TMPDIR','/tmp'))]:
      for pid in pids:
       for q in root.glob(f'ml_kira_{pid}_*'):
        if q.is_dir():shutil.rmtree(q)
     raise RuntimeError('Collection reached its 360 second bound')
    assert out.exists() and out.stat().st_size<8*1024**2
    rows={r['case']:r for r in [json.loads(x) for x in out.read_text().splitlines()]};request.unlink();out.unlink();elapsed=time.perf_counter()-start
    r=dict(action=action,repetition=rep,seconds=elapsed,results=rows,host=socket.gethostname(),returncode=process.returncode,stderr_tail=err.decode(errors='replace')[-1200:],verified=False);write(dest,r)
   checks=0;failed=[]
   for c in cases:
    f=HERE/'test_references'/(c['id']+'.json.gz')
    if not f.exists():f=PRIOR/'test_references'/(c['id']+'.json.gz')
    ok,n=compare(c,rows.get(c['id'],{}).get('result',{}),read(f));checks+=n
    if not ok:failed.append(c['id'])
   r.update(verified=not failed,checks=checks,failed=failed);write(dest,r);print(rep,action,round(elapsed,4),len(failed),flush=True);assert not failed
 write(HERE/f'batch{w}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'test_protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
