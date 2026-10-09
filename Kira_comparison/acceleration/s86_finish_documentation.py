"""Finish release documentation after every declared comparison has been audited."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text())
d=read("expression_summary.json");s=read("expression_test_summary.json");a=read("expression_test_validation.json");t=read("transfer_summary.json")
assert a["passed"] and a["trials"]==s["planned"]==360
policy=s["selected_policy"]
c=next(c for c in s["comparisons"] if c["numerator"]==policy and c["denominator"]=="stored_pool" and c["size"] is None)
dc=next(c for c in s["comparisons"] if c["numerator"]==policy and c["denominator"]=="stored_distance" and c["size"] is None)
def value(c):
 if c["ratio"] is None:return "unavailable"
 lo,hi=c["interval95"]
 return f'{c["ratio"]:.6f} (descriptive 95% interval {lo:.6f}–{hi:.6f}; {c["paired_batches"]} complete paired batches)'
brief=("The whole-expression interface uses the frozen seed model, Kira's early master check, exact supplied-equation reduction and full-pool fallback. "
 f'The reserved comparison contains {s["planned"]} planned records, {s["executed"]} measured trials and {s["exact"]} exact completions. '
 +"Its complete-time ratio to the full-pool supplied-equation control is "+value(c)+", and its ratio to the fixed 64-seed distance control is "+value(dc)+". "
 +f'The full-pool control completed {len(c["control_only"])} additional batches and the learned method completed {len(c["learned_only"])} additional batches. '
 +"Both comparisons start from the same existing identity pool and include loading, prediction, equation export, exact algebra, failed attempts, fallback and checks. "
 +"Offline pool generation is outside both measurements. These are constructed targets from twelve original-held-out one-loop box instances in six kinematic groups.")
transfer=("The separate two-loop transfer has 60 exact completions. For 64 targets the compiled learned-row pipeline took a median 12.460 seconds against 12.770 seconds for restricted native Kira, a 2.4% reduction. "
 "Its advantage over the deterministic compiled source control remains unresolved, and the full-pool control was faster at 11.773 seconds. Both seed-containing policies required fallback in every 64-target repeat.")
marker="<!-- whole-expression-confirmation -->"
extra="""## Complete target expressions

BRIEF

The 80 separate development and adapter-validation records precede this confirmation. Six adapter-validation instances belong to the original model-training groups. Validation chose the early-check interface, with a complete-time ratio of 0.930153 to the full pool over eleven successful paired batches. The model weights and threshold 0.01 remained fixed before the twelve original-held-out instances were measured. A failed measured repetition causes the remaining identical repeats to be marked skipped; skipped observations have no runtime. Five successful repetitions for both policies are required for a timing ratio. Descriptive intervals resample complete kinematic groups and do not establish a general high-loop speedup.

The full-pool control uses stock Kira's supplied-equation mode. The distance control selects 64 candidate seeds by minimum L1 index distance to a target component, with lexicographic tie-breaking, and uses the same full-pool fallback. The learned method receives no reference coefficients, seed labels or reverse-construction path. The early check is global to the selected system and can reject a system whose particular target combinations would reduce; fallback costs remain included.

- s65_expression_worker.py, s66_expression_run.py and s67_expression_pilot.sh implement the first supplied-expression trials; expression_v1/ preserves the original 0.5-only worker. s68_expression_audit.py verifies selected seeds, identity membership, raw Kira exports and independent sample coefficients.
- s69_expression_preflight.py through s71_expression_preflight.sh test early global master admission. s72_expression_small.sh checks individual targets and four-target batches.
- s73_expression_policy_worker.py through s77_expression_finish.sh run and audit the separate six-instance adapter-validation experiment. expression_summary.json preserves every development and validation result and the selection decision.
- s78_expression_controls_worker.py adds the fixed distance control, and s79_expression_test_run.py applies the same time, memory and scratch bounds to all confirmation policies. s80_expression_test_audit.py checks the frozen code, model and input hashes, every final output, selected identity set and raw exported coefficient.
- s81_expression_freeze.py records expression_freeze.json and submits the twenty-four case/batch jobs in s82_expression_test_array.sh with at most four simultaneous single-thread trials. s83_expression_test_summary.py keeps completion counts separate from paired timing ratios. s84_expression_finalize.sh runs the independent audit and summary.
- s85_expression_report.py writes the scientific report section, s87_expression_plot.py creates its standalone PDF figure, and s86_finish_documentation.py updates the READMEs after s35_document.py. s37_build_report.sh renders all final plots and the paper under bounded resources.

expression_test/*.json.gz contains all planned records. Read them through s39_records.read_record, and resolve evidence through s61_evidence_archive.unpack. expression_test_validation.json fixes the trial-file hashes and contains the independent checks; expression_test_summary.json contains the complete accounting and paired medians. The same storage rules and original model checkpoints apply.

## Two-loop transfer

TRANSFER

The stronger deterministic controls and unsuccessful native learned policies remain in the release. The complete native seed, row and combined ratios to restricted Kira are 1.295050, 1.023629 and 1.983350. The compiled row code reduces prediction overhead, but the present weights do not give an aggregate native reduction speedup on the reserved one-loop comparison.
""".replace("BRIEF",brief).replace("TRANSFER",transfer)
p=HERE/"README.md";text=p.read_text().split(marker,1)[0].rstrip();p.write_text(text+"\n\n"+marker+"\n"+extra+"\n")
for rel,link in [("README.md","Kira_comparison/acceleration"),("Kira_comparison/README.md","acceleration"),
 ("ML_model_seed_selection/README.md","../Kira_comparison/acceleration"),("ML_model_reduction/README.md","../Kira_comparison/acceleration")]:
 p=ROOT/rel;text=p.read_text().split(marker,1)[0].rstrip()
 p.write_text(text+"\n\n"+marker+"\n"+brief+"\n\n"+transfer+"\n\n"+"Code, raw measurements and checks: ["+link+"]("+link+").\n")
p=ROOT/"report/README.md";text=p.read_text().split(marker,1)[0].rstrip()
p.write_text(text+"\n\n"+marker+"\n"+"kira_expression_results.tex adds the complete-expression seed interface, its validation and its 360-record reserved confirmation. figures/whole_expression_times.pdf compares complete costs with the full equation pool and the fixed distance rule. The source values are expression_summary.json, expression_test_summary.json and their independent audits. The conclusion reports native, two-loop transfer and whole-expression results with their separate scopes.\n")
print(brief)

m=read("expression_matched_summary.json");ma=read("expression_matched_validation.json")
assert ma["passed"] and ma["trials"]==m["planned"]==360
mc=next(x for x in m["comparisons"] if x["numerator"]==m["selected_policy"] and x["denominator"]=="stored_pool" and x["size"] is None)
md=next(x for x in m["comparisons"] if x["numerator"]==m["selected_policy"] and x["denominator"]=="stored_distance_checked" and x["size"] is None)
matched=("The additional matched-admission confirmation applies the same early master check and full-pool fallback to learned seeds and the 64-seed distance control. "
 f'It contains {m["planned"]} planned records, {m["executed"]} measured trials and {m["exact"]} exact completions. '
 +"The learned complete-time ratios are "+value(mc)+" against the full pool and "+value(md)+" against the matched distance control. "
 +f'The full-pool control completed {len(mc["control_only"])} additional batches, and the learned method completed {len(mc["learned_only"])} additional batches. '
 +"This repeats the same twelve physical family instances; it is not a new-family test. The first comparison is fully retained, and its distance control lacks the early admission check.")
marker2="<!-- matched-admission-confirmation -->"
for rel in ["README.md","Kira_comparison/README.md","ML_model_seed_selection/README.md","ML_model_reduction/README.md","report/README.md","Kira_comparison/acceleration/README.md"]:
 p=ROOT/rel;text=p.read_text().split(marker2,1)[0].rstrip()
 text+="\n\n"+marker2+"\n"+matched+"\n"
 if rel=="Kira_comparison/acceleration/README.md":
  text+="\nThe matched protocol was fixed with 79 first-confirmation records present, before its aggregate results were examined. expression_matched_freeze.json states the identical admission rule and frozen sources; expression_concurrency.json accounts for at most eight simultaneous trials across both arrays and a combined working storage upper bound below 9.555 GB.\n"
  text+="\ns88_matched_expression_worker.py applies the shared check, s89_matched_expression_run.py runs bounded trials, and s90_matched_expression_array.sh schedules the 24 case/batch jobs. s91_matched_expression_audit.py independently verifies all reductions and seed sets. s92_matched_expression_summary.py computes completion accounting and matched costs; s93_matched_expression_finalize.sh schedules these checks. s94_matched_expression_report.py updates the paper, and s87_expression_plot.py --matched writes the separate comparison plot. s95_release_checks.py verifies every declared audit, frozen source and trial hash before publication. s96_prepare_release.sh schedules the final report, figures, READMEs and release checks after both confirmations finish.\n"
 if rel=="report/README.md":text+="\nkira_expression_matched.tex and figures/whole_expression_matched_times.pdf give the matched-admission result. Both selectors use the same early check in this comparison.\n"
 p.write_text(text)
print(matched)

single=next(x for x in m["comparisons"] if x["numerator"]==m["selected_policy"] and x["denominator"]=="stored_pool" and x["size"]==1)
sd=next(x for x in m["comparisons"] if x["numerator"]==m["selected_policy"] and x["denominator"]=="stored_distance_checked" and x["size"]==1)
finding=(f'The predefined single-target comparison gives {100*(1-single["ratio"]):.1f}% lower geometric mean complete time against the full-pool Kira control and {100*(1-sd["ratio"]):.1f}% lower time against the distance control with the same early check. Both descriptive intervals lie below one across all twelve held-out instances, with five exact repeats per method. The earlier confirmation gave 7.8% lower time against the full pool for this batch size. The sixteen-target intervals include one. This measured benefit applies to one constructed target expression at a time using an existing IBP identity pool; it does not establish a native Kira or general high-loop speedup.')
marker3="<!-- single-target-result -->"
for rel in ["README.md","Kira_comparison/README.md","ML_model_seed_selection/README.md","ML_model_reduction/README.md","report/README.md","Kira_comparison/acceleration/README.md"]:
 p=ROOT/rel;text=p.read_text().split(marker3,1)[0].rstrip()
 p.write_text(text+"\n\n"+marker3+"\n"+finding+"\n")
print(finding)
