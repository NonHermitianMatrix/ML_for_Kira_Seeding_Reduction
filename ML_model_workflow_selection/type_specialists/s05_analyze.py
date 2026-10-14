"""Validate all new tests and plot graph-specific complete-time results."""
import collections,json,math,os,statistics
from pathlib import Path
import numpy as np
import s04_train_test as model
st=model.st
METHODS=['native','deterministic','family_fixed','learned']
def main():
 manifest=json.loads((st.HERE/'protocol.json').read_text());f=json.loads((st.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 cases=[];workflows=0;checks=0;apps=0;app_checks=0;fallbacks=collections.Counter();choices=collections.Counter();reasons=collections.Counter();hosts=set();peaks=collections.Counter();stages={m:collections.Counter() for m in METHODS}
 for c in manifest['cases']:
  if c['split']!='reserved':continue
  times={};first={};decisions={}
  for m in METHODS:
   rows=[st.read(st.HERE/'model_test'/f'{c["id"]}_{m}_{i}.json.gz') for i in range(5)]
   assert all(r['success'] for r in rows)
   times[m]=statistics.median(r['complete_seconds'] for r in rows);first[m]=sum(r['fallback_count']==0 for r in rows);decisions[m]=sorted({r['configuration'] for r in rows})
   for r in rows:
    workflows+=1;fallbacks[m]+=r['fallback_count'];a=r['attempts'][-1];assert a['reference_checked']
    checks+=sum(len(row) for row in a['coefficients'].values())
    if m=='learned':choices[r['configuration']]+=1;reasons[r['selection_reason']]+=1
    for a in r['attempts']:
     hosts.add(a['worker_host']);peaks['rss_bytes']=max(peaks['rss_bytes'],a['peak_rss_bytes']);peaks['scratch_bytes']=max(peaks['scratch_bytes'],a['peak_scratch_bytes'])
     stages[m].update(a.get('stage_totals',{}))
  app=st.read(st.HERE/'model_test'/f'{c["id"]}_application.json.gz')
  assert app['success'] and app['reference_coefficients_withheld'] and app['all_exact'];apps+=1;app_checks+=app['independent_exact_checks']
  cases.append(dict(case=c['id'],group=c['group'],topology=c['topology_group'],shape=c['shape'],loops=len(c['definition']['loop_momenta']),targets=c['size'],median_seconds=times,first_attempts=first,decisions=decisions,
   ratios={m:times[m]/times['native'] for m in METHODS[1:]},learned_to_deterministic=times['learned']/times['deterministic'],learned_to_family_fixed=times['learned']/times['family_fixed']))
 keys=METHODS[1:]+['learned_to_deterministic','learned_to_family_fixed'];by_kind={};intervals={}
 for k in st.KINDS:
  cs=[c for c in cases if c['topology']==k];by_kind[k]={};intervals[k]={}
  for m in keys:
   ratios=[c['ratios'][m] if m in METHODS else c[m] for c in cs];by_kind[k][m]=model.geo(ratios)
   # Two fresh kinematic groups: report their range, not a confidence claim.
   grouped=[model.geo([c['ratios'][m] if m in METHODS else c[m] for c in cs if c['group']==g]) for g in sorted({c['group'] for c in cs})]
   intervals[k][m]=[min(grouped),max(grouped)]
 rng=np.random.default_rng(1402026);ids=rng.integers(0,len(st.KINDS),(10000,len(st.KINDS)));aggregate={}
 for m in keys:
  x=np.log([by_kind[k][m] for k in st.KINDS]);interval=np.quantile(np.exp(x[ids].mean(axis=1)),[.025,.975]).tolist()
  aggregate[m]=dict(ratio=float(np.exp(x.mean())),interval=interval)
 counts={s:sum(c['split']==s for c in manifest['cases']) for s in ['training','validation','reserved']}
 label_seconds={s:sum(st.read(p)['complete_seconds'] for p in (st.HERE/s).glob('*.json.gz')) for s in ['training','validation']}
 trained=json.loads((st.HERE/'trained_model/candidates.json').read_text())
 out=dict(complete=True,all_exact=True,workflows=workflows,applications=apps,coefficient_entries_checked=checks,application_coefficient_checks=app_checks,
  cases=cases,by_topology=by_kind,profile_ranges=intervals,aggregate=aggregate,fallbacks=dict(fallbacks),learned_choices=dict(choices),selection_reasons=dict(reasons),
  policies={k:{a:v[a] for a in ['enabled','validation_control','best_fixed','validation']}|dict(model=v['model']['name']) for k,v in f['policies'].items()},
  split_counts=counts,model_candidates=70,worker_hosts=sorted(hosts),resource_peaks=dict(peaks),stage_totals={k:dict(v) for k,v in stages.items()},
  final_label_seconds=label_seconds,fitting_seconds=trained['training_seconds'],
  offline_cost_scope='Sum of complete times in the final training and validation records. Excludes reference construction, development, replaced measurements, model selection and record saving. Fitting time covers all seventy final candidates.',
  freeze_sha256=model.sha(st.HERE/'trained_model/freeze.json'),source_sha256=model.sha(__file__),
  timing='Complete reduction, model decision, exact checks, cleanup and all retries. Offline training, reference discovery and retained measurement serialization excluded.',
  scope=manifest['scope'],uncertainty='Graph-weighted descriptive bootstrap interval for aggregate ratios. Per-graph bars show the range over two new kinematic profiles; they are not significance intervals.')
 assert workflows==counts['reserved']*20 and apps==counts['reserved']
 st.write(st.HERE/'model_test/summary.json',out);st.write(st.ROOT/'report/type_specialist_figure_data.json',out)
 os.environ.setdefault('MPLCONFIGDIR',os.path.join(os.environ.get('TMPDIR','/tmp'),'kira_type_mpl'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 names=['Sunrise (2 loops)','Planar box (2 loops)','Vacuum (3 loops)','Ladder (3 loops)','Nonplanar box (2 loops)','Pentagon (1 loop)','Box with virtuality (1 loop)']
 fig,axes=plt.subplots(1,2,figsize=(8.3,4.6),sharey=True,gridspec_kw={'width_ratios':[1.2,1]})
 colors=['#4879a1','#c68428','#21826a']
 for j,(m,label) in enumerate(zip(METHODS[1:],['Sectors + truncation','Fixed per graph','Selected route'])):
  x=np.array([by_kind[k][m] for k in st.KINDS]);ranges=np.array([intervals[k][m] for k in st.KINDS])
  axes[0].errorbar(x,np.arange(7)+(j-1)*.19,xerr=np.maximum(0,np.vstack([x-ranges[:,0],ranges[:,1]-x])),fmt='o',ms=4,capsize=2,color=colors[j],label=label)
 x=np.array([by_kind[k]['learned_to_family_fixed'] for k in st.KINDS]);ranges=np.array([intervals[k]['learned_to_family_fixed'] for k in st.KINDS])
 axes[1].errorbar(x,np.arange(7),xerr=np.maximum(0,np.vstack([x-ranges[:,0],ranges[:,1]-x])),fmt='o',ms=5,capsize=3,color=colors[2])
 for ax in axes:ax.axvline(1,color='.4',ls='--',lw=1);ax.grid(axis='x',alpha=.2)
 axes[0].set_yticks(range(7));axes[0].set_yticklabels(names);axes[0].invert_yaxis()
 axes[0].set_xlabel('Full time / native time');axes[1].set_xlabel('Selected route / fixed strategy')
 axes[0].set_title('Complete reduction time');axes[1].set_title('Choice within each graph')
 vals=[v for k in st.KINDS for m in METHODS[1:] for v in intervals[k][m]]+[1.]
 axes[0].set_xlim(max(0,min(vals)-.05*(max(vals)-min(vals)+.1)),max(vals)+.05*(max(vals)-min(vals)+.1))
 vals=[v for k in st.KINDS for v in intervals[k]['learned_to_family_fixed']]+[1.];pad=max(.04,.1*(max(vals)-min(vals)))
 axes[1].set_xlim(max(0,min(vals)-pad),max(vals)+pad)
 fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,fontsize=9)
 fig.tight_layout(rect=[0,.08,1,1]);fig.savefig(st.ROOT/'report/paper_figures/type_specialists.pdf',bbox_inches='tight');plt.close(fig)
 st.emit(stage='analysis',workflows=workflows,applications=apps,aggregate=aggregate,policies=out['policies'])
if __name__=='__main__':main()
