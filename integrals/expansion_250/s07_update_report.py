"""Finalize the report after both expanded-data tests pass; keep immutable data citations."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/"report"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);ap.add_argument("--test-commit",required=True);args=ap.parse_args()
 assert all(re.fullmatch("[0-9a-f]{40}",v) for v in (args.data_commit,args.test_commit))
 summary=read(HERE/"integration_summary.json");assert summary["families"]==5100 and summary["targets"]==765272
 for name in ("ML_model_seed_selection","ML_model_reduction"):
  assert read(ROOT/name/"model_test/validation.json")["status"]=="passed"
  assert read(ROOT/name/"trained_model.json")["epochs_completed"]==20
 subprocess.run([sys.executable,str(ROOT/"ML_model_seed_selection/model_test/s06_update_report.py")],check=True)
 subprocess.run([sys.executable,str(ROOT/"ML_model_reduction/model_test/s07_update_report.py")],check=True)
 (REPORT/"higher_loops.tex").write_text((HERE/"report_section_template.tex").read_text(encoding="utf-8"),encoding="utf-8")
 path=REPORT/"report.tex";s=path.read_text(encoding="utf-8")
 abstract=re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",s,re.S).group(1)
 old="""The following subsections define the initial families and construction
method, then explain the additional mass and kinematic conditions and
the resulting data. All integrals remain symbolic throughout."""
 new="""We first added 100 restricted coupled-vacuum mass profiles at each
loop order from two through twelve, then 250 further profiles at each
order from one through twelve. The complete collection contains
5,100 family instances, 21,967 master entries and 765,272 targets.
The following subsections define the earlier construction and then
derive the added vacuum bases and reverse targets.
Every target retains its exact symbolic definition and master
expansion."""
 if old in s:s=s.replace(old,new)
 prior="""We then added 100 restricted coupled-vacuum mass profiles at each
loop order from two through twelve, giving a complete collection of
2,100 family instances, 12,967 master entries and 381,272 targets.
The following subsections define the earlier construction and then
derive the added vacuum bases and reverse targets.
Every target retains its exact symbolic definition and master
expansion."""
 prior=prior.replace("derive the added vacuum bases","derive the added higher-loop bases")
 if prior in s:s=s.replace(prior,new)
 s=s.replace("The combined collection contains 9,678 master entries and",
             "Before the higher-loop extension, the collection contained 9,678 master entries and")
 s=s.replace("Individual targets with more positive denominator indices and\nadditional high-loop families require further constructions.",
             "The higher-loop construction below supplies additional individual targets and expressions in coupled vacuum families.")
 s=s.replace("across the complete\ncollection. We replayed all 240,472",
             "across this earlier\ncollection. We replayed all 240,472")
 s=s.replace("The combined split contains 771 training families with",
             "The original data-generation split contained 771 training families with")
 if "\\input{higher_loops}" not in s:s=s.replace("\\input{seed_model}","\\input{higher_loops}\n\n\\input{seed_model}")
 assert re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",s,re.S).group(1)==abstract
 roles=(HERE/"ml_roles_section_template.tex").read_text(encoding="utf-8")
 start=s.index(r"\section{ML for seed selection and elimination ordering}")
 end=s.index(r"\section{Target Integral Generation for Machine Learning}",start)
 s=s[:start]+roles+s[end:]
 s=s.replace("families, the collection contains 997 one-loop and three two-loop",
             "families, this earlier collection contained 997 one-loop and three two-loop")
 s=s.replace("The validation set contains 183 individual integrals and",
             "The original data-generation validation set contained 183 individual integrals and")
 s=s.replace("while the test set contains 202", "while the corresponding test set contained 202")
 s=s.replace("These counts specify\nthe available tests for each target type.",
             "These counts describe\nthe original construction samples. The grouped model division\ndescribed below replaces this three-way data-generation division.")
 s=re.sub(r"\\date\{[^}]*\}",lambda m:r"\date{October 6, 2026}",s)
 path.write_text(s,encoding="utf-8")
 make=REPORT/"Makefile";text=make.read_text(encoding="utf-8")
 if "background.tex higher_loops.tex" not in text:text=text.replace("report.tex background.tex","report.tex background.tex higher_loops.tex")
 make.write_text(text,encoding="utf-8")
 path=REPORT/"reduction_model.tex";text=path.read_text(encoding="utf-8")
 text=text.replace("693 families with 168,330 targets supply training records, while\n307 families with 72,142 targets remain reserved for testing.",
                   "3,563 families with 535,690 targets supply training records, while\n1,537 families with 229,582 targets remain reserved for testing.")
 text=text.replace('1,463 families with 266,890 targets supply training records, while\n637 families with 114,382 targets remain reserved for testing.','3,563 families with 535,690 targets supply training records, while\n1,537 families with 229,582 targets remain reserved for testing.')
 start=text.index("Training first completed ten passes through the training choice states") if "Training first completed ten passes through the training choice states" in text else text.index("We continued the saved")
 end=text.index("\n\\input{reduction_training}",start)
 text=text[:start]+"""We continued the saved expanded-data model and optimizer for twenty
complete passes over the enlarged training states. The new phase
retains the architecture and optimizer settings while adding 250
mass profiles at every represented loop order. Preparation replays every selected row
operation with exact modular arithmetic and verifies its final
recorded master row. Training shuffles states within bounded
groups of families and retains complete resume states.
The reserved families remain outside parameter updates and
confidence fitting. Earlier project stages evaluated the preceding
held-out families; the current experiment also reserves the newly
assigned mass profiles at every added loop order.
"""+text[end:]
 path.write_text(text,encoding="utf-8")
 bib=REPORT/"references.bib";b=bib.read_text(encoding="utf-8")
 def citation(key,title,commit,folder,description):
  return ("@misc{"+key+",\n  author = {Saraswat, Rushil},\n  title = {"+title+"},\n  year = {2026},\n"+
    "  howpublished = {\\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"+
    commit+"/"+folder+"}{"+description+"}}\n}\n")
 replacements={
 "HigherLoopIntegralData":citation("HigherLoopIntegralData","Coupled Vacuum Master Bases and Reverse Targets through Twelve Loops",args.data_commit,"integrals","Family definitions, source identities, grouped splits and independent checks"),
 "SeedModelTestData":citation("SeedModelTestData","Seed-Selection Model after Twenty Expanded-Data Passes: Held-Out Tests through Twelve Loops",args.test_commit,"ML_model_seed_selection/model_test","Frozen predictions, metrics, plots and validation records"),
 "ReductionModelData":citation("ReductionModelData","Reduction-Propagation Model Trained on Integral Families through Twelve Loops",args.data_commit,"ML_model_reduction","Model, optimizer lineage, state features and training records"),
 "ReductionModelTestData":citation("ReductionModelTestData","Expanded-Data Reduction Model: Held-Out Next-Step and Complete-Path Tests",args.test_commit,"ML_model_reduction/model_test","Frozen predictions, exact row replays, plots and validation")}
 for key,entry in replacements.items():
  pattern=r"@misc\{"+re.escape(key)+r",.*?\n\}\n"
  if re.search(pattern,b,re.S):b=re.sub(pattern,lambda m:entry,b,flags=re.S)
  else:b+="\n"+entry
 bib.write_text(b,encoding="utf-8")
 for name in ("seed_model","reduction_model","reduction_training","seed_model_test","reduction_test","higher_loops"):
  text=(REPORT/(name+".tex")).read_text(encoding="utf-8")
  assert not re.search(r"@[A-Z_0-9]+@",text),name
 report_readme=REPORT/"README.md"
 notes=report_readme.read_text(encoding="utf-8")
 cut=notes.find("The report now includes the completed ten-pass")
 if cut!=-1:notes=notes[:cut].rstrip()+"\n\n"
 else:notes=notes.split("<!-- expanded-report -->")[0].rstrip()+"\n\n"
 notes+="<!-- expanded-report -->\n"
 notes+=("The current report describes 5,100 family instances, 21,967 family-local master entries and 765,272 targets. "
         "The latest addition contains 250 restricted coupled-vacuum mass profiles at each loop order from one through twelve, following the earlier 100 profiles at orders two through twelve. "
         "higher_loops.tex derives their master bases, exact identities, reverse target construction and grouped division.\n\n"
         "seed_model.tex and reduction_model.tex describe the two models and their twenty new passes over 535,690 training targets. "
         "seed_model_test.tex and reduction_test.tex give the frozen results for 229,582 targets in 1537 held-out families. "
         "reduction_training.tex records the expanded-data reduction training. The twelve current PDF plots are in figures/. "
         "Earlier checkpoints and tests remain in the model archives on Hoffman and GitHub.\n\n"
         "The report distinguishes reference-set agreement from seed sufficiency, recorded next-action agreement from complete reductions, "
         "and sampled finite-field checks from symbolic reconstruction. The added family domain and shared lower-sector physics limit "
         "claims about generic high-loop integrals, unseen loop orders and full Kira speedups.\n\n"
         "The bibliography links the expanded data and models to commit "+args.data_commit+" and the tested outputs to commit "+args.test_commit+". "
         "Raw data, models and predictions remain on Hoffman and GitHub; only the complete report is synchronized locally.\n")
 report_readme.write_text(notes,encoding="utf-8")
 record=dict(status="sources_updated_pdf_pending",data_commit=args.data_commit,test_commit=args.test_commit,
   source_hashes={p.name:sha(p) for p in REPORT.glob("*.tex")},abstract_preserved=True)
 (HERE/"report_update.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(record),flush=True)
if __name__=="__main__":main()
