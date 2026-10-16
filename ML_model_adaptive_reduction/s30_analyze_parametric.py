"""Audit complete comparisons and draw figures from the retained measurements."""
import collections,json,statistics
import s24_parametric_runtime as app
from s26_parametric_study import METHODS,write
P=app.policy;rt=app.rt;OUT=app.OUT;HERE=app.HERE;ROOT=app.ROOT
NAMES={'sunrise':'Sunrise (2 loops)','double_box':'Planar double box (2)', 'vacuum3':'Vacuum (3)',
 'ladder3':'Two-point ladder (3)','nonplanar_box':'Nonplanar box (2)','pentagon':'Pentagon (1)',
 'one_mass_box':'Virtuality box (1)','bubble_box3':'Bubble box (3)','bubble_box4':'Bubble box (4)'}
def main():
    protocol=json.loads((OUT/'protocol.json').read_text());assert json.loads((OUT/'completion.json').read_text())['complete']
    for n,h in protocol['sources'].items():assert P.study.sha(HERE/n)==h,n
    assert P.study.sha(P.OUT/'trained_model/freeze.json')==protocol['model_sha256']
    assert P.study.sha(ROOT/'.tools/kira-parametric/kira')==protocol['binary_sha256']
    earlier=json.loads((P.OUT/'protocol.json').read_text())
    assert P.study.sha(HERE/'trained_model/graph_gate.json')==earlier['prior_freeze_sha256']
    def physical_request(c):
        d=c['definition']
        return json.dumps({k:d[k] for k in ['loop_momenta','external_momenta','propagators','scalarproduct_rules','top_level_sectors']}|{'targets':c['targets']},sort_keys=True)
    old_cases=earlier['cases']+json.loads((HERE/'cases.json').read_text())['cases']
    old_requests={physical_request(c) for c in old_cases}
    assert not ({physical_request(c) for c in protocol['cases']} & old_requests)
    zero=rt.read(OUT/'application_test/empty_basis.json.gz')
    assert zero['success'] and zero['analytic_zero_checked'] and len(zero['coefficients'])==1
    assert set(next(iter(zero['coefficients'])).split(','))=={'0'}
    unknown=rt.read(OUT/'application_test/unknown_graph.json.gz')
    assert unknown['success'] and unknown['reference_checked'] and unknown['action']=='native'
    assert json.loads((OUT/'application_test/guards.json').read_text())['complete']
    rows=[];checks=0;peak=0;replays=0;maxcache=0
    for c in protocol['cases']:
        name=c['id'];ref=rt.read(OUT/'references'/(name+'.json.gz'));check=rt.read(OUT/'references'/(name+'_check.json.gz'))
        assert ref['success'] and check['success'] and check['reference_checked']
        assert check['binary_sha256']==protocol['old_binary_sha256']
        checks+=check.get('coefficient_checks',0)
        example=rt.read(OUT/'applications'/(name+'.json.gz'))
        assert example['success'] and example['reference_checked'] and not example['reference_coefficients_supplied']
        checks+=example['coefficient_checks'];times={};cpu={};recover={};actions={};phases={};dispatch={}
        for method in METHODS:
            records=[rt.read(OUT/'model_test'/f'{name}_{method}_{r}.json.gz') for r in range(3)]
            assert all(r['success'] and r['reference_checked'] and not r['reference_coefficients_supplied'] for r in records)
            checks+=sum(r['coefficient_checks'] for r in records)
            times[method]=[r['complete_seconds'] for r in records];cpu[method]=[r['cpu_seconds'] for r in records]
            dispatch[method]=[r.get('decision_seconds',r.get('portfolio_decision_seconds',0.)) for r in records]
            recover[method]=sum(r.get('fallback_count',0) for r in records);actions[method]=[r['action'] for r in records]
            stages=collections.defaultdict(list)
            for r in records:
                stage=collections.defaultdict(float)
                for a in r['attempts']:
                    assert a['binary_sha256'] in [protocol['binary_sha256'],protocol['old_binary_sha256']]
                    peak=max(peak,a['peak_rss_bytes'])
                    for x in a.get('stage_metrics',[]):
                        stage[x['stage']]+=x.get('seconds',0.)
                        if x['stage']=='selected_equation_replay':
                            replays+=1;maxcache=max(maxcache,x['accounted_bytes']);assert x['accounted_bytes']<=4*1024**2 and x['rows']<=4096
                for k,v in stage.items():stages[k].append(v)
            phases[method]={k:statistics.median(v) for k,v in stages.items()}
        assert actions['selected']==actions['previous'],name
        rows.append(dict(case=name,graph=c['topology_group'],loops=len(c['definition']['loop_momenta']),times=times,cpu_times=cpu,
            medians={m:statistics.median(times[m]) for m in METHODS},cpu_medians={m:statistics.median(cpu[m]) for m in METHODS},
            recoveries=recover,actions=actions,stages=phases,dispatch_seconds=dispatch))
    totals={m:sum(r['medians'][m] for r in rows) for m in METHODS}
    alltimes={m:sum(sum(r['times'][m]) for r in rows) for m in METHODS}
    cputotals={m:sum(r['cpu_medians'][m] for r in rows) for m in METHODS}
    graphs={g:{m:sum(r['medians'][m] for r in rows if r['graph']==g) for m in METHODS} for g in NAMES}
    summary=dict(complete=True,all_exact=True,cases=rows,totals=totals,all_repetitions=alltimes,cpu_totals=cputotals,graphs=graphs,
        median_ratios={m:totals['selected']/totals[m] for m in METHODS},all_ratios={m:alltimes['selected']/alltimes[m] for m in METHODS},
        recoveries={m:sum(r['recoveries'][m] for r in rows) for m in METHODS},coefficient_checks=checks,timings=312,applications=26,
        maximum_rss_bytes=peak,replay_hits=replays,maximum_accounted_cache_bytes=maxcache,
        source_hashes=protocol['sources'],unchanged_models=True,previous_actions_identical=True,
        optimistic_control_totals={m:sum(statistics.median(a-b for a,b in zip(r['times'][m],r['dispatch_seconds'][m])) for r in rows) for m in ['native','fixed']},
        maximum_dispatch_seconds=max(max(r['dispatch_seconds'][m]) for r in rows for m in ['native','fixed','selected']),
        fresh_requests=True,protocol_sha256=P.study.sha(OUT/'protocol.json'))
    write(OUT/'summary.json',summary);write(ROOT/'report/parametric_data.json',summary)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
    order=sorted(graphs,key=lambda g:graphs[g]['previous'],reverse=True);y=np.arange(len(order))
    fig,axs=plt.subplots(1,2,figsize=(9.2,5.2),gridspec_kw={'width_ratios':[1.35,1]})
    ax=axs[0]
    ax.barh(y-.18,[graphs[g]['previous'] for g in order],height=.34,label='Previous implementation',color='#a6a6a6')
    ax.barh(y+.18,[graphs[g]['selected'] for g in order],height=.34,label='Revised implementation',color='#2166ac')
    ax.set_yticks(y);ax.set_yticklabels([NAMES[g] for g in order]);ax.invert_yaxis();ax.set_xlim(0,max(graphs[g][m] for g in order for m in ['previous','selected'])*1.12)
    ax.set_xlabel('Sum of batch medians (seconds)');ax.set_title('Same choices; less preparation',fontsize=11);ax.legend(fontsize=9,loc='lower right');ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    ax=axs[1];ratios=[graphs[g]['selected']/graphs[g]['fixed'] for g in order]
    ax.scatter(ratios,y,s=35,color='#2166ac');ax.axvline(1,color='black',ls='--',lw=1);ax.set_yticks(y);ax.set_yticklabels([]);ax.invert_yaxis()
    ax.set_xlim(min(.8,min(ratios)*.95),max(1.15,max(ratios)*1.05));ax.set_xlabel('Selected / fixed portfolio time');ax.set_title('Outer prediction vs fixed choices',fontsize=11);ax.grid(axis='x',alpha=.2)
    fig.tight_layout();fig.savefig(ROOT/'report/paper_figures/parametric_results.pdf');plt.close(fig)
    write(OUT/'validation.json',dict(complete=True,all_exact=True,unchanged_models=True,summary_sha256=P.study.sha(OUT/'summary.json'),
        figure_sha256=P.study.sha(ROOT/'report/paper_figures/parametric_results.pdf'),timings=312,applications=26))
    print(json.dumps(dict(totals=totals,ratios=summary['median_ratios'],all_ratios=summary['all_ratios'],checks=checks,graphs=graphs)),flush=True)
if __name__=='__main__':main()
