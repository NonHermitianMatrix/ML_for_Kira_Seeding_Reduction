"""Reproducible figures of complete exact application times."""
import os
os.environ["MPLCONFIGDIR"]=str(__import__("pathlib").Path(__file__).resolve().parents[2]/".tools/cache/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from s00_common import *
def main():
 summary=json.loads((HERE/"model_test/summary.json").read_text());native=json.loads((HERE/"model_test/native_summary.json").read_text())
 dest=HERE/"model_test/plots";dest.mkdir(exist_ok=True)
 plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"savefig.bbox":"tight"})
 cases=sorted(summary["case_medians"]["previous"],key=lambda s:int(s.split("_")[1]))
 fig,ax=plt.subplots(figsize=(7.2,3.8))
 for j,(m,label,color) in enumerate([("previous","Previous workflow","#777777"),("extreme","Shared checks + simple rule","#377eb8"),("model","Shared checks + learned order","#d95f02")]):
  ax.bar([i+(j-1)*.25 for i in range(len(cases))],[summary["case_medians"][m][c]["complete_seconds"] for c in cases],width=.24,label=label,color=color)
 ax.set_xticks(range(len(cases)));ax.set_xticklabels([s.replace("test_","").replace("_","/") for s in cases],rotation=45,ha="right")
 ax.set_ylabel("Complete calculation time (s)");ax.set_xlabel("Reserved batch: ID / massive denominators / maximum power")
 ax.legend(fontsize=8);fig.tight_layout();fig.savefig(dest/"batch_reuse_single.pdf");plt.close(fig)
 groups=sorted(native["case_medians"]["previous"])
 fig,ax=plt.subplots(figsize=(7.2,3.8))
 styles=[("previous","Previous separate calls","#777777"),("control","Combined + simple rule","#377eb8"),("python","Combined + learned model","#d95f02"),("native","Combined + compiled model","#1b9e77")]
 for j,(m,label,color) in enumerate(styles):
  ax.bar([i+(j-1.5)*.2 for i in range(len(groups))],[native["case_medians"][m][g]["complete_seconds"] for g in groups],width=.19,label=label,color=color)
 ax.set_xticks(range(len(groups)));ax.set_xticklabels(["9 / 32","13 / 32","9 / 80","13 / 80"])
 ax.set_ylabel("Complete calculation time (s)");ax.set_xlabel("Maximum power / requested targets per family (three profiles per batch)")
 ax.legend(fontsize=8);fig.tight_layout();fig.savefig(dest/"batch_reuse_packed.pdf");plt.close(fig)
 for p in dest.glob("*.pdf"):(ROOT/"report/figures"/p.name).write_bytes(p.read_bytes())
if __name__=="__main__":main()
