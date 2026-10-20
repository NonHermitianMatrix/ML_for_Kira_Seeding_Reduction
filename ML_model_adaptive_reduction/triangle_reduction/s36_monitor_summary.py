"""Summarize the final matched collection and all failed native attempts."""
from s00_triangle_common import *
import statistics

def failures(result):
 return [a for b in result.get('blocks',[]) for a in b['result'].get('attempts',[]) if not a.get('success',False)]
def analyze(folder,protocol_name):
 raw=[read(f) for f in sorted((HERE/folder).glob('*.json.gz'))]
 matched=set.intersection(*[{r['repetition'] for r in raw if r['action']==a and r['verified']} for a in ['published','previous','integrated']]);assert matched
 rows=[r for r in raw if r['repetition'] in matched]
 complete=len(raw)==9 and all(r['verified'] for r in raw)
 if folder=='serial_test':assert complete
 rejected=[dict(action=r['action'],repetition=r['repetition'],seconds=r['seconds'],failed=r.get('failed',[])) for r in raw if not r['verified']]
 protocol=read(HERE/protocol_name);assert all(sha(HERE/n)==h for n,h in protocol['source_sha256'].items())
 stats={}
 for action in ['published','previous','integrated']:
  subset=[r for r in rows if r['action']==action];times=[r['seconds'] for r in subset];failed=[a for r in subset for q in r['results'].values() for a in failures(q['result'])]
  scans=[q['result'].get('native_storage_scan',{}) for r in subset for q in r['results'].values()]
  stats[action]=dict(times=times,median=statistics.median(times),mean=statistics.mean(times),minimum=min(times),maximum=max(times),inner_failures=len(failed),file_not_found_failures=sum('FileNotFoundError' in str(a.get('error','')) for a in failed),vanished_entries=sum(x.get('vanished_entries',0) for x in scans),scan_seconds=sum(x.get('seconds',0) for x in scans))
 p=read(HERE/'test_protocol.json.gz');groups={}
 for group in sorted({c['topology_group'] for c in p['cases']+p['regression']}):
  ids=[c['id'] for c in p['cases']+p['regression'] if c['topology_group']==group];sums={a:sum(statistics.median(r['results'][i]['seconds'] for r in rows if r['action']==a) for i in ids) for a in stats};groups[group]=dict(requests=len(ids),seconds=sums,ratio=sums['integrated']/sums['published'])
 out=dict(complete=True,comparison_completed=complete,matched_repetitions=sorted(matched),rejected_collections=rejected,recorded_application_results=sum(len(r['results']) for r in raw),recorded_verified_results=sum(len(r['results'])-len(r.get('failed',[])) for r in raw),protocol_sha256=sha(HERE/protocol_name),methods=stats,ratio=stats['integrated']['median']/stats['published']['median'],scanner_ratio=stats['integrated']['median']/stats['previous']['median'],groups=groups,application_results=sum(len(r['results']) for r in rows),checks=sum(r['checks'] for r in rows),equation_validation=read(HERE/'equation_validation_summary.json'),scanner_checks=read(HERE/'scanner_checks.json'))
 return out

def main():
 parallel=analyze('monitor_test','monitor_protocol.json');write(HERE/'monitor_parallel_summary.json',parallel)
 assert read(HERE/'serial_complete.json')['complete']
 out=analyze('serial_test','serial_protocol.json');out['execution']='One worker; rotating method order and reversed request order in the middle repetition.';out['parallel_comparison']=parallel
 write(HERE/'monitor_summary.json',out);(ROOT/'report/triangle_monitor_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['parallel_comparison','groups']}),flush=True)
if __name__=='__main__':main()
