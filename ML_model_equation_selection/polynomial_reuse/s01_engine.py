"""Preserve exact reduction and verification while reusing arithmetic work."""
from s00_arithmetic import *
from s16_native import load_native
class State:
 def __init__(self):
  self.transforms=Transforms();self.models={};self.requests=0
 def model(self):
  if "forest4" not in self.models:self.models["forest4"]=load_native("forest4.json")
  return self.models["forest4"]
def calculate(requests,variant,policy,state,inject_failure=False):
 start=time.perf_counter();previous.validate_group(requests)
 assert variant in ["transforms","taylor","both"] and policy in ["extreme","model"]
 state.requests+=1;t=time.perf_counter()
 model=state.model() if policy=="model" and any(len(c["mass_ratios"])>2 for c in requests) else None
 load=time.perf_counter()-t;t=time.perf_counter();systems=[];choices=[]
 for c in requests:
  rows,choice=prior.selected(c,policy,model);systems.append(rows);choices.append(dict(case=c["id"],**choice))
 assert sum(map(len,systems))<=12000
 selection=time.perf_counter()-t;t=time.perf_counter()
 exact={c["id"]:prior.recurrence(c,rows) for c,rows in zip(requests,systems)}
 contraction=time.perf_counter()-t;t=time.perf_counter();oracle={};factor_hits=0;factor_builds=0
 for c in requests:
  if variant in ["taylor","both"]:
   checker=TaylorCheck(c["mass_ratios"],c["targets"])
   oracle[c["id"]]=[checker.coefficient(b) for b in c["targets"]]
   factor_hits+=checker.hits;factor_builds+=checker.builds
  else:oracle[c["id"]]=[base.symbolic_oracle(c["mass_ratios"],b) for b in c["targets"]]
 oracle_time=time.perf_counter()-t;t=time.perf_counter();checks=0
 for c in requests:
  for left,right in zip(exact[c["id"]],oracle[c["id"]]):
   keys=set(left)|set(right)
   assert all(base.canonical(left.get(j,()))==base.canonical(right.get(j,())) for j in keys),"Exact coefficient mismatch"
   checks+=len(keys)
 if inject_failure:raise AssertionError("Injected independent-check failure")
 verification=time.perf_counter()-t;t=time.perf_counter();hits=state.transforms.hits;builds=state.transforms.builds
 if variant in ["transforms","both"]:
  coefficients={c["id"]:expand(exact[c["id"]],c["loops"],state.transforms) for c in requests}
 else:
  coefficients={c["id"]:{str(L):base.encode([{j:base.substitute(p,L) for j,p in row.items()} for row in exact[c["id"]]]) for L in c["loops"]} for c in requests}
 substitution=time.perf_counter()-t
 return dict(success=True,variant=variant,policy=policy,kira_invoked=False,fallbacks=0,complete_seconds=time.perf_counter()-start,model_load_seconds=load,selection_seconds=selection,contraction_seconds=contraction,oracle_seconds=oracle_time,verification_seconds=verification,substitution_seconds=substitution,taylor_factor_hits=factor_hits,taylor_factor_builds=factor_builds,transform_hits=state.transforms.hits-hits,transform_builds=state.transforms.builds-builds,transform_cache_entries=len(state.transforms.cache),choices=choices,equations_before=sum(map(len,systems)),equations_sent=0,symbolic_coefficient_checks=checks,loop_coefficient_positions=sum(len(row)*len(c["loops"]) for c in requests for row in exact[c["id"]]),source_choices=[[c["id"],[[list(b),list(p)] for b,p in rows.items()]] for c,rows in zip(requests,systems)],raw_export="",symbolic_coefficients={k:base.encode(v) for k,v in exact.items()},coefficients=coefficients)
def apply(requests,variant="both",policy="extreme",state=None,inject_failure=False):
 start=time.perf_counter()
 previous.validate_group(requests)
 if variant=="baseline":
  result=previous.apply(requests,"direct_model" if policy=="model" else "direct_extreme")
 else:
  try:result=calculate(requests,variant,policy,state or State(),inject_failure)
  except (AssertionError,ValueError,KeyError,RuntimeError) as exc:
   result=prior.pack.apply(requests,"model","forest4.json")
   result.update(fallbacks=result["fallbacks"]+1,failure=str(exc),kira_invoked=True,complete_seconds=time.perf_counter()-start)
 result.update(variant=variant,policy=policy)
 return result
