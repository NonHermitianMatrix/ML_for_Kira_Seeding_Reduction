"""Report paired total times, failures, native work, and exact checks."""
from s00_batch_common import *
import random,subprocess

def group(c):
 if c['scope']=='native_batch':return c['topology_group']
 return c['scope']

def native_operations(r):
 return sum(m.get('operations',0) for b in r.get('blocks',[]) if not b.get('reused') for a in b['result'].get('attempts',[]) for m in a.get('metrics',[]))

def comparison(rows,other,seed=3203):
 pairs=[r for r in rows if r['methods']['learned']['verified'] and r['methods'][other]['verified']]
 a=sum(r['methods']['learned']['median_seconds'] for r in pairs);b=sum(r['methods'][other]['median_seconds'] for r in pairs)
 if not pairs:return dict(matched=0)
 rng=random.Random(seed);ratios=[]
 for _ in range(2000):
  x=y=0.
  for r in pairs:
   left=r['methods']['learned']['seconds'];right=r['methods'][other]['seconds'];ix=[rng.randrange(3) for _ in range(3)]
   x+=statistics.median(left[j] for j in ix);y+=statistics.median(right[j] for j in ix)
  ratios.append(x/y)
 ratios.sort()
 return dict(matched=len(pairs),learned_seconds=a,control_seconds=b,ratio=a/b,speedup=b/a,saving_percent=100*(1-a/b),repetition_interval=[ratios[50],ratios[1950]],slower_requests=sum(r['methods']['learned']['median_seconds']>r['methods'][other]['median_seconds'] for r in pairs),largest_request_ratio=max(r['methods']['learned']['median_seconds']/r['methods'][other]['median_seconds'] for r in pairs),learned_native_operations=sum(r['methods']['learned']['native_operations'] for r in pairs),control_native_operations=sum(r['methods'][other]['native_operations'] for r in pairs))

def main():
 for w in [0,1]:assert read(HERE/f'test_{w}_complete.json')['complete']
 p=read(HERE/'protocol.json');assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
 rows=[];coefficient_checks=0;records=0;first_failures={m:0 for m in p['methods']};reference_seconds=0.
 for c in p['cases']:
  reference=read(HERE/'references'/(c['id']+'.json.gz'));reference_seconds+=reference['preparation_seconds'];methods={}
  for method in p['methods']:
   rs=[read(q) for rep in range(3) if (q:=HERE/'model_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')).exists()]
   records+=len(rs);coefficient_checks+=sum(r.get('coefficient_checks',0) for r in rs);first_failures[method]+=not rs[0]['independently_verified']
   seconds=[r['complete_process_and_check_seconds'] for r in rs]
   methods[method]=dict(verified=len(rs)==3 and all(r['independently_verified'] for r in rs),completed=len(rs)==3 and all(r['success'] for r in rs),seconds=seconds,median_seconds=statistics.median(seconds),native_operations=statistics.median(native_operations(r) for r in rs),actions=[b['result'].get('batch_action') for b in rs[0].get('blocks',[])],batch_model_used=any(b['result'].get('batch_model_used',False) for b in rs[0].get('blocks',[])),failed_attempts=sum(not a['success'] for r in rs for b in r.get('blocks',[]) for a in b['result'].get('attempts',[])),statuses=[r['status'] for r in rs])
  rows.append(dict(case=c['id'],group=group(c),loops=len(c['definition']['loop_momenta']),targets=c['size'],reference_success=reference['success'],methods=methods))
 groups=sorted({r['group'] for r in rows})
 subsets={g:[r for r in rows if r['group']==g] for g in groups}
 subsets['native_all']=[r for r in rows if r['group'] in ['double_box','nonplanar_box','native_batch_new_indices']]
 subsets['all']=rows
 comparisons={g:{m:comparison(selected,m) for m in ['previous','previous_prepared','fixed','all_fixed']} for g,selected in subsets.items()}
 result=dict(complete=True,requests=len(rows),timed_records=records,coefficient_checks=coefficient_checks,first_unverified=first_failures,reference_seconds=reference_seconds,rows=rows,comparisons=comparisons,admission=read(HERE/'admission.json'),model_selection=read(HERE/'trained_model/initial_policy.json')['selection'],model_sha256=p['model_sha256'],protocol_sha256=sha(HERE/'protocol.json'),totals={m:dict(completed=sum(r['methods'][m]['completed'] for r in rows),verified=sum(r['methods'][m]['verified'] for r in rows),sum_medians_seconds=sum(r['methods'][m]['median_seconds'] for r in rows),failed_attempts=sum(r['methods'][m]['failed_attempts'] for r in rows)) for m in p['methods']})
 offline={}
 for phase in ['training','validation','application_validation']:
  rs=[read(q) for q in (HERE/phase).glob('*.json.gz')];rs=[r for r in rs if 'complete_process_and_check_seconds' in r]
  offline[phase]=dict(records=len(rs),summed_measured_seconds=sum(r['complete_process_and_check_seconds'] for r in rs))
 training_rows=read(HERE/'training/rows.json.gz');ids={r['case']['id'] for phase in ['training','validation'] for r in training_rows[phase]}
 ids.update(c['id'] for c in __import__('s03_cases').batches(3041,'application_validation'))
 offline['reference_seconds']=sum(read(HERE/'references'/(name+'.json.gz'))['preparation_seconds'] for name in ids)
 offline['fit_job_wall_seconds']=None
 try:
  job=read(HERE/'scheduled_jobs.json')['fit'];account=subprocess.run(['qacct','-j',job],capture_output=True,text=True,timeout=20)
  match=re.search(r'^ru_wallclock\s+([\d.]+)',account.stdout,re.M)
  if match:offline['fit_job_wall_seconds']=float(match.group(1))
 except (OSError,subprocess.TimeoutExpired):pass
 result['offline_costs']=offline
 result['interrupted_validation']=read(HERE/'interrupted_validation/interruption.json')
 result['test_environment']={str(w):read(HERE/f'test_worker_{w}_environment.json') for w in [0,1]}
 for method in p['methods']:result['totals'][method]['first_pass_seconds']=sum(r['methods'][method]['seconds'][0] for r in rows)
 write(HERE/'summary.json',result)
 import matplotlib
 matplotlib.use('Agg');import matplotlib.pyplot as plt
 plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'font.family':'DejaVu Sans'})
 names={'double_box':'Planar box batches','nonplanar_box':'Nonplanar box batches','native_batch_new_indices':'New index batches','native_all':'All native box batches','triangle_products':'Independent triangle products','exact_triangle':'Symbolic triangle','compatibility':'Compatibility cases','all':'All matched requests'}
 order=[g for g in ['double_box','nonplanar_box','native_batch_new_indices','triangle_products','exact_triangle','compatibility','all'] if g in comparisons and comparisons[g]['previous_prepared']['matched']]
 fig,axes=plt.subplots(2,1,figsize=(6.5,5.5),gridspec_kw={'height_ratios':[1.65,1]},constrained_layout=True)
 for i,g in enumerate(order):
  r=comparisons[g]['previous_prepared'];lo,hi=r['repetition_interval'];axes[0].errorbar(r['ratio'],i,xerr=[[max(0,r['ratio']-lo)],[max(0,hi-r['ratio'])]],fmt='o',color='#087e8b',capsize=2)
 axes[0].set_yticks(range(len(order)));axes[0].set_yticklabels([names[g] for g in order]);axes[0].invert_yaxis();axes[0].axvline(1,color='black',ls='--',lw=.8);axes[0].set_xscale('log');axes[0].set_xlabel('Time / preceding method with the same basis');axes[0].set_title('Exact and learned changes: complete time')
 native=[g for g in ['double_box','nonplanar_box','native_batch_new_indices','native_all'] if comparisons.get(g,{}).get('fixed',{}).get('matched')]
 for i,g in enumerate(native):
  r=comparisons[g]['fixed'];lo,hi=r['repetition_interval'];axes[1].errorbar(r['ratio'],i,xerr=[[max(0,r['ratio']-lo)],[max(0,hi-r['ratio'])]],fmt='o',color='#087e8b',capsize=2)
 axes[1].set_yticks(range(len(native)));axes[1].set_yticklabels([names[g] for g in native]);axes[1].invert_yaxis();axes[1].axvline(1,color='black',ls='--',lw=.8);axes[1].set_xlabel('Time / same workflow with fixed batch choice');axes[1].set_title('Added effect of the new batch model')
 values=[v for g in native for v in comparisons[g]['fixed']['repetition_interval']]+[1];span=max(.12,max(values)-min(values));axes[1].set_xlim(max(0,min(values)-.12*span),max(values)+.12*span)
 for ax in axes:ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 fig.savefig(ROOT/'report/paper_figures/analytic_batch.pdf');plt.close(fig)
 print(json.dumps({k:v for k,v in result.items() if k in ['requests','timed_records','coefficient_checks','totals','admission']}),flush=True)
if __name__=='__main__':main()
