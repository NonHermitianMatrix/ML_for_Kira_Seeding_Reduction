"""Freeze new two-point targets and native ML controls before timing."""
from s00_prop_common import *
from s03_prop_cases import case

def main():
    assert read(HERE/'development.json')['complete']
    cases=[]
    for L in range(1,14):
        for shape in (['star'] if L<3 else ['star','chain'] if L==3 else ['star','chain','branched']):
            c=case(L,shape,5011);c['test_group']='propagator';cases.append(c)
    make=load('prop_triangle_cases',TREE/'s03_cases.py').tree_case
    for L in range(1,14):
        c=make(L,'chain',5013,True);c['test_group']='triangle';cases.append(c)
    many=load('prop_large_triangle_cases',PREVIOUS/'s03_pilot.py').case
    for shape in ['star','chain','branched']:
        c=many(13,shape,5013,128,4);c['test_group']='triangle';cases.append(c)
    old=load('prop_frozen_earlier',TREE/'s02_runtime.py').prior()
    batches=load('prop_native_cases',old.HERE/'s03_cases.py').batches
    for c in batches(5017,'reserved'):
        c['test_group']='native';cases.append(c)
    p=dict(complete=True,cases=cases,repetitions=3,seconds_per_application=12,
           parent_commit='85ff665d3e0e563cef438270f9eea012cc050cfc',
           source_sha256={q.name:sha(q) for q in HERE.glob('s0*.py') if not q.name.startswith('s09')},
           preceding_exact_sha256=sha(PREVIOUS/'s01_gamma_cancellation.py'),
           prior_model_sha256=sha(old.HERE/'trained_model/policy.json'),
           control='same complete application without the new two-point identity; native requests also use all_fixed',
           scope='Connected massless two-point trees at every loop order 1..13; unchanged triangle checks and sixteen native two-loop ML controls.')
    write(HERE/'protocol.json.gz',p);print(json.dumps(dict(cases=len(cases),targets=sum(c['size'] for c in cases))))
if __name__=='__main__':main()
