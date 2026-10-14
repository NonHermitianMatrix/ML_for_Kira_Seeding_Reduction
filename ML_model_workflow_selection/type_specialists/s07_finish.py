"""Run frozen tests, check the public application, and produce the final plot."""
import json,subprocess,sys,time
import s04_train_test as model
st=model.st
def main():
 cases=model.prepare();f=json.loads((st.HERE/'trained_model/freeze.json').read_text());model.test(cases,f)
 checks=[]
 import sympy as sp
 for k in st.KINDS:
  c=next(c for c in cases if c['split']=='reserved' and c['topology_group']==k);ref=st.read(st.reference(c))
  inp=st.HERE/'model_test'/f'{k}_public_input.json';out=st.HERE/'model_test'/f'{k}_public_output.json.gz'
  st.write(inp,dict(case=c,basis=ref['masters']))
  if not out.exists():
   begin=time.perf_counter();p=subprocess.run([sys.executable,str(st.HERE/'s06_reduce.py'),'--input',str(inp),'--output',str(out)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=420)
   st.write(st.HERE/'model_test'/f'{k}_public_execution.json',dict(returncode=p.returncode,stdout=p.stdout,cold_cli_seconds=time.perf_counter()-begin));assert p.returncode==0,p.stdout
  r=st.read(out);assert r['success'] and not r['reference_coefficients_supplied'];got=r['attempts'][-1]['coefficients'];assert set(got)==set(ref['coefficients']);n=0
  for t,row in got.items():
   expected=ref['coefficients'][t]
   for m in set(row)|set(expected):
    a,b=row.get(m,'0'),expected.get(m,'0')
    assert a==b or sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))==0
    n+=1
  checks.append(dict(case=c['id'],success=True,coefficient_checks=n))
 st.write(st.HERE/'model_test/public_checks.json',dict(complete=True,all_exact=True,cases=checks))
 import s05_analyze;s05_analyze.main()
 import s08_validate;s08_validate.main()
if __name__=='__main__':main()
