"""Resume the frozen audit with optional legacy block-status fields handled."""
from s00_fast_common import *
from s08_test import measured,h

def main(worker):
 p=read(HERE/'protocol.json');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 assert read(HERE/f'timing_{worker}_complete.json')['complete']
 assert sha(Path(__file__))==read(HERE/'audit_recorder.json')['source_sha256']
 for i,c in enumerate(p['coverage']):
  if i%2!=worker:continue
  dest=HERE/'audit'/(c['id']+'.json')
  if dest.exists():continue
  order=['learned','previous'] if i%4<2 else ['previous','learned']
  rs={m:measured(c,m,0,None,'audit_records',20) for m in order}
  ok,n=h.compare(rs['learned'],rs['previous']) if all(r['success'] for r in rs.values()) else (False,0)
  row=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],indices=len(c['definition']['propagators']),paired_verified=ok,coefficient_checks=n,methods={m:dict(success=r['success'],status=r.get('status','not_recorded'),seconds=r['application_seconds'],block_statuses=[b['result'].get('status','not_recorded') for b in r.get('blocks',[])],routes=[b['result'].get('route') for b in r.get('blocks',[])]) for m,r in rs.items()})
  write(dest,row);print(json.dumps(dict(audit=c['id'],success={m:r['success'] for m,r in rs.items()},paired_verified=ok)),flush=True)
 write(HERE/f'worker_{worker}_complete.json',dict(complete=True,audit_recorder_sha256=sha(Path(__file__))))
if __name__=='__main__':main(int(sys.argv[1]))
