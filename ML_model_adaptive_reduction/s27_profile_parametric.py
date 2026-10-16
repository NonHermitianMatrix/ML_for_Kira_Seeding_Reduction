"""Keep bounded phase logs for the development four-loop calculation."""
import json
import s24_parametric_runtime as app
def main():
    cases=json.loads((app.HERE/'cases.json').read_text())['cases']
    c=next(c for c in cases if c['id']=='bubble_box4_p301')
    ref=app.HERE/'references'/(c['id']+'.json.gz');basis=app.rt.read(ref)['masters']
    for enabled in [False,True]:
        with app.projected(enabled):r=app.rt.attempt(c,basis,reference=ref)
        r['phase_summary']=[l for l in r['log'].splitlines() if l.startswith(('***','( ','Total time','Parametric')) or 'seconds' in l.lower()]
        app.rt.save(app.OUT/'development'/('profile_'+str(enabled)+'.json.gz'),app.rt.compact(r))
        print(json.dumps(dict(enabled=enabled,seconds=r['complete_seconds'],success=r['success'],phases=r['phase_summary'],stages=[x for x in r['stage_metrics'] if x['stage']=='parametric_construction'])),flush=True)
        assert r['success']
if __name__=='__main__':main()
