"""Apply the frozen route with target data and a prescribed master basis."""
import argparse,json,time
from pathlib import Path
import s06_test as test
w=test.w
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 assert a.output.resolve().is_relative_to((w.HERE/'model_test').resolve())
 begin=time.perf_counter();data=json.loads(a.input.read_text());c=data['case'];basis=data['basis']
 assert 0<c['size']==len(c['targets'])<=128
 f=json.loads((w.HERE/'trained_model/freeze.json').read_text());test.model.check_freeze(f)
 r=test.application(c,basis,f);r['application_seconds']=time.perf_counter()-begin
 w.save(a.output,r);w.emit(success=r['success'],configuration=r['configuration'],seconds=r['application_seconds'])
 if not r['success']:raise SystemExit(2)
if __name__=='__main__':main()
