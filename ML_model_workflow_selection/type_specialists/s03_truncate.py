"""Probe native numerator truncation on development cases."""
import s00_study as study
from s02_native import run

def adapted(c,ref,config,margin=0,basis=None):
 if not config.startswith('truncate'):
  return original(c,ref,config,margin,basis)
 study.previous.study.setup('off')
 study.os.environ.update(KIRA_RUNTIME_BINARY=str(study.previous.BINARY),KIRA_EPHEMERAL_DB='1')
 rank=max(sum(max(0,-a) for a in t) for t in c['targets'])
 l=c['definition']['physical_propagators']-rank+int(config.replace('truncate',''))
 r=run(c,c['size'],'native',study.HERE/'unused',timeout=120,margin=margin,reference=ref,records=False,archive=False,
  check_masters=bool(ref or basis),scratch_cap=32*1024**2,ordering=1,basis=basis,truncate=l)
 r['configuration']=config
 return r
original=study.attempt
study.attempt=adapted

def main():
 for k in study.KINDS:
  for shape in ['top','numerator']:
   c=study.make_case(k,61,shape);ref=study.reference(c)
   for cfg in ['truncate0','truncate1','truncate-1']:
    p=study.HERE/'development'/f'{c["id"]}_{cfg}.json.gz'
    if p.exists():continue
    r=study.workflow(c,ref,cfg);study.save(p,r)
    study.emit(stage='truncation',case=c['id'],config=cfg,success=r['success'],fallback=r['fallback_count'],seconds=r['complete_seconds'])
    assert r['success']
if __name__=='__main__':main()
