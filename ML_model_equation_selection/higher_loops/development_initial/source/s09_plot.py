"""Make standalone figures from the frozen higher-loop cost audit."""
import os
from s00_math import *
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/".tools/cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def main():
 s=json.loads((HERE/"model_test/summary.json").read_text());out=HERE/"model_test/plots";out.mkdir(exist_ok=True)
 cases=sorted(s["batch_medians"]);methods=["separate_dense","separate_learned","shared_dense","shared_control","shared_learned"]
 labels=["Full pool, each loop","Learned, each loop","Full pool, shared z","Rule, shared z","Learned, shared z"]
 fig,ax=plt.subplots(figsize=(8.0,4.4));width=.15
 for k,(m,label) in enumerate(zip(methods,labels)):
  ax.bar([i+(k-2)*width for i in range(len(cases))],[s["batch_medians"][c][m]["external_seconds"] for c in cases],width,label=label)
 ax.set_xticks(range(len(cases)));ax.set_xticklabels([c.replace("test_","").replace("_",", ") for c in cases])
 ax.set_xlabel("Massive-denominator count R and maximum power B");ax.set_ylabel("Complete time for L=1,...,12 (s)")
 ax.legend(fontsize=8,ncol=2);ax.grid(axis="y",alpha=.2);fig.tight_layout();fig.savefig(out/"complete_times.pdf");plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(8.2,3.5))
 ratios=[s["per_loop_solver_ratios"][str(L)] for L in range(1,13)]
 axes[0].errorbar(range(1,13),[r["ratio"] for r in ratios],yerr=[[r["ratio"]-r["interval"][0] for r in ratios],[r["interval"][1]-r["ratio"] for r in ratios]],fmt="o-",capsize=2)
 axes[0].axhline(1,color="black",lw=.8);axes[0].set_xlabel("Loop order L");axes[0].set_ylabel("Learned / full-pool solver time");axes[0].set_xticks([1,3,6,9,12]);axes[0].grid(alpha=.2)
 for k,m in enumerate(["shared_dense","shared_control","shared_learned"]):
  axes[1].bar([i+(k-1)*.25 for i in range(len(cases))],[s["batch_medians"][c][m]["equations"] for c in cases],.25,label={"shared_dense":"Full pool","shared_control":"Rule","shared_learned":"Learned"}[m])
 axes[1].set_xticks(range(len(cases)));axes[1].set_xticklabels([c.replace("test_","").replace("_","\n") for c in cases],fontsize=8);axes[1].set_ylabel("Generated source equations");axes[1].legend(fontsize=8);axes[1].grid(axis="y",alpha=.2)
 fig.tight_layout();fig.savefig(out/"loops_and_equations.pdf");plt.close(fig)
 print("Higher-loop plots written",flush=True)
if __name__=="__main__":main()
