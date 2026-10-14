"""Check reserved records and plot complete reduction-time comparisons."""
import collections,json,math,os,statistics
import numpy as np
import s05_fit as model
w=model.w
METHODS=['native','previous','family_fixed','selected']
NAMES={'sunrise':'Sunrise','double_box':'Planar box','vacuum3':'Vacuum','ladder3':'Ladder','nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Virtuality box'}
def main():
 p=json.loads((w.HERE/'protocol.json').read_text());f=json.loads((w.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 counters={m:collections.Counter() for m in METHODS}
 prediction_times=[]
 cases=[];count=0;checks=0;apps=0;app_checks=0;hosts=set();peaks=collections.Counter();fallbacks=collections.Counter();choices=collections.Counter()
 stages={m:collections.Counter() for m in METHODS}
 for c in (c for c in p['cases'] if c['split']=='reserved'):
  times={};decisions={};case_hosts=set()
  for method in METHODS:
   rows=[w.read(w.HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz') for rep in range(5)]
   assert all(r['success'] and r['reference_checked'] and r['basis_admitted'] and not r['mismatches'] for r in rows)
   times[method]=statistics.median(r['complete_seconds'] for r in rows);decisions[method]=sorted({r['configuration'] for r in rows})
   for r in rows:
    count+=1;checks+=r['coefficient_checks'];fallbacks[method]+=r['fallback_count']
    if method=='selected':
     choices[r['configuration']]+=1
     prediction_times.append(r['ordering_prediction_seconds'])
    for a in r['attempts']:
     case_hosts.add(a['worker_host']);hosts.add(a['worker_host'])
     peaks['rss_bytes']=max(peaks['rss_bytes'],a['peak_rss_bytes']);peaks['scratch_bytes']=max(peaks['scratch_bytes'],a['peak_scratch_bytes'])
     stages[method].update(a.get('stage_totals',{}))
     counters[method].update({key:sum(vals) for key,vals in a.get('counters',{}).items()})
  assert len(case_hosts)==1,(c['id'],case_hosts)
  app=w.read(w.HERE/'model_test'/f'{c["id"]}_application.json.gz')
  assert app['success'] and app['all_exact'] and app['reference_coefficients_supplied'] is False
  apps+=1;app_checks+=app['independent_exact_checks']
  ratios=dict(selected_to_native=times['selected']/times['native'],selected_to_previous=times['selected']/times['previous'],selected_to_fixed=times['selected']/times['family_fixed'],previous_to_native=times['previous']/times['native'],fixed_to_previous=times['family_fixed']/times['previous'])
  cases.append(dict(case=c['id'],topology=c['topology_group'],group=c['group'],shape=c['shape'],loops=len(c['definition']['loop_momenta']),targets=c['size'],median_seconds=times,ratios=ratios,decisions=decisions))
 keys=list(cases[0]['ratios']);by_kind={};ranges={}
 for k in w.st.KINDS:
  cs=[c for c in cases if c['topology']==k]
  by_kind[k]={m:model.geo([c['ratios'][m] for c in cs]) for m in keys}
  ranges[k]={m:[min(vals),max(vals)] for m in keys for vals in [[model.geo([c['ratios'][m] for c in cs if c['group']==g]) for g in sorted({c['group'] for c in cs})]]}
 rng=np.random.default_rng(14102026);ids=rng.integers(0,7,(10000,7));aggregate={}
 for m in keys:
  x=np.log([by_kind[k][m] for k in w.st.KINDS]);aggregate[m]=dict(ratio=float(np.exp(x.mean())),interval=np.quantile(np.exp(x[ids].mean(axis=1)),[.025,.975]).tolist())
 trained=json.loads((w.HERE/'trained_model/candidates.json').read_text())
 summary=dict(complete=True,all_exact=True,workflows=count,applications=apps,coefficient_entries_checked=checks,application_coefficient_checks=app_checks,
  cases=cases,by_topology=by_kind,profile_ranges=ranges,aggregate=aggregate,fallbacks=dict(fallbacks),selected_choices=dict(choices),
  policies={k:{key:v[key] for key in ['enabled','validation_control','best_fixed','validation']}|dict(model=v['model']['name']) for k,v in f['policies'].items()},
  configurations=p['configurations'],split_counts={s:sum(c['split']==s for c in p['cases']) for s in ['training','validation','reserved']},model_candidates=sum(len(v['models']) for v in trained['families'].values()),
  label_seconds={s:sum(w.read(q)['complete_seconds'] for q in (w.HERE/s).glob('*.json.gz')) for s in ['training','validation']},fitting_seconds=trained['training_seconds'],
  ordering_prediction_seconds=dict(median=statistics.median(prediction_times),maximum=max(prediction_times),total=sum(prediction_times)),operation_counters={k:dict(v) for k,v in counters.items()},worker_hosts=sorted(hosts),resource_peaks=dict(peaks),stage_totals={k:dict(v) for k,v in stages.items()},freeze_sha256=model.sha(w.HERE/'trained_model/freeze.json'),
  timing='Input preparation, model decision, exact Kira reduction, any basis conversion, independent exact checks, cleanup and all retries. The caller and model are already loaded; each attempt starts fresh Kira. Offline reference discovery, training and record writing are excluded.',
  scope=p['scope'],uncertainty='Graph-weighted descriptive bootstrap interval. Graph bars show the range across two reserved kinematic profiles and are not significance intervals.')
 assert count==720 and apps==36
 w.write(w.HERE/'model_test/summary.json',summary);w.write(w.ROOT/'report/ordering_policy_figure_data.json',summary)
 os.environ.setdefault('MPLCONFIGDIR',os.path.join(os.environ.get('TMPDIR','/tmp'),'kira_order_mpl'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(8.2,4.5),sharey=True)
 specs=[[('fixed_to_previous','Fixed per graph','#c68428'),('selected_to_previous','New selected route','#21826a')],[('previous_to_native','Previous route','#4879a1'),('selected_to_native','New selected route','#21826a')]]
 for ax,items in zip(axes,specs):
  limits=[1.]
  for j,(key,label,color) in enumerate(items):
   x=np.array([by_kind[k][key] for k in w.st.KINDS]);bounds=np.array([ranges[k][key] for k in w.st.KINDS]);limits.extend(bounds.flatten())
   ax.errorbar(x,np.arange(7)+(j-.5)*.22,xerr=np.maximum(0,np.vstack([x-bounds[:,0],bounds[:,1]-x])),fmt='o',ms=4.5,capsize=2,color=color,label=label)
  ax.axvline(1,color='.4',ls='--',lw=1);ax.grid(axis='x',alpha=.2);pad=max(.04,.08*(max(limits)-min(limits)));ax.set_xlim(max(0,min(limits)-pad),max(limits)+pad)
  ax.legend(loc='best',fontsize=8,frameon=False)
 axes[0].set_yticks(range(7));axes[0].set_yticklabels([NAMES[k] for k in w.st.KINDS]);axes[0].invert_yaxis()
 axes[0].set_title('Change from the previous route');axes[0].set_xlabel('Full time / previous route time')
 axes[1].set_title('Comparison with native choices');axes[1].set_xlabel('Full time / native time')
 fig.tight_layout();fig.savefig(w.ROOT/'report/paper_figures/ordering_policy.pdf',bbox_inches='tight');plt.close(fig)
 w.emit(stage='analysis',workflows=count,aggregate=aggregate,policies=summary['policies'])
if __name__=='__main__':main()
