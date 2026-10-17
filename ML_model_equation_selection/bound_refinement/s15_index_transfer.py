"""Test the unchanged policy on target-index batches absent from training and validation."""
import json,statistics,time
import numpy as np
from s00_probe import HERE,BOUNDS,rt,inputs,save
from s03_refine import reference
from s07_reduce import reduce

DEST=HERE/'index_transfer'
def index_key(c):return (c['topology_group'],tuple(sorted(tuple(a) for a in c['targets'])))

def main():
 f=rt.read(HERE/'trained_model/freeze.json');old=rt.read(BOUNDS/'protocol.json')
 for name,h in f['source_hashes'].items():assert inputs.sha(HERE/name)==h
 for name,h in f['models'].items():assert inputs.sha(HERE/name)==h
 known={index_key(c) for split in ['training','validation'] for c in old['splits'][split]}
 individual={}
 for split in ['training','validation']:
  for c in old['splits'][split]:individual.setdefault(c['topology_group'],set()).update(tuple(a) for a in c['targets'])
 enabled={g for g,v in f['selection'].items() if v['option']}
 cases=[];excluded=[];seen=set();novel={}
 for h in [605,606]:
  for pattern in old['splits']['validation']:
   if pattern['topology_group'] not in enabled:continue
   c=inputs.case(pattern['topology_group'],h,pattern['shape'],'index_transfer');key=index_key(c)
   if key in known:
    excluded.append(dict(case=c['id'],reason='Index batch occurs in training or validation; excluded before timing.'));continue
   unseen=sum(tuple(a) not in individual[c['topology_group']] for a in c['targets'])
   if not unseen:
    excluded.append(dict(case=c['id'],reason='Every individual target index vector occurs in training or validation; excluded before timing.'));continue
   if (h,key) in seen:
    excluded.append(dict(case=c['id'],reason='Duplicate index batch at this profile; excluded before timing.'));continue
   seen.add((h,key));cases.append(c);novel[c['id']]=unseen
 protocol=dict(cases=cases,unseen_target_counts=novel,excluded_by_structure=excluded,profiles=[605,606],repetitions=3,methods=['off','learned'],freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'),script_sha256=inputs.sha(__file__),selection_rule='Validation-enabled graphs only. Require an index batch absent from training and validation, with at least one individual index vector also absent. Remove within-profile duplicates. No primary test timing enters this selection.')
 dest=DEST/'protocol.json'
 if dest.exists():assert rt.read(dest)==protocol
 else:inputs.write(dest,protocol)
 print('INDEX_TRANSFER_PROTOCOL',len(cases),'structural exclusions',len(excluded),flush=True)
 for c in cases:
  ref=reference(c)
  if ref is None:
   inputs.write(DEST/(c['id']+'_excluded.json'),dict(case=c['id'],reason='Reference or enlarged check failed within the common limits.'));continue
  for j in range(protocol['repetitions']):
   for method in (['off','learned'] if j%2==0 else ['learned','off']):
    path=DEST/(c['id']+'_'+method+f'_r{j}.json.gz')
    if path.exists():continue
    start=time.perf_counter();basis=rt.read(ref)['masters'];r=reduce(c,basis,method);rt.verify(r,ref)
    r['complete_seconds']=time.perf_counter()-start;r['index_batch_unseen']=True;save(path,r)
    print('INDEX_TRANSFER',c['id'],method,j,r['success'],r['complete_seconds'],r['fallbacks'],flush=True)
 summarize(protocol)

def summarize(p):
 matched=[];failed=[];incomplete=[];identity=[];runs=[];checks=0
 for c in p['cases']:
  group={m:[rt.read(path) for j in range(p['repetitions']) if (path:=DEST/(c['id']+'_'+m+f'_r{j}.json.gz')).exists()] for m in p['methods']}
  items=[r for rs in group.values() for r in rs];runs.extend(items)
  if not items:failed.append(c['id']);continue
  for r in items:
   if r['success']:
    rt.verify(r,HERE/'references'/(c['id']+'.json.gz'));assert r['success'] and r['reference_checked'];checks+=r['coefficient_checks']
   assert not r['reference_coefficients_supplied']
   for a in r['attempts']:
    assert a['policy']=='native' and not a.get('model') and not a.get('weights_sha256')
    assert a['binary_sha256']==inputs.sha(rt.BINARY)
    if r['method']=='off':assert a['equation_mode']=='off' and not a.get('equation_weights_sha256')
  if not all(len(rs)==p['repetitions'] and all(r['success'] for r in rs) for rs in group.values()):incomplete.append(c['id']);continue
  coeff=group['off'][0]['coefficients']
  if all(row=={t:'1'} for t,row in coeff.items()):identity.append(c['id']);continue
  times={m:[r['complete_seconds'] for r in rs] for m,rs in group.items()};seconds={m:statistics.median(v) for m,v in times.items()}
  matched.append(dict(case=c['id'],graph=c['topology_group'],seconds=seconds,times=times,active=any(r['option'] is not None for r in group['learned']),ratio=seconds['learned']/seconds['off']))
 assert matched
 totals={m:sum(c['seconds'][m] for c in matched) for m in p['methods']};graphs={}
 for g in sorted({c['graph'] for c in matched}):
  cs=[c for c in matched if c['graph']==g];ts={m:sum(c['seconds'][m] for c in cs) for m in p['methods']}
  graphs[g]=dict(cases=len(cs),totals=ts,ratio=ts['learned']/ts['off'])
 rng=np.random.default_rng(813);sums={m:np.zeros(5000) for m in p['methods']}
 for c in matched:
  idx=rng.integers(p['repetitions'],size=(5000,p['repetitions']))
  for m in p['methods']:sums[m]+=np.median(np.array(c['times'][m])[idx],axis=1)
 result=dict(complete=True,requested=len(p['cases']),matched=len(matched),cases=matched,graphs=graphs,totals=totals,ratio=totals['learned']/totals['off'],repeat_interval=np.percentile(sums['learned']/sums['off'],[2.5,97.5]).tolist(),reference_failed=failed,incomplete=incomplete,identity_only=identity,structural_exclusions=p['excluded_by_structure'],timed=len(runs),successful=sum(r['success'] for r in runs),coefficient_checks=checks,all_successful_outputs_exact=True,active=sum(c['active'] for c in matched),fallbacks={m:sum(r['fallbacks'] for r in runs if r['method']==m) for m in p['methods']},freeze_sha256=p['freeze_sha256'],protocol_sha256=inputs.sha(DEST/'protocol.json'))
 inputs.write(DEST/'summary.json',result);print('INDEX_TRANSFER_COMPLETE',json.dumps({k:v for k,v in result.items() if k not in ['cases','graphs','structural_exclusions']}),flush=True)

if __name__=='__main__':main()
