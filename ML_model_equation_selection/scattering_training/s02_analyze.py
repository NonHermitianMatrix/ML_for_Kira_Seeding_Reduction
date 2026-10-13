"""Check all reserved runs and make the scattering results table and figure."""
import gzip, hashlib, json, math, os
from pathlib import Path
import statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SEED=ROOT/'ML_model_seed_selection/scattering_training'

def read(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def geometric(values):return math.exp(statistics.mean(math.log(x) for x in values))
def main():
 import numpy as np
 manifest=json.loads((HERE/'cases.json').read_text());freeze=json.loads((HERE/'freeze.json').read_text())
 for p,h in freeze['weights'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 cases=[c for c in manifest['cases'] if c['split']=='reserved'];methods=freeze['test_methods'];records=[];pairs=0;applications=0
 for c in cases:
  medians={};fallback={};first={};preparation={};skipped={}
  for task in methods:
   runs=[read(HERE/'model_test'/f'{c["id"]}_{task}_{rep}.json.gz') for rep in range(5)]
   assert all(r['success'] for r in runs),(c['id'],task)
   for r in runs:
    last=r['attempts'][-1];assert last['reference_checked'] and not last.get('mismatches')
    assert last['basis_admitted'] and not last.get('unresolved_integrals')
    pairs+=sum(len(row) for row in last['coefficients'].values())
   medians[task]=statistics.median(r['complete_seconds'] for r in runs)
   preparation[task]=statistics.median(r['equation_preparation_seconds'] for r in runs)
   fallback[task]=sum(r['fallback_count']>0 for r in runs)
   first[task]=sum(r['attempts'][0]['success'] for r in runs)
   skipped[task]=statistics.mean(r['attempts'][0].get('equation_metrics',{}).get('construction_skipped_calls',0) for r in runs)
  for task in ['seed','equation']:
   app=read(HERE/'model_test'/f'{c["id"]}_{task}_application.json.gz')
   assert app['success'] and app['answers_withheld'] and app['independent_coefficient_checks']>0
   applications+=1
  records.append(dict(case=c['id'],kind=c['topology_group'],symbolic=bool(c['definition']['invariants']),targets=c['size'],
   median_seconds=medians,preparation_seconds=preparation,fallback_workflows=fallback,first_attempt_successes=first,mean_skipped_calls=skipped,
   ratios={task:medians[task]/medians['native'] for task in methods if task!='native'}))
 aggregate={};rng=np.random.default_rng(20261013)
 for task in methods[1:]:
  group_logs=[statistics.mean(math.log(r['ratios'][task]) for r in records if r['kind']==k) for k in ['nonplanar_box','pentagon','one_mass_box']]
  boot=np.exp(np.mean(rng.choice(group_logs,size=(10000,3),replace=True),axis=1))
  aggregate[task]=dict(ratio=math.exp(statistics.mean(group_logs)),interval95=list(map(float,np.quantile(boot,[.025,.975]))),
   fallback_workflows=sum(r['fallback_workflows'][task] for r in records),first_attempt_successes=sum(r['first_attempt_successes'][task] for r in records),
   by_topology={k:geometric(r['ratios'][task] for r in records if r['kind']==k) for k in ['nonplanar_box','pentagon','one_mass_box']},
   by_kinematics={str(b):geometric(r['ratios'][task] for r in records if r['symbolic']==b) for b in [False,True]})
 training=[]
 for base in [HERE,SEED]:
  for p in sorted((base/'trained_model').glob('*.json')):
   m=json.loads(p.read_text());training.append({k:m[k] for k in ['task','topology','rows','positives','training_seconds'] } | {'nodes':len(m['nodes'])})
 result=dict(complete=True,all_exact=True,workflows=len(cases)*5*len(methods),test_batches=len(cases),targets=sum(c['size'] for c in cases),
   training_batches=9,validation_batches=6,validation_workflows=126,training=training,cases=records,aggregate=aggregate,
   coefficient_pairs=pairs,application_checks=applications,
   independence=manifest['design'],policies=freeze['policies'],
   limitations='Three fitted graph structures. Symbolic target sets are disjoint within symbolic splits, while rational cases reuse index templates at different parameter points. These are new tree adapters, not a controlled same-architecture ablation of training coverage. No claim of calibrated probabilities or general high-loop transfer.')
 (HERE/'model_test/summary.json').write_text(json.dumps(result,indent=2)+'\n')
 (SEED/'model_test/summary.json').write_text(json.dumps({k:v for k,v in result.items() if k not in ['training','aggregate']} | {'aggregate':aggregate['seed'],'training':[m for m in training if m['task']=='seed']},indent=2)+'\n')
 # Only paper assets and their compact evidence table are synchronized locally.
 report=ROOT/'report';(report/'scattering_figure_data.json').write_text(json.dumps(result,indent=2)+'\n')
 os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.tools/paper-mpl'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 names={'nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Box with virtuality'}
 fig,ax=plt.subplots(figsize=(8.5,5.0),constrained_layout=True)
 colors={'old_equation':'#b35835','seed':'#277da8','equation':'#28866e'}
 labels={'old_equation':'Original equation tree','seed':'New seed tree','equation':'New equation tree'}
 for offset,task in zip([-.2,0,.2],methods[1:]):
  ax.scatter([r['ratios'][task] for r in records],np.arange(len(records))+offset,s=26,color=colors[task],label=labels[task],zorder=3)
 ax.axvline(1,color='#333333',linestyle='--',lw=1)
 ax.set_yticks(range(len(records)));ax.set_yticklabels([names[r['kind']]+(': symbolic' if r['symbolic'] else ': point '+r['case'].split('point')[-1]) for r in records]);ax.invert_yaxis()
 vals=[r['ratios'][t] for r in records for t in methods[1:]];lo=min(min(vals),1);hi=max(max(vals),1);pad=max(.04,(hi-lo)*.1)
 ax.set_xlim(max(0,lo-pad),hi+pad);ax.grid(axis='x',color='#e3e6e8');ax.set_axisbelow(True)
 ax.set_xlabel('Full time / native Kira time (below 1 is faster)')
 ax.set_title('No overall time saving after scattering training',loc='left',pad=12,fontsize=11)
 ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=3,frameon=False,fontsize=9)
 fig.savefig(report/'paper_figures/scattering_training.pdf',bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None});plt.close(fig)
 # A second plot records whether learning supplies sufficient equations before fallback.
 fig,ax=plt.subplots(figsize=(7,2.8),constrained_layout=True)
 values=[aggregate[t]['first_attempt_successes'] for t in methods[1:]]
 ax.barh(range(3),values,color=[colors[t] for t in methods[1:]],height=.55)
 ax.set_yticks(range(3));ax.set_yticklabels([labels[t] for t in methods[1:]]);ax.invert_yaxis();ax.set_xlim(0,48);ax.set_xticks([0,15,30,45]);ax.set_xlabel('Complete first attempts out of 45 trials');ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 for i,v in enumerate(values):ax.text(v+.4,i,str(v),va='center')
 fig.savefig(report/'paper_figures/scattering_sufficiency.pdf',bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None});plt.close(fig)
 print(json.dumps({k:result[k] for k in ['workflows','targets','aggregate','coefficient_pairs','application_checks']}),flush=True)
if __name__=='__main__':main()
