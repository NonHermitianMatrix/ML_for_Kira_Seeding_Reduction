"""Document the checked live policy, controls, limits, execution and measured results."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 d=json.load(open(HERE/"summary.json"));v=d["validation"]
 assert v["passed"]
 def measure(base,key):
  return next(x for x in d["comparisons"] if x["baseline"]==base and x["policy"]=="learned")["metrics"][key]
 cold=measure("stock","cold_seconds")["geometric_mean_ratio"]
 fw=measure("native","forward_seconds")["geometric_mean_ratio"]
 ready=measure("native","forward_loaded_seconds")["geometric_mean_ratio"]
 ops=measure("native","operations")
 overview=("Completed %d final trials in seven held-out independent-basis families, with %d incomplete trials. "
    "The learned/stock complete-time ratio is %.3f. The learned/instrumented-native forward-stage "
    "ratio is %.3f, or %.3f after subtracting recorded model loading. Summed median committed "
    "coefficient-operation counts are %d for the learned policy and %d for the native policy."
    %(d["trials"],len(v["incomplete"]),cold,fw,ready,ops["sum_policy"],ops["sum_baseline"]))
 text="""# Learned row choices inside Kira's evolving matrix

"""+overview+"""

The experiment uses the frozen checkpoint in ML_model_reduction/trained_model.pt. It does not retrain, fit confidence, or use reference master coefficients in predictions. It covers three one-loop box profiles, a bubble, triangle and tadpole, and a two-loop propagator, with 99 target expressions. Family selection and the grouped test split match the preceding native comparison.

## Mathematical integration

Kira generates and selects the physical IBP equations. The hook operates inside Kira::run_reduction after that selection, before normalization and back substitution. It chooses the highest Kira leading integral shared by at least two current identity rows. Every ordered pair of distinct rows in that group is an allowed elementary update. The frozen model scores all pairs and returns the source, destination and confidence. Kira's existing insert_equation function performs the exact symbolic update through Fermat. The changed row returns to the matrix and can serve as a later source. All other rows also contribute to the model's current matrix features.

The hook preserves the integral order and prescribed master basis. It does not choose arbitrary pivot columns, alter native numerical equation selection, or learn back-substitution order. The protected-master and finite-field pivot checks fail explicitly if their requirements are violated. The model uses the original 132-feature encoding. Initial symbolic rows and later updates are sampled at the fixed public point solely for inference; the Kira algebra remains symbolic.

A single policy process stays loaded for one forward solve. A matrix with no admissible updates skips model loading. The training states used fixed identities and a changing target row. This experiment tests transfer to changing identity rows.

## Controls and timing

The stock control uses the original installed Kira binary. The instrumented-native control retains Kira's forward algorithm while recording exact updates. The deterministic control uses the hook's serial schedule and Kira's source-row length/integral-order criterion, with stable destination identifiers. The learned method uses the same serial schedule and chooses both rows. Native seed bounds, target components and master preferences are identical across all controls.

Each family has three repeats of each of the four methods, run on one node with rotated order and one computation thread. Only two family tasks run concurrently. Complete time includes process startup, data preparation, model work, symbolic reduction, target combination and exact coefficient checks. The internal forward timer includes all work in the forward phase. The load-excluded diagnostic subtracts the policy server's measured import and model-loading interval from that timer; it retains feature construction, inference, communication and exact algebra. It is a decomposition of the recorded runs; a separate run with a preloaded model has not been measured.

Coefficient-operation counts use 1 + 2 times the source-row nonzero count for each committed exact update. They exclude polynomial simplification internals and candidate feature trial updates. Time includes those costs. Geometric-mean ratios use paired three-repeat medians. Forward-stage ratios exclude cases with zero committed updates. Incomplete cases remain in the audit and are excluded from ratios requiring two complete methods.

## Files and execution

- s00_policy_server.py: persistent frozen-model inference from the current matrix.
- s01_live_policy.h: source hook, admissible operations, native algebra calls and operation records.
- s02_build.py: patch one source translation unit and link unchanged Kira objects into an isolated binary.
- s03_build.sh: bounded scheduled compilation.
- s04_worker.py: native generation, live reduction, exact target combination and master-coefficient checks.
- s05_run.py: repeated trial controller with process, memory and storage guards.
- s06_run.sh: scheduled single-family or pilot execution.
- s07_audit.py: independent export checks and replay of all saved row updates and live choices.
- s08_summarize.py: paired medians, ratios, failures and operation totals.
- s09_array.sh: seven family tasks, with concurrency two.
- s10_prepare.py: exact pilot checks and immutable input/model/source hashes.
- s11_plot.py: two PDF figures and the values used to draw them.
- s12_finalize.sh: scheduled audit, summary and plots after all family tasks finish.
- s13_update_report.py: report sources, bibliography and conclusion using a supplied data-release commit.
- s14_readmes.py: this README and parent-folder summaries.
- s15_build_report.sh: bounded scheduled report update and PDF build using the published data commit.

Submit s03_build.sh first. Run s06_run.sh with --case 0 --pilot, --case 3 --pilot and --case 4 --pilot. After successful diagnostics and compilation, run s10_prepare.py, submit s09_array.sh and hold s12_finalize.sh on that array. Finally run s14_readmes.py, publish the data release, submit s15_build_report.sh with that commit to update the report and rebuild report/report.pdf.

build.json records compiler/link commands and original, modified and binary hashes. frozen_inputs.json fixes the model, public data and execution sources. The experiment reuses the existing symbolic Kira 3.1/Fermat build and does not benchmark FireFly reconstruction. The isolated source and binary remain in .tools/kira-live-build. COPYING supplies the upstream GPL license for the derivative Kira extension.

results/*.json.gz stores each result, exact checked coefficients, native exports, configuration, symbolic row-update records and model choices. summary.json and figure_values.csv contain the reported measurements. validation.json records independent checks and file hashes. The initial 12 successful pilot trials and earlier setup/build logs remain diagnostic records; they are excluded from the 84 final trials. The skip-empty-model-load guard was added after pilots and before the final source freeze.

## Verification and resource bounds

The audit interprets archived native Kira exports independently at the reference sample points. It replays each committed symbolic row operation at three independent finite-field samples, checks the live row identities against the exact operation trace, validates the complete allowed pair list and probabilities, and counts choices that use previously updated sources.

Each trial has a 600-second limit, 1.9 GB address space per process, 1.7 GB sampled summed process memory, and 64 MB scratch. Published outputs have a 128 MB cap. A conservative combined storage guard keeps the project below 10 GB. Data and binaries stay on Hoffman; public data and code are also on GitHub. Only report artifacts are synchronized locally.

"""
 text+="\nThe final audit recorded %d master-sample checks, %d row-sample checks, %d learned choices and %d choices using previously updated sources.\n"%(v["independent_master_sample_checks"],v["row_sample_checks"],v["live_choices"],v["choices_using_previously_updated_source"])
 (HERE/"README.md").write_text(text)
 marker="<!-- kira-live-matrix -->"
 block="\n"+marker+"\n## Live matrix comparison\n\n"+overview+"\n\nThe code, frozen protocol, exact operation records and plots are in [Kira_comparison/live_matrix](Kira_comparison/live_matrix/). The model acts inside Kira's symbolic forward phase on changing identity rows. The report distinguishes this test from the earlier fixed-source target-row procedure.\n"
 for relative in ["README.md","Kira_comparison/README.md","ML_model_reduction/README.md"]:
  p=ROOT/relative;t=p.read_text()
  if marker in t:t=t[:t.index(marker)]
  t=t.replace("The row model still acts on fixed source identities and changing target rows.", "The row comparison in that experiment uses fixed source identities and changing target rows; the live-matrix comparison below tests changing identity rows inside Kira.")
  b=block
  if relative!="README.md":b=b.replace("(Kira_comparison/live_matrix/)","("+("../live_matrix/" if relative.startswith("Kira_comparison/") else "../Kira_comparison/live_matrix/")+")")
  # Kira_comparison README's child path is live_matrix/.
  if relative=="Kira_comparison/README.md":b=b.replace("(../live_matrix/)","(live_matrix/)")
  p.write_text(t+b)
 print(overview,flush=True)
if __name__=="__main__":main()

