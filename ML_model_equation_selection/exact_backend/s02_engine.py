"""Shared integer representation with compiled expansion and learned batch routing."""
from s00_backend import *
MODES=["baseline","integer","native_json","native_binary","learned"]
def calculate(requests,mode,state,forced_policy=None,inject_failure=False):
 start=time.perf_counter();old.previous.validate_group(requests);assert mode in MODES
 if mode=="baseline":
  out=old_apply(requests,"both","extreme",state.setdefault("old_state",OldState()));out.update(mode=mode,route="extreme");return out
 t=time.perf_counter();predictions=[]
 if forced_policy:policy=forced_policy
 elif mode=="learned":policy,predictions=predict(requests,state)
 else:policy="extreme"
 inference=time.perf_counter()-t;t=time.perf_counter()
 systems=[dependencies(c,policy) for c in requests];assert sum(map(len,systems))<=12000
 selection=time.perf_counter()-t;t=time.perf_counter()
 exact=[recurrence(c,rows) for c,rows in zip(requests,systems)];contraction=time.perf_counter()-t;t=time.perf_counter();checks=0
 for c,rows in zip(requests,exact):
  checker=TaylorInteger(c["mass_ratios"],c["targets"])
  for b,row in zip(c["targets"],rows):
   want=checker.coefficient(b);assert row==want,"Exact coefficient mismatch";checks+=len(want)
 if inject_failure:raise AssertionError("Injected independent-check failure")
 verification=time.perf_counter()-t;t=time.perf_counter();symbolic_data={};expanded={};parts=[]
 for c,rows in zip(requests,exact):
  keys=row_keys(rows)
  if mode=="integer":expanded[c["id"]]=python_expand(rows,c["loops"],state)
  else:
   inp=common_packet(rows,c["loops"]);out=native(inp,state)
   if mode=="native_json":expanded[c["id"]]=decode_expanded(out,keys)
   else:parts.append((c["id"],keys,inp,out))
  if mode in ["integer","native_json"]:symbolic_data[c["id"]]=symbolic(rows)
 expansion=time.perf_counter()-t
 result=dict(success=True,mode=mode,route=policy,predicted_log_seconds=predictions,inference_seconds=inference,selection_seconds=selection,contraction_seconds=contraction,verification_seconds=verification,substitution_seconds=expansion,complete_seconds=time.perf_counter()-start,
  fallbacks=0,kira_invoked=False,equations=sum(map(len,systems)),symbolic_coefficient_checks=checks,
  source_choices=[[c["id"],[[list(b),list(p)] for b,p in rows.items()]] for c,rows in zip(requests,systems)],raw_export="")
 if parts:result["_binary"]=binary_payload(parts)
 else:result.update(symbolic_coefficients=symbolic_data,coefficients=expanded)
 return result
def apply(requests,mode,state=None,forced_policy=None,inject_failure=False):
 state={} if state is None else state;start=time.perf_counter();old.previous.validate_group(requests)
 try:return calculate(requests,mode,state,forced_policy,inject_failure)
 except (AssertionError,ValueError,KeyError,RuntimeError,OSError) as exc:
  result=prior.pack.apply(requests,"model","forest4.json")
  result.update(mode=mode,route="kira_fallback",failure=str(exc),fallbacks=result["fallbacks"]+1,kira_invoked=True,complete_seconds=time.perf_counter()-start)
  return result
