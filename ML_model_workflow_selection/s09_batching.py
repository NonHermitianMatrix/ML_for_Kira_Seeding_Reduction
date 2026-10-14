"""Compare separate requests and exact joint reduction with frozen models."""
import copy,json,statistics,time
from s05_study import HERE,ROOT,study,read,write,save,workflow,choose,sha,attempt
from s08_reduce import select

def prepare():
 m=json.loads((HERE/'cases.json').read_text());groups=[]
 for c in m['cases']:
  if c['split']!='reserved':continue
  if '_p44_' in c['id'] and c['size']>4 or c['definition']['invariants']:
   c=copy.deepcopy(c);c['id']='joint_'+c['id'];c['group']=c['id']
   if c['topology_group']=='one_mass_box' and c['definition']['invariants']:
    t=[1]*4;t[3]=3;c['targets'].append(t);c['size']=2
   cut=max(1,c['size']//2);assert cut<c['size'];groups.append(dict(case=c,cut=cut))
 p=HERE/'request_batching/cases.json';r=dict(groups=groups,repetitions=5,methods=['separate_native','joint_native','joint_fixed','joint_learned'],
  scope='Two disjoint target requests with identical integral definitions, submitted together. Shared reserved parameter points; no further model fitting.')
 if p.exists():assert json.loads(p.read_text())==r
 else:write(p,r)
 return r

def main():
 plan=prepare();f=json.loads((HERE/'trained_model/freeze.json').read_text());out=HERE/'request_batching';summary=[]
 manifest=json.loads((HERE/'cases.json').read_text())
 for group in plan['groups']:
  c=group['case'];ref=out/(c['id']+'_reference.json.gz')
  if not ref.exists():
   r=attempt(c,None,'native',margin=1);assert r['success'];save(ref,r)
  basis=read(ref)['masters'];parts=[]
  for index,targets in enumerate([c['targets'][:group['cut']],c['targets'][group['cut']:]]):
   child=dict(c,id=c['id']+f'_part{index}',targets=targets,size=len(targets));parts.append(child)
  for rep in range(5):
   methods=plan['methods'];order=methods[rep%4:]+methods[:rep%4]
   for method in order:
    dest=out/f'{c["id"]}_{method}_{rep}.json.gz'
    if dest.exists():continue
    begin=time.perf_counter();runs=[]
    requests=copy.deepcopy(parts)
    if method=='separate_native':
     for child in requests:runs.append(workflow(child,ref,'native'))
     coefficients={k:v for r in runs for k,v in r['attempts'][-1].get('coefficients',{}).items()}
    else:
     unique=list(dict.fromkeys(tuple(t) for req in requests for t in req['targets']))
     joint=dict(c,targets=[list(t) for t in unique],size=len(unique))
     cfg='native' if method=='joint_native' else 'fixed' if method=='joint_fixed' else select(joint,f,manifest)[0]
     runs=[workflow(joint,ref,cfg)];coefficients=runs[0]['attempts'][-1].get('coefficients',{})
    partition=[{','.join(map(str,t)):coefficients[','.join(map(str,t))] for t in req['targets']} for req in requests]
    success=all(r['success'] for r in runs)
    result=dict(case=c['id'],method=method,repetition=rep,success=success,complete_seconds=time.perf_counter()-begin,
      workflows=runs,partition_coefficients=partition,fallback_count=sum(r['fallback_count'] for r in runs),solver_calls=sum(len(r['attempts']) for r in runs))
    save(dest,result);assert success
    print(json.dumps(dict(stage='batching',case=c['id'],method=method,success=success,seconds=result['complete_seconds'])),flush=True)
  times={method:statistics.median(read(out/f'{c["id"]}_{method}_{r}.json.gz')['complete_seconds'] for r in range(5)) for method in plan['methods']}
  summary.append(dict(case=c['id'],topology=c['topology_group'],symbolic=bool(c['definition']['invariants']),targets=c['size'],median_seconds=times,
   ratios={k:v/times['separate_native'] for k,v in times.items()},learned_to_joint_native=times['joint_learned']/times['joint_native'],learned_to_joint_fixed=times['joint_learned']/times['joint_fixed']))
 import math,numpy as np
 kinds=sorted({r['topology'] for r in summary});bykind={k:{} for k in kinds}
 for k in kinds:
  rows=[r for r in summary if r['topology']==k]
  for method in plan['methods'][1:]:bykind[k][method]=math.exp(statistics.mean(math.log(r['ratios'][method]) for r in rows))
  for method in ['learned_to_joint_native','learned_to_joint_fixed']:bykind[k][method]=math.exp(statistics.mean(math.log(r[method]) for r in rows))
 aggregate={};rng=np.random.default_rng(48014);ids=rng.integers(0,len(kinds),(10000,len(kinds)))
 for method in list(bykind[kinds[0]]):
  x=np.log([bykind[k][method] for k in kinds]);aggregate[method]=dict(ratio=float(np.exp(x.mean())),interval=np.quantile(np.exp(x[ids].mean(axis=1)),[.025,.975]).tolist())
 result=dict(complete=True,all_exact=True,workflows=len(summary)*20,cases=summary,by_topology=bykind,aggregate=aggregate,
  freeze_sha256=sha(HERE/'trained_model/freeze.json'),protocol_sha256=sha(out/'cases.json'),scope=plan['scope'])
 write(out/'summary.json',result);write(ROOT/'report/batching_figure_data.json',result)
 print(json.dumps(dict(stage='batching_complete',aggregate=aggregate)),flush=True)
if __name__=='__main__':main()
