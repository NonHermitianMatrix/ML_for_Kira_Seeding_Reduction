"""Check seven consecutive requests through the persistent public worker."""
import json,os,subprocess,sys,time
from pathlib import Path
import s05_fit as model
w=model.w

def main():
 assert int(os.environ.get('NSLOTS','1'))==2,'Check the retained policy in a two-core allocation'
 requests=[json.loads((w.HERE/'model_test'/f'{kind}_public_input.json').read_text()) for kind in w.st.KINDS]
 data=''.join(json.dumps(r,separators=(',',':'))+'\n' for r in requests)
 begin=time.perf_counter()
 run=subprocess.run([sys.executable,str(w.HERE/'s15_worker.py')],input=data,capture_output=True,text=True,timeout=600)
 elapsed=time.perf_counter()-begin
 assert run.returncode==0,(run.returncode,run.stderr[-4000:])
 rows=[json.loads(line) for line in run.stdout.splitlines()];assert len(rows)==len(requests)==7
 records=[]
 for request,row in zip(requests,rows):
  case=request['case'];result=row['result'];assert row['case']==case['id']
  assert result['success'] and result['reused_loaded_model'] and result['reference_coefficients_supplied'] is False
  duration=result['application_seconds'];w.verify(case,result,request['basis'],w.reference(case));assert result['success']
  result['independent_exact_checks']=result['coefficient_checks']
  w.save(w.HERE/'model_test'/f'{case["topology_group"]}_worker_output.json.gz',result)
  records.append(dict(case=case['id'],success=True,configuration=result['configuration'],application_seconds=duration,coefficient_checks=result['coefficient_checks']))
 out=dict(complete=True,all_exact=True,applications=7,requests_in_one_worker=True,allocated_cores=2,reference_coefficients_supplied=False,
  external_wall_seconds=elapsed,cases=records,source_sha256=model.sha(w.HERE/'s15_worker.py'),checker_sha256=model.sha(Path(__file__)),freeze_sha256=model.sha(w.HERE/'trained_model/freeze.json'))
 w.write(w.HERE/'model_test/worker_checks.json',out);w.emit(stage='persistent_worker_checked',applications=7,all_exact=True,seconds=elapsed)
if __name__=='__main__':main()
