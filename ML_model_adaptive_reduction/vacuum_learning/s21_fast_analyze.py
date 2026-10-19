"""Separate the final application change from the unchanged learned contribution."""
from s00_vac_common import *
from s12_analyze import compare

def main():
 p=read(HERE/'output_protocol.json.gz');assert all(read(HERE/f'output_test{w}_complete.json')['complete'] for w in [0,1])
 rows=[read(HERE/'output_test'/(c['id']+'.json.gz')) for c in p['cases']]
 exact=[r for r in rows if r['group']!='native'];native=[r for r in rows if r['group']=='native'];retained=[r for r in rows if 'previous' in r['times']]
 s=dict(complete=True,all=compare(rows,'fast','first'),exact=compare(exact,'fast','first'),native=compare(native,'fast','first'),retained_exact=compare(retained,'fast','previous'),ml=compare(native,'fast','fast_fixed'),checks=sum(r['checks'] for r in rows),rows=[{k:v for k,v in r.items() if k!='results'} for r in rows],protocol_sha256=sha(HERE/'output_protocol.json.gz'),model_sha256=sha(HERE/'trained_model/policy.json'))
 write(HERE/'output_summary.json',s);print(json.dumps({k:v for k,v in s.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
