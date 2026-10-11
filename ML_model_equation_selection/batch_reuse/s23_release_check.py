"""Release guards for exactness, unchanged earlier studies and the storage ceiling."""
import ast,gzip
from s00_common import *
def main():
 for name in ["trained_model/freeze.json","trained_model/native_freeze.json"]:
  freeze=json.loads((HERE/name).read_text())
  for n,h in freeze["sha256"].items():assert sha(ROOT/n)==h,n
 for path in [OLD/"trained_model/freeze.json",HERE.parent/"early_generation/trained_model/freeze.json"]:
  if path.exists():
   data=json.loads(path.read_text())
   for n,h in data.get("sha256",{}).items():assert sha(ROOT/n)==h,n
 summaries={n:json.loads((HERE/"model_test"/n).read_text()) for n in ["summary.json","pack_summary.json","native_summary.json"]}
 assert summaries["summary.json"]["workflows"]==300
 assert summaries["pack_summary.json"]["workflows"]==80
 assert summaries["native_summary.json"]["workflows"]==80
 assert all(x["all_exact"] for x in summaries.values())
 assert json.loads((HERE/"model_test/integration/summary.json").read_text())["all_passed"]
 assert json.loads((HERE/"training/native_check.json").read_text())["all_passed"]
 for p in HERE.glob("*.py"):ast.parse(p.read_text())
 plan=json.loads((HERE/"resource_plan.json").read_text())
 retained=sum(p.stat().st_blocks*512 for p in HERE.rglob("*") if p.is_file())
 tools=sum(p.stat().st_blocks*512 for p in (ROOT/".tools/kira-batch-reuse").rglob("*") if p.is_file())
 assert retained<plan["new_retained_cap_bytes"] and tools<plan["new_tools_cap_bytes"]
 assert plan["combined_upper_bytes"]<10000000000
 for p in (HERE/"objects").glob("*.json.gz"):
  data=gzip.decompress(p.read_bytes());assert hashlib.sha256(data).hexdigest()==p.name[:-8]
 text=(ROOT/"report/report.tex").read_text()
 abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 import re
 tex="\n".join(p.read_text() for p in (ROOT/"report").glob("*.tex"))
 labels=set(re.findall(r"\\label\{([^}]+)\}",tex));references=set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",tex))
 assert references<=labels,sorted(references-labels)
 cites={k for values in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",tex) for k in values.split(",")}
 keys=set(re.findall(r"@\w+\{([^,]+),",(ROOT/"report/references.bib").read_text()))
 assert cites<=keys,sorted(cites-keys)
 write(HERE/"model_test/release_check.json",dict(all_passed=True,reserved_applications=460,earlier_freezes_preserved=True,retained_allocated_bytes=retained,tools_allocated_bytes=tools,combined_storage_upper_bytes=plan["combined_upper_bytes"],abstract_preserved=True,all_latex_references_resolved=True))
 print("release checks passed",retained,plan["combined_upper_bytes"],flush=True)
if __name__=="__main__":main()
