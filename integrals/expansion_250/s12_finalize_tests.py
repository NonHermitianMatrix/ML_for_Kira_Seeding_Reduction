"""Record independently checked frozen tests and update affected READMEs."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def replace_tail(p,marker,text):
 s=p.read_text(encoding="utf-8").split(marker)[0].rstrip()
 p.write_text(s+"\n\n"+marker+"\n"+text.strip()+"\n",encoding="utf-8")
def main():
 summaries={}
 for name in ("ML_model_seed_selection","ML_model_reduction"):
  folder=ROOT/name;test=folder/"model_test";v=read(test/"validation.json")
  t=read(folder/"trained_model.json");r=read(test/"test_results.json")
  release=read(folder/"release_manifest.json")
  assert v["status"]=="passed" and t["epochs_completed"]==20
  assert sha(folder/"trained_model.pt")==t["model_sha256"]==release["model_sha256"]
  seed=name.endswith("seed_selection")
  if seed:
   assert r["checkpoint_sha256"]==release["model_sha256"]
   assert r["overall"]["targets"]==229582 and v["families"]==1537
   metrics=dict(precision=r["overall"]["micro"]["precision"],
    recall=r["overall"]["micro"]["recall"],f1=r["overall"]["micro"]["f1"],
    exact_reference_set=r["overall"]["target_macro"]["exact_reference_set_at_0_5"],
    mean_average_precision=r["overall"]["target_macro"]["average_precision"])
   text=("The frozen model was tested on all 229,582 targets in 1537 held-out families. "
    "At the fixed threshold 0.5, pooled precision is {precision:.6%}, recall is {recall:.6%}, "
    "F1 is {f1:.6%}, and complete reference-set agreement is {exact_reference_set:.6%}. "
    "Mean target average precision is {mean_average_precision:.6%}.\n\n").format(**metrics)
   files=("predictions/ stores per-family probability arrays, labels and target IDs; prediction_manifest.json identifies their hashes. "
    "per_target_metrics.jsonl.gz, family_metrics.json, test_results.json and curves.json give the measurements. "
    "s01_evaluate.py performs frozen inference, s02_run_test.sh runs the bounded test, s03_plot_results.py draws the six plots, "
    "s04_validate_outputs.py independently checks counts and saved probabilities, and s06_update_report.py renders the scientific sections.\n\n")
   figures=read(test/"figure_manifest.json")["figures"]
   scope=("The labels identify one sufficient reference seed set. Alternative sufficient sets can differ, and this evaluation does not run "
    "Kira with the predicted sets or establish globally minimal seeds. Candidate-label accuracy must be read with the sparse positive-label fraction.\n")
  else:
   assert r["signature"]["model_sha256"]==release["model_sha256"] and r["targets"]==229582 and r["families"]==1537
   metrics=dict(choice_top1=r["overall"]["top1"],choice_top3=r["overall"]["top3"],
    tie_averaged_top1=read(test/"tie_metrics.json")["overall"]["tie_neutral_top1"],
    top_tie_fraction=read(test/"tie_metrics.json")["overall"]["top_tie_fraction"],
    same_next_row=r["overall"]["equivalent_next_row"],model_success=r["model"]["success_all_samples"],
    greedy_success=r["greedy"]["success_all_samples"],model_runtime_ms=r["model"]["mean_runtime_ms"],
    greedy_runtime_ms=r["greedy"]["mean_runtime_ms"])
   text=("The frozen model was tested on all 229,582 targets in 1537 held-out families. "
    "Recorded-action top-one agreement on choice states is {choice_top1:.6%}; top-three agreement is {choice_top3:.6%}. "
    "Averaging credit over highest-scoring ties gives {tie_averaged_top1:.6%} agreement; the tied fraction is {top_tie_fraction:.6%}. "
    "The selected action gives the same next sampled row in {same_next_row:.6%} of choice states. "
    "The learned policy matches all three sampled master expansions for {model_success:,} targets, "
    "and the local comparison rule does so for {greedy_success:,}. "
    "Mean attempted reduction times are {model_runtime_ms:.6f} ms and {greedy_runtime_ms:.6f} ms, respectively.\n\n").format(**metrics)
   files=("families/ stores probability arrays and complete model/comparison paths. test_results.json, family_metrics.json, "
    "paired_comparison.json, tie_metrics.json and target_metrics.jsonl.gz provide measured results. "
    "s00_test_common.py and s01_policies.py define the fixed protocol; s02_evaluate.py runs it. "
    "s03_check_metrics.py checks metric formulas, s04_run_test.sh runs the bounded workflow and accepts --plots-only to redraw checked results, "
    "s05_validate_outputs.py independently replays saved paths and probabilities, s06_plot_results.py draws the six plots, "
    "s07_update_report.py renders the scientific sections, s09_validate_checkpoint.py checks the frozen twenty-pass weights, and s10_parallel_test.py runs four disjoint family groups on one compute node before aggregation.\n\n")
   figures=read(test/"figure_manifest.json")["figures"]
   scope=("The model changes one target row against fixed source identities. The local rule minimizes the next nonmaster count, "
    "total row support, immediate operation count and fixed equation-ID tie-break in that order. "
    "Three finite-field samples check complete paths. The test establishes neither global path minimality nor a full Kira runtime improvement.\n")
  assert len(figures)==6
  for fig in figures:
   title=fig if isinstance(fig,str) else fig["name"]
   assert (test/"figures"/(title+".pdf")).is_file()
  shared=("Every loop order from one through twelve occurs in training and testing. Related new mass profiles stay within one split across loop orders. "
   "The new data use restricted coupled vacuum families, and different profiles can share lower-sector physics. "
   "Weights, split, threshold and confidence maps remain fixed during evaluation. The tests do not establish transfer to unseen loop orders.\n\n")
  (test/"README.md").write_text("# Frozen expanded-data test\n\n"+text+files+
   "figures/ contains six PDF plots and PNG previews. validation.json records independent checks. "
   "archive_before_expansion_250/ retains the preceding tests and their source.\n\n"+
   shared+scope+"\nCheckpoint SHA-256: "+release["model_sha256"]+".\n",encoding="utf-8")
  p=folder/"README.md";s=p.read_text(encoding="utf-8")
  s=s.replace("The frozen expanded-data test is the next stage.","The frozen expanded-data test is complete.")
  s=s.replace("Current tests and plots will replace the active results in model_test/ and the report.",
              "Current tests and plots occupy model_test/; the report is updated from these checked records.")
  p.write_text(s,encoding="utf-8")
  replace_tail(p,"<!-- expanded-test-results -->",text+scope+"\nSee model_test/README.md for the complete frozen protocol and artifacts.")
  release.update(status="twenty_expanded_data_epochs_and_frozen_tests_complete",
    test_results_sha256=sha(test/"test_results.json"),test_validation_sha256=sha(test/"validation.json"))
  write(folder/"release_manifest.json",release)
  summaries[name]=dict(model_sha256=release["model_sha256"],metrics=metrics,validation_sha256=sha(test/"validation.json"))
 root=ROOT/"README.md";s=root.read_text(encoding="utf-8")
 s=s.replace("Frozen expanded-data testing is the next stage; earlier test artifacts remain in each model_test/archive_before_expansion_250/ folder. "
  "The current report still describes the preceding tests until the new evaluation and report update finish.",
  "Both frozen expanded-data tests are complete; their measurements, exact checks and six plots per model occupy each model_test/ folder. "
  "Earlier test artifacts remain in model_test/archive_before_all_loops/. The scientific report is rebuilt from the current checked results.")
 root.write_text(s,encoding="utf-8")
 for d in ("integrals/training","integrals/testing"):
  p=ROOT/d/"README.md"
  text=p.read_text(encoding="utf-8").replace("The frozen expanded-data models will be evaluated on the separate testing split.",
                                         "The frozen expanded-data models were evaluated on the separate testing split.")
  p.write_text(text,encoding="utf-8")
  replace_tail(ROOT/d/"README.md","<!-- expanded-model-use -->",
   "Both models completed twenty passes over the fixed expanded training division. The frozen test covers all 229,582 targets in the separate testing division. "
   "Model outputs and exact checks are stored in each model's model_test/ folder. Training used no held-out labels.")
 write(HERE/"test_release.json",dict(status="both_frozen_tests_validated",models=summaries,targets_per_model=229582,families_per_model=1537))
 print("Both frozen tests recorded",flush=True)
if __name__=="__main__":main()
