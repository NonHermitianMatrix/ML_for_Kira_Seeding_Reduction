"""Plot complete application time and the separate learned contribution."""
from s00_direct_common import *

def main():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 s=read(HERE/'final_summary.json');dest=ROOT/'report/paper_figures';dest.mkdir(exist_ok=True)
 plt.rcParams.update({'font.size':9,'axes.labelsize':9,'legend.fontsize':8,'pdf.fonttype':42})
 fig,axs=plt.subplots(1,2,figsize=(6.4,3.1),constrained_layout=True)
 for ax,g,title in zip(axs,['vacuum_products','connected_vacuum'],['Independent two-mass factors','Connected one-mass trees']):
  rows=sorted([r for r in s['rows'] if r['group']==g],key=lambda r:r['loops'])
  for method,name,color,marker in [('previous','Preceding','#a55d3a','s'),('integrated','Integrated','#236b8e','o')]:
   rr=[r for r in rows if all(r['success'][method])];ls=sorted({r['loops'] for r in rr});times=[[1000*r['median_seconds'][method] for r in rr if r['loops']==L] for L in ls];ax.plot(ls,[statistics.median(v) for v in times],marker=marker,markersize=3.3,linewidth=1,color=color,label=name)
   if g=='connected_vacuum':ax.fill_between(ls,[min(v) for v in times],[max(v) for v in times],color=color,alpha=.12,linewidth=0)
  vals=[1000*r['median_seconds'][m] for r in rows for m in ['previous','integrated'] if all(r['success'][m])];ax.set(title=title,xlabel='Number of loops',ylabel='Complete time (ms)',yscale='log',xlim=(.5,13.5),ylim=(min(vals)*.65,max(vals)*1.5));ax.set_xticks([1,3,5,7,9,11,13]);ax.legend(frameon=False);ax.grid(alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
 fig.savefig(dest/'direct_vacuum.pdf');plt.close(fig)
 rows=[r for r in s['rows'] if r['group']=='native' and all(r['success']['integrated']) and all(r['success']['fixed'])];rows.sort(key=lambda r:r['median_seconds']['fixed']);q=s['native_ml'];ratios=[r['median_seconds']['integrated']/r['median_seconds']['fixed'] for r in rows]
 fig,ax=plt.subplots(figsize=(6.4,3.1),constrained_layout=True)
 for non,name,col in [(False,'Planar','#236b8e'),(True,'Nonplanar','#a55d3a')]:
  ids=[i for i,r in enumerate(rows) if ('nonplanar' in r['case'])==non];ax.scatter([i+1 for i in ids],[ratios[i] for i in ids],s=30,marker='s' if non else 'o',label=name,color=col)
 x=len(rows)+2;ax.errorbar([x],[q['ratio']],yerr=[[max(0,q['ratio']-q['interval'][0])],[max(0,q['interval'][1]-q['ratio'])]],fmt='D',color='black',capsize=4,label='Aggregate, 95% interval');ax.axhline(1,color='.4',linestyle='--',linewidth=1);vals=ratios+q['interval']+[1];span=max(.08,max(vals)-min(vals));ax.set(xlabel='Request, ordered by fixed-choice time; aggregate at right',ylabel='Integrated / fixed complete time',xlim=(0,x+1),ylim=(min(vals)-.15*span,max(vals)+.3*span));ax.legend(frameon=False,ncol=3,loc='upper left');ax.grid(axis='y',alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);fig.savefig(dest/'direct_native.pdf');plt.close(fig)
if __name__=='__main__':main()
