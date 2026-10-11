"""Check frozen methods, exact evidence, report references and resource bounds."""
import ast,re
from s04_study import *
def main():
 check_freeze()
 for folder in ["higher_loops","early_generation"]:
  for n,h in json.loads((HERE.parent/folder/"trained_model/freeze.json").read_text()).get("sha256",{}).items():assert base.sha(ROOT/n)==h,n
 audit=json.loads((HERE/"model_test/audit.json").read_text());summary=json.loads((HERE/"model_test/summary.json").read_text())
 assert audit["all_exact"] and audit["applications"]==352 and audit["expanded_coefficient_positions"]==28860
 assert summary["all_exact"] and summary["single_applications"]==160 and summary["stream_applications"]==192
 assert json.loads((HERE/"model_test/integration/summary.json").read_text())["all_passed"]
 assert json.loads((HERE/"validation/kernel_check.json").read_text())["all_passed"]
 for p in (HERE/"objects").glob("*.json.gz"):assert hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()==p.name[:-8]
 for p in HERE.glob("*.py"):ast.parse(p.read_text())
 guard();plan=json.loads((HERE/"resource_plan.json").read_text())
 tools=allocated(ROOT/".tools/kira-polynomial-reuse");assert tools<plan["new_tools_cap_bytes"]
 text=(ROOT/"report/report.tex").read_text();abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 tex="\n".join(p.read_text() for p in (ROOT/"report").glob("*.tex"))
 labels=set(re.findall(r"\\label\{([^}]+)\}",tex));refs=set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",tex));assert refs<=labels,refs-labels
 cites={k for v in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",tex) for k in v.split(",")}
 keys=set(re.findall(r"@\w+\{([^,]+),",(ROOT/"report/references.bib").read_text()));assert cites<=keys,cites-keys
 assert "@@" not in (ROOT/"report/polynomial_reuse.tex").read_text()
 assert base.sha(ROOT/"report/figures/polynomial_reuse_times.pdf")==base.sha(HERE/"model_test/plots/polynomial_reuse_times.pdf")
 assert base.sha(ROOT/"report/figures/polynomial_reuse_streams.pdf")==base.sha(HERE/"model_test/plots/polynomial_reuse_streams.pdf")
 base.write(HERE/"model_test/release_check.json",dict(all_passed=True,applications=352,earlier_freezes_preserved=True,abstract_preserved=True,report_references_resolved=True,combined_storage_upper_bytes=plan["combined_upper_bytes"]))
 print("release checks passed",allocated(HERE),plan["combined_upper_bytes"])
if __name__=="__main__":main()
