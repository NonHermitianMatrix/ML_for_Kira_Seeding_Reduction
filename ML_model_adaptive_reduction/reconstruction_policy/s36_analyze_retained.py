"""Keep the inherited-ML contribution separate from reconstruction gains."""
from s00_reconstruction_common import *
from s26_analyze import comparison

def main():
 p=read(HERE/'retained_protocol.json.gz')
 for w in [0,1]:assert read(HERE/f'retained{w}_complete.json')['protocol_sha256']==sha(HERE/'retained_protocol.json.gz')
 rows=[read(HERE/'retained_ml_test'/(c['id']+'.json.gz')) for c in p['cases']]
 stat=comparison(rows,'retained_fixed','retained_ml')
 groups={g:comparison([r for r in rows if r['topology']==g],'retained_fixed','retained_ml') for g in sorted({r['topology'] for r in rows})}
 out=dict(complete=True,protocol_sha256=sha(HERE/'retained_protocol.json.gz'),all=stat,structures=groups,checks=sum(r['checks'] for r in rows),changed_seed_sequences=sum(r['actions']['retained_ml']!=r['actions']['retained_fixed'] for r in rows),rows=[{k:v for k,v in r.items() if k not in ['results','failed_applications']} for r in rows])
 write(HERE/'retained_summary.json',out);print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
