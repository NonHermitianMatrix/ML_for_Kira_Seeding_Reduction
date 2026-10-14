"""Check the public entry point without supplying target coefficients."""
import json,subprocess,sys,time
import s05_fit as model
w=model.w
def main():
 f=json.loads((w.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 cs=json.loads((w.HERE/'protocol.json').read_text())['cases'];records=[]
 for k in w.st.KINDS:
  c=next(c for c in cs if c['split']=='reserved' and c['topology_group']==k)
  ref=w.reference(c);basis=w.read(ref)['masters'];inp=w.HERE/'model_test'/f'{k}_public_input.json';out=w.HERE/'model_test'/f'{k}_public_output.json.gz'
  w.write(inp,dict(case=c,basis=basis))
  start=time.perf_counter();run=subprocess.run([sys.executable,str(w.HERE/'s07_reduce.py'),'--input',str(inp),'--output',str(out)],capture_output=True,text=True,timeout=600)
  elapsed=time.perf_counter()-start
  assert run.returncode==0,(run.returncode,run.stderr[-4000:])
  r=w.read(out);assert r['success'] and r['reference_coefficients_supplied'] is False
  w.verify(c,r,basis,ref);assert r['success']
  records.append(dict(case=c['id'],success=True,configuration=r['configuration'],external_wall_seconds=elapsed,coefficient_checks=r['coefficient_checks']))
 w.write(w.HERE/'model_test/public_checks.json',dict(complete=True,all_exact=True,cases=records))
 w.emit(stage='public_checks',cases=len(records),all_exact=True)
if __name__=='__main__':main()
