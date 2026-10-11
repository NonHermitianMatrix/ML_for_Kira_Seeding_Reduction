"""Verify frozen code, exact evidence, report references and resource bounds."""
import ast,re
from s00_contract import *
from s02_study import check_freeze
def main():
 check_freeze()
 for folder in ["higher_loops","early_generation"]:
  p=HERE.parent/folder/"trained_model/freeze.json"
  for n,h in json.loads(p.read_text()).get("sha256",{}).items():assert base.sha(ROOT/n)==h,n
 assert json.loads((HERE/"model_test/summary.json").read_text())["all_exact"]
 assert json.loads((HERE/"model_test/audit.json").read_text())["workflows"]==200
 assert json.loads((HERE/"model_test/integration/summary.json").read_text())["all_passed"]
 for p in (HERE/"objects").glob("*.json.gz"):assert hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()==p.name[:-8]
 for p in HERE.glob("*.py"):ast.parse(p.read_text())
 guard();plan=json.loads((HERE/"resource_plan.json").read_text())
 tools=allocated(ROOT/".tools/kira-pre-reduction");assert tools<plan["new_tools_cap_bytes"]
 text=(ROOT/"report/report.tex").read_text();abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 tex="\n".join(p.read_text() for p in (ROOT/"report").glob("*.tex"))
 labels=set(re.findall(r"\\label\{([^}]+)\}",tex));refs=set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",tex));assert refs<=labels,refs-labels
 cites={k for v in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",tex) for k in v.split(",")}
 keys=set(re.findall(r"@\w+\{([^,]+),",(ROOT/"report/references.bib").read_text()));assert cites<=keys,cites-keys
 base.write(HERE/"model_test/release_check.json",dict(all_passed=True,applications=200,earlier_freezes_preserved=True,abstract_preserved=True,report_references_resolved=True,retained_allocated_bytes=allocated(HERE),tools_allocated_bytes=tools,combined_storage_upper_bytes=plan["combined_upper_bytes"]))
 print("release checks passed",allocated(HERE),plan["combined_upper_bytes"])
if __name__=="__main__":main()
