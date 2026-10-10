"""Write the report and release summaries from audited fixed-test results."""
import argparse,hashlib,json,re
from s04_workflows import HERE,PARENT,ROOT,guard
def block(path,start,end,text,prepend=False):
 s=path.read_text();text=start+"\n"+text.rstrip()+"\n"+end
 if start in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+text+s[b:]
 elif prepend:s=text+"\n\n"+s
 else:s=s.rstrip()+"\n\n"+text+"\n"
 path.write_text(s)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");args=ap.parse_args()
 s=json.loads((HERE/"model_test/summary.json").read_text());v=json.loads((HERE/"model_test/verification.json").read_text())
 assert s["all_exact"] and v["all_passed"] and json.loads((HERE/"trained_model/deployment_verification.json").read_text())["all_passed"]
 c=s["comparisons"];full=c["deployed_vs_native"]["complete_seconds"];prep=c["deployed_vs_native"]["equation_preparation_seconds"];previous=c["deployed_vs_previous"]["complete_seconds"];control=c["deployed_vs_control"]["complete_seconds"]
 fmt=lambda x:f"{x:.3f}"
 interval=lambda d:"["+fmt(d["interval"][0])+","+fmt(d["interval"][1])+"]"
 notice=f"""The current early equation policy predicts which seed/operator identities to construct. On eight fresh physical profiles, its complete-time ratio to matched native choices is {full['ratio']:.6f}, with descriptive 95% interval {interval(full)}. Its preparation ratio is {prep['ratio']:.6f}, with interval {interval(prep)}. The complete-time ratio to the previous release is {previous['ratio']:.6f}, and the ratio to the distance control is {control['ratio']:.6f}. All {s['workflows']} comparisons and eight basis-only applications pass exact checks. The selected route keeps native seed and row choices and preserves the preceding sunrise policy. These results include every fallback cost and cover known two-/three-loop structures at fixed rational kinematics with symbolic d."""
 for path in [ROOT/"README.md",ROOT/"Kira_comparison/README.md"]:
  block(path,"<!-- early-equation-release -->","<!-- early-equation-release-end -->",notice+"\n\nSee [early equation selection]("+("ML_model_equation_selection" if path.parent==ROOT else "../ML_model_equation_selection")+"/early_generation/README.md).")
 path=ROOT/"README.md";path.write_text(path.read_text().replace("selecting IBP seeds and allowed elimination steps","selecting IBP seeds, equations and allowed elimination steps"))
 path=PARENT/"README.md"
 block(path,"<!-- early-equation-current -->","<!-- early-equation-current-end -->","The current application is [early_generation/s12_reduce.py](early_generation/s12_reduce.py).\n\n"+notice+"\n\nSee the [extension README](early_generation/README.md). The remaining text describes the preceding frozen release.",True)
 path.write_text(path.read_text().replace("The current application is s35_reduce.py.","The preceding application is s35_reduce.py.").replace("The current interface prevents an equation-filter combination","That preceding interface prevents an equation-filter combination"))
 block(HERE/"README.md","<!-- checked-results -->","<!-- checked-results-end -->",notice+f"\n\nThe audit checks {v['coefficient_pairs']:,} coefficient pairs, including {v['distinct_coefficient_pairs']:,} distinct pairs. It retains {v['failed_attempts']} failed attempts from all methods. Maximum observed process-tree RSS is {v['peak_process_tree_rss_bytes']/1024**2:.2f} MiB; maximum scratch is {v['peak_scratch_bytes']/1024**2:.2f} MiB.")
 (HERE/"model_test/README.md").write_text(f"""# Frozen tests

summary.json contains all batch medians and profile-weighted comparisons. verification.json checks {v['workflows']} workflows, including eight applications without reference target answers. plots/ contains standalone PDF figures. The methods, targets and repeats follow ../families_test.json and ../trained_model/freeze.json.

Load workflows through s04_workflows.read to resolve exact payloads in ../objects/. Each record includes every attempt, timing, log, native export and exact check. Training and routing stayed fixed during tests. See the parent README for timing exclusions and scope.
""")
 (HERE/"trained_model/README.md").write_text("""# Trained early equation policies

early_d8/ and early_d12/ contain saved CART trees and native weights. deployment.json specifies structures, target lists, models and thresholds. freeze.json fixes source, weight and binary hashes before tests. deployment_verification.json checks application choices and previous release hashes.

Scores predict recorded support membership. Exact algebra, prescribed-basis admission and fallback enforce the application contract.
""")
 guard()
 if not args.data_commit:return
 assert re.fullmatch("[0-9a-f]{40}",args.data_commit)
 report=ROOT/"report"
 results=f"The deployed policy has a complete-time ratio of {fmt(full['ratio'])} to native choices, with descriptive interval ¤{interval(full)}¤, and a preparation ratio of {fmt(prep['ratio'])}, with interval ¤{interval(prep)}¤. These correspond to {(1-full['ratio'])*100:.1f}\\% lower complete time and {(1-prep['ratio'])*100:.1f}\\% lower preparation time in the profile-weighted comparison. Its complete-time ratio to the preceding release is {fmt(previous['ratio'])}, with interval ¤{interval(previous)}¤. Its ratio to the distance control is {fmt(control['ratio'])}, with interval ¤{interval(control)}¤.\n\n"
 names={"sunrise":"two-loop sunrise","double_box":"two-loop double box","vacuum3":"three-loop vacuum","ladder3":"three-loop ladder"}
 for top in ["sunrise","double_box","vacuum3","ladder3"]:
  d=s["by_topology"][top]["deployed_vs_native"]
  results+=f"For the {names[top]} profiles, the complete-time ratio is {fmt(d['complete_seconds']['ratio'])} and the preparation ratio is {fmt(d['equation_preparation_seconds']['ratio'])}. "
 native=[b["methods"]["native"]["complete_seconds"] for b in s["batches_detail"]];deployed=[b["methods"]["deployed"]["complete_seconds"] for b in s["batches_detail"]]
 results+="\n\n"+f"Across fourteen batches, native median complete times range from {min(native):.3f} to {max(native):.3f} seconds, and deployed medians range from {min(deployed):.3f} to {max(deployed):.3f} seconds. Summing one median per batch gives {s['batch_median_total_seconds']['native']:.2f} seconds for native choices and {s['batch_median_total_seconds']['deployed']:.2f} seconds for the deployed route. This workload sum uses a different weighting from Eq.~\\eqref{{eq:early-cost-ratio}}."
 audit=f"All {v['main_workflows']} comparison workflows and {v['basis_only_applications']} additional applications pass the independent exact audit. The applications receive only the prescribed basis, and their coefficients agree with the reference after execution. The audit checks {v['coefficient_pairs']:,} coefficient pairs, including {v['distinct_coefficient_pairs']:,} distinct pairs. It retains {v['failed_attempts']} failed attempts across all methods; the deployed comparison arm requires {c['deployed_vs_native']['fallback_workflows']} fallback workflows. Maximum observed process-tree memory is {v['peak_process_tree_rss_bytes']/1024**2:.2f} MiB, and maximum temporary solver storage is {v['peak_scratch_bytes']/1024**2:.2f} MiB."
 template=(HERE/"report_template.tex.in").read_text()
 (report/"equation_selection_early.tex").write_text(template.replace("@@RESULTS@@",results).replace("@@AUDIT@@",audit).replace("¤","$"))
 path=report/"equation_selection.tex";t=path.read_text()
 if r"\input{equation_selection_early}" not in t:t+=r"\input{equation_selection_early}"+"\n"
 path.write_text(t)
 path=report/"Makefile";path.write_text(path.read_text().replace("equation_selection_confirmation.tex references.bib","equation_selection_confirmation.tex equation_selection_early.tex references.bib"))
 path=report/"report.tex";t=path.read_text()
 abstract=t.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 t=t.replace("The ladder topology is absent from the new row-policy training and validation","The ladder topology is absent from that row-policy training and validation")
 t=t.replace("The deployed equation\npolicy uses the recorded 21-target sunrise domain","The preceding deployed equation\npolicy uses the recorded 21-target sunrise domain")
 t=t.replace("The deployed interface therefore retains native equation choices when either earlier learned policy is active.","That preceding interface therefore retains native equation choices when either earlier learned policy is active.")
 start="% BEGIN EARLY EQUATION CONCLUSION";end="% END EARLY EQUATION CONCLUSION"
 conclusion=f"""Later training moves the equation decision before coefficient construction.
The trees use 17 seed, operator and target features and train on
153,124 native candidates in eight physical profiles.
Validation selects early filtering with native seed and row choices for
the recorded double-box, vacuum and ladder batches and retains the earlier
sunrise route. On eight fresh profiles, the deployed policy gives a
complete-time ratio of {fmt(full['ratio'])} to native choices, with descriptive interval
¤{interval(full)}¤, and a preparation ratio of {fmt(prep['ratio'])}, with interval
¤{interval(prep)}¤. Its complete-time ratio to the preceding release is
{fmt(previous['ratio'])}. All 280 comparisons and eight basis-only applications pass
independent exact checks. These results include inference and fallback costs
and support the measured fixed-kinematic domain. The validation comparisons
with the seed and row models remain recorded, and their added costs keep
those combinations out of the selected route~\\cite{{KiraEarlyEquationData}}.
""".replace("¤","$")
 if start in t:
  x=t.index(start);y=t.index(end,x)+len(end);t=t[:x]+start+"\n"+conclusion+end+t[y:]
 else:t=t.replace(r"\clearpage"+"\n"+r"\renewcommand{\refname}{Citations}",start+"\n"+conclusion+end+"\n\n"+r"\clearpage"+"\n"+r"\renewcommand{\refname}{Citations}")
 path.write_text(t)
 url="https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"+args.data_commit+"/ML_model_equation_selection/early_generation"
 bib=f"""@misc{{KiraEarlyEquationData,
 author = {{Saraswat, Rushil}},
 title = {{Learned equation selection before native Kira identity construction}},
 year = {{2026}},
 howpublished = {{\\href{{{url}}}{{Frozen models, native integration, complete timings and independent exact checks}}}},
 note = {{GitHub repository, commit \\texttt{{{args.data_commit[:12]}}}}}
}}"""
 block(report/"references.bib","% early-equation-data-begin","% early-equation-data-end",bib)
 guard();print(json.dumps(dict(report_updated=True,data_commit=args.data_commit,abstract_unchanged=True)))
if __name__=="__main__":main()
