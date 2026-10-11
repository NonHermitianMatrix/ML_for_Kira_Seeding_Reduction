"""Verify both frozen studies, exact evidence, report references and storage bounds."""
import ast,re
from s16_reader_study import *
def main():
 check_freeze()
 archived=HERE/"development/reader_protocol_v1"
 for name,digest in read(archived/"reader_freeze.json")["sha256"].items():
  path=ROOT/name
  if path.name in ["s15_application.py","s16_reader_study.py"]:path=archived/path.name
  assert sha(path)==digest,name
 assert len(list((HERE/"reader_test/results").glob("*.json")))==360
 for folder in ["higher_loops","early_generation"]:
  for n,h in read(HERE.parent/folder/"trained_model/freeze.json").get("sha256",{}).items():assert sha(ROOT/n)==h,n
 total=0
 for stage in ["model_test","reader_final_test"]:
  audit=read(HERE/stage/"audit.json");assert audit["all_exact"] and audit["stream_applications"]==144
  assert read(HERE/stage/"summary.json")["all_exact"] and read(HERE/stage/"integration/summary.json")["all_passed"];total+=audit["applications"]
 assert read(HERE/"development/kernel_check.json")["exact_checks"]==3277
 assert read(HERE/"development/reader_check.json")["all_passed"]
 for p in (HERE/"objects").glob("*.gz"):
  h=p.name.split(".")[0];assert hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()==h
 for p in HERE.glob("*.py"):ast.parse(p.read_text())
 guard();plan=read(HERE/"resource_plan.json");tools=allocated(ROOT/".tools/kira-exact-backend");assert tools<plan["new_tools_cap_bytes"]
 text=(ROOT/"report/report.tex").read_text();abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 tex="\n".join(p.read_text() for p in (ROOT/"report").glob("*.tex"))
 labels=set(re.findall(r"\\label\{([^}]+)\}",tex));refs=set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",tex));assert refs<=labels,refs-labels
 cites={k for v in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",tex) for k in v.split(",")}
 keys=set(re.findall(r"@\w+\{([^,]+),",(ROOT/"report/references.bib").read_text()));assert cites<=keys,cites-keys
 assert "@@" not in (ROOT/"report/exact_backend.tex").read_text()
 for name in ["exact_backend_reader_times.pdf","exact_backend_reader_streams.pdf"]:
  assert sha(ROOT/"report/figures"/name)==sha(HERE/"reader_final_test/plots"/name)
 write(HERE/"reader_final_test/release_check.json",dict(all_passed=True,applications=total,earlier_freezes_preserved=True,excluded_run_preserved=True,abstract_preserved=True,report_references_resolved=True,combined_storage_upper_bytes=plan["combined_upper_bytes"]))
 print("release checks passed",total,allocated(HERE),plan["combined_upper_bytes"],flush=True)
if __name__=="__main__":main()
