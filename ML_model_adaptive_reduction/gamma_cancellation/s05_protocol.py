"""Freeze fresh power assignments before application comparisons."""
from s00_gamma_common import *
from s03_pilot import case

def main():
    assert read(HERE/'development.json')['complete']
    requests=[]
    make=load('cancellation_target_families',BASE/'s03_cases.py').tree_case
    for L in range(1,14):
        for shape in (['star'] if L<3 else ['star','chain'] if L==3 else ['star','chain','branched']):
            c=case(L,shape,4013,128,4);c['test_group']='large';requests.append(c)
            c=make(L,shape,4019,True);c['test_group']='small';requests.append(c)
    old=load('cancellation_previous_application',BASE/'s02_runtime.py').prior()
    h=old.legacy().h
    for kind in ['vacuum_one_mass','propagator_massless']:
        c=h.gen.case(kind,13,False,4027);c['test_group']='fallback';requests.append(c)
    mod=load('cancellation_native_batches',old.HERE/'s03_cases.py')
    native=mod.batches(4027,'reserved')
    for c in [native[0],native[8]]:
        c['test_group']='fallback';requests.append(c)
    assert len(requests)==72
    p=dict(complete=True,cases=requests,repetitions=5,seconds_per_application=20,
           parent_commit='881ad5a260b422ffb4634328680270f103968a7f',
           source_sha256={q.name:sha(q) for q in HERE.glob('s0*.py') if q.name[:3] in ['s00','s01','s02','s03','s05','s06']},
           preceding_exact_sha256=sha(BASE/'s01_bubble_tree.py'),
           prior_model_sha256=sha(old.HERE/'trained_model/policy.json'),
           control='same application with the preceding coefficient routine',
           scope='Defined connected massless bubble trees, fresh symbolic power batches at all orders one through thirteen; four unchanged-path regression cases.')
    write(HERE/'protocol.json.gz',p);print(json.dumps(dict(cases=len(requests),targets=sum(len(c['targets']) for c in requests))))
if __name__=='__main__':main()
