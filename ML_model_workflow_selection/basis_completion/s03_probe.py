"""Measure new strategies only on the development profile."""
import s01_workflow as w

def main():
 configs=['previous','completion','completion_full','delta_100','delta_010','delta_001','delta_101','delta_110','delta_011']
 cs=w.cases(71,'development')
 cs.sort(key=lambda c:(c['topology_group'] not in ['ladder3','nonplanar_box','double_box'],c['id']))
 w.write(w.HERE/'development_cases.json',dict(cases=cs,configurations=configs))
 for c in cs:
  ref=w.reference(c);basis=w.read(ref)['masters']
  for cfg in configs:
   p=w.HERE/'development'/f'{c["id"]}_{cfg}.json.gz'
   if p.exists():continue
   r=w.workflow(c,basis,cfg,ref);w.save(p,r)
   w.emit(stage='development',case=c['id'],configuration=cfg,seconds=r['complete_seconds'],success=r['success'],fallback=r['fallback_count'],temporary=len(r.get('temporary_masters',[])))
   assert r['success'],(c['id'],cfg,r.get('mismatches'))
if __name__=='__main__':main()
