"""Create paper figures from frozen result summaries; no training or reductions."""
import hashlib
import json
import math
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1]/'.tools/paper-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, ScalarFormatter
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'paper_figures'
BLUE='#176E9A'
GREEN='#27806A'
ORANGE='#B65A25'
GRAY='#657080'
sources={}
def read(name):
    p=ROOT/name
    assert p.stat().st_size<5*1024**2,name
    data=p.read_bytes()
    sources[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    return json.loads(data)

def style():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
      'axes.labelsize':10,'axes.titlesize':11,'axes.titleweight':'medium',
      'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,
      'axes.spines.top':False,'axes.spines.right':False,
      'axes.linewidth':0.7,'lines.linewidth':1.5,
      'pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'})

def finish(fig,name):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=0.08,
                metadata={'Title':name.replace('_',' '),'CreationDate':None,'ModDate':None})
    plt.close(fig)

def ratio_axis(ax,limits):
    ax.set_xlim(*limits)
    ax.axvline(1,color='#252C35',linestyle='--',linewidth=1,zorder=1)
    ax.grid(axis='x',color='#E4E7EB',linewidth=.7)
    ax.set_axisbelow(True)
    ax.set_xlabel('Complete time / control time')

def point(ax,value,y,interval=None,color=BLUE,marker='o',label=None):
    if interval:
        lo,hi=interval
        assert lo<=value<=hi
        ax.errorbar(value,y,xerr=[[value-lo],[hi-value]],fmt=marker,
                    color=color,ms=6,capsize=3,elinewidth=1.4,zorder=3,label=label)
    else:ax.plot(value,y,marker,color=color,ms=6,zorder=3,label=label)

def main():
    style();OUT.mkdir(exist_ok=True)
    seed=read('ML_model_seed_selection/model_test/report_values.json')
    seedraw=read('ML_model_seed_selection/model_test/test_results.json')
    seedtime=read('Kira_comparison/acceleration/expression_matched_summary.json')
    live=read('Kira_comparison/live_matrix/summary.json')
    parallel=read('Kira_comparison/parallel_inference/confirmation_summary.json')
    rowlabels=read('ML_model_reduction/model_test/report_values.json')
    equation=read('ML_model_equation_selection/early_generation/model_test/summary.json')
    transfer=read('Kira_comparison/generalization/summary.json')
    cumulative=read('Kira_comparison/cumulative_speedup/test/summary.json')
    # The sufficiency result is also checked against the saved underlying audit.
    suffroot=ROOT/'ML_model_seed_selection/kira_sufficiency_test'
    evidence=[]
    for p in sorted(suffroot.glob('*.json')):
        if p.stat().st_size>5*1024**2:continue
        text=p.read_text()
        if '652517' in text:
            read(str(p.relative_to(ROOT)));evidence.append(str(p.relative_to(ROOT)))
    assert evidence,'Missing measured 652517-target sufficiency evidence'
    sufficient=652517/690382*100
    comps=[r for r in seedtime['comparisons'] if r['denominator']=='stored_pool' and r['size'] in [1,16]]
    comps.sort(key=lambda r:r['size'])
    assert len(comps)==2 and abs(comps[0]['ratio']-.914)<.0005
    seedpoints=[float(seed[k]) for k in ['PRECISION','RECALL','F1','EXACT']]+[sufficient]
    fig,axs=plt.subplots(1,2,figsize=(9.0,3.65),gridspec_kw={'width_ratios':[1.12,1]},constrained_layout=True)
    ax=axs[0];labels=['Seed precision','Seed recall',r'Seed $F_1$','Recorded set match','Sufficient equations']
    for y,v in enumerate(seedpoints):
        ax.plot(v,y,'o',color=GREEN if y==4 else BLUE,ms=6)
        ax.annotate(f'{v:.2f}%',(v,y),xytext=(6,-3),textcoords='offset points',fontsize=9)
    ax.set_yticks(range(5));ax.set_yticklabels(labels);ax.set_ylim(4.6,-.6);ax.set_xlim(81,102)
    ax.set_xticks([85,90,95,100]);ax.set_xlabel('Measured fraction or score (%)')
    ax.grid(axis='x',color='#E4E7EB');ax.set_title('(a) Recovery and sufficiency',loc='left',pad=12)
    ax=axs[1];ratio_axis(ax,(.74,1.19))
    for y,r in enumerate(comps):
        point(ax,r['ratio'],y,r['interval95'],color=GREEN if y==0 else GRAY)
        ax.annotate(f"{r['ratio']:.3f}",(r['ratio'],y),xytext=(0,11),textcoords='offset points',ha='center',fontsize=9)
    ax.set_yticks([0,1]);ax.set_yticklabels(['1 target\n12 paired batches','16 targets\n11 paired batches']);ax.set_ylim(1.55,-.55)
    ax.set_title('(b) Saving depends on batch size',loc='left',pad=12)
    finish(fig,'seed_results')

    initial=next(r for r in live['comparisons'] if r['baseline']=='stock' and r['policy']=='learned')['metrics']['cold_seconds']['geometric_mean_ratio']
    late={name:parallel['comparisons'][name+'_new_over_native_new']['complete_seconds']['all'] for name in ['row','seed','both']}
    assert abs(initial-1.305)<.0005 and abs(late['row']['ratio']-.982)<.0005
    fig,ax=plt.subplots(figsize=(8.1,3.35),constrained_layout=True);ratio_axis(ax,(.93,1.37))
    point(ax,initial,0,color=ORANGE,marker='s')
    point(ax,late['row']['ratio'],1,late['row']['descriptive_interval'],color=BLUE)
    point(ax,late['both']['ratio'],2,late['both']['descriptive_interval'],color=GRAY)
    ax.set_yticks([0,1,2]);ax.set_yticklabels(['Initial frozen row model\nvs original Kira','Later compiled row policy\nvs shared native control','Later seed + row policies\nvs shared native control'])
    ax.set_ylim(2.55,-.65);ax.set_title('Complete native row-selection gain remains unestablished',loc='left',pad=13)
    for y,v in [(0,initial),(1,late['row']['ratio']),(2,late['both']['ratio'])]:
        ax.annotate(f'{v:.3f}',(v,y),xytext=(0,12),textcoords='offset points',ha='center',fontsize=9)
    finish(fig,'row_results')

    eq=equation['comparisons']['deployed_vs_native']
    assert equation['all_exact'] and abs(eq['complete_seconds']['ratio']-.943)<.0005
    order=['double_box','vacuum3','ladder3','sunrise']
    names=['Aggregate (8 profiles)','Two-loop double box','Three-loop vacuum','Three-loop ladder','Two-loop sunrise']
    eqdata=[eq]+[equation['by_topology'][k]['deployed_vs_native'] for k in order]
    fig,axs=plt.subplots(1,2,figsize=(9.0,3.5),sharey=True,constrained_layout=True)
    for ax,key,title,limits,col in zip(axs,['complete_seconds','equation_preparation_seconds'],
            ['(a) Complete time: 5.7% lower','(b) Preparation: 36.2% lower'],[(.85,1.03),(.39,1.04)],[BLUE,GREEN]):
        ratio_axis(ax,limits)
        for y,d in enumerate(eqdata):point(ax,d[key]['ratio'],y,d[key]['interval'] if y==0 else None,color=col,marker='D' if y==0 else 'o')
        ax.set_yticks(range(5));ax.set_yticklabels(names);ax.set_ylim(4.6,-.6)
        ax.set_title(title,loc='left',pad=12)
        ax.set_xlabel(('Complete time' if key=='complete_seconds' else 'Preparation time')+' / native time')
    finish(fig,'equation_results')

    pretty={'nonplanar_box_point2':'Nonplanar box: rational profile 1',
      'nonplanar_box_point3':'Nonplanar box: rational profile 2',
      'pentagon_point2':'Pentagon: rational profile 1','pentagon_point3':'Pentagon: rational profile 2',
      'nonplanar_box_symbolic':'Nonplanar box: symbolic d, s, t',
      'pentagon_symbolic':'Pentagon: symbolic d and 5 invariants',
      'one_mass_box_symbolic':'Box: symbolic d, s, t, virtuality'}
    fig,ax=plt.subplots(figsize=(8.3,3.8),constrained_layout=True)
    cases=transfer['cases'];ratios=[c['learned_to_native'] for c in cases]
    ratio_axis(ax,(.97,max(ratios)+.13))
    for y,c in enumerate(cases):
        point(ax,c['learned_to_native'],y,color=ORANGE if c['symbolic'] else GRAY,marker='D' if c['symbolic'] else 'o')
        ax.annotate(f"{c['learned_to_native']:.3f}",(c['learned_to_native'],y),xytext=(7,-3),textcoords='offset points',fontsize=9)
    ax.set_yticks(range(len(cases)));ax.set_yticklabels([pretty[c['case']] for c in cases]);ax.set_ylim(len(cases)-.4,-.7)
    ax.set_title('New scattering cases require fallback and increase time',loc='left',pad=13)
    ax.set_xlabel('Filtered workflow with fallback / native workflow time')
    finish(fig,'transfer_results')

    groups=cumulative['groups'];primary=cumulative['primary_metric'];assert primary=='roundtrip_seconds'
    cc=cumulative['comparisons']['original_kira'][primary]
    assert abs(cc['speedup']-543.815)<.001 and cumulative['all_exact']
    xx=np.arange(1,len(groups)+1)
    times={m:[g['medians'][m][primary] for g in groups] for m in ['original_kira','chain_baseline','final']}
    speed=[a/b for a,b in zip(times['original_kira'],times['final'])]
    fig,axs=plt.subplots(1,2,figsize=(9.0,3.6),constrained_layout=True)
    for m,name,color,marker in [('original_kira','Original Kira',GRAY,'s'),('chain_baseline','Later full-pool control',ORANGE,'^'),('final','Exact specialized route',GREEN,'o')]:
        axs[0].plot(xx,times[m],marker=marker,label=name,color=color,ms=4)
    axs[0].set_yscale('log');axs[0].set_ylim(.1,max(times['original_kira'])*1.75)
    axs[0].set_ylabel('Complete time (seconds; log scale)');axs[0].set_title('(a) Same targets, different exact workflows',loc='left',pad=12)
    axs[0].legend(loc='center right',frameon=True,framealpha=.95,fontsize=8)
    axs[1].plot(xx,speed,'o',color=GREEN,ms=5)
    axs[1].axhline(cc['speedup'],color=BLUE,linestyle='--',label=f"Geometric mean: {cc['speedup']:.1f}")
    axs[1].axhspan(*cc['speedup_interval95'],color=BLUE,alpha=.09,label='Aggregate descriptive 95% interval')
    axs[1].set_ylim(min(speed)*.85,max(speed)*1.18);axs[1].set_ylabel('Original time / final time (speedup)')
    axs[1].set_title('(b) Cumulative gain within this family',loc='left',pad=12)
    axs[1].legend(loc='upper right',fontsize=8,frameon=False)
    for ax in axs:
        ax.set_xticks(xx);ax.set_xlabel('Reserved batch');ax.grid(axis='y',color='#E4E7EB',linewidth=.7);ax.set_axisbelow(True)
    finish(fig,'cumulative_results')

    payload={'sources':sources,'note':'Existing measurements; no new training or reductions. Each uncertainty interval retains its original grouping and definition.',
      'seed_label_scores':dict(zip(['precision','recall','f1','set_match','sufficiency'],seedpoints)),
      'seed_time_comparisons':[{k:v for k,v in r.items() if k!='pairs'} for r in comps],
      'row_initial_ratio':initial,'later_native':late,'row_label_metrics':rowlabels,
      'equation':{'aggregate':eq,'topologies':{k:equation['by_topology'][k]['deployed_vs_native'] for k in order}},
      'transfer':{'cases':cases,'ratio':transfer['geometric_mean_learned_to_native']},
      'cumulative':{'groups':groups,'comparison':cc,'primary_metric':primary},
      'figures':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.pdf'))}}
    (HERE/'paper_figure_data.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'figures':len(payload['figures']),'source_files':len(sources),'headline_ratios':{
       'seed':comps[0]['ratio'],'row':late['row']['ratio'],'equation':eq['complete_seconds']['ratio'],
       'transfer':transfer['geometric_mean_learned_to_native'],'cumulative_speedup':cc['speedup']}}))
if __name__=='__main__':main()
