"""Document only verified higher-loop measurements and the selected deployment."""
import argparse,hashlib,re,shutil
from s00_math import *
def block(p,start,end,text,prepend=False):
 s=p.read_text();v=start+"\n"+text.rstrip()+"\n"+end
 if start in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+v+s[b:]
 elif prepend:s=v+"\n\n"+s
 else:s=s.rstrip()+"\n\n"+v+"\n"
 p.write_text(s)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");args=ap.parse_args()
 s=json.loads((HERE/"model_test/summary.json").read_text());v=json.loads((HERE/"model_test/verification.json").read_text())
 policy=json.loads((HERE/"trained_model/deployment.json").read_text());model=json.loads((HERE/"trained_model"/policy["model"]).read_text())
 audit=json.loads((HERE/"validation/reader_audit.json").read_text())
 assert s["all_exact"] and v["all_passed"] and audit["all_passed"]
 c=s["comparisons"];deployed="shared_learned" if policy["deployed_mode"]=="learned" else "shared_control"
 result=c[deployed+"_over_separate_dense"]["external_seconds"]
 separate=c["separate_learned_over_separate_dense"]["external_seconds"]
 shared=c["shared_learned_over_shared_dense"]["external_seconds"]
 control=c["shared_learned_over_shared_control"]["external_seconds"]
 fmt=lambda d:f"{d['ratio']:.3f} (descriptive interval {d['interval'][0]:.3f}--{d['interval'][1]:.3f})"
 notice=f"The higher-loop extension generates exact Euler and mass partial-fraction equations for the restricted coupled vacuum family, then uses Kira's user-defined-system solver. A shared variable z=L(d-2) supports every positive loop order mathematically. Tests cover L=1,...,12, with additional applications at 13, 16, 24 and 32. Across six reserved batches, the deployed route has complete-time ratio {fmt(result)} to separate full-pool reductions. The learned separate-loop route has ratio {fmt(separate)} to the same full-pool baseline. Learned/shared versus rule/shared has ratio {fmt(control)}. Validation selects the {policy['deployed_mode']} route. These are supplied-identity results, with exact coefficient checks and all runtime costs; they do not establish a generic high-loop native Kira speedup."
 for p in [ROOT/"README.md",ROOT/"Kira_comparison/README.md",HERE.parent/"README.md"]:
  prefix="ML_model_equation_selection/higher_loops" if p.parent==ROOT else "../ML_model_equation_selection/higher_loops" if p.parent.name=="Kira_comparison" else "higher_loops"
  block(p,"<!-- higher-loop-acceleration -->","<!-- higher-loop-acceleration-end -->",notice+"\n\nSee ["+prefix+"/README.md]("+prefix+"/README.md).")
 p=ROOT/"integrals/higher_loops/README.md"
 block(p,"<!-- higher-loop-solver -->","<!-- higher-loop-solver-end -->","The generated scalar components can now use the [higher-loop Kira workflow](../../ML_model_equation_selection/higher_loops/README.md). Its request exporter reads existing family definitions and target components. The exact substitution z=L(d-2) shares coefficient reductions across loop orders within this restricted domain. The original family data and grouped split remain the training-data reference.")
 p=HERE/"README.md";t=p.read_text().replace("twelve exponent features","eighteen exponent features").replace("The model has twelve","The model has eighteen")
 t=t.replace("Results and frozen deployment will be added after the scheduled comparisons. No measured speedup is claimed before those tests.",notice)
 if "The archived development_initial/ directory" not in t:t=t.replace("Then run s06_select.py","The archived development_initial/ directory preserves the first 144 validation workflows and three pilots. The final integration adds ordered-index features and an exact reader checked on 277 distinct coefficients. The refined training and validation records are in training/ and validation/.\n\nThen run s06_select.py")
 if "The frozen application is s08_application.py." not in t:t+="\nThe frozen application is s08_application.py. It selects the validation-approved route automatically; --policy learned runs the saved System 1 model explicitly. s16_export_existing.py prepares scalar-component requests from the existing coupled vacuum collection. The exporter retains the original expression identifiers; combine the returned component reductions with the original target weights when reducing those expressions.\n\ns07_analyze.py audits all saved exports, s09_plot.py makes the figures, and s14_extrapolate.py checks the deployed application above twelve loops. model_test/ contains 90 paired workflows and six additional applications. Its source choices identify every generated equation and Euler seed. Exact exports and solver logs are content-addressed in objects/; each JSON record stores their SHA256 digest.\n"
 p.write_text(t)
 for name,text in {
 "training/README.md":f"Training examples contain {model['training_rows']} candidate actions in {model['training_groups']} exponent shapes. examples.json.gz stores indices, candidate pairs, features, teacher counts and labels. The maximum total power is nine. The reference minimizes a local union of recursively selected dependencies; no global optimum is claimed.\n",
 "trained_model/README.md":f"depth4.json, depth8.json and depth12.json retain the trained trees. Validation selects {policy['model']} as the learned candidate. deployment.json selects {policy['deployed_mode']} for the current application because complete validation cost determines the route. freeze.json fixes runtime sources, training code, all weights, target definitions and the Kira binary before tests. Leaf frequencies are uncalibrated ranking scores.\n",
 "validation/README.md":"results/ contains 144 refined validation workflows on six batches with three repetitions of eight candidates. The split uses distinct mass profiles. reader_audit.json compares 277 unique coefficients against symbolic algebra, checks five special cases and rejects five unsupported expressions. The earlier integration remains in ../development_initial/ and does not select the final route.\n",
 "model_test/README.md":notice+"\n\nsummary.json gives six batch medians, complete ratios, per-loop solver ratios, equation counts and resource use. verification.json checks 90 comparisons and six additional applications against an independent partial-fraction formula. The primary set covers all loop orders one through twelve. Extra applications cover 13, 16, 24 and 32. Ratios use geometric means of batch median ratios; descriptive intervals resample six batches. See inputs/, results/, extrapolation/ and plots/.\n"
 }.items():(HERE/name).write_text(text)
 if not args.data_commit:return
 assert re.fullmatch("[0-9a-f]{40}",args.data_commit)
 report=ROOT/"report";template=(HERE/"report_template.tex.in").read_text()
 training=f"""The training set contains {model['training_rows']:,} candidate actions in
{model['training_groups']:,} exponent shapes, with total power through nine.
We fit depth limits four, eight and twelve using a minimum child size of
four examples. Validation selects the depth-{model['maximum_depth']} candidate, which
contains {len(model['nodes'])} nodes. We preserve the first development pass
and repeat validation after refining the ordered-index features and the
coefficient reader. On 277 distinct development coefficients, the reader
agrees with symbolic algebra and takes {audit['fast_seconds']:.3f} seconds,
compared with {audit['symbolic_seconds']:.3f} seconds for the symbolic
reader. This reading improvement applies to every comparison arm and is
separate from the learned decision.
"""
 design=f"""The refined validation contains 144 workflows on six mass-profile batches.
It compares the three trees with first-pair, smallest-pair, largest-pair and
extreme-pair rules and the full pool. Each candidate has three repetitions.
The extreme-pair rule chooses an active denominator with the smallest
power and one with the largest power. Validation selects the
{policy['deployed_mode']} route; the selected learned candidate costs
{100*(policy['learned_over_control']-1):.1f}\\\\% more than the selected rule.
We freeze sources, weights, profiles and target lists before 90 reserved
workflows. The reserved set has two profiles for each of
\\\\(R=2,3,4\\\\), with maximum powers eight and twelve, and runs every
\\\\(L=1,\\\\ldots,12\\\\). Some lower-power exponent shapes also occur in
training; the power-twelve cases extend its power bound. The tests vary
mass profiles within the same topology and do not test new graph classes.
We use three repetitions and report geometric means of the six ratios of
batch medians. Descriptive intervals resample those six batches.
""".replace("\\\\","\\")
 results=f"""For separate reductions at each loop order, learned selection gives
a complete-time ratio of {separate['ratio']:.3f} to the full pool, with
descriptive interval \\\\([{separate['interval'][0]:.3f},{separate['interval'][1]:.3f}]\\\\).
With exact loop reuse in both arms, learned selection gives a ratio of
{shared['ratio']:.3f} to the shared full pool, with interval
\\\\([{shared['interval'][0]:.3f},{shared['interval'][1]:.3f}]\\\\).
The learned/shared ratio to the rule/shared control is
{control['ratio']:.3f}, with interval
\\\\([{control['interval'][0]:.3f},{control['interval'][1]:.3f}]\\\\).
These comparisons keep the incremental learned effect separate from
the exact reuse of coefficient equations.

The deployed shared route gives a complete-time ratio of
{result['ratio']:.3f} to separate full-pool reductions, with interval
\\\\([{result['interval'][0]:.3f},{result['interval'][1]:.3f}]\\\\).
This corresponds to {1/result['ratio']:.2f} times faster execution of the
twelve-order workload under the stated timing definition.
Figures~\\\\ref{{fig:higher-loop-complete-time}} and
\\\\ref{{fig:higher-loop-equations}} show the batch costs and equation counts.
Validation fixes the deployed rule before these tests; we retain the
learned results as a measured alternative.
""".replace("\\\\","\\")
 check=f"""All 90 reserved workflows and six additional applications pass exact
checks. The extra applications use loop orders 13, 16, 24 and 32.
The audit checks {s['coefficient_checks']:,} coefficient positions, including
{s['distinct_coefficient_positions']:,} distinct positions, across
{s['kira_calls']} Kira calls. It finds {s['attempt_failures']} failed attempts
and {s['fallbacks']} fallback workflows.
The largest sampled Kira process-tree memory is
{s['peak_kira_tree_rss_bytes']/1024**2:.2f} MiB, and the largest temporary
solver storage is {s['peak_scratch_bytes']/1024**2:.2f} MiB.
The analytic reference also supplies a direct reduction for this
special family. The reported comparisons measure Kira-backed routes.
"""
 for key,value in [("TRAINING",training),("DESIGN",design),("RESULTS",results),("AUDIT",check)]:template=template.replace("@@"+key+"@@",value)
 assert "@@" not in template
 (report/"higher_loop_acceleration.tex").write_text(template)
 shutil.copy2(HERE/"model_test/plots/complete_times.pdf",report/"figures/higher_loop_complete_times.pdf")
 shutil.copy2(HERE/"model_test/plots/loops_and_equations.pdf",report/"figures/higher_loop_equations.pdf")
 p=report/"equation_selection.tex";t=p.read_text()
 if r"\input{higher_loop_acceleration}" not in t:t+=r"\input{higher_loop_acceleration}"+"\n"
 p.write_text(t)
 p=report/"Makefile";p.write_text(p.read_text().replace("equation_selection_early.tex references.bib","equation_selection_early.tex higher_loop_acceleration.tex references.bib"))
 p=report/"report.tex";t=p.read_text();abstract=t.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 conclusion=f"""The higher-loop extension uses the exact variable \\\\(z=L(d-2)\\\\) for the
restricted coupled vacuum family. The trained equation selector and a
shared symbolic reduction cover every tested order from one through
twelve, with exact applications at 13, 16, 24 and 32.
The separate-loop learned route has complete-time ratio
{separate['ratio']:.3f} to the supplied full pool. Validation selects a
simple mass-pair rule for deployment; its shared route has complete-time
ratio {result['ratio']:.3f} to separate full-pool reductions.
All 96 workflows pass exact checks. These results establish the stated
family-specific coefficient reuse and cost comparisons. General
higher-loop native IBP generation remains outside this test domain
\\\\cite{{KiraHigherLoopData}}.
""".replace("\\\\","\\")
 marker="% BEGIN HIGHER LOOP CONCLUSION";end="% END HIGHER LOOP CONCLUSION"
 if marker not in t:t=t.replace(r"\clearpage"+"\n"+r"\renewcommand{\refname}{Citations}",marker+"\n"+conclusion+end+"\n\n"+r"\clearpage"+"\n"+r"\renewcommand{\refname}{Citations}")
 else:
  a=t.index(marker);b=t.index(end,a)+len(end);t=t[:a]+marker+"\n"+conclusion+end+t[b:]
 p.write_text(t)
 url="https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"+args.data_commit+"/ML_model_equation_selection/higher_loops"
 bib=f"""@misc{{KiraHigherLoopData,
 author = {{Saraswat, Rushil}},
 title = {{Equation selection and exact coefficient reuse across loop orders}},
 year = {{2026}},
 howpublished = {{\\href{{{url}}}{{Frozen models, identities, complete timings and exact higher-loop checks}}}},
 note = {{GitHub repository, commit \\texttt{{{args.data_commit[:12]}}}}}
}}"""
 block(report/"references.bib","% higher-loop-data-begin","% higher-loop-data-end",bib)
 print(json.dumps(dict(documented=True,data_commit=args.data_commit,abstract_unchanged=True)))
if __name__=="__main__":main()
