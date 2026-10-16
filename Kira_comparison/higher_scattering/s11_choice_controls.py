"""Disable only one learned choice while keeping its validation control."""
import json
import s03_ablation as a
from s06_sector_test import read,save,emit
HERE=a.HERE

def main():
    protocol=json.loads((HERE/'ablation_protocol.json').read_text())
    plan=[]
    for stage,model,f in [('graph',a.gm,a.GF),('seed',a.bm,a.BF),('worker',a.tm,a.TF)]:
        for c in protocol['cases']:
            if f['policies'][c['topology_group']]['enabled']:plan.append(dict(stage=stage,case=c))
    p=HERE/'choice_control_protocol.json'
    value=dict(plan=plan,repetitions=3,source_sha256=a.sha(__file__),
               purpose='Change only the current learned decision to its frozen validation control. Earlier stages remain identical.',
               frozen_models=protocol['frozen_models'])
    if p.exists():assert json.loads(p.read_text())==value
    else:p.write_text(json.dumps(value,indent=2)+'\n')
    for ci,item in enumerate(plan):
        stage=item['stage'];c=item['case'];ref=HERE/'references'/(c['id']+'.json.gz');basis=read(ref)['masters']
        model,f={'graph':(a.gm,a.GF),'seed':(a.bm,a.BF),'worker':(a.tm,a.TF)}[stage]
        original=model.select
        def control(frozen,case):
            p=frozen['policies'][case['topology_group']]
            assert model.structure(case)==p['structure']
            x=model.features(case)
            if any(v<lo or v>hi for v,lo,hi in zip(x,p['features_min'],p['features_max'])):
                return ('native' if stage=='graph' else 'previous'),'feature_range'
            cfg=p['validation_control']
            if stage=='graph':cfg=model.canonical(case,cfg)
            return cfg,'learned_choice_disabled'
        for rep in range(3):
            order=['selected','control'] if (ci+rep)%2==0 else ['control','selected']
            for method in order:
                out=HERE/'choice_control_test'/f'{stage}_{c["id"]}_{method}_{rep}.json.gz'
                if out.exists():continue
                try:
                    if method=='control':model.select=control
                    r=a.run(c,basis,stage+'_model',ref)
                finally:model.select=original
                r.update(stage=stage,comparison_method=method,repetition=rep)
                save(out,r);emit(stage='choice_control',choice=stage,case=c['id'],method=method,success=r['success'],seconds=r['complete_seconds'])
    emit(stage='choice_controls_complete')
if __name__=='__main__':main()
