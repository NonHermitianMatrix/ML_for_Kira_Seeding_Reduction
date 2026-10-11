"""Write measured cumulative results into the scientific report and READMEs."""
from s00_cumulative import *
import argparse,re
def replace_block(text,start,end,body):
 value=start+"\n"+body+"\n"+end
 if start in text:return text.split(start,1)[0]+value+text.split(end,1)[1]
 return text.rstrip()+"\n\n"+value+"\n"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");a=ap.parse_args()
 s=read(HERE/"test/summary.json");assert s["all_exact"];audit=s["audit"]
 c=s["comparisons"]["original_kira"];chain=s["comparisons"]["chain_baseline"]
 main=c["roundtrip_seconds"];calculation=c["complete_seconds"]
 fmt=lambda x:format(x,".6f" if 0<x<0.01 else ".3f")
 pct=lambda x:format(x,".2f")
 low,high=main["speedup_interval95"];rlo,rhi=main["ratio_interval95"]
 totals=s["sum_of_batch_medians"];orig=totals["original_kira"]["roundtrip_seconds"];final=totals["final"]["roundtrip_seconds"]
 values=dict(speed=fmt(main["speedup"]),saved=pct(main["time_saved_percent"]),ratio=fmt(main["time_ratio"]),lower=fmt(low),upper=fmt(high),rlo=fmt(rlo),rhi=fmt(rhi),chain_speed=fmt(chain["roundtrip_seconds"]["speedup"]),chain_ratio=fmt(chain["roundtrip_seconds"]["time_ratio"]),calc_speed=fmt(calculation["speedup"]),calc_ratio=fmt(calculation["time_ratio"]),base_seconds=fmt(orig),final_seconds=fmt(final),workload_speed=fmt(orig/final),positions=str(audit["expanded_coefficient_positions"]),systems=str(audit["regenerated_systems"]),raw_positions=str(audit["sympy_raw_export_positions"]),rss=fmt(audit["peak_tree_rss_bytes"]/1024**2),scratch=fmt(audit["peak_scratch_bytes"]/1024**2))
 template=(HERE/"report_template.tex.in").read_text()
 for k,v in values.items():template=template.replace("@"+k+"@",v)
 assert not re.search(r"@[a-z_]+@",template)
 (ROOT/"report/cumulative_speedup.tex").write_text(template)
 p=ROOT/"report/equation_selection.tex";text=p.read_text()
 if r"\input{cumulative_speedup}" not in text:text=text.rstrip()+"\n\n"+r"\input{cumulative_speedup}"+"\n"
 p.write_text(text)
 p=ROOT/"report/Makefile";text=p.read_text()
 if "cumulative_speedup.tex" not in text:text=text.replace("exact_backend.tex references.bib","exact_backend.tex cumulative_speedup.tex references.bib")
 p.write_text(text)
 conclusion=(r"The direct cumulative comparison uses the saved original Kira executable and the final deployed route on identical restricted vacuum targets at every loop order from one through twelve. "
 +r"Eight independent mass-profile groups and five repetitions of three methods give 120 complete workflows. "
 +r"Including process startup, output saving and output reading, the final-to-original time ratio is "+values["ratio"]+r", corresponding to "+values["speed"]+r" times faster execution and "+values["saved"]+r"\% less time. "
 +r"The descriptive 95\% speedup interval is \(["+values["lower"]+","+values["upper"]+r"]\). "
 +r"All matched outputs agree exactly, and the independent audit checks "+values["positions"]+r" nonzero target--master coefficient polynomials after loop-order substitution. "
 +r"This directly measures the cumulative change without multiplying earlier ratios. The gain includes shared symbolic reductions, direct checked recurrences, compiled arithmetic and output changes. The selected route uses a fixed recurrence rule and makes no Kira call on these successful cases, so the result retains the restricted supplied-identity scope \cite{KiraCumulativeData}.")
 p=ROOT/"report/report.tex";text=p.read_text();start="% BEGIN CUMULATIVE CONCLUSION";end="% END CUMULATIVE CONCLUSION"
 if start in text:text=replace_block(text,start,end,conclusion)
 else:text=text.replace("\\clearpage\n\\renewcommand{\\refname}{Citations}",start+"\n"+conclusion+"\n"+end+"\n\n\\clearpage\n\\renewcommand{\\refname}{Citations}")
 abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 p.write_text(text)
 citation=ROOT/"report/references.bib";bib=citation.read_text()
 link="https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"+(a.data_commit or "main")+"/Kira_comparison/cumulative_speedup"
 if not a.data_commit and "% cumulative-data-begin" in bib:
  previous=bib.split("% cumulative-data-begin",1)[1].split("% cumulative-data-end",1)[0]
  match=re.search(r"/tree/([0-9a-f]{40})/",previous)
  if match:link=link.replace("/tree/main/","/tree/"+match[1]+"/")
 body=r"""@misc{KiraCumulativeData,
 author = {Saraswat, Rushil},
 title = {Direct cumulative speedup comparison on identical restricted vacuum integrals},
 year = {2026},
 howpublished = {\href{LINK}{Frozen original and final implementations, identical inputs, timing records and exact audits}}
}""".replace("LINK",link)
 citation.write_text(replace_block(bib,"% cumulative-data-begin","% cumulative-data-end",body))
 summary=("The direct cumulative comparison uses eight new groups of three restricted vacuum mass profiles, loop orders 1--12, and five repetitions of three methods. All 120 workflows pass exact checks. Relative to the original saved Kira binary with the full supplied equation pool and separate loop reductions, the final route has total-time ratio "+values["ratio"]+", speedup "+values["speed"]+"x (descriptive 95% interval "+values["lower"]+"--"+values["upper"]+"), and "+values["saved"]+"% less time, including startup, saving and output reading. Against the earlier full-pool pipeline binary, the speedup is "+values["chain_speed"]+"x. The selected final route uses a fixed recurrence and exact direct arithmetic. The result measures the complete restricted-family replacement; it does not establish a corresponding native general-IBP or ML-only speedup.")
 for p in [ROOT/"README.md",ROOT/"Kira_comparison/README.md",ROOT/"ML_model_equation_selection/README.md",HERE/"README.md"]:
  text=p.read_text()
  text=text.replace("Status: comparison code prepared; results pending. Scientific data stay on Hoffman and GitHub. The final report will also be synchronized locally.","Status: complete. Scientific data stay on Hoffman and GitHub; the complete report is also synchronized locally.")
  text=text.replace("Status: the corrected pilot passed all three methods; the frozen reserved comparison is running. Scientific data stay on Hoffman and GitHub. The final report will also be synchronized locally.","Status: complete. Scientific data stay on Hoffman and GitHub; the complete report is also synchronized locally.")
  text=replace_block(text,"<!-- cumulative-results-begin -->","<!-- cumulative-results-end -->",summary)
  p.write_text(text)
 p=HERE/"README.md";text=p.read_text()
 if "s05_audit.py verifies" not in text:text+="\ns05_audit.py verifies every saved coefficient, regenerates each unique baseline system and independently reads selected raw Kira coefficients with SymPy. s06_analyze.py reports matched ratios, descriptive batch-bootstrap intervals and absolute times. s07_plot.py writes the standalone comparison figure. s08_document.py updates the report and READMEs; s09_finish.sh runs the final audit, analysis and report build. test/environment.json records the node and executable versions. test/summary.json contains every batch median, metric and aggregate. The pilot is excluded from reported speedups. No older policy, training record or checkpoint is changed.\n"
 p.write_text(text)
 guard();print(summary,flush=True)
if __name__=="__main__":main()
