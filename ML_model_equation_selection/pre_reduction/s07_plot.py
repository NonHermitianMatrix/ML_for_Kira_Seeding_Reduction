"""Standalone plots from matched independent measurements."""
from s00_contract import *
def main():
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 s=json.loads((HERE/"model_test/summary.json").read_text());groups=s["groups"];methods=["baseline","model","direct_model","direct_extreme","direct_analytic"]
 labels=["Prior learned + Kira","Pre-reduced + Kira","Learned exact shortcut","Simple exact shortcut","Analytic control"]
 fig,axes=plt.subplots(1,2,figsize=(9.2,3.9))
 for ax,key,title in zip(axes,["complete_seconds","external_seconds"],["Calculation, including exact checks","Full worker, including output saving"]):
  for m,label in zip(methods,labels):
   ax.plot(range(1,len(groups)+1),[g["medians"][m][key] for g in groups],marker="o",markersize=3,label=label)
  ax.set_xlabel("Reserved batch");ax.set_ylabel("Median time (s)");ax.set_title(title,fontsize=10);ax.grid(alpha=.2);ax.set_ylim(bottom=0)
 handles,names=axes[0].get_legend_handles_labels();fig.legend(handles,names,loc="lower center",ncol=3,fontsize=8)
 fig.tight_layout(rect=[0,.13,1,1])
 for p in [HERE/"model_test/plots/pre_reduction_times.pdf",ROOT/"report/figures/pre_reduction_times.pdf"]:
  p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(p,bbox_inches="tight")
 plt.close(fig)
if __name__=="__main__":main()
