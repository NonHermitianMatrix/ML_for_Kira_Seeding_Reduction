"""Update the scientific seed-model sections from the frozen expanded-data results."""
import argparse,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;MODEL=HERE.parent;ROOT=MODEL.parent;REPORT=ROOT/"report"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def render(name,values):
 s=(HERE/name).read_text(encoding="utf-8")
 for k,v in values.items():s=s.replace("@"+k+"@",str(v))
 import re
 assert not re.search(r"@[A-Z_0-9]+@",s),re.findall(r"@[A-Z_0-9]+@",s)
 return s
def main():
 assert read(HERE/"validation.json")["status"]=="passed"
 r=read(HERE/"test_results.json");t=read(MODEL/"trained_model.json")
 assert r["checkpoint_sha256"]==t["model_sha256"] and t["epochs_completed"]==20
 n=lambda x:format(x,",");pc=lambda x:format(100*x,".3f")
 history=t["history"];overall=r["overall"];macro=overall["target_macro"];micro=overall["micro"]
 values=dict(TRAIN_TARGETS=n(t["training_targets"]),TRAIN_FAMILIES=n(t["training_families"]),
  TEST_TARGETS=n(t["held_out_targets"]),TEST_FAMILIES=n(t["held_out_families"]),
  PRIOR_EPOCHS=t["lineage"]["completed_prior_epochs"],PRIOR_PARTIAL=n(t["lineage"]["targets_in_prior_partial_epoch"]),
  PRESENTATIONS=n(sum(h["targets"] for h in history)),UPDATES=n(t["optimizer_steps"]),
  FIRST_LOSS=format(history[0]["mean_loss"],".7g"),LAST_LOSS=format(history[-1]["mean_loss"],".7g"))
 path=REPORT/"seed_model.tex";s=path.read_text(encoding="utf-8")
 s=s.replace("the existing families use at most five.","the expanded collection uses up to sixteen.")
 s=s[:s.index("\\subsection{Training labels and the 70:30 data division}")]+render("training_section_template.tex",values) if "\\subsection{Training labels and the 70:30 data division}" in s else s[:s.index("\\subsection{Training labels and the grouped data division}")]+render("training_section_template.tex",values)
 path.write_text(s,encoding="utf-8")
 families=read(HERE/"family_metrics.json")
 low_loop=min(range(2,13),key=lambda loop:r["groups"]["loops:"+str(loop)]["micro"]["recall"])
 values.update(SINGLE=n(r["groups"]["kind:single_integral"]["targets"]),
  EXPRESSION=n(r["groups"]["kind:integral_expression"]["targets"]),LABELS=n(overall["candidate_labels"]),
  POSITIVES=n(overall["positive_labels"]),PRECISION=pc(micro["precision"]),RECALL=pc(micro["recall"]),F1=pc(micro["f1"]),
  EXACT=pc(macro["exact_reference_set_at_0_5"]),ACCURACY=pc(micro["accuracy"]),ZERO_ACCURACY=pc(r["baseline_all_zero"]["micro"]["accuracy"]),
  MAP=pc(macro["average_precision"]),RECALL10=pc(macro["recall_at_10"]),COVERAGE10=pc(macro["reference_coverage_at_10"]),
  ONE_FAMILIES=sum(f["loops"]==1 for f in families.values()),TWO_FAMILIES=sum(f["loops"]==2 for f in families.values()),
  ONE_RECALL=pc(r["groups"]["loops:1"]["micro"]["recall"]),ONE_F1=pc(r["groups"]["loops:1"]["micro"]["f1"]),
  TWELVE_RECALL=pc(r["groups"]["loops:12"]["micro"]["recall"]),TWELVE_F1=pc(r["groups"]["loops:12"]["micro"]["f1"]),
  MIN_HIGH_RECALL=pc(r["groups"]["loops:"+str(low_loop)]["micro"]["recall"]),MIN_HIGH_LOOP=low_loop,
  INFERENCE_MS=format(1000*(r["encoding_seconds"]+r["model_inference_seconds"])/overall["targets"],".4f"))
 (REPORT/"seed_model_test.tex").write_text(render("report_section_template.tex",values),encoding="utf-8")
 (HERE/"report_values.json").write_text(json.dumps(values,indent=2)+"\n",encoding="utf-8")
 print("Seed report sections updated",flush=True)
if __name__=="__main__":main()
