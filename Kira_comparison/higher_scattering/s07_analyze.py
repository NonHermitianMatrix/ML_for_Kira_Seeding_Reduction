"""Summarize complete comparisons and retain unsuccessful calculations."""
import collections,gzip,hashlib,json,math,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.load(gzip.open(p,'rt'))
def gm(v):return math.exp(statistics.mean(math.log(x) for x in v))
def status(r):
    text=r.get('log',r.get('failure_log_tail',''))
    if 'More than 31 propagators' in text:return 'propagator_limit'
    if 'bad_alloc' in text:return 'allocation_limit'
    return r.get('status','unknown')
def collect(base):return [read(p) for p in sorted(base.glob('*.json.gz'))]

def main():
    protocol=json.loads((HERE/'ablation_protocol.json').read_text())
    records=collect(HERE/'ablation_test');grouped=collections.defaultdict(list)
    for r in records:grouped[(r['case'],r['method'])].append(r)
    cases=[];excluded=[]
    for c in protocol['cases']:
        ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
        if not check.exists() or not read(check)['success']:
            excluded.append(dict(case=c['id'],reason=status(read(check if check.exists() else ref))));continue
        medians={};methods={}
        for method in protocol['methods']:
            rows=grouped[(c['id'],method)]
            assert len(rows)==protocol['repetitions'],(c['id'],method,len(rows))
            ok=all(r['success'] and r['reference_checked'] and not r['mismatches'] for r in rows)
            methods[method]=dict(successful=sum(r['success'] for r in rows),trials=len(rows),
                fallbacks=sum(r.get('fallback_count',0) for r in rows),cpu_seconds=sum(r['cpu_seconds'] for r in rows),
                decisions=[dict(choice=r['choice'],reason=r['selection_reason']) for r in rows])
            if ok:medians[method]=statistics.median(r['complete_seconds'] for r in rows)
        cases.append(dict(case=c['id'],topology=c['topology_group'],loops=len(c['definition']['loop_momenta']),
                          targets=c['size'],median_seconds=medians,methods=methods))
    pairs=[(m,'native') for m in protocol['methods'] if m!='native']
    pairs += [('graph_model','graph_fixed'),('seed_model','seed_fixed'),('worker_model','worker_fixed'),
              ('seed_model','graph_model'),('worker_model','seed_model')]
    comparisons={}
    for num,den in pairs:
        good=[c for c in cases if num in c['median_seconds'] and den in c['median_seconds']]
        ratios=[c['median_seconds'][num]/c['median_seconds'][den] for c in good]
        if not ratios:continue
        comparisons[num+'_to_'+den]=dict(numerator=num,denominator=den,cases=len(good),ratio=gm(ratios),
             range=[min(ratios),max(ratios)],numerator_sum=sum(c['median_seconds'][num] for c in good),
             denominator_sum=sum(c['median_seconds'][den] for c in good))
    by_family={}
    for k in sorted({c['topology'] for c in cases}):
        rows=[c for c in cases if c['topology']==k]
        by_family[k]=dict(loops=rows[0]['loops'],cases=len(rows),seconds={m:sum(c['median_seconds'][m] for c in rows)
             for m in protocol['methods'] if all(m in c['median_seconds'] for c in rows)})
    pilot=[]
    for p in sorted((HERE/'development').glob('*.gz')):
        r=read(p);pilot.append(dict(case=r['case'],status=status(r),success=r['success'],
             seconds=r['complete_seconds'],peak_rss_bytes=r['peak_rss_bytes'],peak_scratch_bytes=r['peak_scratch_bytes'],
             generation_reached=bool(r.get('equation_metrics')),log_tail=r.get('log','')[-500:]))
    parity=collect(HERE/'parity');high=collect(HERE/'higher_test')
    hp=json.loads((HERE/'sector_protocol.json').read_text());higher=[]
    import s03_ablation as a
    guards=[]
    for c in hp['cases']+json.loads((HERE/'protocol.json').read_text())['cases']:
        choices={key:model.select(f,c) for key,model,f in [('graph',a.gm,a.GF),('seed',a.bm,a.BF),('workers',a.tm,a.TF)]}
        assert choices['graph'][0]=='native' and choices['seed'][0]==choices['workers'][0]=='previous',choices
        guards.append(dict(case=c['id'],choices=choices,vacuum_recurrence_applicable=False))
    for c in hp['cases']:
        ref=HERE/'higher_references'/(c['id']+'.json.gz');check=HERE/'higher_references'/(c['id']+'_check.json.gz')
        rr=read(ref);cr=read(check) if check.exists() else None
        rows=[r for r in high if r['case']==c['id']];ms={}
        for method in hp['methods']:
            trials=[r for r in rows if r['method']==method]
            if trials:
                ms[method]=dict(trials=len(trials),successful=sum(r['success'] for r in trials),
                    all_exact=all(r['success'] and r['reference_checked'] for r in trials),
                    fallbacks=sum(r.get('fallback_count',0) for r in trials),
                    statuses=[status(r['attempts'][-1]) for r in trials])
                if len(trials)==hp['repetitions'] and ms[method]['all_exact']:
                    ms[method]['median_seconds']=statistics.median(r['complete_seconds'] for r in trials)
                attempts=[at for r in trials for at in r['attempts']]
                stages=sorted({k for at in attempts for k in at.get('stage_totals',{})})
                ms[method]['stage_median_seconds']={k:statistics.median(sum(at.get('stage_totals',{}).get(k,0) for at in r['attempts']) for r in trials) for k in stages}
                metrics=[at['equation_metrics'] for at in attempts if at.get('equation_metrics')]
                if metrics:
                    ms[method]['equation_counts']=metrics[0]
                    ms[method]['median_filter_seconds']=statistics.median(at['equation_metrics']['filter_seconds'] for at in attempts if at.get('equation_metrics'))
        higher.append(dict(case=c['id'],kind=c['topology_group'],loops=len(c['definition']['loop_momenta']),
             physical_propagators=c['definition']['physical_propagators'],independent_propagators=len(c['definition']['propagators']),
             reference_status=status(rr),reference_seconds=rr['complete_seconds'],check_status=status(cr) if cr else 'not_reached',
             nonidentity_targets=sum(bool(row) and row!={t:'1'} for t,row in rr.get('coefficients',{}).items()),methods=ms))
    ep=json.loads((HERE/'extended_protocol.json').read_text());extended=[]
    for c in ep['cases']:
        ref=HERE/'extended_references'/(c['id']+'.json.gz');rr=read(ref)
        check=HERE/'extended_references'/(c['id']+'_check.json.gz');cr=read(check) if check.exists() else None
        methods={}
        for method in ep['methods']:
            rows=[read(p) for p in sorted((HERE/'extended_test').glob(c['id']+'_'+method+'_*.json.gz'))]
            if not rows:continue
            methods[method]=dict(trials=len(rows),successful=sum(r['success'] for r in rows),
                 all_exact=all(r['success'] and r['reference_checked'] for r in rows),fallbacks=sum(r['fallback_count'] for r in rows))
            if len(rows)==ep['repetitions'] and methods[method]['all_exact']:
                methods[method]['median_seconds']=statistics.median(r['complete_seconds'] for r in rows)
        row=HERE/'extended_test'/(c['id']+'_row_probe.json.gz');row=read(row) if row.exists() else None
        extended.append(dict(case=c['id'],kind=c['topology_group'],loops=len(c['definition']['loop_momenta']),
            reference_status=status(rr),reference_seconds=rr['complete_seconds'],check_status=status(cr) if cr else 'not_reached',
            methods=methods,row_probe=dict(status=status(row),seconds=row['complete_seconds'],success=row['success']) if row else None))
    mp=json.loads((HERE/'memory_protocol.json').read_text());memory=[]
    for c in mp['cases']:
        ref=HERE/'memory_references'/(c['id']+'.json.gz')
        if not ref.exists():
            assert (HERE/'pause.json').exists()
            memory.append(dict(case=c['id'],kind=c['topology_group'],loops=len(c['definition']['loop_momenta']),reference_status='paused_before_start',reference_seconds=None,check_status='not_reached',check_seconds=None,methods={}))
            continue
        rr=read(ref)
        check=HERE/'memory_references'/(c['id']+'_check.json.gz');cr=read(check) if check.exists() else None
        methods={}
        for method in mp['methods']:
            rows=[read(p) for p in sorted((HERE/'memory_test').glob(c['id']+'_'+method+'_*.json.gz'))]
            if not rows:continue
            methods[method]=dict(trials=len(rows),successful=sum(r['success'] for r in rows),
                all_exact=all(r['success'] and r['reference_checked'] for r in rows),fallbacks=sum(r['fallback_count'] for r in rows))
            methods[method]['completed_seconds']=[r['complete_seconds'] for r in rows]
            methods[method]['insufficient_basis_attempts']=sum('check_masters: found additional master integrals' in at.get('failure_log_tail','') for r in rows for at in r['attempts'])
            if len(rows)==mp['repetitions'] and methods[method]['all_exact']:
                methods[method]['median_seconds']=statistics.median(r['complete_seconds'] for r in rows)
        memory.append(dict(case=c['id'],kind=c['topology_group'],loops=len(c['definition']['loop_momenta']),
            reference_status=status(rr),reference_seconds=rr['complete_seconds'],check_status=status(cr) if cr else 'not_reached',
            check_seconds=cr['complete_seconds'] if cr else None,methods=methods))
    cp=json.loads((HERE/'choice_control_protocol.json').read_text());choice_records=collect(HERE/'choice_control_test')
    assert len(choice_records)==len(cp['plan'])*cp['repetitions']*2
    choice_cases=[]
    for item in cp['plan']:
        stage=item['stage'];c=item['case'];rows=[r for r in choice_records if r['stage']==stage and r['case']==c['id']]
        d={m:[r for r in rows if r['comparison_method']==m] for m in ['selected','control']}
        assert all(len(v)==3 and all(r['success'] and r['reference_checked'] for r in v) for v in d.values())
        times={m:statistics.median(r['complete_seconds'] for r in v) for m,v in d.items()}
        choice_cases.append(dict(stage=stage,case=c['id'],seconds=times,ratio=times['selected']/times['control'],
             selected_choices=[r['choice'] for r in d['selected']],control_choices=[r['choice'] for r in d['control']]))
    choice_summary={}
    for stage in ['graph','seed','worker']:
        rows=[c for c in choice_cases if c['stage']==stage]
        choice_summary[stage]=dict(cases=len(rows),ratio=gm([c['ratio'] for c in rows]),
             selected_sum=sum(c['seconds']['selected'] for c in rows),control_sum=sum(c['seconds']['control'] for c in rows))
    allrefs=list((HERE/'higher_references').glob('*.gz'))+list((HERE/'extended_references').glob('*.gz'));allcases=list((HERE/'references').glob('*.gz'))
    summary=dict(complete=True,paused_study=json.loads((HERE/'pause.json').read_text()),scope='Completed evidence summarized after the user paused remaining comparisons for model redesign. Finite connected four-point test families; no claim for every scattering integral.',
        ablation=dict(cases=cases,by_family=by_family,comparisons=comparisons,excluded=excluded,trials=len(records),
                      successful=sum(r['success'] for r in records),coefficient_checks=sum(r.get('coefficient_checks',0) for r in records)),
        pilot=pilot,higher_cases=higher,extended_cases=extended,memory_cases=memory,policy_guards=guards,higher_trials=len(high),higher_successful=sum(r['success'] for r in high),
        choice_controls=dict(cases=choice_cases,summary=choice_summary,trials=len(choice_records),all_exact=True),
        parity_trials=len(parity),parity_all_exact=bool(parity) and all(r['success'] and r['reference_checked'] for r in parity),
        reference_trials=len(allrefs)+len(allcases),new_models_trained=False,
        uncertainty='Three repetitions per completed arm. Ranges describe tested cases, not confidence intervals.',
        source_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))},
        storage=json.loads((HERE/'resource_plan.json').read_text()))
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'report/higher_scattering_data.json').write_text(json.dumps(summary,indent=2)+'\n')
    plot(summary)
    print(json.dumps(dict(complete=True,ablation_trials=len(records),higher_trials=len(high),parity_trials=len(parity),comparisons=comparisons)),flush=True)

def plot(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    labels={'graph_fixed':'Fixed graph strategy','graph_model':'Learned graph strategy','seed_fixed':'Graph + fixed seed limits',
      'seed_model':'Graph + learned seed limits','worker_fixed':'Prior stages + fixed workers','worker_model':'Full selected method',
      'equation_filter':'Equation filter','seed_filter':'Seed filter','row_model':'Row model'}
    fig,axes=plt.subplots(2,1,figsize=(7.4,6.5),gridspec_kw={'height_ratios':[2.3,1]},constrained_layout=True)
    comp=dict(data['ablation']['comparisons'])
    keys=[m+'_to_native' for m in labels if m+'_to_native' in comp]
    choices=data['choice_controls']['summary']
    for stage,v in choices.items():
        comp[stage+'_isolated']=dict(numerator=stage+'_model',denominator='matched_control',ratio=v['ratio'],
          numerator_sum=v['selected_sum'],denominator_sum=v['control_sum'])
    for ax,ks,title in [(axes[0],keys,'Complete time relative to native choices'),
                        (axes[1],[k+'_isolated' for k in ['graph','seed','worker']],'Changing only the learned decision')]:
        ks=[k for k in ks if k in comp];xs=[comp[k]['numerator_sum']/comp[k]['denominator_sum'] for k in ks]
        ax.axvline(1,color='0.4',lw=1,ls='--')
        ax.scatter(xs,range(len(xs)),color='#145b83',s=43,zorder=3)
        names=labels if ax is axes[0] else {'graph_model':'Learned graph strategy','seed_model':'Learned seed expansion','worker_model':'Learned worker count'}
        ax.set_yticks(range(len(ks)));ax.set_yticklabels([names[comp[k]['numerator']] for k in ks]);ax.invert_yaxis()
        for i,x in enumerate(xs):ax.annotate(f'{x:.3f}',(x,i),xytext=(6,5),textcoords='offset points',fontsize=9)
        lo=min([1]+xs);hi=max([1]+xs);pad=max(.04,(hi-lo)*.2)
        ax.set_xlim(max(0,lo-pad),hi+2*pad);ax.grid(axis='x',alpha=.2)
        ax.set_xlabel('Workload time ratio (below 1 is faster)');ax.set_title(title,fontsize=11,pad=12)
    fig.savefig(ROOT/'report/paper_figures/component_ablation.pdf');plt.close(fig)
if __name__=='__main__':main()
