"""Update the report and READMEs from frozen arithmetic-reuse measurements."""
import argparse,re
from s00_arithmetic import *
def block(path,key,text):
 old=path.read_text();start="<!-- "+key+" -->";end="<!-- "+key+"-end -->";new=start+"\n"+text+"\n"+end
 if start in old:old=re.sub(re.escape(start)+r".*?"+re.escape(end),lambda m:new,old,flags=re.S)
 else:old+="\n"+new+"\n"
 path.write_text(old)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");a=ap.parse_args()
 if a.data_commit:assert re.fullmatch("[0-9a-f]{40}",a.data_commit)
 s=json.loads((HERE/"model_test/summary.json").read_text());assert s["all_exact"]
 comp=s["comparisons"];chosen=comp["both"];streams=s["stream_comparisons"]
 def f(x):return f"{x:.3f}"
 def interval(c):return r"\(["+f(c["interval95"][0])+","+f(c["interval95"][1])+r"]\)"
 values={"SELECTED":{"both":"both arithmetic changes","transforms":"shared transformations","taylor":"shared Taylor terms","baseline":"the preceding arithmetic"}[s["selected"]],
 "BOTH":f(chosen["complete_seconds"]["ratio"]),"BCI":interval(chosen["complete_seconds"]),
 "EXTERNAL":f(chosen["external_seconds"]["ratio"]),"ECI":interval(chosen["external_seconds"]),
 "TRANSFORM":f(comp["transforms"]["complete_seconds"]["ratio"]),"TAYLOR":f(comp["taylor"]["complete_seconds"]["ratio"]),
 "EXPANSION":f(chosen["substitution_seconds"]["ratio"]),"ORACLE":f(chosen["oracle_seconds"]["ratio"]),
 "WORKER":f(streams["worker_reuse_only"]["ratio"]),"STREAM":f(streams["combined_vs_previous"]["ratio"]),
 "POSITIONS":str(s["audit"]["expanded_coefficient_positions"])}
 text=(HERE/"report_template.tex.in").read_text()
 for k,v in values.items():text=text.replace("@@"+k+"@@",v)
 assert "@@" not in text
 (ROOT/"report/polynomial_reuse.tex").write_text(text)
 p=ROOT/"report/equation_selection.tex";old=p.read_text()
 if r"\input{polynomial_reuse}" not in old:p.write_text(old+"\n"+r"\input{polynomial_reuse}"+"\n")
 p=ROOT/"report/Makefile";old=p.read_text()
 if "polynomial_reuse.tex" not in old:
  assert "pre_reduction.tex references.bib" in old
  p.write_text(old.replace("pre_reduction.tex references.bib","pre_reduction.tex polynomial_reuse.tex references.bib"))
 # Preserve the pinned citation on later regeneration without a commit argument.
 p=ROOT/"report/references.bib";old=p.read_text()
 match=re.search(r"% polynomial-reuse-data-begin.*?/tree/([0-9a-f]{40})/",old,re.S)
 commit=a.data_commit or (match.group(1) if match else "pending")
 bib=r"""% polynomial-reuse-data-begin
@misc{KiraPolynomialReuseData,
 author = {Saraswat, Rushil},
 title = {Exact polynomial reuse and persistent reduction workers},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/COMMIT/ML_model_equation_selection/polynomial_reuse}{Frozen arithmetic comparisons, stream measurements and exact checks}},
 note = {Data commit \texttt{SHORT}}
}
% polynomial-reuse-data-end
""".replace("COMMIT",commit).replace("SHORT",commit[:12])
 if "% polynomial-reuse-data-begin" in old:old=re.sub(r"% polynomial-reuse-data-begin.*?% polynomial-reuse-data-end\n",lambda m:bib,old,flags=re.S)
 else:old+="\n"+bib
 p.write_text(old)
 conclusion=r"""% BEGIN POLYNOMIAL REUSE CONCLUSION
The final extension shares the exact transformations for \(z=L(d-2)\)
and the Taylor terms in the independent check. On eight new reserved
batches, both changes together have calculation-time ratio CALC to
the preceding direct route and full worker-time ratio EXTERNAL.
Keeping one process for several batches gives combined full-time ratio
STREAM across the three specified request streams. These streams share
inputs, so this last ratio describes those sequences.
All 352 reserved applications pass exact checks, including an independent
audit of POSITIONS expanded coefficient positions. The request-interface
checks also pass, including recovery through Kira after an injected failure.
The changes reuse exact mathematical work and process startup; the
previous model and ordering choice remain fixed. The supported domain
remains the restricted coupled vacuum family, with native IBP-generation
results retaining their earlier scope \cite{KiraPolynomialReuseData}.
% END POLYNOMIAL REUSE CONCLUSION""".replace("CALC",values["BOTH"]).replace("EXTERNAL",values["EXTERNAL"]).replace("STREAM",values["STREAM"]).replace("POSITIONS",values["POSITIONS"])
 p=ROOT/"report/report.tex";old=p.read_text()
 old=old.replace("The final extension evaluates selected triangular identities","The direct-reduction extension evaluates selected triangular identities")
 if "% BEGIN POLYNOMIAL REUSE CONCLUSION" in old:old=re.sub(r"% BEGIN POLYNOMIAL REUSE CONCLUSION.*?% END POLYNOMIAL REUSE CONCLUSION",lambda m:conclusion,old,flags=re.S)
 else:
  marker=r"\clearpage"+"\n"+r"\renewcommand{\refname}"
  assert marker in old
  old=old.replace(marker,conclusion+"\n\n"+marker)
 p.write_text(old)
 status=("The current restricted vacuum-family interface shares exact loop-order transformations and Taylor factors, with an optional persistent worker. Validation selects both arithmetic changes and preserves the simple extreme ordering. "
 +"Across eight reserved batches, calculation-time ratio to the preceding direct arithmetic is "+values["BOTH"]+", and full-worker ratio is "+values["EXTERNAL"]+". "
 +"Arithmetic plus persistent execution has full-time ratio "+values["STREAM"]+" across three specified overlapping streams. All 352 reserved applications pass exact checks; "+values["POSITIONS"]+" expanded coefficient positions also match the older loop-dependent formula. "
 +"These gains come from exact reuse and process startup. The unchanged learned model remains optional. General native high-loop IBP generation retains its earlier scope.")
 scripts="\n".join("- "+p.name+": "+p.read_text().splitlines()[0].strip('"') for p in sorted(HERE.glob("*.py")))
 (HERE/"README.md").write_text("""# Exact polynomial reuse and persistent workers

"""+status+"""

This extension retains the exact selected recurrence and the independent Taylor check. It builds integer matrices for z=L(d-2) once per loop order, converts each polynomial to a common denominator once, and reuses Taylor factors within each physical mass profile. The preceding frozen pre_reduction, batch_reuse and native policies remain unchanged. No model was trained in this extension.

The input schema follows ../pre_reduction/: a requests list with unique id values, family=coupled_vacuum_unit_massless, 2--4 distinct positive integer mass_ratios, mass_scale_squared=1, nonnegative target powers with total 1--14, and positive integer loop orders. It requires unit massless powers. Limits remain eight profiles, 512 total targets, 128 targets per profile, 32 loop values and 12,000 intermediate equations. This is one restricted vacuum topology with mass profiles.

Use a bounded Hoffman scheduler allocation, without Python -O:

    .tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s02_application.py --input request.json --output ML_model_equation_selection/polynomial_reuse/model_test/application.json

--variant deployed uses the frozen validation result. The alternatives baseline, transforms, taylor and both isolate each arithmetic change. --policy extreme is the preceding validation-selected default; --policy model uses the unchanged compiled four-tree model from ../batch_reuse/. A failed exact comparison invokes the preserved Kira route and includes the failed attempt in its calculation time.

For several batches, start the same command with --stream and send one JSON object per line, with input and output paths. Paths resolve from the project working directory; absolute project paths also work. The input must stay within the project and the output within this module. Each response reports success or the request error. The worker keeps at most 128 transforms and one unchanged model, while each new mass profile gets fresh mass-dependent Taylor terms. It accepts at most 64 commands by default; --max-requests can lower that limit. Each command and input file is limited to 1 MiB. An invalid request reports an error and permits later requests; exceeding the line or command cap stops the process.

Validation uses four new batches, masses 2003--3000, four variants and three repetitions (48 applications). It selects both arithmetic changes before the reserved test. The test uses eight new batches, masses 4001--6006, four variants and five repetitions (160 applications). Each batch contains profiles with two, three and four massive denominators and loops 1--12. The total massive power is at most 14, and requested targets per profile are 16, 48 or 96, limited by the available distinct vectors.

The stream study runs four configurations on sequences of four, four and eight batches, with three repetitions: 36 process-sequence runs and 192 batch applications. The eight-batch sequence reuses the two four-batch inputs. Its descriptive aggregate has no statistical interval. The frozen test and stream comparisons use the same default simple ordering. Model retention is checked separately in the integration tests.

complete_seconds includes request reading, model loading if enabled, selection, exact recurrence, independent verification, loop expansion and fallback. external_seconds also includes Python startup and saving results. The matched baseline and all arithmetic variants use the same content-addressed output writer. Ratios use geometric means of within-batch median ratios; descriptive cold-test intervals resample eight groups. These matched ratios must not be multiplied into earlier full-worker results with a different writer or input set.

objects/ contains gzip JSON blocks addressed by the SHA256 of canonical decompressed JSON. Coefficient blocks and source evidence are separate so variants share identical outputs. Per-application records refer to these hashes. The independent audit verifies 352 applications, identical method outputs and every distinct expanded coefficient against the older loop-dependent formula. The 2,126 arithmetic checks cover exact substitution, Taylor construction and cache eviction. Integration tests cover changed masses and loop orders, invalid input, request limits, retained model evaluation and a forced Kira fallback.

Script order:
"""+scripts+"""

s05_run.sh is the original validation, freeze and test scheduler wrapper. Preserve its completed records; new policy development requires fresh inputs and a separate module. s11_finish.sh documents and checks the frozen results and builds the PDF; --data-commit pins their immutable GitHub citation. s06_audit.py, s07_analyze.py and s08_plot.py independently reconstruct the audit, summaries and figures from preserved results.

resource_plan.json starts from a fresh full-project allocation audit and reserves retained evidence, Git copies, pack/index space, PDF output, local report growth and drift below the combined 10 GB ceiling. Experiments use one CPU and a 2,800 MiB address-space limit. Kira fallback retains its 90-second, 1.5 GiB sampled tree-RSS and 64 MiB scratch limits. Generated scientific records stay on Hoffman and GitHub; only the report also synchronizes locally.
""")
 descriptions={
 "validation":"Validation inputs, 48 measurements and 2,126 exact arithmetic checks. Only validation selected the arithmetic default.",
 "model_test":"Frozen test inputs, 160 cold applications, 192 stream applications, exact audits, integration tests, summary and plots. These outcomes never select or tune the default.",
 "model_test/inputs":"Eight frozen batches, each with three new mass profiles. The mass range is disjoint from validation and previous studies.",
 "model_test/results":"160 separate-process measurements: eight batches, four variants and five repetitions. complete_seconds and external_seconds separate calculation work from full-worker cost.",
 "model_test/streams":"36 bounded process-sequence measurements. Four modes, three sequences and three repetitions contain 192 batch applications. The sequences overlap; the aggregate ratios are descriptive.",
 "model_test/stream_results":"Individual batch outputs referenced by the 36 stream records. All coefficient hashes agree with their frozen separate-process baseline.",
 "model_test/integration":"Interface checks for changed physics inputs under one identifier, invalid requests, process reuse, request cap and forced Kira fallback. summary.json records their results.",
 "model_test/plots":"Scientific plots generated from frozen measurements by s08_plot.py. Identical copies appear in report/figures/.",
 "objects":"Exact coefficient and evidence blocks. The filename gives SHA256 of decompressed canonical JSON. Every referenced hash is checked."}
 for folder,description in descriptions.items():
  p=HERE/folder;p.mkdir(exist_ok=True);(p/"README.md").write_text(description+"\n")
 for path,link in [(ROOT/"README.md","ML_model_equation_selection/polynomial_reuse/README.md"),(ROOT/"ML_model_equation_selection/README.md","polynomial_reuse/README.md"),(ROOT/"Kira_comparison/README.md","../ML_model_equation_selection/polynomial_reuse/README.md")]:
  old=path.read_text().replace("The latest restricted vacuum-family interface is [batch_reuse]","The earlier batch interface is [batch_reuse]")
  path.write_text(old)
  block(path,"polynomial-reuse-current",status+"\n\nSee [exact polynomial reuse]("+link+").")
 block(ROOT/"report/README.md","polynomial-reuse-current","polynomial_reuse.tex explains shared exact loop-order transformations, reused Taylor terms and persistent reduction workers. It records 48 validation applications, 352 reserved applications and all independent checks. Figures polynomial_reuse_times.pdf and polynomial_reuse_streams.pdf separate arithmetic and process reuse. The data citation is pinned when the release is published. The supplied abstract and previous results remain preserved.")
 base.write(HERE/"model_test/document_values.json",values)
 print(status,flush=True)
if __name__=="__main__":main()
