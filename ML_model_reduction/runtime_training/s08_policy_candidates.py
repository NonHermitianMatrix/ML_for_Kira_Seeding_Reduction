"""Initialize bounded policy families for optimization on full native trajectories."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def main():
 policies=[("fill",{})]
 for feature,values in [(1,[-.5,.25,.5,1.,2.]),(2,[.01,.03,.1]),(22,[.1,.3,1.]),(16,[-.002,-.01,-.03,-.1])]:
  for value in values:policies.append((f"f{feature}_{value:g}",{feature:value}))
 policies += [("mixed",{1:.5,22:.3,16:-.01}),("length_only",{18:0,1:1})]
 out=[]
 for name,extra in policies:
  w=[0.]*24;w[18]=1.
  for k,v in extra.items():w[k]=v
  p=HERE/"trajectory_candidates"/name;p.mkdir(parents=True,exist_ok=True)
  (p/"weights.txt").write_text("\n".join(["24 0 0"," ".join(["0"]*24)," ".join(["1"]*24)," ".join(map(str,w))])+"\n")
  out.append(dict(id=name,weights=w))
 (HERE/"trajectory_candidates.json").write_text(json.dumps(dict(candidates=out,objective="Choose coefficients from measured complete native trajectories on training families; use separate validation for deployment."),indent=2)+"\n")
if __name__=="__main__":main()
