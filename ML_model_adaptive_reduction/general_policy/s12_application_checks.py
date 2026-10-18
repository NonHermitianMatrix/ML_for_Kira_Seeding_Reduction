"""Check the public interface without supplying reference coefficients to it."""
from s00_common import *
import subprocess
PYTHON=ROOT/'.tools/seed-model/venv/bin/python'

def invoke(c,basis,reference,name):
 folder=HERE/'application_checks';folder.mkdir(exist_ok=True)
 cp=folder/(name+'_case.json');bp=folder/(name+'_basis.json');out=folder/(name+'_output.json.gz');write(cp,c);write(bp,basis)
 if out.exists() and READ(out).get('reference_checked'):return READ(out)
 begin=time.perf_counter();subprocess.run([str(PYTHON),str(HERE/'s11_reduce.py'),'--case',str(cp),'--basis',str(bp),'--output',str(out),'--method','learned'],stdout=subprocess.DEVNULL,check=True,timeout=240)
 r=READ(out);rt.verify(r,reference);r['fresh_application_with_check_seconds']=time.perf_counter()-begin;write(out,r);assert r['success'] and r['reference_checked'];return r

def main():
 import sympy as sp
 gen=module('general_interface_physics',ROOT/'Kira_comparison/coverage_study/s00_cases.py');dim=sp.Symbol('d');rows=[]
 for L in range(1,13):
  d=gen.definition('propagator_massless',L,1217);N=len(d['propagators']);P=L+1;a=[1]*P+[0]*(N-P);targets=[a.copy() for _ in range(3)];targets[1][0]+=1;targets[2][0]+=1;targets[2][P-1]+=2
  c=dict(id='public_scalar_L'+str(L),definition=d,targets=targets,size=3);basis=[a];ref={}
  for target in targets:
   powers=[1]*P;v=sp.Integer(1)
   for j in range(P):
    while powers[j]<target[j]:
     total=sum(powers);v*=(total-L*dim/2)*(P*dim/2-total-1)/((dim/2-powers[j]-1)*powers[j]*(-2*1217-29));powers[j]+=1
   ref[','.join(map(str,target))]={','.join(map(str,a)):str(sp.cancel(v))}
  rp=HERE/'application_checks'/(c['id']+'_reference.json.gz');write(rp,dict(coefficients=ref));r=invoke(c,basis,rp,c['id']);assert not r['model_used'];rows.append(dict(loops=L,method='exact',checks=r['coefficient_checks'],seconds=r['fresh_application_with_check_seconds']))
 # Deterministic first successful non-scalar example from each requested domain.
 candidates=READ(HERE/'refit/protocol.json')['reserved'];chosen=[]
 for domain in ['vacuum_one_mass','vacuum_all_mass','nonplanar_box','pentagon']:
  eligible=[c for c in candidates if domain in c['topology_group'] and READ(HERE/'refit/coverage'/(c['id']+'.json'))['status']=='verified']
  if eligible:chosen.append(eligible[0])
 for c in chosen:
  rp=HERE/'refit/references'/(c['id']+'.json.gz');r=invoke(c,READ(rp)['masters'],rp,'public_'+c['id']);assert r['model_used'];rows.append(dict(case=c['id'],loops=len(c['definition']['loop_momenta']),method='learned',checks=r['coefficient_checks'],seconds=r['fresh_application_with_check_seconds']))
 write(HERE/'application_checks/summary.json',dict(complete=True,all_exact=True,rows=rows,scope='Scalar exact identities at loops 1--12; learned public calls on predefined available domains. Native inputs are a subset of the reserved grid and add no coverage.'))
 print('PUBLIC CHECKS',len(rows),flush=True)
if __name__=='__main__':main()
