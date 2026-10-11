"""Update scientific text and READMEs from checked measurements."""
import argparse,re
from s00_contract import *
def block(path,key,text):
 old=path.read_text();start="<!-- "+key+" -->";end="<!-- "+key+"-end -->";new=start+"\n"+text+"\n"+end
 if start in old:old=re.sub(re.escape(start)+r".*?"+re.escape(end),lambda m:new,old,flags=re.S)
 else:old+="\n"+new+"\n"
 path.write_text(old)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");a=ap.parse_args()
 if a.data_commit:assert re.fullmatch("[0-9a-f]{40}",a.data_commit)
 s=json.loads((HERE/"model_test/summary.json").read_text());mode=s["selected"];comp=s["comparisons"]
 labels={"baseline":"the preceding Kira route","model":"pre-reduction followed by Kira","direct_model":"the learned direct route","direct_extreme":"the simple direct route","direct_analytic":"the independently checked analytic route"}
 chosen=comp[mode+"_vs_baseline"]
 def f(x):return f"{x:.3f}"
 def interval(c):return r"\(["+f(c["interval95"][0])+","+f(c["interval95"][1])+r"]\)"
 calc=chosen["complete_seconds"];external=chosen["external_seconds"]
 ls=comp["direct_model_vs_direct_extreme"]["complete_seconds"];la=comp["direct_model_vs_direct_analytic"]["complete_seconds"]
 finding="The comparison does not establish a further complete-time advantage from learned ordering over both direct controls."
 if ls["interval95"][1]<1 and la["interval95"][1]<1:finding="Within these reserved batches, learned ordering also reduces complete time relative to both direct controls."
 values={"SELECTED":labels[mode],"COEFFICIENTS":str(s["coefficient_audit"]["expanded_coefficient_positions"]),"RAW":str(s["coefficient_audit"]["raw_kira_coefficients_compared"]),"RATIO":f(calc["ratio"]),"CI":interval(calc),"EXTERNAL":f(external["ratio"]),"ECI":interval(external),"LEARNED_SIMPLE":f(ls["ratio"]),"LSCI":interval(ls),"LEARNED_ANALYTIC":f(la["ratio"]),"LACI":interval(la),"MODEL_FINDING":finding,"CONTRACT":f(comp["model_vs_baseline"]["complete_seconds"]["ratio"])}
 text=(HERE/"report_template.tex.in").read_text()
 for k,v in values.items():text=text.replace("@@"+k+"@@",v)
 assert "@@" not in text
 (ROOT/"report/pre_reduction.tex").write_text(text)
 p=ROOT/"report/equation_selection.tex";old=p.read_text()
 if r"\input{pre_reduction}" not in old:p.write_text(old+"\n"+r"\input{pre_reduction}"+"\n")
 p=ROOT/"report/Makefile";old=p.read_text()
 if "pre_reduction.tex" not in old:p.write_text(old.replace("batch_reuse.tex references.bib","batch_reuse.tex pre_reduction.tex references.bib"))
 commit=a.data_commit or "pending"
 bib=r"""% pre-reduction-data-begin
@misc{KiraPreReductionData,
 author = {Saraswat, Rushil},
 title = {Exact pre-reduction with learned ordering and a checked Kira fallback},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/COMMIT/ML_model_equation_selection/pre_reduction}{Frozen comparisons, exact outputs and implementation}},
 note = {Data commit \texttt{SHORT}}
}
% pre-reduction-data-end
""".replace("COMMIT",commit).replace("SHORT",commit[:12])
 p=ROOT/"report/references.bib";old=p.read_text()
 if "% pre-reduction-data-begin" in old:old=re.sub(r"% pre-reduction-data-begin.*?% pre-reduction-data-end\n",lambda m:bib,old,flags=re.S)
 else:old+="\n"+bib
 p.write_text(old)
 conclusion=(r"% BEGIN PRE REDUCTION CONCLUSION"+"\n"+
 "The final extension evaluates selected triangular identities with exact\n"+
 "integer polynomial arithmetic and checks every master coefficient through\n"+
 "an independent Taylor construction. Validation selects "+labels[mode]+".\n"+
 "On eight fresh three-profile batches, its calculation-time ratio to the\n"+
 "preceding combined workflow is "+f(calc["ratio"])+", with descriptive interval\n"+
 interval(calc)+". The full worker-time ratio is "+f(external["ratio"])+".\n"+
 "All 200 reserved calculations pass exact checks, and an injected failure\n"+
 "recovers through Kira. "+finding+"\n"+
 "The direct saving follows mainly from the exact family-specific recurrence;\n"+
 "the native IBP-generation results retain their earlier scope\n"+
 r"\cite{KiraPreReductionData}."+"\n% END PRE REDUCTION CONCLUSION")
 p=ROOT/"report/report.tex";old=p.read_text()
 if "% BEGIN PRE REDUCTION CONCLUSION" in old:old=re.sub(r"% BEGIN PRE REDUCTION CONCLUSION.*?% END PRE REDUCTION CONCLUSION",lambda m:conclusion,old,flags=re.S)
 else:old=old.replace(r"\clearpage"+"\n"+r"\renewcommand{\refname}",conclusion+"\n\n"+r"\clearpage"+"\n"+r"\renewcommand{\refname}")
 p.write_text(old)
 status=("Validation selects "+labels[mode]+". On 200 reserved applications, its calculation-time ratio to the preceding combined learned Kira route is "+f(calc["ratio"])+
 ", with descriptive interval ["+",".join(f(x) for x in calc["interval95"])+"]. The full-worker ratio is "+f(external["ratio"])+
 ". All exact checks pass with zero reserved fallbacks. The earlier trained four-tree model remains available with unchanged weights; learned/direct versus simple/direct has calculation ratio "+f(ls["ratio"])+
 ". "+finding+" This is a checked shortcut for the restricted coupled vacuum family. Native IBP generation keeps its earlier supported domains.")
 scripts="\n".join("- "+p.name+": "+p.read_text().splitlines()[0].strip('"') for p in sorted(HERE.glob("*.py")))
 (HERE/"README.md").write_text("""# Exact pre-reduction and checked direct execution

The earlier learned equation policy supplies a terminating dependency graph for the restricted coupled scalar vacuum family. Exact polynomial substitutions solve this graph, and an independent Taylor construction checks every coefficient. Kira remains the fallback. The model is reused without retraining.

"""+status+"""

The request schema matches batch_reuse/s17_application.py: requests contains objects with a unique id, family=coupled_vacuum_unit_massless, 2--4 distinct positive integer mass_ratios, unique targets with nonnegative powers and total power 1--14, positive loops and mass_scale_squared=1. Limits are eight profiles, 512 total targets, 128 targets per profile, 32 requested loop values and 12,000 selected intermediate equations. Unit massless powers are required. These profiles share topology; they are not arbitrary graph families.

Run inside a bounded scheduler allocation, without Python -O:

    .tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s01_application.py --input request.json --output ML_model_equation_selection/pre_reduction/model_test/application.json

The default --mode deployed uses the frozen validation choice. Other modes are baseline (preceding learned Kira route), model (pre-reduce, then Kira), direct_model (compiled unchanged forest and exact recurrence), direct_extreme (simple recurrence), and direct_analytic (Taylor construction checked by the simple recurrence). Retained extreme and analytic modes submit completed relations to Kira and occur only in the development pilot. Scores estimate log weighted equation cost, without a confidence-calibration claim.

Each direct result must equal the independent exact formula in Q[z] before substitution z=L(d-2). A failed check retries Kira with all costs included. Invalid requests are rejected. Returning a completed direct reduction avoids invoking Kira for this supported case. The new direct path does not accelerate native IBP generation.

The earlier model and training evidence remain in ../batch_reuse/. Validation uses six groups, mass ratios 503--796 and 90 applications. The frozen test uses eight further groups, masses 809--1296 and 200 applications. The ranges are disjoint from prior model training. Five methods have five repetitions per test group. Validation fixes the default before the reserved test. The analytic control includes an independent recurrence check.

Calculation time includes input reading, loading, inference, preparation, exact algebra, checks, loop substitution and fallback. external_seconds adds interpreter startup and evidence saving. Ratios use geometric means of batch median ratios and descriptive bootstrap intervals over eight groups.

All exact source choices, coefficients and raw Kira outputs reside in objects/, addressed by SHA256 of decompressed JSON. Identical payloads share one file. Direct outputs contain an empty raw Kira export because no Kira process ran. Every record hash is verified. The independent audit checks each distinct expanded batch against the older loop-specific oracle and reads every raw Kira coefficient with the earlier reader.

The initial eight pilot runs and their matching source remain in pilot/ and development_pilot/. The storage guard interrupted the first reserved run after two complete applications; the completed coefficient record from the interrupted serialization remains in model_test/interrupted/. Its missing worker time excludes it from timing. The remaining frozen trials resumed with unchanged code, inputs and policy after increasing the reserved storage allowance within 10 GB.

Script order:
"""+scripts+"""

s03_run.sh preserves the pilot launch. s05_run.sh runs arithmetic checks, validation, freeze, testing, fallback checks and the independent audit. The saved s11_resume.sh continues an interrupted test without changing the freeze. s10_report.sh runs analysis, plots, documentation, release checks and the PDF build after testing. Preserve completed experiments; use a new directory for further policy selection.

The resource plan bounds the complete project below 10 GB. One experiment job runs at a time with a 2,800 MiB address-space limit. Kira retains its 90-second, 1.5 GiB sampled tree-RSS and 64 MiB scratch limits. Generated data stay on Hoffman and GitHub. Report files also synchronize locally.
""")
 for folder,description in [("validation","Validation inputs, timing records and arithmetic checks. Only this stage selects the default."),("model_test","Frozen reserved results, exact audits, integration checks and plots. These results never tune the default."),("pilot","Eight development measurements from the original pre-reduction implementation, with matching source in development_pilot/."),("development_pilot","Original source for the eight pilot measurements. The direct shortcut was added before final validation."),("objects","Content-addressed exact evidence; each filename gives the SHA256 of decompressed canonical JSON.")]:
  (HERE/folder).mkdir(exist_ok=True);(HERE/folder/"README.md").write_text(description+"\n")
 for path,link in [(ROOT/"README.md","ML_model_equation_selection/pre_reduction/README.md"),(ROOT/"ML_model_equation_selection/README.md","pre_reduction/README.md"),(ROOT/"Kira_comparison/README.md","../ML_model_equation_selection/pre_reduction/README.md")]:
  block(path,"pre-reduction-current",status+"\n\nSee [exact pre-reduction]("+link+").")
 base.write(HERE/"model_test/document_values.json",values)
 print(status,flush=True)
if __name__=="__main__":main()
