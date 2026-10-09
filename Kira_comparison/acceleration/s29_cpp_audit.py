"""Check native coefficient sampling, features, probabilities and chosen updates."""
import argparse,gzip,json,pathlib,sys
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s01_common import load_module,write
from s08_verify import evaluate
live=load_module("cpp_trace_audit",HERE.parent/"live_matrix/s07_audit.py")
sys.path.insert(0,str(ROOT/"ML_model_reduction"))
from s01_state import encode_state
from s09_fast_row import FastRow
ap=argparse.ArgumentParser();ap.add_argument("--stage",default="cpp_pilot");ap.add_argument("--diagnostic",action="store_true");args=ap.parse_args()
predictor=FastRow();features=0;sample_checks=0;decisions=0;forced=0;feature_error=0.;probability_error=0.;float32_difference=0.;files=[];reference_near_ties=0;max_selected_gap=0.
def reference64(features):
 w={k:v.astype(np.float64) for k,v in predictor.w.items()}
 h=np.tanh(features.astype(np.float64)@w["encoder.0.weight"].T+w["encoder.0.bias"])
 joined=np.concatenate((h,np.broadcast_to(h.mean(0),h.shape),np.broadcast_to(h.max(0),h.shape)),axis=-1)
 z=np.tanh(joined@w["scorer.0.weight"].T+w["scorer.0.bias"])
 logits=(z@w["scorer.2.weight"].T+w["scorer.2.bias"]).ravel()
 values=np.exp(logits-logits.max());return values/values.sum()
for path in sorted((HERE/args.stage).glob("*row_cpp_audit.json.gz")):
 record=json.load(gzip.open(path,"rt"));assert record["success"] and not record["fallback"],path.name
 ev=record["evidence"];context=json.loads(ev["context.json"]);point=tuple(sorted(context["point"].items()));prime=context["prime"]
 steps=live.trace_rows(ev["attempt0/row_trace.txt"])
 events=[json.loads(line) for line in ev["attempt0/cpp_choices.jsonl"].splitlines()]
 assert len(events)==len(steps)
 for event,(src,dst,after) in zip(events,steps):
  group=[str(x) for x in event["group"]];q=str(event["source"]);r=str(event["destination"])
  assert q in group and r==group[-1] and q!=r
  if not event["used_model"]:
   assert len(group)==2 and event["probabilities"]==[1];forced+=1;continue
  for rid,row in event["symbolic_rows"].items():
   expected={k:v for k,s in row.items() if (v:=evaluate(s,point,prime))}
   assert expected==event["rows"][rid];sample_checks+=len(row)
  assert event["symbolic_rows"][q]==src and event["symbolic_rows"][r]==dst
  actions=[dict(id="%08d:%08d"%(int(s),int(r)),source_row=s,destination_row=r,
           pivot_indices=list(map(int,event["pivot"].split(",")))) for s in group if s!=r]
  state=dict(family=context["family"],prime=prime,rows=event["rows"],
   row_roles={s:("target" if s==r else "identity") for s in group},
   master_columns=context["master_columns"],actions=actions,enforce_reference_order=False)
  expected=encode_state(state,predictor.cfg);got=np.asarray(event["features"],np.float32)
  e=float(np.max(np.abs(expected-got)));feature_error=max(feature_error,e);assert e<2e-6
  p=predictor.probabilities(expected);g=np.asarray(event["probabilities"],np.float64)
  truth=reference64(expected);e=float(np.max(np.abs(truth-g)))
  probability_error=max(probability_error,e);assert args.diagnostic or e<1e-10
  float32_difference=max(float32_difference,float(np.max(np.abs(p-g))))
  assert actions[int(p.argmax())]["source_row"]==q
  selected_index=next(i for i,x in enumerate(actions) if x["source_row"]==q)
  gap=float(truth.max()-truth[selected_index]);max_selected_gap=max(max_selected_gap,gap)
  assert gap<1e-10
  reference_near_ties+=int(actions[int(truth.argmax())]["source_row"]!=q)
  features+=len(actions);decisions+=1
 files.append(path.name)
assert len(files)==2 and decisions>0
write(HERE/("cpp_equivalence_initial.json" if args.diagnostic else "cpp_equivalence.json"),dict(passed=probability_error<1e-10,trials=files,model_decisions=decisions,forced_actions=forced,
 candidate_feature_vectors=features,independent_coefficient_samples=sample_checks,
 max_feature_error=feature_error,max_probability_error=probability_error,
 max_original_float32_probability_difference=float32_difference,inference_precision="float32 features and unchanged learned weights; float64 neural arithmetic",
 selected_sources_equal=True,reference_near_ties=reference_near_ties,max_selected_probability_gap=max_selected_gap))
print(json.dumps(dict(decisions=decisions,forced=forced,feature_error=feature_error,probability_error=probability_error)),flush=True)
