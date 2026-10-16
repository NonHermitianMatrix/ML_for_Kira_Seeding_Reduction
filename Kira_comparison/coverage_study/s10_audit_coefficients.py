"""Recheck saved vacuum exports with symbolic algebra and the independent oracle."""
import gzip,json,sys
from fractions import Fraction
from pathlib import Path
import sympy as sp
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_equation_selection/higher_loops'))
import s02_reduce as math
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def main():
    d,z=sp.symbols('d z');parsed={};oracles={};proved=set();checks=0;files=0;failed=[]
    def want(L,rho,b):
        key=(L,tuple(rho),tuple(b))
        if key not in oracles:oracles[key]={j:math.canonical(p) for j,p in math.oracle(L,rho,tuple(b)).items()}
        return oracles[key]
    for p in sorted((HERE/'vacuum_test').glob('*.json.gz')):
        r=read(p)
        if not r['success']:failed.append(p.name);continue
        c=r['request'];files+=1
        if r['mode']=='recurrence':
            for L,rows in r['coefficients'][c['id']].items():
                for b,row in zip(c['targets'],rows):
                    expected=want(int(L),c['mass_ratios'],b)
                    got={int(j):math.canonical(tuple(Fraction(a,b) for a,b in poly)) for j,poly in row.items()}
                    for j in set(got)|set(expected):assert got.get(j,())==expected.get(j,());checks+=1
        else:
            for a in r['attempts']:
                if 'raw_export' not in a:continue
                rows=math.parse(a['raw_export']);loops=c['loops'] if a['loop'] is None else [a['loop']]
                for L in loops:
                    for i,b in enumerate(c['targets']):
                        expected=want(L,c['mass_ratios'],b);got=rows[a['target_start']+i]
                        for j in set(got)|set(expected):
                            text=got.get(j,'0');poly=expected.get(j,());key=(text,a['loop'] is None,L,poly)
                            if key not in proved:
                                if text not in parsed:parsed[text]=sp.sympify(text.replace('^','**'),rational=True)
                                expr=parsed[text].subs(z,L*(d-2)) if a['loop'] is None else parsed[text]
                                target=sum(sp.Rational(x.numerator,x.denominator)*d**n for n,x in enumerate(poly))
                                assert sp.cancel(expr-target)==0,(p.name,L,b,j)
                                proved.add(key)
                            checks+=1
    result=dict(complete=True,successful_files=files,failed_files=failed,coefficient_comparisons=checks,distinct_symbolic_equalities=len(proved),all_successful_saved_outputs_verified=True,method='Parse saved Kira exports with SymPy and compare exact polynomials to the independent analytic oracle; compare the stored recurrence coefficient arrays directly.')
    (HERE/'coefficient_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
