"""Check exact selected-equation replay, bypass, and application guards."""
import copy,json,os
import s24_parametric_runtime as app
def main():
    cases=json.loads((app.HERE/'cases.json').read_text())['cases']
    for name in ['bubble_box4_p301','double_box_p301_mixed','nonplanar_box_symbolic_training','sunrise_p301_dots']:
        c=next(c for c in cases if c['id']==name);ref=app.HERE/'references'/(name+'.json.gz');basis=app.rt.read(ref)['masters']
        for mode in ['off','on']+(['tiny'] if name=='sunrise_p301_dots' else []):
            if mode=='tiny':os.environ['KIRA_SELECTED_CACHE_BYTES']='1'
            else:os.environ.pop('KIRA_SELECTED_CACHE_BYTES',None)
            with app.projected(replay=mode!='off'):r=app.rt.attempt(c,basis,reference=ref)
            hit=[x for x in r['stage_metrics'] if x['stage']=='selected_equation_replay']
            app.rt.save(app.OUT/'development'/f'replay_{name}_{mode}.json.gz',app.rt.compact(r))
            print(json.dumps(dict(case=name,mode=mode,seconds=r['complete_seconds'],success=r['success'],replay=hit)),flush=True)
            assert r['success']
            if mode in ['off','tiny']:assert not hit
            elif name=='bubble_box4_p301':assert hit
    os.environ.pop('KIRA_SELECTED_CACHE_BYTES',None)
    c=next(c for c in cases if c['id']=='sunrise_p301_dots')
    ref=app.HERE/'references'/(c['id']+'.json.gz');basis=app.rt.read(ref)['masters'];p=app.Reducer()
    try:
        unknown=dict(c,topology_group='unseen_parametric_graph')
        r=p.reduce(unknown,basis);app.rt.verify(c,r,ref)
        assert r['success'] and r['reference_checked'] and r['action']=='native'
        app.rt.save(app.OUT/'application_test/unknown_graph.json.gz',r)
        zero=copy.deepcopy(c);zero.update(id='parametric_scaleless',targets=[[0]*len(c['targets'][0])],size=1)
        r=p.reduce(zero,[]);assert r['success']
        import sympy as sp
        assert all(sp.cancel(sp.sympify(v.replace('^','**'),rational=True))==0 for row in r['coefficients'].values() for v in row.values())
        r['analytic_zero_checked']=True;app.rt.save(app.OUT/'application_test/empty_basis.json.gz',r)
        rejected=[]
        for kind in ['float_index','outside_sector','cut']:
            bad=copy.deepcopy(c)
            if kind=='float_index':bad['targets'][0][0]=1.2
            elif kind=='outside_sector':bad['targets'][0][-1]=1
            else:bad['definition']['cut_propagators']=[1]
            try:p.reduce(bad,basis)
            except AssertionError:rejected.append(kind)
        assert len(rejected)==3
        (app.OUT/'application_test/guards.json').write_text(json.dumps(dict(rejected=rejected,complete=True),indent=2)+'\n')
    finally:p.close()
    print('REPLAY_CHECKS_COMPLETE',flush=True)
if __name__=='__main__':main()
