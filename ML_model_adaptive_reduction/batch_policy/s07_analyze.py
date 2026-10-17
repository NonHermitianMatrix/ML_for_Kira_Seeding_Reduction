"""Audit exact answers and compare all completed and incomplete target batches."""
import collections,json,statistics
import numpy as np
from s00_runtime import HERE,ROOT,rt,inputs

def main():
 p=rt.read(HERE/'model_test/protocol.json');f=rt.read(HERE/'trained_model/freeze.json');assert inputs.sha(HERE/'trained_model/freeze.json')==p['freeze_sha256']
 assert rt.read(HERE/'model_test/completion.json')['complete']
 for n,h in f['sources'].items():assert inputs.sha(HERE/n)==h,n
 matched=[];failed=[];incomplete=[];identity=[];runs=[];checks=0;peak=0;batch_hosts={}
 bymethod={m:dict(requested=0,successful=0,seconds=0.,fallbacks=0) for m in p['methods']}
 for c in p['cases']:
  ref=HERE/'references'/(c['id']+'.json.gz')
  if not ref.exists() or not rt.read(ref)['success']:failed.append(c['id']);continue
  data={m:[rt.read(HERE/'model_test'/(c['id']+'_'+m+f'_r{j}.json.gz')) for j in range(p['repetitions'])] for m in p['methods']}
  hosts={a['worker_host'] for rows in data.values() for r in rows for a in r['attempts']}
  assert len(hosts)==1,(c['id'],hosts)
  batch_hosts[c['id']]=next(iter(hosts))
  for method,rows in data.items():
   for r in rows:
    runs.append(r);v=bymethod[method];v['requested']+=1;v['successful']+=r['success'];v['seconds']+=r['complete_seconds'];v['fallbacks']+=r['fallbacks']
    assert not r['reference_coefficients_supplied']
    if r['success']:
     rt.verify(r,ref);assert r['success'] and r['reference_checked'];checks+=r['coefficient_checks']
    for a in r['attempts']:
     assert a['policy']=='native' and not a.get('model') and not a.get('weights_sha256')
     assert a['binary_sha256']==f['native_sha256']
     if method in ['off','fixed_off']:assert a.get('equation_mode','off')=='off' and not a.get('equation_weights_sha256')
     peak=max(peak,a.get('peak_rss_bytes',0))
  if not all(r['success'] for rows in data.values() for r in rows):
   incomplete.append(dict(case=c['id'],success={m:sum(r['success'] for r in rows) for m,rows in data.items()},seconds={m:[r['complete_seconds'] for r in rows] for m,rows in data.items()}));continue
  if all(row=={t:'1'} for t,row in data['off'][0]['coefficients'].items()):identity.append(c['id']);continue
  times={m:[r['complete_seconds'] for r in rows] for m,rows in data.items()}
  reported_work={m:{key:statistics.median(sum(sum(a.get('counters',{}).get(key,[])) for a in r['attempts']) for r in rows) for key in ['generated_equations','selected_equations','forward_insertions']} for m,rows in data.items()}
  active=any(a.get('equation_mode')=='learned' for r in data['learned'] for a in r['attempts'])
  matched.append(dict(case=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),size=c['size'],pattern=c['shape'],times=times,seconds={m:statistics.median(v) for m,v in times.items()},choice=data['learned'][0]['action'],decisions=[r['decision_seconds'] for r in data['learned']],equation_filter_active=active,reported_work=reported_work))
 assert matched
 rng=np.random.default_rng(813);draws={}
 for c in matched:
  ix=rng.integers(p['repetitions'],size=(5000,p['repetitions']));draws[c['case']]={m:np.median(np.array(c['times'][m])[ix],axis=1) for m in p['methods']}
 def aggregate(cs):
  total={m:sum(c['seconds'][m] for c in cs) for m in p['methods']};intervals={}
  for m in ['previous','off','fixed','fixed_off']:
   ratio=sum(draws[c['case']]['learned'] for c in cs)/sum(draws[c['case']][m] for c in cs);intervals[m]=np.percentile(ratio,[2.5,97.5]).tolist()
  work={m:{key:sum(c['reported_work'][m][key] for c in cs) for key in ['generated_equations','selected_equations','forward_insertions']} for m in p['methods']}
  return dict(batches=len(cs),totals=total,ratios={m:total['learned']/total[m] for m in ['previous','off','fixed','fixed_off']},repeat_intervals=intervals,reported_work=work)
 groups={g:aggregate([c for c in matched if c['graph']==g]) for g in sorted({c['graph'] for c in matched})};loops={str(l):aggregate([c for c in matched if c['loops']==l]) for l in sorted({c['loops'] for c in matched})}
 training=rt.read(HERE/'training/protocol.json')['cases'];validation=rt.read(HERE/'validation/protocol.json')['cases'];known={(c['topology_group'],tuple(sorted(map(tuple,c['targets'])))) for c in training+validation}
 repeated=[c['id'] for c in p['cases'] if (c['topology_group'],tuple(sorted(map(tuple,c['targets'])))) in known]
 cost={s:sum(rt.read(q).get('complete_seconds',0.) for q in (HERE/s).glob('*.json.gz')) for s in ['development','training','validation','validation_off']}
 from s04_fit import records
 validation=records('validation')
 retrospective=sum(min(r['times']) for r in validation)
 out=aggregate(matched)|dict(complete=True,requested=len(p['cases']),matched=matched,graphs=groups,loops=loops,reference_failed=failed,incomplete=incomplete,identity_only=identity,timed=len(runs),successful=sum(r['success'] for r in runs),coefficient_checks=checks,controls_disable_all_ml=True,all_successful_outputs_exact=True,peak_rss_mib=peak/1024**2,completion=bymethod,offline_costs=cost,fitting_seconds=f['fitting_seconds'],selector_enabled=f['enabled'],selected=f['selected'],training_cases=f['training_cases'],validation_cases=f['validation_cases'],repeated_index_batches=repeated,freeze_sha256=p['freeze_sha256'],decision_median_seconds=statistics.median(v for c in matched for v in c['decisions']),choices=dict(collections.Counter(c['choice'] for c in matched)))
 out['validation_candidate_bound']=dict(batches=len(validation),minimum_recorded_cost=retrospective,fixed_cost=f['validation_fixed_cost'],ratio=retrospective/f['validation_fixed_cost'],meaning='Sum of each validation batch\'s smallest recorded candidate cost. This uses future timing knowledge and is not a deployable result.')
 out['batch_hosts']=batch_hosts
 active=[c for c in matched if c['equation_filter_active']]
 out['equation_filter_active']=aggregate(active) if active else dict(batches=0)
 if (HERE/'interruption_recovery.json').exists():
  recovery=rt.read(HERE/'interruption_recovery.json');archived=[]
  for batch in recovery['archived_batches']:
   for entry in batch['trials']:
    path=HERE/entry['archived'];assert inputs.sha(path)==entry['sha256']
    r=rt.read(path);assert not r['reference_coefficients_supplied']
    if r['success']:
     rt.verify(r,HERE/'references'/(batch['case']+'.json.gz'));assert r['success'] and r['reference_checked']
    archived.append(r)
  out['interruption_recovery']=dict(archived_trials=len(archived),archived_successes=sum(r['success'] for r in archived),
    archived_coefficient_checks=sum(r.get('coefficient_checks',0) for r in archived),
    archived_seconds=sum(r['complete_seconds'] for r in archived),
    retained_complete_batches=len(recovery['retained_complete_cases']),
    resumed_batches=len(recovery['remaining_cases']),
    same_host_per_comparison_batch=True,excluded_from_ratios=True,
    assignment_basis=recovery['assignment_basis'],models_changed=False,scientific_protocol_changed=False)
 inputs.write(HERE/'summary.json',out);inputs.write(ROOT/'report/batch_policy_data.json',out);plot(out)
 print('SUMMARY',json.dumps({k:v for k,v in out.items() if k not in ['matched','graphs','incomplete','selected','repeated_index_batches']}),flush=True)

def plot(d):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axs=plt.subplots(1,2,figsize=(7.8,4.7),constrained_layout=True)
 names={'sunrise':'Sunrise (2 loops)','double_box':'Planar box (2)','vacuum3':'Vacuum (3)','ladder3':'Ladder (3)','nonplanar_box':'Nonplanar box (2)','pentagon':'Pentagon (1)','one_mass_box':'Virtuality box (1)','bubble_box3':'Bubble box (3)','bubble_box4':'Bubble box (4)','massless4':'Propagator (4)'}
 for ax,base,title in zip(axs,['previous','fixed_off'],['Effect on the previous\ncomplete workflow','Comparison with\nall models disabled']):
  points=[];bounds=[]
  for i,(g,r) in enumerate(d['graphs'].items()):
   lo,hi=r['repeat_intervals'][base];v=r['ratios'][base];ax.plot([lo,hi],[i,i],color='#1d6c91',lw=1.6);ax.scatter([v],[i],color='#1d6c91',s=34);points.append(v);bounds.extend([lo,hi])
  ax.set_yticks(range(len(d['graphs'])));ax.set_yticklabels([names[g] for g in d['graphs']]);ax.invert_yaxis();ax.axvline(1,color='.4',ls='--');ax.set_xlim(max(0,min(bounds+points)-.05),max(1.04,max(bounds+points)+.05));ax.set_xlabel('Selected / control complete time');ax.set_title(title);ax.grid(axis='x',alpha=.2)
  if ax is axs[1]:ax.tick_params(axis='y',left=False,labelleft=False)
 fig.savefig(ROOT/'report/paper_figures/batch_policy_times.pdf',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
