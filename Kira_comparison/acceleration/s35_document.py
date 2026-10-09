"""Update documentation from the complete, independently checked comparison."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=json.loads((HERE/"summary.json").read_text());a=json.loads((HERE/"results_validation.json").read_text())
f=json.loads((HERE/"frozen_policy.json").read_text())
assert a["passed"] and a["trials"]==s["planned_records"]
seed=f["selected_seed_policy"]
def item(p):
 c=next(x for x in s["comparisons"] if (x["numerator"],x["denominator"],x["metric"])==(p,"trim","total_seconds"))
 t=s["totals"][p]
 timing="unavailable" if c["ratio"] is None else f'{c["ratio"]:.6f} (descriptive 95% interval {c["interval95"][0]:.6f}–{c["interval95"][1]:.6f}, {c["batches"]} complete paired batches)'
 return f'{p}: complete-time ratio to restricted native Kira {timing}; {t["exact_successes"]} exact completions, {t["failed_attempts"]} failed trials and {t["skipped"]} skipped repeats.'
results="\n\n".join(item(p) for p in [seed,"row_cpp","combined"])
text="""# Native Kira integration and measured costs

This folder contains direct seed filtering and an in-process source-row policy using the existing frozen models. It preserves earlier experiments and original checkpoints. The goal is lower complete calculation time; the measurements below determine whether each tested policy achieved that goal.

## Integration

The seed model uses its original weights through NumPy. It scores the public candidate pool using family data, target terms and master labels. The selected configuration in frozen_policy.json is the result of a six-family adapter-validation comparison. It is fixed before the reserved timing tests. s16_select_seeds.py uses this configuration by default and emits an individual seed whitelist, scores and enclosing sector bounds.

KIRA_ML_SEEDS activates a native pyRed gate before each selected seed produces IBP and Lorentz identities. The gate preserves symmetry handling. Without this variable, generation follows the existing code. KIRA_ML_SEED_AUDIT records allowed and actually used vectors. Bounds must contain the whitelist; a whitelist alone does not configure the reduction job.

The row network scores possible sources for the largest-ID destination in the current repeated-leading-column group. Kira's ordering fixes the pivot. Both rows can have changed in earlier exact updates. A two-row group has one allowed action and skips network evaluation. The model uses sampled coefficients for features, while Kira/Fermat retains exact symbolic arithmetic. The current compiled interface accepts at most sixteen integral indices and uses the fixed public prime 2147483647; unsupported inputs require the stock fallback. The compiled implementation uses float32 features and unchanged float32 weights with float64 neural arithmetic. cpp_equivalence.json gives independent sampling, feature, probability and source-choice checks. The probability check uses 1e-10 absolute tolerance, including roundoff ties in the maximum. Original float32 probability differences are reported separately.

The combined policy uses individual learned seeds and compiled row choices in the same isolated Kira binary. All experimental modes retain the prescribed master basis. Incomplete learned reductions trigger restricted stock-Kira fallback within the remaining time. Exact final coefficients are checked against stored references after prediction and reduction. Reference coefficients, seed labels and construction histories do not enter prediction.

## Fixed comparison and results

Development comparisons used three reserved training-family instances. Six adapter-validation instances use different kinematic groups from the original neural-training partition. Adapter validation selects an interface and threshold; it does not measure neural generalization. The twelve new cost-test instances belong to six original-test groups and exclude every box group in earlier cost comparisons. All new cases are one-loop boxes with independent propagator bases. Broader high-loop speedups are outside this experiment.

The reserved modes are restricted native bounds (trim), exact target-derived bounds with fallback (tight), the complete stored candidate pool (pool_filter), the validation-selected learned seed policy, the compiled source-row policy and both learned policies together. Each family has batches of 16 and 64 stored expressions. Each batch uses five rotated repetitions, one thread, one node and identical targets and masters. The array allowance increased from two jobs to four after 128 measured trials and then to eight after 317 measured trials, following node-memory and storage checks; execution_amendment.json records both scheduler-only changes. The frozen computation policies and per-trial limits stayed fixed. The initial native allowance is 160 seconds for all reserved methods, within a 180-second full-process cap. Earlier seed development/validation attempts used a shorter initial allowance, as recorded in validation_protocol.json.

After the first failed measured repeat for a method and batch, remaining repeats are explicitly marked skipped, with no assigned time. Medians and ratios require all five repeats to succeed for both methods. Completion counts include failures and skipped repetitions. The 95% intervals resample complete kinematic groups 10,000 times and are descriptive for that completed subset.

RESULTS

The planned, executed, completed and skipped counts are in summary.json and results_validation.json. The complete time includes input loading, features and model inference, native algebra, final expression combination, failed attempts, fallback and exact checks. The native-with-inference subtotal excludes input preparation, final combination and verification. Generation counters count reported equations across passes, and forward updates count committed row eliminations. Neither counter measures all symbolic arithmetic.

## Reproduction and files

Use the existing project scientific Python environment and the documented Kira 3 source/build dependencies. The original stock binary is preserved. build.json and cpp_build.json contain exact compile/link commands and hashes. The thin pyRed archive references unchanged original object files and must be rebuilt with those dependencies.

1. s00_prepare.py selects grouped development, validation and reserved cost-test cases and writes plan.json. Preserve the released frozen plan when reproducing this study.
2. s01_fast_seed.py implements seed inference; s02_export_seed.py exports/checks unchanged weights. s03_seed_filter.h supplies the gate; s04_build.py builds the isolated filtered binary; s05_setup.sh schedules export and compilation.
3. s06_worker.py runs one exact comparison; s07_run.py rotates repeated trials and enforces resource bounds; s08_run.sh configures its scratch and environment.
4. s09_fast_row.py implements exported row inference; s10_export_row.py checks/export weights; s11_row_server.py supplies the full-group and source-only Python row interfaces; s12_export_row.sh schedules export and checks.
5. s13_audit.py independently verifies final master coefficients at stored sample points, exact row updates, action legality and recorded probability maxima, seed gating and frozen inputs. s14_summary.py writes completion accounting, paired ratios, group bootstrap intervals and figure_values.csv.
6. s15_array.sh runs the six adapter-validation cases. s16_select_seeds.py is the seed-selection CLI. s17_update_report.py writes checked results into the paper after the data release.
7. The component_pilot/ and row_source_pilot/ records retain development variants. s20_freeze.py freezes the validation-selected seed mode, runtime sources, unchanged model hashes and all scientific inputs. s21_freeze.sh runs validation checks, freezes the policy, verifies the combined mode, and submits the final array and final audit. s22_test_array.sh runs the 24 reserved family/batch cases with at most eight simultaneous jobs.
8. s23_cpp_model.h implements native sampled features and neural inference; s24_export_cpp.py writes s24_row_weights.h; s25_cpp_live_policy.h supplies the exact-row integration; s26_build_cpp.py builds the combined-capable native binary; s27_build_cpp.sh schedules compilation.
9. s28_cpp_pilot.sh and s30_cpp_pilot_v2.sh retain the initial precision checks. s29_cpp_audit.py checks independent coefficient sampling, features, probabilities and source choices. s33_cpp_pilot_v3.sh runs the double-precision development trials and s34_cpp_check.sh schedules their audit.
10. s40_preflight_worker.py through s46_adaptive_check.sh test early master checks and ranked budget expansion. s47_residual_worker.py through s49_residual_pilot.sh test expansion from remaining unreduced integrals. s50_development_summary.py and s51_development_audit.sh verify all 26 development records; s52_development_report.py writes the corresponding report subsection. These preserve the frozen reserved comparison.
11. transfer_plan.json and transfer_freeze.json fix a separate two-loop propagator check before execution. s53_transfer_worker.py and s54_transfer_run.py use the same frozen models and exact checks on the specified target offset. s55_transfer_audit.py independently checks the outputs. s56_transfer_test.sh schedules sixty planned records, including a deterministic compiled row control. s57_transfer_summary.py and s58_transfer_plot.py report complete-cost timing and paired-repeat descriptive intervals. s59_transfer_report.py writes their report text, and s60_finish_transfer.sh schedules these final steps. The family appeared in earlier comparisons; this check does not establish generalization to a newly unseen family.
12. s31_plot.py creates the two report figures. s32_finalize.sh runs the final independent audit, summary and plots. s35_document.py updates these READMEs. s36_evidence.py stores and checks shared solver text without repeated copies. s37_build_report.sh renders the final paper under resource limits. s38_compact_records.py deduplicates completed prediction/check arrays; s39_records.py restores them and verifies an unchanged logical-record hash.

The exact script filenames are part of this release; older development variants and plan amendments remain for reproducibility. The archived cpp_initial/ and cpp_v2/ sources document earlier numerical implementations. Production timing uses the frozen source hashes in frozen_policy.json.

Example seed-selection command from the project root:

    .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s16_select_seeds.py --help

The worker is the current complete integration driver. Supplying a standalone whitelist still requires a correctly configured Kira family, targets, bounds, master checks and fallback. A limited public candidate pool is not a list of every possible IBP seed.

## Evidence and storage

results/*.json.gz contains each planned record. Large evidence values contain a SHA-256 digest and uncompressed byte count; their complete UTF-8 text is stored once in evidence/<digest>.txt.gz or evidence/<digest>.txt.xz. Verified lossless recompression uses s61_evidence_archive.py and s62_compress_evidence.sh; s63_maintain_archive.sh keeps the retained-data cap clear during remaining trials. s64_resume_trials.py records and submits storage-interrupted trials on their original nodes. Compression changes no evidence bytes, decisions, timings or logical-record hashes. Load each trial with s39_records.read_record(path), then call s61_evidence_archive.unpack(record["evidence"]) to restore and hash-check the original mapping. Smaller values remain inline. Completed prediction arrays and final coefficient-check arrays can also refer to structured_evidence/<digest>.json.gz. The _storage field records a hash of the full original logical record; read_record restores the arrays and verifies that hash. This postprocessing changes storage only, with no change to frozen execution code, decisions or measurements. result_sha256 in results_validation.json fixes every trial file, while the evidence digests fix their shared text.

Raw records, models and scientific data stay on Hoffman and GitHub. Only report sources and plots are synchronized locally. Limits are one thread per trial, at most eight concurrent array jobs plus one bounded development job, 1.9 GB child address space, 1.7 GB sampled process-tree RSS, 64 MiB trial scratch and 190 MB retained acceleration output. The publication check includes up to four copies of new data plus two Git indexes and remains under the user's 10 GB total project ceiling. Failed jobs preserve their available evidence. Repeated evidence is deduplicated without dropping equations or row histories.

No threshold, weight, action rule or target choice is tuned from the reserved timing results. Deployment decisions must use the measured scope, completion rates and full cost rather than seed counts alone.
""".replace("RESULTS",results)
(HERE/"README.md").write_text(text)
block=("The native integration in [Kira_comparison/acceleration](Kira_comparison/acceleration) filters individual IBP seeds before generation and evaluates the unchanged row network in Kira's process. The reserved comparison has "+str(s["planned_records"])+" planned records, "+str(s["executed_trials"])+" measured trials and "+str(s["exact_successes"])+" exact completions; remaining repeats after a failed trial are explicitly skipped. "+results.replace("\n\n"," ")+" All ratios include complete checked calculation time on complete paired cohorts. The report gives the controls, failures, descriptive intervals and one-loop scope.")
for rel,link in [("README.md","Kira_comparison/acceleration"),("Kira_comparison/README.md","acceleration"),
                 ("ML_model_seed_selection/README.md","../Kira_comparison/acceleration"),
                 ("ML_model_reduction/README.md","../Kira_comparison/acceleration")]:
 p=ROOT/rel;old=p.read_text();marker="<!-- native-acceleration -->"
 if marker in old:old=old.split(marker,1)[0].rstrip()+"\n"
 old+="\n"+marker+"\n"+block.replace("(Kira_comparison/acceleration)","("+link+")")+"\n"
 p.write_text(old)
p=ROOT/"report/README.md";old=p.read_text();marker="<!-- native-acceleration -->"
if marker in old:old=old.split(marker,1)[0].rstrip()+"\n"
old+="\n"+marker+"\nkira_acceleration.tex and kira_acceleration_results.tex explain direct seed filtering, NumPy seed inference, the compiled source-row policy and their reserved native comparisons. The new plots are native_acceleration_times.pdf, native_acceleration_work.pdf and native_transfer_times.pdf. kira_adaptive_development.tex records the separate early-admission experiments, and kira_transfer_results.tex gives the two-loop transfer comparison. The numerical values come from Kira_comparison/acceleration/summary.json and its independent audit. The supplied abstract and earlier results remain unchanged. The complete report folder, including the new figures, is synchronized to Hoffman, GitHub and the local report directory.\n"
p.write_text(old)
print(results)
