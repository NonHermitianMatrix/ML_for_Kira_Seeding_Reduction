"""Document both frozen comparisons, the new cost model and final deployment."""
import argparse,re
from s00_backend import *
def block(path,key,text):
 old=path.read_text();a="<!-- "+key+" -->";b="<!-- "+key+"-end -->";new=a+"\n"+text+"\n"+b
 if a in old:old=re.sub(re.escape(a)+".*?"+re.escape(b),lambda m:new,old,flags=re.S)
 else:old+="\n"+new+"\n"
 path.write_text(old)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");args=ap.parse_args()
 if args.data_commit:assert re.fullmatch("[0-9a-f]{40}",args.data_commit)
 first=read(HERE/"model_test/summary.json");s=read(HERE/"reader_final_test/summary.json");assert first["all_exact"] and s["all_exact"]
 dep=s["deployment"];arm=s["deployed_arm"]
 unit=dict(ratio=1.,interval95=[1.,1.]);selected=s["comparisons"].get(arm,{k:unit for k in ["complete_seconds","external_seconds","roundtrip_seconds"]})
 def f(x):return f"{x:.3f}"
 def ci(x):return r"\(["+f(x["interval95"][0])+","+f(x["interval95"][1])+r"]\)"
 labels={"baseline":"the preceding arithmetic","integer":"integer polynomials with decimal output","native_json":"compiled expansion with decimal output","native_binary":"compiled expansion and binary output with a fixed recurrence rule","learned":"compiled expansion and binary output with the learned strategy"}
 label=labels[dep["mode"]]
 model=s["model_vs_best_fixed"]["roundtrip_seconds"]
 if model["interval95"][1]<1:finding="The reserved comparison supports a further time reduction from the learned choices relative to this fixed rule."
 elif model["interval95"][0]>1:finding="The learned choices add time relative to this fixed rule in the reserved comparison."
 else:finding="This interval includes one, so the reserved comparison does not establish a further time reduction from learned choices."
 if dep["mode"]!="learned":finding+=" The deployed default uses the fixed validation choice."
 else:finding+=" The deployed default retains the learned choice fixed during validation."
 values={"FEATURES":str(read(HERE/"trained_model/cost_tree.json")["feature_count"]),"NODES":str(s["training"]["node_count"]),
 "SELECTED":label,"COLD":str(s["audit"]["cold_applications"]),"CALC":f(selected["complete_seconds"]["ratio"]),"EXTERNAL":f(selected["external_seconds"]["ratio"]),"ECI":ci(selected["external_seconds"]),
 "ROUNDTRIP":f(selected["roundtrip_seconds"]["ratio"]),"RCI":ci(selected["roundtrip_seconds"]),
 "INTEGER":f(s["comparisons"]["integer"]["roundtrip_seconds"]["ratio"]),"NATIVEJSON":f(s["comparisons"]["native_json"]["roundtrip_seconds"]["ratio"]),
 "NATIVEBIN":f(s["comparisons"]["native_binary"]["roundtrip_seconds"]["ratio"]),"MODELBASE":f(s["comparisons"]["learned"]["roundtrip_seconds"]["ratio"]),"MODELFIXED":f(model["ratio"]),"MCI":ci(model),
 "MODEL_FINDING":finding,"STREAM":f(s["stream_ratios"]["deployed"]["external_seconds"]),"STREAMREAD":f(s["stream_ratios"]["deployed"]["roundtrip_seconds"]),
 "TOTAL":str(s["audit"]["applications"]),"ALLTOTAL":str(s["audit"]["applications"]+first["audit"]["applications"]),"POSITIONS":str(s["audit"]["expanded_coefficient_positions"]),
 "READER":f(s["reader_comparison"]["ratio"])}
 t=(HERE/"report_template.tex.in").read_text()
 for k,v in values.items():t=t.replace("@@"+k+"@@",v)
 assert "@@" not in t
 (ROOT/"report/exact_backend.tex").write_text(t)
 p=ROOT/"report/equation_selection.tex";old=p.read_text()
 if r"\input{exact_backend}" not in old:p.write_text(old+"\n"+r"\input{exact_backend}"+"\n")
 p=ROOT/"report/Makefile";old=p.read_text()
 if "exact_backend.tex" not in old:
  assert "polynomial_reuse.tex references.bib" in old
  p.write_text(old.replace("polynomial_reuse.tex references.bib","polynomial_reuse.tex exact_backend.tex references.bib"))
 p=ROOT/"report/references.bib";old=p.read_text()
 match=re.search(r"% exact-backend-data-begin.*?/tree/([0-9a-f]{40})/",old,re.S);commit=args.data_commit or (match.group(1) if match else "pending")
 bib=r"""% exact-backend-data-begin
@misc{KiraExactBackendData,
 author = {Saraswat, Rushil},
 title = {Exact integer expansion, lossless coefficient output and learned batch strategies},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/COMMIT/ML_model_equation_selection/exact_backend}{Frozen implementations, runtime-trained tree, full comparisons and exact checks}},
 note = {Data commit \texttt{SHORT}}
}
% exact-backend-data-end
""".replace("COMMIT",commit).replace("SHORT",commit[:12])
 if "% exact-backend-data-begin" in old:old=re.sub(r"% exact-backend-data-begin.*?% exact-backend-data-end\n",lambda m:bib,old,flags=re.S)
 else:old+="\n"+bib
 if "@misc{GMPIntegerManual," not in old:old+=r"""
@misc{GMPIntegerManual,
 author = {{GNU MP developers}},
 title = {{GNU MP} Manual: Integer Functions},
 howpublished = {\href{https://gmplib.org/manual/Integer-Functions}{Integer arithmetic documentation}},
 note = {The recorded cluster implementation uses GMP 6.0.0}
}
"""
 p.write_text(old)
 conclusion=r"""% BEGIN EXACT BACKEND CONCLUSION
The final extension retains integer polynomial coefficients, compiles exact
loop-order expansion and supplies lossless binary coefficient output.
A 19-node regression tree learns batch strategies from 1,440 complete
warm-worker measurements on 96 training batches. The first frozen test
finds no established complete-time gain from the initial selected
integer route once output reading is included. Compiling the binary
reader then permits a new validation and independent test.
Validation selects SELECTED. Its full process-time ratio to the preceding
arithmetic is EXTERNAL, and its ratio including output reading is ROUNDTRIP,
with descriptive interval RCI. The deployed persistent-worker ratio
including reading is STREAMREAD across three disjoint test streams.
All ALLTOTAL reserved batch calculations across both studies pass exact
checks. MODEL_FINDING
The new tree, fixed-rule controls and earlier results remain preserved,
and the supported domain remains the stated coupled vacuum family
\cite{KiraExactBackendData}.
% END EXACT BACKEND CONCLUSION"""
 for k in ["SELECTED","EXTERNAL","ROUNDTRIP","RCI","STREAMREAD","ALLTOTAL","MODEL_FINDING"]:conclusion=conclusion.replace(k,values[k])
 p=ROOT/"report/report.tex";old=p.read_text().replace("The final extension shares the exact transformations","The polynomial-reuse extension shares the exact transformations")
 if "% BEGIN EXACT BACKEND CONCLUSION" in old:old=re.sub(r"% BEGIN EXACT BACKEND CONCLUSION.*?% END EXACT BACKEND CONCLUSION",lambda m:conclusion,old,flags=re.S)
 else:
  marker=r"\clearpage"+"\n"+r"\renewcommand{\refname}";assert marker in old;old=old.replace(marker,conclusion+"\n\n"+marker)
 p.write_text(old)
 status=("The latest restricted vacuum-family route uses "+label+". Its complete-process time ratio is "+values["EXTERNAL"]+" and its ratio including output decoding is "+values["ROUNDTRIP"]+
 ", with descriptive interval ["+",".join(f(x) for x in selected["roundtrip_seconds"]["interval95"])+"]. The persistent-stream ratio including decoding is "+values["STREAMREAD"]+". "+
 values["ALLTOTAL"]+" reserved applications across the original and compiled-reader comparisons pass exact checks. Learned versus validation-selected fixed-rule time ratio is "+values["MODELFIXED"]+". "+finding+" These results retain the restricted vacuum-family scope; native IBP generation keeps its earlier supported domains.")
 scripts="\n".join("- "+f.name+": "+f.read_text().splitlines()[0].strip('\"/') for f in sorted(HERE.glob("s*")) if f.suffix in [".py",".cpp"])
 (HERE/"README.md").write_text("""# Exact integer arithmetic and learned batch strategies

"""+status+"""

The implementation keeps each exact polynomial as integer coefficients over one positive common denominator. The recurrence and independent Taylor construction use that representation, and GMP 6.0.0 expands z=L(d-2) into every requested loop order. Each output coefficient retains a reduced integer numerator and denominator. A small regression tree selects one of five recurrence rules from measured total cost. Its 49 features include powers, mass differences, loop orders and shared immediate predecessors.

The request schema remains requests=[...], with unique id, family=coupled_vacuum_unit_massless, mass_scale_squared=1, 2--4 distinct positive integer mass_ratios, nonnegative target powers with total 1--14, and positive loop orders. Unit massless powers are required. Limits remain eight profiles, 512 total targets, 128 targets per profile, 32 loop values and 12,000 intermediate equations. These are mass profiles of one restricted topology.

Use the current interface inside a bounded Hoffman scheduler allocation, without Python -O:

    .tools/seed-model/venv/bin/python ML_model_equation_selection/exact_backend/s15_application.py --input request.json --output ML_model_equation_selection/exact_backend/reader_final_test/application.json

The default --mode deployed follows reader_final_deployment.json. Explicit modes baseline, integer, native_json, native_binary and learned support the frozen controls. --policy can select extreme, ascending, descending, mass_gap or first for an explicit comparison. --stream accepts JSON lines with input and output paths and retains the worker for at most 64 commands; --max-requests can lower the cap. Inputs must stay inside the project and outputs inside this module. Each command/input file is capped at 1 MiB. Invalid requests report an error, and later valid commands can continue. The old s03_application.py interface and deployment.json preserve the first frozen comparison.

Every direct calculation compares the recurrence with the independent Taylor construction. A failed check or failed native operation invokes the preserved Kira path, with all failed-attempt costs included. Generated coefficients remain exact. The integer transform cache is bounded to 128 loop orders, and all mass-dependent checks receive fresh inputs.

Coefficient records specify coefficient_format and coefficients_sha256. JSON objects retain the earlier arrays. Binary KXB1 objects contain a small JSON index, common-denominator symbolic polynomials and all expanded reduced fractions as signed base-256 integers. Their SHA256 addresses refer to uncompressed bytes; gzip level 6 stores them. source_choices and raw Kira evidence have separate hashes.

Use load_coeff(record) from s14_reader.py to obtain the identical legacy coefficient dictionaries with the compiled reader. s00_backend.py also provides the portable Python decoder. The compiled reader uses the recorded CPython 3.9 integer interface and must be rebuilt for another Python ABI. build/ records the compiler, Python, GMP version and binary hashes. s17_reader_run.sh records the build command; completed experiment wrappers must not be rerun over their frozen records.

Training uses 96 batches, five rules and three repetitions: 1,440 labels. Each label includes request reading, selection, exact reduction, independent checking and output writing in a warm worker. Training records preserve exact coefficient hashes, costs and inputs; temporary expanded training outputs are removed after each batch to bound scratch space. The tree has maximum depth four, at least six training batches per leaf, 19 fitted nodes and five log-time outputs. All 480 exported training-score comparisons match scikit-learn. The tree scores estimate runtime, without calibrated confidence or globally optimal-path claims.

The first validation has 12 batches and 324 measurements; it selects integer polynomials. Its independent reserved study has 360 cold applications and 144 stream applications. It passes all exact checks but establishes no complete-time gain once output decoding is included. These records remain in validation/ and model_test/.

The slow Python decoding observed during validation motivates the compiled reader. The trained model and arithmetic remain unchanged. reader_validation/ and reader_final_test/ use fresh mass profiles and targets, with a second freeze before testing. Each profile covers loop orders 1--12; the interface checks also cover 13, 16, 24 and 32. The second validation again has 324 measurements. An incomplete 360-application reader run remains in reader_test/ and is excluded because its selection step referenced the earlier validation set and its stream paths were incorrect. Matching source and the original freeze are preserved in development/reader_protocol_v1/. The corrected s21_reader_finish.sh freezes the prescribed choice from reader_validation/ and evaluates fresh reader_final_test/ inputs. The final test contains """+values["COLD"]+""" cold and 144 stream applications. Each stream has four batches; the three streams are disjoint.

complete_seconds includes input reading, model load and inference where used, recurrence selection, exact algebra, required checks and expansion. external_seconds adds process startup and output saving. roundtrip_seconds also includes reading and decoding every coefficient. The same wrapper and writer support matched controls. Independent reference audits and timing-record bookkeeping occur outside these production timers. Median repeat times and geometric ratios weight the twelve batches equally; bootstrap intervals describe this finite test. Stream ratios describe three specified sequences without an inferential interval.

Script sequence:
"""+scripts+"""

s06_run.sh builds/checks the original backend, then runs training, validation, freezing, testing and integration checks. s07_audit.py, s08_analyze.py and s09_plot.py preserve its independent audit, analysis and figures. s17_reader_run.sh preserves the initial reader build and validation launch; its incomplete comparison is documented above. s21_reader_finish.sh runs the corrected freeze and fresh reserved comparison, integration checks, audit, reader-cost comparison and plots. s12_report.sh updates documentation, verifies releases and renders the report; --data-commit pins its immutable citation.

resource_plan.json bounds retained records, scratch, Git copies, report growth and temporary pack/index space below the combined 10 GB ceiling. Only one experiment job runs at a time, using one CPU and a 2,800 MiB address-space cap. Kira fallback retains its 90-second, 1.5 GiB sampled tree-RSS and 64 MiB scratch limits. Scientific data and models stay on Hoffman and GitHub; the report also synchronizes locally. Earlier frozen studies and models remain unchanged.
""")
 descriptions={
 "build":"Compiled arithmetic and coefficient-reader libraries with source, compiler, dependency and ABI hashes. Rebuild for a different Python ABI.",
 "development":"Initial exact arithmetic and compiled-reader checks. Both precede their respective validation and reserved comparisons.",
 "training":"Ninety-six independent training batches, 1,440 complete warm-worker timing labels and exported-score parity checks. No validation or reserved targets train the tree.",
 "trained_model":"New 19-node, 49-feature cost regression tree. Its five outputs estimate log runtime for five recurrence rules. Earlier models remain unchanged.",
 "validation":"First 324 validation measurements. Their frozen selection and slower binary-reading results remain preserved.",
 "model_test":"First reserved comparison: 360 cold applications, 144 streamed applications and exact independent audits. Keep these outcomes separate from the later fresh reader test.",
 "reader_validation":"Second 324 validation measurements on fresh profiles. These choose the final mode and fixed-rule control before reader_final_freeze.json.",
 "reader_final_test":"Final independent reserved comparison, 36 stream runs, exact audits, interface checks, plots and direct measurements of both readers.",
 "objects":"Content-addressed exact coefficient and source-evidence objects. Filenames identify SHA256 of uncompressed bytes. JSON and KXB1 binary objects decode to equal coefficient arrays."}
 for folder,description in descriptions.items():(HERE/folder/"README.md").write_text(description+"\n")
 for stage in ["validation","model_test","reader_validation","reader_final_test"]:
  for sub,desc in [("inputs","Physical inputs fixed for this stage."),("results","Complete per-application records and exact coefficient references."),("streams","Three disjoint four-batch sequences, four configurations and three repetitions."),("stream_results","Individual applications referenced by the stream records."),("integration","Checks of physical-input isolation, invalid requests, worker limits, output integrity and Kira fallback."),("plots","Figures generated from preserved stage measurements.")]:
   folder=HERE/stage/sub
   if folder.exists():(folder/"README.md").write_text(desc+"\n")
 for path,link in [(ROOT/"README.md","ML_model_equation_selection/exact_backend/README.md"),(ROOT/"ML_model_equation_selection/README.md","exact_backend/README.md"),(ROOT/"Kira_comparison/README.md","../ML_model_equation_selection/exact_backend/README.md")]:
  old=path.read_text().replace("The current restricted vacuum-family interface shares exact loop-order transformations","The polynomial-reuse interface shares exact loop-order transformations")
  path.write_text(old);block(path,"exact-backend-current",status+"\n\nSee [exact arithmetic and batch strategies]("+link+").")
 block(ROOT/"report/README.md","exact-backend-current","exact_backend.tex explains retained integer polynomials, compiled exact expansion, lossless output, the runtime-trained batch tree and both frozen comparisons. It preserves the initial negative complete-time result, reports the fresh compiled-reader measurements and updates the conclusion. The supplied abstract remains unchanged. Source data are pinned by KiraExactBackendData.")
 write(HERE/"reader_final_test/document_values.json",values)
 print(status,flush=True)
if __name__=="__main__":main()
