"""Draw paired timing results and keep the ML contribution separate."""
from s00_reconstruction_common import *
import statistics
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.tools/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAMES={'double_box':'Planar box','nonplanar_box':'Nonplanar box','sunrise':'Massive sunrise','vacuum3':'Three-loop vacuum'}
COLORS={'before_formulas':'#59616b','previous':'#b37541','fixed':'#42899a','integrated':'#2356a1'}
def clean(ax):
 ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(axis='y',color='.9',linewidth=.6)

def main():
 s=read(HERE/'summary.json');rows=s['rows'];out=ROOT/'report/paper_figures';out.mkdir(exist_ok=True)
 plt.rcParams.update({'font.size':9,'axes.labelsize':9,'legend.fontsize':8,'pdf.fonttype':42,'ps.fonttype':42})
 methods=['before_formulas','previous','fixed','integrated']
 matched=[r for r in rows if all(all(r['success'][m]) for m in methods)]
 totals=[sum(r['median_seconds'][m] for r in matched) for m in methods]
 fig,ax=plt.subplots(figsize=(6.3,2.8),constrained_layout=True)
 labels=['Earlier\napplication','Added vacuum\nformulas','Fixed\nreconstruction','Integrated\nselection']
 bars=ax.bar(range(4),totals,color=[COLORS[m] for m in methods],width=.62)
 for b,v in zip(bars,totals):ax.text(b.get_x()+b.get_width()/2,v+max(totals)*.025,f'{v:.2f} s',ha='center',va='bottom',fontsize=9)
 ax.set(xticks=range(4),xticklabels=labels,ylabel='Sum of median application times (s)',ylim=(0,max(totals)*1.16),title=f'The same {len(matched)} completed requests');clean(ax)
 fig.savefig(out/'reconstruction_components.pdf');plt.close(fig)
 native=[r for r in rows if r['group']=='native']
 fig,ax=plt.subplots(figsize=(6.3,3.0),constrained_layout=True);all_values=[1.]
 kinds=list(NAMES)
 for j,kind in enumerate(kinds):
  selected=[r for r in native if r['topology']==kind and all(r['success']['previous']) and all(r['success']['integrated'])]
  ratios=[r['median_seconds']['integrated']/r['median_seconds']['previous'] for r in selected]
  xx=[j+(i-(len(ratios)-1)/2)*min(.06,.35/max(1,len(ratios))) for i in range(len(ratios))]
  ax.scatter(xx,ratios,s=28,color=COLORS['integrated'],alpha=.85,zorder=3)
  stat=s['native_structures'][kind]
  if stat['ratio'] is not None:
   lo,hi=stat['interval'];v=stat['ratio'];ax.errorbar(j+.23,v,yerr=[[v-lo],[hi-v]],fmt='D',color='#171b20',markersize=4,capsize=3)
   all_values.extend([lo,hi])
  all_values.extend(ratios)
 span=max(.1,max(all_values)-min(all_values));ax.axhline(1,color='.35',linestyle='--',linewidth=1)
 ax.set(xticks=range(4),xticklabels=['Planar\nbox','Nonplanar\nbox','Massive\nsunrise','Three-loop\nvacuum'],ylabel='Integrated time / preceding time',ylim=(max(0,min(all_values)-.12*span),max(all_values)+.15*span),xlim=(-.4,3.5));clean(ax)
 fig.savefig(out/'reconstruction_native.pdf');plt.close(fig)
 fig,ax=plt.subplots(figsize=(6.3,3.0),constrained_layout=True)
 if s['model_enabled']:
  selected=sorted([r for r in native if all(r['success']['fixed']) and all(r['success']['integrated'])],key=lambda r:r['median_seconds']['fixed'])
  ratios=[r['median_seconds']['integrated']/r['median_seconds']['fixed'] for r in selected]
  ax.scatter(range(1,len(ratios)+1),ratios,s=26,color=COLORS['integrated'])
  stat=s['new_ml'];v=stat['ratio'];lo,hi=stat['interval'];ax.errorbar(len(ratios)+1.5,v,yerr=[[v-lo],[hi-v]],fmt='D',color='#171b20',capsize=4)
  values=ratios+[1.,lo,hi];span=max(.04,max(values)-min(values))
  ax.axhline(1,color='.35',linestyle='--',linewidth=1)
  ax.set(xlabel='Native request, ordered by fixed-method time',ylabel='Integrated time / fixed-method time',xlim=(.3,len(ratios)+2.3),ylim=(min(values)-.15*span,max(values)+.2*span))
  ax.annotate('Aggregate',(len(ratios)+1.5,v),xytext=(-5,14),textcoords='offset points',ha='right',fontsize=8)
 else:
  t=read(HERE/'training_summary.json');ratio=t['best_validation']['seconds']/t['fixed_validation']['seconds']
  ax.scatter([0,1],[1.,ratio],s=48,c=[COLORS['fixed'],COLORS['integrated']],zorder=3)
  ax.axhline(1,color='.5',linestyle=':',linewidth=1)
  ax.axhline(.97,color='#a34e3e',linestyle='--',linewidth=1,label='Required validation ratio')
  values=[.97,1.,ratio];span=max(.04,max(values)-min(values))
  ax.set(xticks=[0,1],xticklabels=['Fixed setting per structure','Selected cost model'],ylabel='Validation time / fixed time',ylim=(min(values)-.25*span,max(values)+.4*span),xlim=(-.45,1.45))
  ax.legend(frameon=False,loc='upper left')
 clean(ax);fig.savefig(out/'reconstruction_ml.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(6.4,2.9),constrained_layout=True)
 for ax,group,title in zip(axes,['vacuum_products','connected_vacuum'],['Independent vacuum factors','Connected one-mass trees']):
  selected=[r for r in rows if r['group']==group and all(r['success']['before_formulas']) and all(r['success']['integrated'])]
  for method,label in [('before_formulas','Earlier application'),('integrated','Integrated method')]:
   orders=sorted({r['loops'] for r in selected});buckets=[[r['median_seconds'][method] for r in selected if r['loops']==L] for L in orders]
   med=[statistics.median(v) for v in buckets]
   ax.plot(orders,med,'o-',markersize=3,linewidth=1.2,color=COLORS[method],label=label)
   if group=='connected_vacuum':ax.fill_between(orders,[min(v) for v in buckets],[max(v) for v in buckets],color=COLORS[method],alpha=.12)
  ax.set(title=title,xlabel='Number of loops',yscale='log',xticks=[1,3,5,7,9,11,13]);clean(ax)
 axes[0].set_ylabel('Complete application time (s)');axes[1].legend(frameon=False)
 fig.savefig(out/'reconstruction_exact.pdf');plt.close(fig)
 print('Four paired-comparison figures written',flush=True)
if __name__=='__main__':main()
