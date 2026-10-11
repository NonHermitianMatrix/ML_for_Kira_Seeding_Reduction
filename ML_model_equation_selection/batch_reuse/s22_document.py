"""Write report and READMEs from audited complete calculation results."""
import argparse,re
from s00_common import *
def read(n):return json.loads((HERE/n).read_text())
def ratio(x):return f'{x["ratio"]:.3f}'
def interval(x):return r"\(["+f'{x["interval"][0]:.3f},{x["interval"][1]:.3f}'+r"]\)"
def block(path,start,end,new):
 text=path.read_text()
 text=text.split(start)[0]+new+text.split(end,1)[1] if start in text else text+"\n\n"+new+"\n"
 path.write_text(text)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");args=ap.parse_args()
 s=read("model_test/summary.json");p=read("model_test/pack_summary.json");n=read("model_test/native_summary.json");integration=read("model_test/integration/summary.json")
 assert all(x["all_exact"] for x in [s,p,n]) and integration["all_passed"]
 policy=read("trained_model/deployment.json");np=read("trained_model/native_deployment.json");cm=read("training/native_check.json")
 nodes=sum(map(len,read("trained_model/"+policy["model"])["trees"]))
 rss=max(x["peak_kira_tree_rss_bytes"] for x in [s,p,n])/1024**2;scratch=max(x["peak_kira_scratch_bytes"] for x in [s,p,n])/1024**2
 checks=sum(x["independent_loop_coefficient_checks"] for x in [s,p,n])+integration["independent_coefficient_checks"]
 tokens={"VALID_SINGLE":f'{policy["model_vs_control"]:.3f}',"VALID_PACK":f'{policy["packed_model_vs_control"]:.3f}',"NODES":str(nodes),"INFERENCE_RATIO":f'{cm["timings"][policy["model"]]["ratio"]:.3f}',"REGRET":f'{s["model_cost_regret"]["mean"]:.3f}',"LOOP_CHECKS":f'{checks:,}',"RAW_CHECKS":f'{n["independent_raw_coefficient_checks"]:,}',"RSS":f"{rss:.2f}","SCRATCH":f"{scratch:.2f}"}
 for tag,x in [
 ("SINGLE",s["comparisons"]["model_vs_previous"]["complete_seconds"]),("SINGLE_CTRL",s["comparisons"]["model_vs_extreme"]["complete_seconds"]),
 ("PACK",p["comparisons"]["model_packed_vs_model_separate"]["complete_seconds"]),("PACK_CTRL",p["comparisons"]["model_packed_vs_"+policy["control"]+"_packed"]["complete_seconds"]),
 ("NATIVE",n["comparisons"]["native_vs_previous"]["complete_seconds"]),("NATIVE_CTRL",n["comparisons"]["native_vs_control"]["complete_seconds"]),("NATIVE_PY",n["comparisons"]["native_vs_python"]["complete_seconds"])]:
  tokens[tag]=ratio(x);tokens[tag+"_CI"]=interval(x)
 tokens["DEPLOYMENT"]={
 "native":"The frozen deployment uses compiled learned inference for combined requests and retains the validated simple rule for a single profile.",
 "python":"Complete-time validation retains the Python learned backend for combined requests and the simple rule for a single profile. The compiled backend remains available with its measured comparison.",
 "control":"The last complete-time validation retains the simple control for deployment. Both learned backends remain available with their measured comparisons."}[np["backend"]]
 text=(HERE/"report_template.tex.in").read_text()
 for k,v in tokens.items():text=text.replace("@"+k+"@",v)
 assert not re.search(r"@[A-Z_]+@",text)
 (ROOT/"report/batch_reuse.tex").write_text(text)
 f=ROOT/"report/equation_selection.tex";text=f.read_text()
 if r"\input{batch_reuse}" not in text:f.write_text(text+"\n"+r"\input{batch_reuse}"+"\n")
 f=ROOT/"report/Makefile";text=f.read_text()
 if "batch_reuse.tex" not in text:f.write_text(text.replace("higher_loop_acceleration.tex references.bib","higher_loop_acceleration.tex batch_reuse.tex references.bib"))
 selected=n["comparisons"][np["backend"]+"_vs_previous"]["complete_seconds"]
 conclusion=r"""% BEGIN BATCH REUSE CONCLUSION
The next extension learns shared equation choices for entire target batches
and reduces repeated exact checks in the common variable \(z\). Its
four-tree cost model trains on 420 batches and 6,300 candidate orderings.
Combining independent profiles in one Kira call preserves separate master
bases and reduces repeated startup work. On the final twelve reserved
profiles, the selected combined route has complete-time ratio """+ratio(selected)+r"""
to the preceding separate workflow, with descriptive interval
"""+interval(selected)+r""". All 460 reserved applications and the additional
integration checks pass exact comparisons; the integration tests also
verify the full-system fallback. Compiled and Python inference produce
identical equation systems. The comparisons separate model decisions,
shared exact arithmetic and shared Kira calls, and apply to the stated
restricted vacuum family~\cite{KiraBatchReuseData}.
% END BATCH REUSE CONCLUSION"""
 f=ROOT/"report/report.tex";text=f.read_text()
 if "% BEGIN BATCH REUSE CONCLUSION" in text:text=text.split("% BEGIN BATCH REUSE CONCLUSION")[0]+conclusion+text.split("% END BATCH REUSE CONCLUSION",1)[1]
 else:text=text.replace(r"\renewcommand{\refname}{Citations}",conclusion+"\n\n"+r"\clearpage"+"\n"+r"\renewcommand{\refname}{Citations}")
 text=text.replace("\n\\clearpage\n"+conclusion,"\n"+conclusion);f.write_text(text)
 abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 f=ROOT/"report/references.bib";text=f.read_text()
 if "@article{Geurts2006ExtraTrees" not in text:text+=r"""
@article{Geurts2006ExtraTrees,
 author = {Geurts, Pierre and Ernst, Damien and Wehenkel, Louis},
 title = {Extremely randomized trees},
 journal = {Machine Learning},
 volume = {63},
 pages = {3--42},
 year = {2006},
 doi = {10.1007/s10994-006-6226-1}
}
"""
 commit=args.data_commit or "main"
 entry=r"""% batch-reuse-data-begin
@misc{KiraBatchReuseData,
 author = {Saraswat, Rushil},
 title = {Learned batch equation reuse with shared exact checks and Kira calls},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"""+commit+r"""/ML_model_equation_selection/batch_reuse}{Models, complete timings, exact checks and integration}},
 note = {"""+("Frozen data commit "+r"\texttt{"+commit[:12]+"}" if args.data_commit else "Development snapshot")+r"""}
}
% batch-reuse-data-end"""
 text=text.split("% batch-reuse-data-begin")[0]+entry+text.split("% batch-reuse-data-end",1)[1] if "% batch-reuse-data-begin" in text else text+"\n"+entry+"\n";f.write_text(text)
 scripts="\n".join("- "+f.name+": "+(f.read_text().split('"""',2)[1] if f.suffix==".py" and '"""' in f.read_text() else "Bounded scheduler wrapper.") for f in sorted(HERE.glob("s[0-9][0-9]_*")))
 readme=f"""# Learned batch equation reuse

This extension reduces supplied Euler and partial-fraction systems of the restricted coupled vacuum family. It supports two to four distinct massive denominators, total massive power at most fourteen, unit massless powers and any positive loop order (at most 32 loop orders in one request). Tests cover loops one through twelve and separate exact applications at 16, 24 and 32. General native high-loop IBP generation remains outside this domain.

The model predicts a weighted equation count for each fixed mass ordering. Its choice supplies a terminating dependency closure, including the actual Euler seeds. Kira performs exact elimination. A polynomial reference checks coefficients before exact substitution to each loop order. Grouped requests retain distinct master bases for their mass profiles.

Training uses 420 batches and 6,300 candidate orderings. Validation selects {policy["model"]}, with {nodes} nodes. Scores predict log cost and are not confidence probabilities. Original JSON trees, lossless compact weights, generated C inference and shared libraries remain in trained_model/. Compiled and Python scores match for 12,600 checked candidates.

## Deployment and results

Single-profile default: {policy["mode"]}. Final grouped default: {np["backend"]} backend with {np["model"]}; control: {np["control"]}. Validation requires a 2% complete-time improvement for learned deployment.

There are 300 first reserved calculations, 80 grouped comparisons and 80 fresh backend comparisons. All pass exact checks without fallback. Seven further normal integration applications pass; one injected check failure verifies the full-system fallback. The selected final complete-time ratio to the preceding separate workflow is {ratio(selected)}, with descriptive interval {selected["interval"]}. The compiled learned ratio to the updated grouped control is {tokens["NATIVE_CTRL"]}. Mean weighted-cost regret against enumerated mass orders is {tokens["REGRET"]}.

Savings include separate contributions from equation sharing, exact verification in z, integer polynomial arithmetic and sharing Kira calls. A direct analytic solution exists for this restricted family. These tests do not establish a globally fastest reduction.

## Usage on Hoffman

Use bounded scheduler jobs. A single-profile request has the format documented in ../higher_loops/README.md:

~~~bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s09_application.py --input request.json --output ML_model_equation_selection/batch_reuse/model_test/application.json
~~~

For grouped use, put single-profile requests in an object with a requests list. Limits are eight profiles, 512 targets and 12,000 selected equations.

~~~bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s17_application.py --input group.json --output ML_model_equation_selection/batch_reuse/model_test/group_application.json
~~~

Explicit backends are native, python and control. The previous backend runs the preceding separate workflow. Rebuild platform-specific libraries with s16_native.py when required. The earlier s11_pack.py interface preserves the first packed deployment.

Result JSON files reference SHA-256-checked compressed objects containing source choices, raw Kira exports, logs and exact rational coefficients as numerator/denominator pairs. Symbolic coefficients use z; expanded coefficients use d and are grouped by loop order and profile. Failed combined systems retry profiles separately; failed selected systems retry the full supplied pool.

## Reproduction

Run s01_train.py, then s04_run.sh validation. Use s13_run.sh for validation selection, packed validation, freezing and reserved tests. Use s19_run.sh for integration checks, identical compiled inference and fresh backend validation/testing. Finish with the audit, plot, document and release-check scripts. Completed experiment records are preserved. development_initial/ contains the original pilot code.

{scripts}

## Resource accounting

Only one experiment job runs at a time. Each Kira attempt has a 90-second limit, a 1,800 MiB address-space limit, a 1,500 MiB sampled process-tree RSS guard and a 64 MiB scratch guard. The job has separate memory limits. resource_plan.json bounds combined local and cluster storage below 10,000,000,000 bytes. Scientific data stay on Hoffman and GitHub; only report material is copied locally.
"""
 (HERE/"README.md").write_text(readme)
 for folder,body in [
 ("training","420 batches and 6,300 candidate mass orderings. examples.json.gz records targets, candidate features and exact weighted dependency costs. summary.json records training; compact_check.json and native_check.json check unchanged inference."),
 ("trained_model","Original trees, compact weights and compiled inference. Deployment files record validation choices; freeze files pin evaluated code, weights and reserved inputs before testing."),
 ("validation","Separate mass profiles select model size and deployment: 324 single-profile, 48 grouped and 36 fresh backend comparisons. The initial pilot retains earlier representation overhead."),
 ("model_test","Frozen independent tests: 300 single-profile, 80 grouped and 80 fresh backend comparisons. Summary files contain full times, intervals and audits. integration/ covers larger loop orders and forced fallback; plots/ contains publication figures.")]:
  (HERE/folder/"README.md").write_text("# "+folder.replace("_"," ").capitalize()+"\n\n"+body+"\n")
 new=f"""<!-- batch-reuse-begin -->
## Learned equation reuse across target batches

The latest restricted vacuum-family interface is [batch_reuse](ML_model_equation_selection/batch_reuse/README.md). It trains a batch equation-cost model, shares exact coefficient checks across loop orders and combines independent systems in one Kira call. All 460 reserved applications pass exact checks. The selected combined route has complete-time ratio {ratio(selected)} to the preceding separate workflow. Matched simple-rule and inference-backend comparisons remain recorded. General high-loop native IBP generation is outside this scope.
<!-- batch-reuse-end -->"""
 block(ROOT/"README.md","<!-- batch-reuse-begin -->","<!-- batch-reuse-end -->",new)
 for f in [ROOT/"ML_model_equation_selection/README.md",ROOT/"Kira_comparison/README.md"]:
  link="../ML_model_equation_selection/batch_reuse/README.md" if f.parent.name=="Kira_comparison" else "batch_reuse/README.md"
  block(f,"<!-- batch-reuse-begin -->","<!-- batch-reuse-end -->",new.replace("ML_model_equation_selection/batch_reuse/README.md",link))
 write(HERE/"model_test/document_values.json",dict(tokens=tokens,selected_ratio=selected))
 print("Documentation updated; abstract preserved")
if __name__=="__main__":main()
