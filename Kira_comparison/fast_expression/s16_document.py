"""Update the experiment and project READMEs from audited results."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 s=json.loads((HERE/"test_summary.json").read_text());audit=json.loads((HERE/"test_validation.json").read_text());assert audit["passed"]
 find=lambda n,d,b:next(c for c in s["comparisons"] if (c["numerator"],c["denominator"],c["size"])==(n,d,b))
 c=find("exit_ml","stock_ml",1);m=find("exit_ml","exit_pool",1);b=find("exit_ml","stock_ml",16)
 note=(f'The responsive Fermat shutdown comparison contains {s["planned"]} planned records, {s["executed"]} measured trials and {s["exact"]} exact completions in twelve new held-out one-loop box instances. '
 f'For one target, the modified learned workflow has a complete-time ratio of {c["ratio"]:.6f} to the original learned workflow '
 f'(descriptive 95% interval {c["interval95"][0]:.6f}–{c["interval95"][1]:.6f}; {c["paired_batches"]} paired batches), '
 f'with geometric mean times {c["denominator_geometric_mean_seconds"]:.3f} and {c["numerator_geometric_mean_seconds"]:.3f} seconds. '
 f'For sixteen targets the corresponding ratio is {b["ratio"]:.6f} (interval {b["interval95"][0]:.6f}–{b["interval95"][1]:.6f}). '
 f'Against the full pool with the same shutdown improvement, the single-target learned ratio is {m["ratio"]:.6f} '
 f'(interval {m["interval95"][0]:.6f}–{m["interval95"][1]:.6f}). '
 'All completed reductions matched exact references. Both learned methods use the same original weights, threshold, early master check and fallback. '
 'The shutdown change preserves symbolic operations and also applies to the full-pool control. These measurements use existing IBP identity pools; they exclude their original generation.')
 marker="<!-- responsive-fermat-exit -->"
 for name in ["README.md","Kira_comparison/README.md","ML_model_seed_selection/README.md","report/README.md"]:
  p=ROOT/name;t=p.read_text()
  if marker in t:t=t.split(marker)[0].rstrip()+"\n"
  t+="\n"+marker+"\n"+note+"\n\n"
  t+=("Code, measurements, source patch, frozen inputs and independent checks are in Kira_comparison/fast_expression/. "
       "The report explains the separate shutdown and learned-seed effects in kira_fast_expression.tex and figures/responsive_exit_times.pdf.\n")
  if name=="report/README.md":
   t=t.replace("only report, rules and .gitignore blobs","only report, rules, .gitignore and root .gitattributes metadata blobs")
   t=t.replace("only the explicitly allowed report/rules blobs","only the explicitly allowed report/rules and root Git attributes blobs")
  p.write_text(t)
 p=HERE/"README.md";t=p.read_text()
 t=t.replace("Each method will run five rotated repeats", "Each method used five rotated repeats")
 t=t.replace("At most two single-thread trials run concurrently", "The array began with two single-thread trials, increased to three after 95 records and later to six, with unchanged per-trial limits")
 if marker in t:t=t.split(marker)[0].rstrip()+"\n"
 t+="\n"+marker+"\n## Measured results\n\n"+note+"\n\n"
 t+="Completion counts, paired medians, group-resampled intervals and failures appear in test_summary.json. test_validation.json independently checks raw exports, master coefficients, selected identities and model probabilities. Read trial records with s13_records.read_record; this restores losslessly shared arrays and verifies their SHA-256 hashes. Evidence text is stored in evidence/ by digest and is decoded with acceleration/s36_evidence.py after setting its HERE path to this folder. The shared/ directory avoids repeating large identical manifests, source lists, predictions and final coefficients across timing repeats.\n\n"
 t+="## Running and checking the experiment\n\nThe original Kira remains at .tools/kira/bin/kira; the isolated modified executable is .tools/kira-fast-expression/kira. build.json identifies the exact upstream source commit, original and modified hashes, and compile/link commands. connect2kira.patch plus s01_reap_child.h reproduce the only source change. Compilation uses gcc/9.5.0 and the existing Kira dependencies. The patch and helper carry GPL-3.0-or-later licensing.\n\n"
 t+="s05_worker.py runs the existing learned-seed or full-pool workflow with the selected binary. Its arguments are partition, case index, target count, policy, scratch directory and output JSON. The policies are stock_pool, stock_ml, exit_pool and exit_ml; use exit_ml for the measured faster learned workflow. s06_run.py wraps these calls in full-process time, memory and scratch limits and rotates their order. s07_development.sh runs the three development instances. s08_freeze.py fixes runtime code, both original model checkpoints, targets, identities, references and binaries. s09_test_array.sh schedules twelve cases with two batch sizes; s15_confirm.sh submits this array initially with at most two concurrent trials and then the independent audit. scheduler_amendment.json and scheduler_amendment_02.json record the increases to three and then six jobs. The final working storage bound is 9.970 GB, with a temporary 300 MB local allowance while the cluster comparisons run. Local report synchronization is deferred until those jobs finish, when the ordinary 400 MB publication allowance is restored. Frozen calculation code and individual trial limits stayed fixed.\n\n"
 t+="s10_audit.py checks all retained results and verifies original/modified equation-input hashes, elimination counters and unchanged predictions. s11_summary.py reports paired costs and all completion outcomes; s12_check.sh schedules both operations. s13_records.py handles shared arrays. s14_report.py writes measured report text, a standalone PDF figure and figure_values.csv, taking the published data commit for the citation. s16_document.py updates the READMEs. s17_build_report.sh renders the final paper through s21_report_compat.py, which adapts two plotting calls to the installed Matplotlib API without changing the frozen source or results, with s20_report_finish.py stating the completed comparison cohorts and formatting the citation. s18_release.py verifies release readiness, and s19_finalize.sh schedules the final checks and documentation. Use fresh output directories when reproducing the released experiment; the runner refuses to overwrite existing trial records.\n\n"
 t+="The full benchmark has five cold process repetitions per method and case; filesystem caches are not cleared. A failed measured repetition suppresses subsequent identical repetitions and leaves explicit skipped records. Timing ratios require five successes for each compared method. Samples resample entire kinematic groups 10,000 times; intervals describe the completed subset. Development retains two full-pool time-limit failures as well as its successful reductions. Compilation initially used the cluster's older default compiler; loading gcc/9.5.0 fixed that setup error. Both build logs remain outside Git history.\n"
 p.write_text(t)
 print("Experiment, project, model and report READMEs updated",flush=True)
if __name__=="__main__":main()
