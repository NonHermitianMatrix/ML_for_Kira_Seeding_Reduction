"""Check all repetitions and summarize completed reductions without dropping failures."""
from s00_loop_common import *
from collections import Counter,defaultdict
import statistics,random

def comparison(rows,control):
 keep=[r for r in rows if r['paired_verified'] and (control!='all_fixed' or r['fixed_verified']) and all(r['methods'][m]['success'] and len(r['methods'][m]['times'])==3 for m in ['integrated',control])]
 if not keep:return dict(pairs=0)
 a=sum(r['methods']['integrated']['median_seconds'] for r in keep);b=sum(r['methods'][control]['median_seconds'] for r in keep);rng=random.Random(3173);ratios=[]
 for _ in range(2000):
  sample=[rng.choice(keep) for i in keep];ratios.append(sum(r['methods']['integrated']['median_seconds'] for r in sample)/sum(r['methods'][control]['median_seconds'] for r in sample))
 ratios.sort()
 return dict(pairs=len(keep),new_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,saving_percent=100*(1-a/b),request_interval=[ratios[49],ratios[1949]],slower_requests=sum(r['methods']['integrated']['median_seconds']>r['methods'][control]['median_seconds'] for r in keep))

def main():
 assert all(read(HERE/f'worker_{w}_complete.json')['complete'] for w in [0,1])
 p=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 h=prior().legacy().h;rows=[];records=0;repetition_checks=0
 for group in ['trees','batches','grid']:
  for c in p[group]:
   row=read(HERE/'outcomes'/(group+'_'+c['id']+'.json.gz'));rows.append(row)
   for m,e in row['methods'].items():
    first=None;repeat_success=[];repeat_status=[]
    for rep in range(len(e['times'])):
     r=read(HERE/group/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz'));records+=1;repeat_success.append(r['success']);repeat_status.append(r.get('status','not_recorded'))
     if first is None:first=r
     elif r['success'] and first['success']:
      ok,n=h.compare(r,first);assert ok,(c['id'],m,rep);repetition_checks+=n
    e['first_success']=e['success'];e['success']=all(repeat_success) and len(repeat_success)==(1 if group=='grid' else 3);e['repeat_statuses']=repeat_status
   if group=='trees':assert row['checks']['passed']
   if group=='batches':assert row['paired_verified'] and row['fixed_verified'],c['id']
 grouped={g:[r for r in rows if r['group']==g] for g in ['trees','batches','grid']}
 coverage={};byloop={}
 for group,rs in grouped.items():
  coverage[group]=dict(requests=len(rs),targets=sum(r['targets'] for r in rs),methods={m:dict(completed=sum(r['methods'][m]['success'] for r in rs),failed=sum(not r['methods'][m]['success'] for r in rs),failed_statuses=dict(Counter(status for r in rs if not r['methods'][m]['success'] for status in (r['methods'][m]['block_statuses'] or [r['methods'][m]['status']]))),first_pass_seconds=sum(r['methods'][m]['times'][0] for r in rs)) for m in rs[0]['methods']})
  byloop[group]={str(L):dict(requests=len(z),new=sum(r['methods']['integrated']['success'] for r in z),previous=sum(r['methods']['previous']['success'] for r in z),paired=sum(r['paired_verified'] for r in z)) for L in range(1,14) if (z:=[r for r in rs if r['loops']==L])}
 scopes={}
 for kind in sorted({r['scope'] for r in grouped['grid']}):
  rs=[r for r in grouped['grid'] if r['scope']==kind];scopes[kind]=dict(requests=len(rs),new=sum(r['methods']['integrated']['success'] for r in rs),previous=sum(r['methods']['previous']['success'] for r in rs),paired=sum(r['paired_verified'] for r in rs))
 s=dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz'),comparisons={'trees':comparison(grouped['trees'],'previous'),'batches_previous':comparison(grouped['batches'],'previous'),'batches_ml_off':comparison(grouped['batches'],'all_fixed')},coverage=coverage,by_loop=byloop,by_scope=scopes,rows=rows,timed_records=records,repeat_coefficient_checks=repetition_checks,paired_coefficient_checks=sum(r['coefficient_checks']+r['fixed_checks'] for r in rows),gamma_sample_checks=sum(r['checks'].get('checks',0) for r in rows),worst_gamma_relative_error=max(float(r['checks'].get('maximum_relative_error',0)) for r in rows),development=read(HERE/'development_checks.json'),tree_median_seconds_range=[min(r['methods']['integrated']['median_seconds'] for r in grouped['trees']),max(r['methods']['integrated']['median_seconds'] for r in grouped['trees'])],study_allocated_bytes=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file()))
 write(HERE/'summary.json',s);print(json.dumps({k:s[k] for k in ['comparisons','coverage','timed_records','gamma_sample_checks','study_allocated_bytes']}),flush=True)
 # A finite coverage matrix makes the mathematical limits visible at each order.
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import numpy as np
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 names=['one-mass vacuum','massive vacuum','massless propagator','massive propagator','massless ladder','box + bubbles','scaleless vacuum','connected bubble trees']
 keys=['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive','ladder','bubble_box','scaleless','trees']
 matrix=np.full((len(keys),13),np.nan)
 for i,key in enumerate(keys):
  for L in range(1,14):
   z=[r for r in rows if r['loops']==L and (r['group']=='trees' if key=='trees' else r['group']=='grid' and r['scope']==key)]
   if z:matrix[i,L-1]=sum(r['methods']['integrated']['success'] for r in z)/len(z)
 from matplotlib.colors import ListedColormap,BoundaryNorm
 fig,ax=plt.subplots(figsize=(9,4));cmap=ListedColormap(['#e9b4aa','#f0ddb0','#94c6b4']);cmap.set_bad('#ededed')
 ax.imshow(matrix,cmap=cmap,norm=BoundaryNorm([-.01,.01,.99,1.01],3),aspect='auto')
 for i in range(len(keys)):
  for j in range(13):
   v=matrix[i,j];ax.text(j,i,'—' if np.isnan(v) else 'all' if v==1 else '0' if v==0 else f'{v:.0%}',ha='center',va='center',fontsize=8)
 ax.set_xticks(range(13));ax.set_xticklabels(range(1,14));ax.set_yticks(range(len(keys)));ax.set_yticklabels(names);ax.set_xlabel('Number of loops');ax.set_title('Exact bubble-tree reductions extend connected coverage; general graphs remain limited',fontsize=11,pad=13)
 fig.tight_layout();q=ROOT/'report/paper_figures/loop_coverage13.pdf';fig.savefig(q);plt.close(fig)
 # Show the added connected family times, without inventing ratios for failed controls.
 fig,ax=plt.subplots(figsize=(8,3.5))
 for shape,color in [('star','#256a86'),('chain','#a65336'),('branched','#547e46')]:
  z=sorted([r for r in grouped['trees'] if r['shape']==shape and r['kinematics']=='rational'],key=lambda r:r['loops'])
  ax.plot([r['loops'] for r in z],[1000*r['methods']['integrated']['median_seconds'] for r in z],marker='o',ms=4,label=shape,color=color)
 ax.set_xlim(.7,13.3);ax.set_xticks(range(1,14));ax.set_ylim(bottom=0);ax.set_xlabel('Number of loops');ax.set_ylabel('Complete application time (ms)');ax.set_title('Connected bubble trees reduce without a growing IBP system',fontsize=11);ax.legend(frameon=False,ncol=3);fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/loop_coverage13_time.pdf');plt.close(fig)
if __name__=='__main__':main()
