"""Summarize matched full times, completion, and separate learned effects."""
from s00_light_common import *

def main():
 p=read(HERE/'protocol.json.gz');assert all(read(HERE/f'test{i}.json')['complete'] for i in [0,1]);rows=[read(HERE/'model_test'/(c['id']+'.json.gz')) for c in p['cases']];compare=load('lightlike_comparison',PRIOR/'s12_analyze.py').compare
 groups={g:compare([r for r in rows if r['group']==g]) for g in sorted({r['group'] for r in rows})};native=[r for r in rows if r['group']=='native'];model=read(HERE/'trained_model/policy.json')
 summary=dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz'),all=compare(rows),groups=groups,native_ml=compare(native,old='all_fixed'),checks=sum(r['checks'] for r in rows),reference_failures=sum(not r['reference_success'] for r in rows),native_model_enabled=model['enabled'],native_model_used=sum(r['results']['integrated'].get('model_used',False) for r in native),rows=[{k:v for k,v in r.items() if k not in ['results','reference']} for r in rows])
 summary['native_failure_gates']={reason:sum((r['results']['integrated'].get('failure_gate') or {}).get('reason')==reason for r in native) for reason in ['admitted','predicted_failure_risk','outside_training_range','model_disabled']}
 summary['native_failed_applications']={method:sum(sum(not v for v in r['success'][method]) for r in native) for method in ['integrated','all_fixed','previous']}
 write(HERE/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
