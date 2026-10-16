"""Use broader fresh massive two-point batches after identity-only initial outputs."""
import itertools,json
from pathlib import Path
import s01_study as study
from s00_cases import case,write,sha
HERE=Path(__file__).resolve().parent;OUT=HERE/'nontrivial_followup'
def make():
    cases=[]
    for L,symbolic in [(L,False) for L in range(1,7)]+[(1,True),(2,True)]:
        c=case('propagator_massive',L,symbolic,h=419 if not symbolic else 420)
        p=c['definition']['physical_propagators'];N=len(c['definition']['propagators']);a=[1]*p+[0]*(N-p)
        targets=[a]
        for i in range(p):
            for dots in [1,2]:t=a.copy();t[i]+=dots;targets.append(t)
        for i,j in itertools.combinations(range(p),2):t=a.copy();t[i]+=1;t[j]+=1;targets.append(t)
        c.update(targets=targets,size=len(targets),shape='all_physical_dots_through_two',loops=L,scalar_product_count=N,preflight='eligible',coverage_stage='nontrivial_followup')
        cases.append(c)
    return cases
def bounds(c,check=False):return [c['definition']['physical_propagators']+2,2 if check else 1,2]
def main():
    OUT.mkdir(exist_ok=True);cases=make()
    protocol=dict(cases=cases,methods=study.METHODS,repetitions=3,
        source_sha256=sha(Path(__file__)),base_study_sha256=sha(HERE/'s01_study.py'),
        reason='Initial massive two-point requests can be retained entirely as masters. These separate batches include every distribution of up to two dots over physical lines; all supported loop orders are included, regardless of their initial outcome.',
        policy='No model refitting, threshold changes or deployment selection. Preserve the initial study. Freeze the complete follow-up before its calculations.',
        references='Fresh rational profile 419 or independent symbolic masses, r=n+2,s=1,dots=2; independent previous-build check raises s to two.',
        time='The same six methods and timing rules as the initial study. Each loop order one through six has its own rational request; one and two loops also have symbolic requests.')
    path=OUT/'protocol.json'
    if path.exists():assert json.loads(path.read_text())==protocol
    else:write(path,protocol)
    study.HERE=OUT;study.bounds=bounds
    client=study.app.Reducer()
    try:
        with study.bounded():
            for c in cases:study.process(c,client)
    finally:client.close()
    write(OUT/'completion.json',dict(complete=True,cases=len(cases)))
    print('NONTRIVIAL_FOLLOWUP_COMPLETE',flush=True)
if __name__=='__main__':main()
