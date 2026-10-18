"""Check the unified application without giving it reference coefficients."""
from s00_common import *
from s14_prepare import equal
import subprocess

def main():
 folder=HERE/'optional_basis_checks';folder.mkdir(exist_ok=True);rows=[]
 candidates=[(READ(HERE/'application_checks/public_scalar_L12_case.json'),READ(HERE/'application_checks/public_scalar_L12_reference.json.gz'),False)]
 for c in READ(HERE/'recovery/protocol.json')['cases']:
  f=HERE/'recovery/model_test'/(c['id']+'_cached_learned_r0.json.gz');r=READ(f)
  if r['success'] and r.get('basis_refreshed'):
   candidates.append((c,r,READ(HERE/'preparation/deployment.json')['preparation_method']=='learned'));break
 if len(candidates)<2:
  for c in READ(HERE/'recovery/protocol.json')['cases']:
   r=READ(HERE/'recovery/model_test'/(c['id']+'_cached_learned_r0.json.gz'))
   if r['success']:candidates.append((c,r,READ(HERE/'preparation/deployment.json')['preparation_method']=='learned'));break
 assert len(candidates)==2
 for c,reference,ml in candidates:
  cp=folder/(c['id']+'_case.json');out=folder/(c['id']+'_output.json.gz');write(cp,c)
  if not out.exists():
   tick=time.perf_counter();subprocess.run([sys.executable,str(HERE/'s22_reduce.py'),'--case',str(cp),'--output',str(out)],check=True,timeout=145)
   r=READ(out);r['complete_process_seconds']=time.perf_counter()-tick;write(out,r)
  r=READ(out);assert r['success'] and r['model_used']==ml
  agree,checks=equal(r['coefficients'],reference['coefficients']);assert agree
  rows.append(dict(case=c['id'],model_used=ml,basis_refreshed=r.get('basis_refreshed',False),route=r['route'],coefficient_checks=checks,seconds=r['complete_process_seconds']))
 write(folder/'summary.json',dict(complete=True,all_exact=True,cases=rows,no_basis_or_reference_coefficients_supplied=True,scope='Interface checks on previously defined cases. No additional timing-speedup or coverage claim.'))
 (folder/'README.md').write_text('# Optional basis interface checks\n\n`s23_check_optional_basis.py` calls the public `s22_reduce.py` application. It supplies a family and targets, with no basis or reference coefficients.\nIt checks a scalar twelve-loop case against the independent recurrence output and a native case against the recorded recovery result.\nThe reference coefficients enter only the comparison after the application exits. These are interface checks, not a new timing benchmark.\nRead the main general_policy guide for commands and limits.\n')
 print('OPTIONAL BASIS CHECKS',len(rows),flush=True)

if __name__=='__main__':main()
