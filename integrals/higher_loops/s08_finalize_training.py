"""Validate both expanded-data models and describe the current trained release."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,o):p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 validation_path=ROOT/"integrals/validation_summary.json"
 audit=read(validation_path)
 if not (audit.get("family_count")==2100 and audit.get("status")=="passed"
         and audit.get("catalog_sha256")==sha(ROOT/"integrals/catalog.json")
         and audit.get("split_sha256")==sha(ROOT/"ML_model_seed_selection/split_manifest.json")
         and audit.get("higher_loop_mathematical_validation",{}).get("sha256")==sha(HERE/"validation.json")):
  subprocess.run([sys.executable,str(ROOT/"integrals/s02_validate.py")],check=True)
 subprocess.run([sys.executable,str(ROOT/"ML_model_seed_selection/s16_validate_all_loops.py")],check=True)
 red=ROOT/"ML_model_reduction"
 red_check=read(red/"validation.json") if (red/"validation.json").exists() else {}
 if not (red_check.get("status")=="passed" and red_check.get("expanded_dataset_epochs")==20
         and red_check.get("model_sha256")==sha(red/"trained_model.pt")
         and (red/"model_test/test_config.json").exists()
         and read(red/"model_test/test_config.json").get("model_sha256")==red_check["model_sha256"]
         and red_check.get("test_config_sha256")==sha(red/"model_test/test_config.json")):
  subprocess.run([sys.executable,str(red/"model_test/s09_validate_checkpoint.py")],check=True)
 data=read(HERE/"integration_summary.json")
 assert data["families"]==2100 and data["targets"]==381272
 releases={}
 for name in ("ML_model_seed_selection","ML_model_reduction"):
  folder=ROOT/name;t=read(folder/"trained_model.json");v=read(folder/"validation.json")
  assert v["status"]=="passed" and t["epochs_completed"]==20
  release=dict(status="twenty_expanded_data_epochs_complete_testing_pending",model_sha256=sha(folder/"trained_model.pt"),
    optimizer_checkpoint_sha256=sha(folder/"runs/all_loops_latest.pt"),config_sha256=sha(folder/"config.json"),
    split_sha256=sha(ROOT/"ML_model_seed_selection/split_manifest.json"),lineage=t["lineage"],epochs_completed=20,
    loop_orders=list(range(1,13)),training_families=1463,training_targets=266890,held_out_families=637,held_out_targets=114382,
    test_data_used_in_training=False,raw_data_locations="Hoffman and GitHub only")
  write(folder/"release_manifest.json",release);releases[name]=release
  seed=name.endswith("seed_selection")
  description=("The model gives each supplied candidate seed a separate reference-membership probability, a binary label at p>=0.5 and the probability of the returned label. Several seeds can receive label one. It uses the symbolic target terms, every ordered pair of distinct terms, public family information and the chosen master indices. It has 28,097 parameters.\n\n"
    if seed else
    "The model scores the supplied allowed source-row eliminations at the current target row, returns a probability for every action and selects the highest-scoring action with its estimated confidence. The exact solver performs the selected finite-field operation. It has 10,529 parameters and 132 input features per action.\n\n")
  steps=("The active sequence is s12_prepare_features.py (training-only encoded features), s13_batch.py (masked batch calculation and comparisons with the original score function), s14_train_all_loops.py (twenty-pass continuation), s15_run_all_loops.sh (bounded scheduler wrapper), s16_validate_all_loops.py (checkpoint and source validation), s17_run_batch_pilot.sh (bounded execution pilot), and s18_validate_mixed_batches.py with s19_run_batch_validation.sh (mixed-target score and derivative comparisons). Earlier scripts s00 through s11 preserve the initial preparation and training workflow.\n\n"
    if seed else
    "s00_common.py, s01_state.py and s03_model.py define file guards, exact row features and the neural scorer. s02_prepare_data.py replays training traces and creates bounded state files. s10_train_all_loops.py continues the saved weights and optimizer for twenty expanded-data passes; s11_run_all_loops.sh runs preparation and training. s05_predict.py exposes prediction and optional exact row application. Earlier s04 and s06 through s09 scripts preserve the initial workflow.\n\n")
  text="# "+("Seed-selection model" if seed else "Reduction-propagation model")+"\n\n"+description
  text+="The current checkpoint completed twenty new passes over 266,890 training targets from 1,463 complete families. Every loop order from one through twelve occurs in training. The fixed test division contains 114,382 targets from 637 families. New mass profiles remain in one split across all loop orders; earlier assignments are preserved. The higher-loop families are restricted coupled vacuum integrals. Both splits share some lower-sector physics and every loop order. Reference seed sets and paths are sufficient; their minimality is not proved.\n\n"
  text+=steps
  text+="trained_model.pt stores the current inference model; trained_model.json records measured training results. runs/all_loops_latest.pt retains the optimizer and exact resume position, and runs/all_loops_history.json records all twenty new passes. runs/before_all_loops_20/ preserves the preceding weights, optimizer, metadata and source. The saved lineage records the earlier dataset progress separately. validation.json and release_manifest.json verify the current model. data/ contains only encoded training examples, with source hashes and the held-out count recorded separately.\n\n"
  if seed:text+="The new phase uses batches of 32 targets. Factoring the first score layer avoids repeated target-context matrix multiplications without changing the network function. Direct comparisons with the original interface verify scores, loss and gradients. AdamW retains the previous optimizer state, learning rate 0.001 and weight decay 0.0001; the gradient norm is bounded by one. Scores describe membership in one reference seed set, and this model test alone does not run Kira with the predicted sets.\n\n"
  else:text+="Training retains the prior thirty-epoch weights and AdamW state, learning rate 0.001, weight decay 0.0001, gradient norm limit one and state batch bounds. Only states with multiple allowed actions contribute ranking loss. The experiment changes one target row against fixed source identities; it does not benchmark a complete Kira elimination system.\n\n"
  text+="The frozen expanded-data test is the next stage. model_test/archive_before_all_loops/ retains the previous tests and their exact source. Current tests and plots will replace the active results in model_test/ and the report. Generated data, model files and tests stay on Hoffman and GitHub; the report also stays on the local machine. Jobs bound CPU use, virtual memory and output sizes, and enforce the combined 10 GB ceiling.\n"
  text+="The training metadata records the state at training completion; release_manifest.json records the current publication and test stage.\n\n"
  if seed:
   text+="Prediction uses s04_predict.py --checkpoint ML_model_seed_selection/trained_model.pt --target FAMILY:ID, with an optional --seeds file containing an indices list. Run it with the existing .tools/seed-model/venv/bin/python after loading the Hoffman Python 3.9.6 module. The output includes predicted_label, probability_1, probability_0 and confidence for every candidate, ranked by probability_1. The public prediction path reads no reference labels.\n\n"
   text+="The shared network uses 32-component hidden descriptions and a 64-component score layer with tanh activations. It compresses symbolic coefficient tokens into 64 signed hash components, which permits collisions. Ordered combinations mean all ordered pairs of distinct stored terms. Inputs accept at most sixteen indices, 512 terms and 10,000 supplied candidates. The candidate list is a bounded pool, and the chosen master basis is public input. Family IDs, split labels, reference coefficients, construction histories and future operation counts do not enter the scores.\n\n"
  else:
   text+="Prediction uses s05_predict.py state.json --apply --output prediction.json with the existing .tools/seed-model/venv/bin/python after loading the Hoffman Python 3.9.6 module. The input gives prime, public family information, sparse rows, row_roles, master_columns and supplied actions. Each action contains id, source_row, destination_row and pivot_indices. The optional --apply flag performs the selected exact modular row update. Source rows must represent zero identities and pivots must be nonzero.\n\n"
   text+="The 132 action features describe pivot indices, row support, candidate cancellations, immediate arithmetic and public family information. A sparse modular trial update supplies local counts for each action; future trajectories and recorded selected-action IDs do not enter predictive features. The interface accepts multiple destination rows, while current training uses one changing target row. Limits are sixteen indices, 10,000 rows, 10,000 actions, 250,000 matrix entries and 4,096 entries per row.\n\n"
  (folder/"README.md").write_text(text.rstrip()+"\n",encoding="utf-8")
  rp=folder/"runs/README.md";rt=rp.read_text(encoding="utf-8")
  rt=rt.replace("The current phase runs twenty complete passes","The current phase completed twenty complete passes")
  rt=rt.replace("The compact inference model is written to ../trained_model.pt after pass twenty.",
                "The compact inference model is stored in ../trained_model.pt.")
  rp.write_text(rt,encoding="utf-8")

  (folder/"model_test/README.md").write_text("# Frozen expanded-data test\n\nThe model completed twenty expanded-data training passes. Checkpoint SHA-256: "+release["model_sha256"]+". The next test uses 114,382 targets from 637 held-out families spanning one through twelve loops. Weights, thresholds and confidence maps remain fixed. Training consumed no held-out labels.\n\nPrevious tests, figures and source are preserved in archive_before_all_loops/. Active test scripts now use the expanded manifest and report per-loop results. The seed test measures reference-set membership; the reduction test also replays complete exact target-row paths and compares their three sampled master expansions. Neither test proves globally optimal reductions or a full Kira speedup.\n",encoding="utf-8")
 (ROOT/"README.md").write_text("# ML for Kira seed selection and reduction\n\nThis project studies lightweight models for selecting IBP seeds and allowed elimination steps while exact arithmetic retains responsibility for the reductions.\n\nThe [integral collection](integrals/README.md) contains 2,100 family instances, 12,967 family-local master entries and 381,272 targets. It includes 997 one-loop families, 103 two-loop families and 100 families at every order from three through twelve. The added families are 100 mass profiles per loop order for restricted coupled vacuum integrals. Their analytic bases, Euler IBP and mass partial-fraction identities give exact reverse constructions. The profiles share a small set of graph structures; the collection does not represent arbitrary high-loop scattering integrals.\n\n[master_integrals/](integrals/master_integrals/README.md) stores definitions and bases; [target_integrals/](integrals/target_integrals/README.md) stores targets; [master_to_target/](integrals/master_to_target/README.md) stores master expansions, seeds, equations, constructions, elimination traces and operation counts. Matching IDs connect all records. [higher_loops/](integrals/higher_loops/README.md) documents the new mathematical domain and independent checks.\n\nThe grouped split gives 266,890 training targets in 1,463 families and 114,382 test targets in 637 families. Related added mass profiles remain together across loop orders, and prior assignments remain fixed. The separate [training](integrals/training/README.md) and [testing](integrals/testing/README.md) views link to canonical data without copying it. Shared lower-sector physics can occur across profiles.\n\nBoth the [seed model](ML_model_seed_selection/README.md) and [reduction model](ML_model_reduction/README.md) completed twenty new passes over the expanded training set, starting from their saved weights and optimizer states. Their previous progress remains recorded separately. Frozen expanded-data testing is the next stage; earlier test artifacts remain in each model_test/archive_before_all_loops/ folder. The current report still describes the preceding tests until the new evaluation and report update finish.\n\nThe [report PDF](report/report.pdf), [LaTeX source](report/report.tex), [bibliography](report/references.bib) and [rules](rules.md) accompany the project. Hoffman is the primary working location. Generated integral data, encoded examples, trained models and tests stay on Hoffman and GitHub; only report files are also synchronized locally. The combined storage ceiling is 10 GB.\n",encoding="utf-8")
 write(HERE/"training_release.json",dict(status="both_models_validated",models=releases))
 request=read(HERE/"request.json")
 request["status"]="both_models_trained_and_validated"
 request["model_hashes"]={name:r["model_sha256"] for name,r in releases.items()}
 write(HERE/"request.json",request)
 print("Both expanded-data models validated",flush=True)
if __name__=="__main__":main()
