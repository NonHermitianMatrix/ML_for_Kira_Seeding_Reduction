"""Audit all saved reductions and measure the additional cost effect of equation learning."""
import collections,json,statistics
import numpy as np
from s00_probe import HERE,ROOT,BOUNDS,rt,inputs

def summarize():
 f=rt.read(HERE/'trained_model/freeze.json');protocol=rt.read(HERE/'model_test/protocol.json');assert rt.read(HERE/'model_test/completion.json')['complete']
 assert inputs.sha(HERE/'trained_model/freeze.json')==protocol['freeze_sha256']
 for name,h in f['models'].items():assert inputs.sha(HERE/name)==h
 cases=[];identity=[];incomplete=[];excluded=[];runs=[];checks=0;maximum=0
 byid={c['id']:c for c in protocol['cases']}
 for c in protocol['cases']:
  group={m:[rt.read(p) for j in range(protocol['repetitions']) if (p:=HERE/'model_test'/(c['id']+'_'+m+f'_r{j}.json.gz')).exists()] for m in protocol['methods']}
  items=[r for v in group.values() for r in v];runs.extend(items)
  if not items:excluded.append(c['id']);continue
  for r in items:
   if r['success']:
    rt.verify(r,HERE/'references'/(c['id']+'.json.gz'));assert r['success'] and r['reference_checked'];checks+=r['coefficient_checks']
   for a in r['attempts']:
    assert a['policy']=='native' and not a.get('model') and not a.get('weights_sha256')
    assert a['binary_sha256']==inputs.sha(rt.BINARY)
    if r['method']=='off':assert a['equation_mode']=='off' and not a.get('equation_weights_sha256')
    maximum=max(maximum,a.get('peak_rss_bytes',0))
   if r['option']:
    assert r['option']==f['selection'][c['topology_group']]['option']
    weight=HERE/'trained_model'/(r['option']['name']+'.txt');assert r['attempts'][0]['equation_weights_sha256']==inputs.sha(weight)
  if not all(len(v)==protocol['repetitions'] and all(r['success'] for r in v) for v in group.values()):incomplete.append(c['id']);continue
  coeff=group['off'][0]['coefficients']
  if all(row=={t:'1'} for t,row in coeff.items()):identity.append(c['id']);continue
  times={m:[r['complete_seconds'] for r in v] for m,v in group.items()};seconds={m:statistics.median(v) for m,v in times.items()}
  active=any(r['option'] for r in group['learned'])
  cases.append(dict(id=c['id'],graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),shape=c['shape'],seconds=seconds,times=times,ratio=seconds['learned']/seconds['off'],active=active,fallbacks={m:sum(r['fallbacks'] for r in v) for m,v in group.items()},filter_seconds=sum(a.get('equation_metrics',{}).get('filter_seconds',0) for r in group['learned'] for a in r['attempts'])/protocol['repetitions'],candidate_calls=sum(a.get('equation_metrics',{}).get('candidate_calls',0) for r in group['learned'] for a in r['attempts'])/protocol['repetitions'],skipped=sum(a.get('equation_metrics',{}).get('construction_skipped_calls',0) for r in group['learned'] for a in r['attempts'])/protocol['repetitions']))
 graphs={}
 for g in inputs.GRAPHS:
  group=[c for c in cases if c['graph']==g]
  if group:
   totals={m:sum(c['seconds'][m] for c in group) for m in protocol['methods']};graphs[g]=dict(cases=len(group),totals=totals,ratio=totals['learned']/totals['off'],active=sum(c['active'] for c in group))
 totals={m:sum(c['seconds'][m] for c in cases) for m in protocol['methods']};active=[c for c in cases if c['active']];active_totals={m:sum(c['seconds'][m] for c in active) for m in protocol['methods']}
 rng=np.random.default_rng(714);ci={};draws={}
 # Draw paired repetition positions once per case. Use the same draws for all subsets.
 for c in cases:
  idx=rng.integers(protocol['repetitions'],size=(5000,protocol['repetitions']))
  draws[c['id']]={m:np.median(np.array(c['times'][m])[idx],axis=1) for m in protocol['methods']}
 def interval(cs):
  num=sum(draws[c['id']]['learned'] for c in cs);den=sum(draws[c['id']]['off'] for c in cs)
  return np.percentile(num/den,[2.5,97.5]).tolist()
 for name,cs in [('all',cases),('active',active)]:
  if cs:ci[name]=interval(cs)
 for g,v in graphs.items():v['repeat_interval']=interval([c for c in cases if c['graph']==g])
 train=rt.read(HERE/'trained_model/candidates.json');costs={s:sum(rt.read(p).get('seconds',rt.read(p).get('complete_seconds',0)) for p in (HERE/s).rglob('*.json.gz')) for s in ['training','validation','validation_cost','development']}
 out=dict(complete=True,requested=len(protocol['cases']),matched=len(cases),cases=cases,graphs=graphs,totals=totals,ratio=totals['learned']/totals['off'],active_matched=len(active),active_totals=active_totals,active_ratio=active_totals['learned']/active_totals['off'] if active else None,repeat_intervals=ci,reference_failed=excluded,identity_only=identity,incomplete=incomplete,timed=len(runs),successes=sum(r['success'] for r in runs),coefficient_checks=checks,all_successful_outputs_exact=True,fallbacks={m:sum(r['fallbacks'] for r in runs if r['method']==m) for m in protocol['methods']},peak_rss_mib=maximum/1024**2,training={k:v for k,v in train.items() if k!='candidates'},offline_seconds=sum(costs.values())+train['training_seconds']+rt.read(HERE/'trained_model/prediction_parity.json')['seconds'],cost_collection=costs,freeze_sha256=protocol['freeze_sha256'],enabled_graphs=[g for g,v in f['selection'].items() if v['option']],filter_seconds_per_active_request=sum(c['filter_seconds'] for c in active)/len(active) if active else 0,candidate_rejection_fraction=sum(c['skipped'] for c in active)/sum(c['candidate_calls'] for c in active) if sum(c['candidate_calls'] for c in active)>0 else 0)
 out['index_transfer']=rt.read(HERE/'index_transfer/summary.json')
 inputs.write(HERE/'summary.json',out);inputs.write(ROOT/'report/equation_refinement_data.json',out);print(json.dumps({k:v for k,v in out.items() if k not in ['cases','graphs','training']}),flush=True);plot(out)

def plot(d):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from s08_analyze import NAMES
 plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(9,4.8),gridspec_kw={'width_ratios':[1.6,1]},constrained_layout=True);g=list(d['graphs']);v=[d['graphs'][x]['ratio'] for x in g];colors=['#176b95' if d['graphs'][x]['active'] else '#899399' for x in g]
 ax=axes[0];
 for i,graph in enumerate(g):
  lo,hi=d['graphs'][graph]['repeat_interval'];ax.plot([lo,hi],[i,i],color=colors[i],linewidth=1.5)
 ax.scatter(v,np.arange(len(g)),c=colors,s=42);aux=[z for graph in g for z in d['graphs'][graph]['repeat_interval']];ax.set_yticks(np.arange(len(g)));ax.set_yticklabels([NAMES[x] for x in g]);ax.invert_yaxis();ax.axvline(1,color='.4',linestyle='--');ax.set_xlim(max(0,min(v+aux)-.05),max(1.04,max(v+aux)+.05));ax.set_xlabel('Learned / all-ML-disabled complete time');ax.set_title('Effect of learned filtering');ax.grid(axis='x',alpha=.2)
 ax=axes[1];vals=[d['active_totals']['off'],d['active_totals']['learned']];b=ax.bar([0,1],vals,color=['#899399','#176b95']);[ax.annotate(f'{v:.2f}',(i,v),xytext=(0,3),textcoords='offset points',ha='center',va='bottom') for i,v in enumerate(vals)];ax.set_xticks([0,1]);ax.set_xticklabels(['ML off','ML on']);ax.set_ylabel('Sum of median times (s)');ax.set_ylim(0,max(vals)*1.2 if max(vals)>0 else 1);ax.set_title(f"Filtering enabled\n({d['active_matched']} target batches)",fontsize=11);ax.grid(axis='y',alpha=.2)
 fig.savefig(ROOT/'report/paper_figures/equation_refinement_times.pdf',bbox_inches='tight');plt.close(fig)
if __name__=='__main__':summarize()
