"""Compare Kira worker counts on development inputs."""
import s01_study as w
def main():
 cs=w.cases(91,'development')
 configs=['previous','threads2','threads4']
 w.write(w.HERE/'development_cases.json',dict(cases=cs,configurations=configs))
 for c in cs:
  ref=w.reference(c);basis=w.read(ref)['masters']
  for cfg in configs:
   p=w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz'
   if p.exists():continue
   r=w.workflow(c,basis,cfg,ref);w.save(p,r)
   w.emit(stage='development',case=c['id'],config=cfg,seconds=r['complete_seconds'],success=r['success'],fallback=r['fallback_count'])
   assert r['success'],(c['id'],cfg)
 w.emit(stage='development_complete')
if __name__=='__main__':main()
