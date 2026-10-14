"""Apply the frozen graph-specific policy with a prescribed master basis."""
import argparse,json,time
from pathlib import Path
import s04_train_test as model
st=model.st
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 assert a.output.resolve().is_relative_to((st.HERE/'model_test').resolve())
 start=time.perf_counter();data=json.loads(a.input.read_text());c=data['case'];basis=data['basis']
 assert c['size']==len(c['targets']) and c['size']<=128
 f=json.loads((st.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 cfg,reason=model.select(f,c);r=st.workflow(c,None,cfg,basis=basis)
 r.update(application_seconds=time.perf_counter()-start,selection_reason=reason,reference_coefficients_supplied=False)
 st.save(a.output,r);st.emit(success=r['success'],configuration=cfg,reason=reason,seconds=r['application_seconds'])
 if not r['success']:raise SystemExit(2)
if __name__=='__main__':main()
