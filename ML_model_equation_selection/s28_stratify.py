"""Stratify frozen test results by the topology route fixed in validation."""
import hashlib,json,pathlib
from s10_summarize import aggregate,ratio
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def main():
 config=json.loads((HERE/"trained_model/deployment.json").read_text())
 batches,rows=aggregate(HERE/"model_test")
 assert len(rows)==280 and all(r["success"] and r["reference_checked"] for r in rows)
 keys=sorted({k for b in batches for k in b["methods"] if k!="off:0"})
 subsets={t:[b for b in batches if b["topology"]==t] for t in sorted({b["topology"] for b in batches})}
 subsets["validation_enabled"]=[b for b in batches if config["by_topology"].get(b["topology"],{}).get("mode")=="learned"]
 stats={name:{k:{f:ratio(bs,k,f) for f in ["complete_seconds","equation_preparation_seconds","generated_equations"]} for k in keys} for name,bs in subsets.items()}
 result=dict(comparisons=stats,enabled_topologies=sorted({b["topology"] for b in subsets["validation_enabled"]}),selection="Topologies enabled before held-out testing, using validation only.",summary_sha256=hashlib.sha256((HERE/"model_test/summary.json").read_bytes()).hexdigest())
 (HERE/"model_test/topology_summary.json").write_text(json.dumps(result,indent=2)+"\n")
 a=stats["validation_enabled"]["auto:0"]
 def fmt(z):return f'{z["ratio"]:.3f}, with descriptive interval $[{z["interval95"][0]:.3f},{z["interval95"][1]:.3f}]$'
 text=r"\subsection{The domain selected before testing}"+"\n"
 text+="Validation enables the equation model for the sunrise and three-loop vacuum topologies. This identifies four of the eight test profiles before any test timing is available. On these profiles, the automatic route has a complete-time ratio of "+fmt(a["complete_seconds"])+". Its equation-preparation ratio is "+fmt(a["equation_preparation_seconds"])+". The corresponding generated-equation ratio is "+f'{a["generated_equations"]["ratio"]:.3f}'+".\n\n"
 for topology in ["sunrise","vacuum3","double_box","ladder3"]:
  if topology not in stats:continue
  z=stats[topology]["auto:0"]
  text+=f'For {topology.replace("_"," ")} profiles, the automatic complete-time ratio is {z["complete_seconds"]["ratio"]:.3f} and the preparation ratio is {z["equation_preparation_seconds"]["ratio"]:.3f}. '
 text+="The double-box and ladder routes retain native equation choices, so differences between their automatic and native timings mainly reflect repeated-run variation and routing overhead. The all-profile comparison remains the primary result; these fixed-domain results state where the learned filter was active.\n"
 (ROOT/"report/equation_selection_domain.tex").write_text(text)
 p=ROOT/"report/equation_selection_results.tex";s=p.read_text()
 if "\\input{equation_selection_domain}" not in s:s+="\n\\input{equation_selection_domain}\n"
 p.write_text(s)
 p=ROOT/"report/Makefile";s=p.read_text().replace("equation_selection_results.tex references.bib","equation_selection_results.tex equation_selection_domain.tex references.bib");p.write_text(s)
 print(json.dumps(dict(enabled_topologies=result["enabled_topologies"],ratios=a),indent=2))
if __name__=="__main__":main()
