"""Check the rendered report against the frozen releases before publication."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/"report"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 published=read(HERE/"publication.json")
 assert published["training"]["status"]==published["tests"]["status"]=="pushed"
 update=read(HERE/"report_update.json");request=read(HERE/"request.json")
 assert update["data_commit"]==published["training"]["commit"]
 assert update["test_commit"]==published["tests"]["commit"]
 assert read(HERE/"test_release.json")["status"]=="both_frozen_tests_validated"
 text=(REPORT/"report.tex").read_text(encoding="utf-8")
 abstract=re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",text,re.S).group(1)
 assert hashlib.sha256(abstract.encode()).hexdigest()==request["abstract_sha256"]
 for name,digest in update["source_hashes"].items():assert sha(REPORT/name)==digest,name
 figures=[]
 for model in ("ML_model_seed_selection","ML_model_reduction"):
  folder=ROOT/model;test=folder/"model_test";trained=read(folder/"trained_model.json")
  assert trained["epochs_completed"]==20
  assert sha(folder/"trained_model.pt")==trained["model_sha256"]
  assert read(test/"validation.json")["status"]=="passed"
  entries=read(test/"figure_manifest.json")["figures"];assert len(entries)==6
  for entry in entries:
   name=entry if isinstance(entry,str) else entry["name"]
   p=test/"figures"/(name+".pdf");assert p.is_file(),p
   digest=sha(p)
   matches=[f for f in (REPORT/"figures").glob("*.pdf") if sha(f)==digest]
   assert matches,("Missing current report plot",model,name)
   figures.append(dict(model=model,name=name,sha256=digest,report_paths=[str(f.relative_to(REPORT)) for f in matches]))
 tex="\n".join(p.read_text(encoding="utf-8") for p in REPORT.glob("*.tex"))
 assert not re.search(r"@[A-Z_0-9]+@",tex)
 labels=re.findall(r"\\label\{([^}]+)\}",tex)
 assert len(labels)==len(set(labels)),"Duplicate LaTeX labels"
 refs=re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",tex)
 assert not set(refs)-set(labels),set(refs)-set(labels)
 for name in re.findall(r"\\input\{([^}]+)\}",tex):
  assert (REPORT/(name if name.endswith(".tex") else name+".tex")).is_file(),name
 bibliography=(REPORT/"references.bib").read_text(encoding="utf-8")
 keys=set(re.findall(r"@\w+\{([^,]+),",bibliography))
 cites=set(k.strip() for group in re.findall(r"\\cite(?:p|t)?(?:\[[^]]*\])*\{([^}]+)\}",tex) for k in group.split(","))
 assert not cites-keys,cites-keys
 for commit in (update["data_commit"],update["test_commit"]):assert commit in bibliography
 log=(REPORT/"report.log").read_text(encoding="utf-8",errors="replace")
 bad=[line for line in log.splitlines() if "undefined" in line.lower() or "Fatal error" in line or "Emergency stop" in line]
 assert not bad,bad
 pdf=REPORT/"report.pdf";data=pdf.read_bytes()
 sources=list(REPORT.glob("*.tex"))+list(REPORT.glob("*.bib"))+list((REPORT/"figures").glob("*.pdf"))
 latest_source=max(p.stat().st_mtime for p in sources)
 assert pdf.stat().st_mtime+2>=latest_source,"Rendered PDF predates its current sources"
 assert (REPORT/"report.log").stat().st_mtime+2>=latest_source,"LaTeX log predates its current sources"
 assert data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:] and len(data)>100000
 checks=dict(status="rendered_report_checks_passed",pdf_sha256=sha(pdf),abstract_sha256=request["abstract_sha256"],
  data_commit=update["data_commit"],test_commit=update["test_commit"],figures=figures,
  source_hashes={str(p.relative_to(REPORT)):sha(p) for p in sorted(REPORT.rglob("*")) if p.is_file() and p.suffix in (".tex",".bib",".pdf")},
  visual_review="pending_local_review_after_publication")
 (HERE/"report_validation.json").write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 update.update(status="rendered_report_checked_publication_pending",pdf_sha256=checks["pdf_sha256"])
 (HERE/"report_update.json").write_text(json.dumps(update,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print("Report sources, references, twelve current plots and rendered PDF passed release checks.",flush=True)
if __name__=="__main__":main()
