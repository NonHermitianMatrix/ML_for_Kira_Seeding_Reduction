"""Declare independent matched requests without fitting any policy."""
from s00_cumulative import *
def make_group(index,maximum,count,pilot=False):
 requests=[]
 for r in [2,3,4]:
  rng=random.Random(831791+index*157+r)
  pool=[b for B in range(2,maximum+1) for b in legacy.compositions(B,r)]
  rng.shuffle(pool)
  chosen=pool[:min(count,len(pool))]
  endpoint=tuple([maximum-r+1]+[1]*(r-1))
  if endpoint not in chosen:chosen[-1]=endpoint
  massbase=(700000 if pilot else 200000)+index*1009+r*101
  masses=sorted(massbase+x for x in rng.sample(range(1,600),r))
  requests.append(dict(id=("pilot" if pilot else "cumulative")+str(index)+"_r"+str(r),family="coupled_vacuum_unit_massless",mass_scale_squared=1,mass_ratios=masses,targets=[list(b) for b in sorted(chosen)],loops=list(range(1,13))))
 return dict(requests=requests)
def main():
 assert not (HERE/"freeze.json").exists()
 for i in range(8):
  maximum=[8,10,12,14][i//2];count=[16,32,48,64][i//2]
  write(HERE/"test/inputs"/("group%02d.json"%i),make_group(i,maximum,count))
 write(HERE/"pilot/input.json",make_group(100,14,64,True))
 protocol=dict(family="coupled_vacuum_unit_massless",massless_powers="all one",massive_denominators=[2,3,4],loops=list(range(1,13)),batches=8,profiles_per_batch=3,repetitions=5,arms=ARMS,maximum_powers=[8,10,12,14],requested_targets_per_profile=[16,32,48,64],master_basis="one single-power massive master per distinct mass",
 primary_metric="cold process wall time plus complete coefficient reading and decoding",
 calculation_metric="request loading through checked expanded coefficients, before output saving",
 baseline="full Euler and all mass-pair identity pool, separate Kira reduction for every mass profile and loop order",
 original_binary="saved Kira 3.1 executable whose SHA256 matches the first frozen cost comparison",
 final="unchanged validation-selected compiled arithmetic, binary output and fixed extreme recurrence",
 equation_generation="explicit Euler and partial-fraction identities, not native general IBP generation",
 hardware="one scheduled node, sequential arms in independently shuffled three-arm blocks",
 inference_and_fallback="all used costs included; no retraining or policy selection",
 failure_rule="retain every failure and stop for diagnosis; never silently omit a paired arm",
 excluded_costs=["scheduler waiting","offline training","one independent after-run audit"],
 independent_scope="new mass profiles in the same restricted topology; index shapes may overlap earlier work")
 write(HERE/"protocol.json",protocol)
 print("declared eight reserved batches and one separate resource pilot",flush=True)
if __name__=="__main__":main()
