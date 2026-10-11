"""Export standalone figures for exact arithmetic and persistent processing."""
from s00_arithmetic import *
def main():
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 s=json.loads((HERE/"model_test/summary.json").read_text());groups=s["groups"]
 fig,axes=plt.subplots(1,2,figsize=(9.2,3.9))
 for ax,key,title in zip(axes,["complete_seconds","external_seconds"],["Complete calculation","Including startup and output saving"]):
  for variant,label in [("baseline","Previous arithmetic"),("transforms","Shared loop transforms"),("taylor","Shared Taylor terms"),("both","Both changes")]:
   ax.plot(range(1,9),[g["medians"][variant][key] for g in groups],marker="o",markersize=3,label=label)
  ax.set_xlabel("Reserved batch");ax.set_ylabel("Median time (s)");ax.set_ylim(bottom=0);ax.set_title(title,fontsize=10);ax.grid(alpha=.2)
 handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc="lower center",ncol=2,fontsize=8)
 fig.tight_layout(rect=[0,.13,1,1])
 for dest in [HERE/"model_test/plots/polynomial_reuse_times.pdf",ROOT/"report/figures/polynomial_reuse_times.pdf"]:
  dest.parent.mkdir(parents=True,exist_ok=True);fig.savefig(dest,bbox_inches="tight")
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.8,3.7));methods=["baseline_cold","baseline_stream","optimized_cold","optimized_stream"];labels=["Previous, separate workers","Previous, persistent worker","Updated, separate workers","Updated, persistent worker"]
 for k,(m,label) in enumerate(zip(methods,labels)):
  ax.bar([i+(k-1.5)*.19 for i in range(3)],[v["median_external_seconds"][m] for v in s["sequences"]],width=.19,label=label)
 ax.set_xticks(range(3));ax.set_xticklabels(["First four batches","Last four batches","All eight batches"])
 ax.set_ylabel("Median total stream time (s)");ax.set_ylim(bottom=0);ax.legend(fontsize=8);ax.grid(axis="y",alpha=.2)
 fig.tight_layout()
 for dest in [HERE/"model_test/plots/polynomial_reuse_streams.pdf",ROOT/"report/figures/polynomial_reuse_streams.pdf"]:fig.savefig(dest,bbox_inches="tight")
 plt.close(fig)
if __name__=="__main__":main()
