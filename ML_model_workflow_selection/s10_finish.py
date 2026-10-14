"""Run frozen tests, public application checks and joint-request comparisons."""
import copy,json,os,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
import s05_study as s
sys.path.insert(0,str(HERE))
import s08_reduce as app

def main():
 manifest=json.loads((HERE/'cases.json').read_text());f=json.loads((HERE/'trained_model/freeze.json').read_text())
 for c in manifest['cases']:
  if c['split']=='reserved':
   cfg,reason=app.select(copy.deepcopy(c),f,manifest)
   assert cfg==s.choose(f['model'],c,f['gate']),(c['id'],cfg,reason)
 s.test(manifest['cases'])
 import s07_analyze
 s07_analyze.main()
 checks=[]
 for c in manifest['cases']:
  if c['split']!='reserved' or not ('_p44_' in c['id'] and c['size']>4 or c['definition']['invariants']):continue
  out=HERE/'model_test'/('public_'+c['id']+'.json.gz')
  ref=s.read(HERE/'references'/(c['id']+'.json.gz'))
  if not out.exists():
   with tempfile.TemporaryDirectory(prefix='kira_public_',dir=os.environ['TMPDIR']) as td:
    td=Path(td);(td/'case.json').write_text(json.dumps(c));(td/'basis.json').write_text(json.dumps(ref['masters']))
    begin=time.perf_counter();subprocess.run([sys.executable,str(HERE/'s08_reduce.py'),'--input',str(td/'case.json'),'--basis',str(td/'basis.json'),'--output',str(out)],check=True,timeout=400)
    r=s.read(out);r['cold_process_seconds']=time.perf_counter()-begin;s.save(out,r)
  r=s.read(out);assert r['success'] and r['answers_withheld'];got=r['attempts'][-1]['coefficients'];assert got.keys()==ref['coefficients'].keys()
  import sympy as sp
  count=0
  for target,row in got.items():
   want=ref['coefficients'][target]
   for m in set(row)|set(want):
    a,b=row.get(m,'0'),want.get(m,'0');assert a==b or sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))==0;count+=1
  checks.append(dict(case=c['id'],passed=True,coefficient_checks=count,configuration=r['configuration'],cold_process_seconds=r['cold_process_seconds']))
 s.write(HERE/'model_test/public_application_checks.json',dict(complete=True,all_exact=True,cases=checks))
 import s09_batching
 s09_batching.main()
 s.emit(stage='all_tests_and_analysis_complete')
if __name__=='__main__':main()
